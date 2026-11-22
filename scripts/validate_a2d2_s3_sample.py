#!/usr/bin/env python3
"""Bounded anonymous S3 layout/sample preflight for A2D2.

The extracted mirror stores semantic data under camera_lidar_semantic/ and
instance-related data under camera_lidar_semantic_instance/. This diagnostic
downloads at most one front-center PNG plus its same-stem JSON sidecar from
each available root, then inspects the JSON structure. It does not assume the
sidecar is a raster mask or certify annotation semantics.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from PIL import Image

BUCKET = "audi-autonomous-driving-dataset"
REGION = "eu-central-1"
ROOTS = ("camera_lidar_semantic/", "camera_lidar_semantic_instance/")
MAX_OBJECTS_PER_ROOT = 5000
MAX_SAMPLE_BYTES = 80 * 1024 * 1024


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_shape(value):
    if isinstance(value, dict):
        return {"type": "object", "keys": sorted(value.keys())[:80]}
    if isinstance(value, list):
        return {"type": "array", "length": len(value),
                "first_item": json_shape(value[0]) if value else None}
    return {"type": type(value).__name__}


def main() -> int:
    s3 = boto3.client(
        "s3", region_name=REGION,
        config=Config(signature_version=UNSIGNED, retries={"max_attempts": 3}),
    )
    report = {
        "bucket": BUCKET, "region": REGION, "anonymous_access": False,
        "roots": {}, "status": "FAIL",
        "note": "A readable image/JSON pair is a layout check only; semantic and instance encodings require separate decoding.",
    }
    root = s3.list_objects_v2(Bucket=BUCKET, Delimiter="/", MaxKeys=100)
    report["anonymous_access"] = True
    report["available_root_prefixes"] = [
        item["Prefix"] for item in root.get("CommonPrefixes", [])
    ]

    with tempfile.TemporaryDirectory(prefix="a2d2-preflight-") as tmp:
        for prefix in ROOTS:
            response = s3.list_objects_v2(
                Bucket=BUCKET, Prefix=prefix, MaxKeys=MAX_OBJECTS_PER_ROOT
            )
            keys = [item["Key"] for item in response.get("Contents", [])]
            candidates = [
                key for key in keys
                if key.lower().endswith(".png")
                and "/camera/cam_front_center/" in f"/{key}"
            ]
            selected = None
            key_set = set(keys)
            for image_key in candidates:
                json_key = image_key[:-4] + ".json"
                if json_key in key_set:
                    selected = (image_key, json_key)
                    break
            entry = {
                "listed_objects": len(keys),
                "is_truncated": response.get("IsTruncated", False),
                "candidate_front_center_pngs": len(candidates),
                "sample": None,
            }
            if selected:
                image_key, json_key = selected
                image_path = os.path.join(tmp, prefix.replace("/", "_") + "_image.png")
                json_path = os.path.join(tmp, prefix.replace("/", "_") + "_sidecar.json")
                for key, target in ((image_key, image_path), (json_key, json_path)):
                    head = s3.head_object(Bucket=BUCKET, Key=key)
                    size = int(head["ContentLength"])
                    if size > MAX_SAMPLE_BYTES:
                        raise RuntimeError(f"Refusing oversized sample object ({size} bytes): {key}")
                    s3.download_file(BUCKET, key, target)
                with Image.open(image_path) as image:
                    image.load()
                    image_info = {
                        "format": image.format, "mode": image.mode,
                        "width": image.width, "height": image.height,
                    }
                with open(json_path, encoding="utf-8") as handle:
                    annotation = json.load(handle)
                entry["sample"] = {
                    "image_key": image_key, "json_key": json_key,
                    "image_bytes": os.path.getsize(image_path),
                    "image_sha256": sha256(image_path),
                    "json_bytes": os.path.getsize(json_path),
                    "json_sha256": sha256(json_path),
                    "image": image_info,
                    "json_shape": json_shape(annotation),
                }
            report["roots"][prefix] = entry

    semantic_sample = report["roots"].get("camera_lidar_semantic/", {}).get("sample")
    report["status"] = "PASS_SAMPLE_LAYOUT" if semantic_sample else "INCOMPLETE_LAYOUT"
    report["semantic_annotation_decoding"] = "PENDING"
    report["instance_annotation_decoding"] = (
        "SAMPLE_AVAILABLE_PENDING_FORMAT_INSPECTION"
        if report["roots"].get("camera_lidar_semantic_instance/", {}).get("sample")
        else "NOT_CONFIRMED"
    )
    with open("a2d2_s3_preflight_report.json", "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))
    return 0 if semantic_sample else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        failure = {"status": "FAIL", "error": repr(exc), "bucket": BUCKET}
        with open("a2d2_s3_preflight_report.json", "w", encoding="utf-8") as handle:
            json.dump(failure, handle, indent=2)
        print(json.dumps(failure, indent=2), file=sys.stderr)
        raise
