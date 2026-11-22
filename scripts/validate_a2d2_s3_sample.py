#!/usr/bin/env python3
"""Bounded anonymous S3 preflight for A2D2 semantic/instance label PNGs.

A2D2 stores RGB frames under camera/cam_front_center/ and pixel labels under
label/cam_front_center/. The label basename uses _label_frontcenter_ rather
than _camera_frontcenter_. This script downloads at most one image+mask pair
per annotation root, to a temporary directory, and never downloads archives.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from PIL import Image

BUCKET = "audi-autonomous-driving-dataset"
REGION = "eu-central-1"
ROOTS = ("camera_lidar_semantic/", "camera_lidar_semantic_instance/")
MAX_SEQUENCES_PER_ROOT = 8
MAX_SAMPLE_BYTES = 80 * 1024 * 1024


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def image_to_label_key(image_key: str, sequence_prefix: str) -> str:
    filename = image_key.rsplit("/", 1)[-1]
    label_name = re.sub(r"_camera_frontcenter_", "_label_frontcenter_", filename)
    return sequence_prefix + "label/cam_front_center/" + label_name


def image_info(path: str) -> dict:
    with Image.open(path) as image:
        image.load()
        return {
            "format": image.format, "mode": image.mode,
            "width": image.width, "height": image.height,
        }


def main() -> int:
    s3 = boto3.client(
        "s3", region_name=REGION,
        config=Config(signature_version=UNSIGNED, retries={"max_attempts": 3}),
    )
    report = {
        "bucket": BUCKET, "region": REGION, "anonymous_access": False,
        "roots": {}, "status": "FAIL",
        "note": "PASS confirms one decodable RGB/mask pair per available root, not full-dataset coverage or official metric equivalence.",
    }
    root_listing = s3.list_objects_v2(Bucket=BUCKET, Delimiter="/", MaxKeys=100)
    report["anonymous_access"] = True
    report["available_root_prefixes"] = [
        item["Prefix"] for item in root_listing.get("CommonPrefixes", [])
    ]

    with tempfile.TemporaryDirectory(prefix="a2d2-preflight-") as tmp:
        for root_prefix in ROOTS:
            root_sequences = s3.list_objects_v2(
                Bucket=BUCKET, Prefix=root_prefix, Delimiter="/", MaxKeys=100
            )
            sequences = [x["Prefix"] for x in root_sequences.get("CommonPrefixes", [])]
            result = {"sequence_prefixes_seen": len(sequences), "sample": None}
            for sequence_prefix in sequences[:MAX_SEQUENCES_PER_ROOT]:
                camera_prefix = sequence_prefix + "camera/cam_front_center/"
                label_prefix = sequence_prefix + "label/cam_front_center/"
                camera_response = s3.list_objects_v2(
                    Bucket=BUCKET, Prefix=camera_prefix, MaxKeys=1000
                )
                label_response = s3.list_objects_v2(
                    Bucket=BUCKET, Prefix=label_prefix, MaxKeys=1000
                )
                label_keys = {x["Key"] for x in label_response.get("Contents", [])}
                candidates = [
                    x["Key"] for x in camera_response.get("Contents", [])
                    if x["Key"].lower().endswith(".png")
                ]
                pair = next(
                    ((key, image_to_label_key(key, sequence_prefix))
                     for key in candidates
                     if image_to_label_key(key, sequence_prefix) in label_keys),
                    None,
                )
                if pair:
                    image_key, mask_key = pair
                    image_path = os.path.join(tmp, "image.png")
                    mask_path = os.path.join(tmp, "mask.png")
                    for key, target in ((image_key, image_path), (mask_key, mask_path)):
                        head = s3.head_object(Bucket=BUCKET, Key=key)
                        size = int(head["ContentLength"])
                        if size > MAX_SAMPLE_BYTES:
                            raise RuntimeError(f"Refusing oversized sample ({size} bytes): {key}")
                        s3.download_file(BUCKET, key, target)
                    image_meta = image_info(image_path)
                    mask_meta = image_info(mask_path)
                    with Image.open(mask_path) as mask:
                        colors = len(set(mask.convert("RGB").getdata()))
                    result["sample"] = {
                        "image_key": image_key, "mask_key": mask_key,
                        "image_bytes": os.path.getsize(image_path),
                        "image_sha256": sha256(image_path),
                        "mask_bytes": os.path.getsize(mask_path),
                        "mask_sha256": sha256(mask_path),
                        "image": image_meta, "mask": mask_meta,
                        "dimensions_match": (
                            image_meta["width"] == mask_meta["width"]
                            and image_meta["height"] == mask_meta["height"]
                        ),
                        "unique_mask_colors": colors,
                    }
                    break
            report["roots"][root_prefix] = result

    semantic = report["roots"].get("camera_lidar_semantic/", {}).get("sample")
    instance = report["roots"].get("camera_lidar_semantic_instance/", {}).get("sample")
    report["status"] = (
        "PASS_SEMANTIC_SAMPLE" if semantic and semantic["dimensions_match"]
        else "INCOMPLETE_SEMANTIC_SAMPLE"
    )
    report["instance_sample_status"] = (
        "SAMPLE_DECODED_PENDING_INSTANCE_ID_ANALYSIS"
        if instance and instance["dimensions_match"] else "NOT_CONFIRMED"
    )
    report["class_mapping_status"] = "PENDING_CLASS_LIST_JSON_AND_COLOR_MAP"
    with open("a2d2_s3_preflight_report.json", "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS_SEMANTIC_SAMPLE" else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        failure = {"status": "FAIL", "error": repr(exc), "bucket": BUCKET}
        with open("a2d2_s3_preflight_report.json", "w", encoding="utf-8") as handle:
            json.dump(failure, handle, indent=2)
        print(json.dumps(failure, indent=2), file=sys.stderr)
        raise
