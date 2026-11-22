#!/usr/bin/env python3
"""Bounded anonymous S3 preflight for A2D2 semantic/instance label PNGs.

RGB images live in camera_lidar_semantic/<sequence>/camera/cam_front_center/.
Semantic masks live in the matching label/cam_front_center/ directory and use
_label_frontcenter_ in the filename. The instance-labelled mirror is inspected
separately, pairing its label file with the RGB frame from the semantic root.
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
SEMANTIC_ROOT = "camera_lidar_semantic/"
INSTANCE_ROOT = "camera_lidar_semantic_instance/"
MAX_SEQUENCES = 12
MAX_SAMPLE_BYTES = 80 * 1024 * 1024


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def label_key_for(image_key: str, sequence_prefix: str) -> str:
    filename = image_key.rsplit("/", 1)[-1]
    label_name = re.sub(r"_camera_frontcenter_", "_label_frontcenter_", filename)
    return sequence_prefix + "label/cam_front_center/" + label_name


def describe_image(path: str) -> dict:
    with Image.open(path) as image:
        image.load()
        return {
            "format": image.format, "mode": image.mode,
            "width": image.width, "height": image.height,
        }


def list_sequences(s3, prefix: str) -> list[str]:
    response = s3.list_objects_v2(
        Bucket=BUCKET, Prefix=prefix, Delimiter="/", MaxKeys=100
    )
    return [item["Prefix"] for item in response.get("CommonPrefixes", [])]


def find_label_for_sequence(s3, sequence_prefix: str, image_key: str):
    key = label_key_for(image_key, sequence_prefix)
    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return key
    except Exception:
        return None


def download_pair(s3, image_key: str, mask_key: str, tmp: str, tag: str) -> dict:
    image_path = os.path.join(tmp, f"{tag}_image.png")
    mask_path = os.path.join(tmp, f"{tag}_mask.png")
    for key, target in ((image_key, image_path), (mask_key, mask_path)):
        head = s3.head_object(Bucket=BUCKET, Key=key)
        size = int(head["ContentLength"])
        if size > MAX_SAMPLE_BYTES:
            raise RuntimeError(f"Refusing oversized sample ({size} bytes): {key}")
        s3.download_file(BUCKET, key, target)
    image_meta, mask_meta = describe_image(image_path), describe_image(mask_path)
    with Image.open(mask_path) as mask:
        colors = mask.convert("RGB").getcolors(maxcolors=100000)
        unique_colors = len(colors) if colors is not None else None
        color_values = sorted([list(color) for _, color in colors])[:60] if colors else []
    return {
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
        "unique_mask_colors": unique_colors,
        "mask_rgb_colors_sample": color_values,
    }


def main() -> int:
    s3 = boto3.client(
        "s3", region_name=REGION,
        config=Config(signature_version=UNSIGNED, retries={"max_attempts": 3}),
    )
    report = {
        "bucket": BUCKET, "region": REGION, "anonymous_access": False,
        "semantic": {"sample": None}, "instance": {"sample": None},
        "class_list_candidates": [], "status": "FAIL",
        "note": "A readable mask pair is a sample-level check, not full-dataset coverage or official metric equivalence.",
    }
    root_listing = s3.list_objects_v2(Bucket=BUCKET, Delimiter="/", MaxKeys=100)
    report["anonymous_access"] = True
    report["available_root_prefixes"] = [
        item["Prefix"] for item in root_listing.get("CommonPrefixes", [])
    ]

    # Look for the official class map at common extracted-mirror locations.
    for key in (
        "class_list.json",
        SEMANTIC_ROOT + "class_list.json",
        SEMANTIC_ROOT + "20180807_145028/class_list.json",
    ):
        try:
            head = s3.head_object(Bucket=BUCKET, Key=key)
            report["class_list_candidates"].append(
                {"key": key, "bytes": int(head["ContentLength"])}
            )
        except Exception:
            continue

    class_list_key = next(
        (item["key"] for item in report["class_list_candidates"]), None
    )
    class_map = {}
    if class_list_key:
        class_list_path = os.path.join(tempfile.gettempdir(), "a2d2_class_list_preflight.json")
        s3.download_file(BUCKET, class_list_key, class_list_path)
        with open(class_list_path, encoding="utf-8") as handle:
            class_list = json.load(handle)
        class_map = class_list if isinstance(class_list, dict) else {}
        report["class_list"] = {
            "json_type": type(class_list).__name__,
            "class_count": len(class_map),
            "keys": sorted(class_map.keys())[:80] if isinstance(class_list, dict) else None,
            "sample_entries": (
                list(class_list.items())[:12] if isinstance(class_list, dict)
                else class_list[:12] if isinstance(class_list, list) else None
            ),
        }
        os.remove(class_list_path)

    semantic_sequences = list_sequences(s3, SEMANTIC_ROOT)
    semantic_image = None
    semantic_sequence = None
    with tempfile.TemporaryDirectory(prefix="a2d2-preflight-") as tmp:
        for sequence_prefix in semantic_sequences[:MAX_SEQUENCES]:
            camera_prefix = sequence_prefix + "camera/cam_front_center/"
            camera_response = s3.list_objects_v2(
                Bucket=BUCKET, Prefix=camera_prefix, MaxKeys=1000
            )
            images = [
                item["Key"] for item in camera_response.get("Contents", [])
                if item["Key"].lower().endswith(".png")
            ]
            for image_key in images:
                mask_key = find_label_for_sequence(s3, sequence_prefix, image_key)
                if mask_key:
                    semantic_image, semantic_sequence = image_key, sequence_prefix
                    report["semantic"]["sample"] = download_pair(
                        s3, image_key, mask_key, tmp, "semantic"
                    )
                    break
            if semantic_image:
                break

        instance_sequences = list_sequences(s3, INSTANCE_ROOT)
        instance_diagnostics = []
        if semantic_image and semantic_sequence:
            frame_name = semantic_image.rsplit("/", 1)[-1]
            matching_sequence = INSTANCE_ROOT + semantic_sequence[len(SEMANTIC_ROOT):]
            instance_mask_key = label_key_for(
                semantic_image, matching_sequence
            )
            try:
                s3.head_object(Bucket=BUCKET, Key=instance_mask_key)
                report["instance"]["sample"] = download_pair(
                    s3, semantic_image, instance_mask_key, tmp, "instance"
                )
            except Exception:
                # Explore label paths in a bounded number of sequences to
                # distinguish absent annotations from a filename/layout mismatch.
                for sequence_prefix in instance_sequences[:MAX_SEQUENCES]:
                    label_prefix = sequence_prefix + "label/cam_front_center/"
                    labels = s3.list_objects_v2(
                        Bucket=BUCKET, Prefix=label_prefix, MaxKeys=1000
                    ).get("Contents", [])
                    pngs = [x["Key"] for x in labels if x["Key"].lower().endswith(".png")]
                    instance_diagnostics.append({
                        "sequence": sequence_prefix,
                        "label_png_count": len(pngs),
                        "first_label_keys": pngs[:3],
                    })
                    match = next((key for key in pngs if key.rsplit("/", 1)[-1]
                                  == re.sub(r"_camera_frontcenter_", "_label_frontcenter_", frame_name)), None)
                    if match:
                        report["instance"]["sample"] = download_pair(
                            s3, semantic_image, match, tmp, "instance"
                        )
                        break
        report["instance"]["sequence_prefixes_seen"] = len(instance_sequences)
        report["instance"]["diagnostics"] = instance_diagnostics[:MAX_SEQUENCES]

    semantic = report["semantic"]["sample"]
    instance = report["instance"]["sample"]
    report["status"] = (
        "PASS_SEMANTIC_SAMPLE" if semantic and semantic["dimensions_match"]
        else "INCOMPLETE_SEMANTIC_SAMPLE"
    )
    if semantic and class_map:
        mapped = []
        for rgb in semantic.get("mask_rgb_colors_sample", []):
            color_key = "#{:02x}{:02x}{:02x}".format(*rgb)
            mapped.append({"color": color_key, "class_name": class_map.get(color_key)})
        report["semantic"]["mask_color_mapping"] = mapped
        instance_names = [
            value for value in class_map.values()
            if re.match(r"^(car|truck|pedestrian|bicycle|cyclist|motor biker|motorcycle)\\s+[1-4]$", str(value), re.I)
        ]
        report["semantic"]["instance_subclass_names_found"] = sorted(instance_names)
    report["instance_sample_status"] = (
        "SEPARATE_INSTANCE_MASK_SAMPLE_DECODED_PENDING_ID_ANALYSIS"
        if instance and instance["dimensions_match"]
        else "INSTANCE_SUBCLASSES_PRESENT_PENDING_COMPONENT_EXTRACTION"
        if report.get("semantic", {}).get("instance_subclass_names_found")
        else "NOT_CONFIRMED"
    )
    report["class_mapping_status"] = (
        "CLASS_LIST_FOUND_PENDING_PARSE"
        if report["class_list_candidates"] else "PENDING_CLASS_LIST_LOCATION"
    )
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
