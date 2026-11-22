#!/usr/bin/env python3
"""Bounded anonymous S3 preflight for A2D2; never downloads dataset archives."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import PurePosixPath

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from PIL import Image

BUCKET = "audi-autonomous-driving-dataset"
REGION = "eu-central-1"
MAX_SEQUENCE_PREFIXES = 8
MAX_OBJECTS_PER_SEQUENCE = 5000
MAX_SAMPLE_BYTES = 80 * 1024 * 1024


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    s3 = boto3.client(
        "s3",
        region_name=REGION,
        config=Config(signature_version=UNSIGNED, retries={"max_attempts": 3}),
    )
    report = {
        "bucket": BUCKET,
        "region": REGION,
        "anonymous_access": False,
        "root_prefixes": [],
        "sample": None,
        "instance_related_keys": [],
        "status": "FAIL",
    }

    root = s3.list_objects_v2(Bucket=BUCKET, Delimiter="/", MaxKeys=100)
    report["anonymous_access"] = True
    prefixes = [x["Prefix"] for x in root.get("CommonPrefixes", [])]
    report["root_prefixes"] = prefixes[:30]
    if not prefixes:
        raise RuntimeError("Anonymous bucket listing succeeded but returned no sequence prefixes")

    selected = None
    inspected = []
    for sequence_prefix in prefixes[:MAX_SEQUENCE_PREFIXES]:
        response = s3.list_objects_v2(
            Bucket=BUCKET, Prefix=sequence_prefix, MaxKeys=MAX_OBJECTS_PER_SEQUENCE
        )
        keys = [x["Key"] for x in response.get("Contents", [])]
        inspected.extend(keys[:30])
        camera_candidates = [
            key for key in keys
            if key.lower().endswith((".png", ".jpg", ".jpeg"))
            and "/camera/cam_front_center/" in f"/{key}"
        ]
        for image_key in camera_candidates:
            label_key = image_key.replace("/camera/", "/label/", 1)
            if label_key in keys:
                selected = (image_key, label_key)
                break
        if selected:
            break

    report["sample_search_preview"] = inspected[:60]
    if not selected:
        report["status"] = "INCOMPLETE_LAYOUT"
        report["note"] = (
            "Anonymous bucket listing works, but no front_center image/label pair "
            "was found within the bounded prefix scan. Inspect artifact preview."
        )
        with open("a2d2_s3_preflight_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print(json.dumps(report, indent=2))
        return 2

    image_key, label_key = selected
    report["sample"] = {"image_key": image_key, "semantic_label_key": label_key}
    instance_keys = [
        key for key in inspected
        if any(token in key.lower() for token in ("instance", "panoptic", "label3d"))
    ]
    report["instance_related_keys"] = instance_keys[:30]

    with tempfile.TemporaryDirectory(prefix="a2d2-preflight-") as tmp:
        image_path = os.path.join(tmp, "image")
        label_path = os.path.join(tmp, "label")
        for key, target in ((image_key, image_path), (label_key, label_path)):
            head = s3.head_object(Bucket=BUCKET, Key=key)
            size = int(head["ContentLength"])
            if size > MAX_SAMPLE_BYTES:
                raise RuntimeError(f"Refusing oversized sample object ({size} bytes): {key}")
            s3.download_file(BUCKET, key, target)
        with Image.open(image_path) as image:
            image.load()
            image_info = {
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
            }
        with Image.open(label_path) as mask:
            mask.load()
            label_info = {
                "format": mask.format,
                "mode": mask.mode,
                "width": mask.width,
                "height": mask.height,
                "unique_rgb_colors_sample": len(set(mask.convert("RGB").getdata())),
            }
        report["sample"].update({
            "image_bytes": os.path.getsize(image_path),
            "image_sha256": sha256(image_path),
            "label_bytes": os.path.getsize(label_path),
            "label_sha256": sha256(label_path),
            "image": image_info,
            "semantic_label": label_info,
            "dimensions_match": (
                image_info["width"] == label_info["width"]
                and image_info["height"] == label_info["height"]
            ),
        })

    # A2D2's official paper describes instance masks for traffic participants,
    # but the public extracted mirror must be inspected to establish whether
    # instance IDs are independently encoded or reconstructed from polygons.
    report["instance_annotation_status"] = (
        "RELATED_FILES_FOUND" if instance_keys else
        "NO_SEPARATE_INSTANCE_FILE_IN_BOUNDED_SCAN"
    )
    report["status"] = (
        "PASS_SEMANTIC_SAMPLE" if report["sample"]["dimensions_match"]
        else "FAIL_DIMENSION_MISMATCH"
    )
    report["note"] = (
        "This preflight verifies anonymous S3 access and one RGB/semantic-mask pair. "
        "It does not certify instance-mask encoding, detection labels, condition metadata, "
        "or full-dataset coverage."
    )
    with open("a2d2_s3_preflight_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS_SEMANTIC_SAMPLE" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        failure = {"status": "FAIL", "error": repr(exc), "bucket": BUCKET}
        with open("a2d2_s3_preflight_report.json", "w") as f:
            json.dump(failure, f, indent=2)
        print(json.dumps(failure, indent=2), file=sys.stderr)
        raise
