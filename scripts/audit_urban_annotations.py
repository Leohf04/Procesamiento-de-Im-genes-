#!/usr/bin/env python3
"""Audit class coverage and annotation consistency on a bounded manifest sample.

Downloads only selected rows (per split) to the runner's temporary storage.
It does not redistribute source images or annotations.
"""
from __future__ import annotations

import argparse
import io
import json
import random
import re
import tempfile
from collections import Counter
from pathlib import Path

import boto3
import numpy as np
from botocore import UNSIGNED
from botocore.config import Config
from PIL import Image
from huggingface_hub import hf_hub_download

from src.data_adapters import (
    DEFAULT_CANONICAL_CLASSES, decode_a2d2_instances, decode_a2d2_semantic,
    decode_urbansyn_panoptic, decode_urbansyn_semantic, load_a2d2_class_list,
    normalize_class_name,
)

A2D2_BUCKET = "audi-autonomous-driving-dataset"
A2D2_REGION = "eu-central-1"
URBANSYN_REPO = "UrbanSyn/UrbanSyn"
DYNAMIC_IDS = set(range(11, 19))


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def deterministic_sample(records: list[dict], count: int, seed: int) -> list[dict]:
    """Choose stable, bounded samples without changing the original manifests."""
    return sorted(records, key=lambda row: __import__("hashlib").sha256(
        f"{seed}:{row['sample_id']}".encode()).hexdigest())[:count]


def color_histogram(rgb: np.ndarray) -> Counter:
    colors, counts = np.unique(rgb.reshape(-1, 3), axis=0, return_counts=True)
    return Counter({tuple(int(v) for v in color): int(n) for color, n in zip(colors, counts)})


def audit_a2d2(manifest_dir: Path, samples_per_split: int) -> dict:
    s3 = boto3.client("s3", region_name=A2D2_REGION,
                      config=Config(signature_version=UNSIGNED, retries={"max_attempts": 5}))
    class_list_obj = s3.get_object(Bucket=A2D2_BUCKET, Key="camera_lidar_semantic/class_list.json")
    class_map_raw = json.loads(class_list_obj["Body"].read())
    color_to_name = load_a2d2_class_list(class_map_raw)
    canonical_hist, source_hist, instance_hist = Counter(), Counter(), Counter()
    unknown_colors, checks = Counter(), []
    selected_total = 0

    for split in ("train", "val", "test"):
        records = read_jsonl(manifest_dir / f"a2d2_{split}.jsonl")
        chosen = deterministic_sample(records, samples_per_split, 2026)
        for row in chosen:
            rgb_key = row["assets"]["rgb"].split(f"s3://{A2D2_BUCKET}/", 1)[1]
            mask_key = row["assets"]["semantic"].split(f"s3://{A2D2_BUCKET}/", 1)[1]
            rgb_bytes = s3.get_object(Bucket=A2D2_BUCKET, Key=rgb_key)["Body"].read()
            mask_bytes = s3.get_object(Bucket=A2D2_BUCKET, Key=mask_key)["Body"].read()
            with Image.open(io.BytesIO(rgb_bytes)) as im:
                rgb_size = im.size
            with Image.open(io.BytesIO(mask_bytes)) as im:
                mask = np.asarray(im.convert("RGB"))
            if rgb_size != (mask.shape[1], mask.shape[0]):
                raise ValueError(f"A2D2 dimensions mismatch: {row['sample_id']}")
            hist = color_histogram(mask)
            semantic = decode_a2d2_semantic(mask, color_to_name)
            instances = decode_a2d2_instances(mask, color_to_name, min_component_area=8)
            pixel_count = mask.shape[0] * mask.shape[1]
            for color, count in hist.items():
                name = color_to_name.get(color)
                if name is None:
                    unknown_colors[str(color)] += count
                    continue
                source_hist[name] += count
                canonical = normalize_class_name(name)
                if canonical in DEFAULT_CANONICAL_CLASSES:
                    canonical_hist[canonical] += count
            for label, count in zip(*np.unique(instances["labels"], return_counts=True)):
                instance_hist[str(int(label))] += int(count)
            if semantic.shape != mask.shape[:2] or int((semantic != 255).sum()) == 0:
                raise ValueError(f"A2D2 semantic decoder produced empty/invalid map: {row['sample_id']}")
            checks.append({
                "split": split, "sample_id": row["sample_id"], "size": list(rgb_size),
                "unique_source_colors": len(hist), "mapped_semantic_pixels": int((semantic != 255).sum()),
                "ignored_pixels": int((semantic == 255).sum()),
                "instance_components": int(len(instances["labels"])),
                "instance_labels": sorted(int(x) for x in np.unique(instances["labels"])),
                "pixel_count": pixel_count,
            })
            selected_total += 1

    return {
        "dataset": "a2d2", "manifest_counts": {
            s: len(read_jsonl(manifest_dir / f"a2d2_{s}.jsonl")) for s in ("train", "val", "test")},
        "sampled_per_split": samples_per_split, "samples_audited": selected_total,
        "class_list_entries": len(class_map_raw),
        "source_pixel_counts": dict(sorted(source_hist.items())),
        "canonical_pixel_counts": dict(sorted(canonical_hist.items())),
        "instance_pixel_counts_by_canonical_id": dict(sorted(instance_hist.items())),
        "unknown_color_pixel_counts": dict(unknown_colors),
        "samples": checks,
        "caveat": "A2D2 instance labels are reconstructed from participant sub-class colors and connected components; occlusion fragmentation remains a known limitation."
    }


def _bbox_record_count(value) -> int | None:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        for key in ("objects", "annotations", "bboxes", "boxes", "labels", "instances"):
            if isinstance(value.get(key), list):
                return len(value[key])
    return None


def audit_urbansyn(manifest_dir: Path, samples_per_split: int) -> dict:
    reports, semantic_hist, panoptic_hist = [], Counter(), Counter()
    bbox_counts, agreement = [], []
    revision = None
    for split in ("train", "val", "test"):
        records = read_jsonl(manifest_dir / f"urbansyn_{split}.jsonl")
        chosen = deterministic_sample(records, samples_per_split, 2026)
        for row in chosen:
            revision = row.get("revision", revision)
            local = {}
            for kind in ("rgb", "semantic", "panoptic", "bbox"):
                local[kind] = hf_hub_download(
                    repo_id=URBANSYN_REPO, repo_type="dataset",
                    revision=row["revision"], filename=row["assets"][kind])
            with Image.open(local["rgb"]) as im:
                size = im.size
                if im.mode != "RGB":
                    raise ValueError(f"UrbanSyn RGB is not RGB: {row['sample_id']}")
            with Image.open(local["semantic"]) as im:
                raw_sem = np.asarray(im)
                sem = raw_sem[..., 0] if raw_sem.ndim == 3 else raw_sem
            with Image.open(local["panoptic"]) as im:
                pan = np.asarray(im.convert("RGB"))
            if sem.shape[:2] != (size[1], size[0]) or pan.shape[:2] != (size[1], size[0]):
                raise ValueError(f"UrbanSyn dimensions mismatch: {row['sample_id']}")
            sem_ids, sem_counts = np.unique(sem, return_counts=True)
            for class_id, count in zip(sem_ids, sem_counts):
                semantic_hist[str(int(class_id))] += int(count)
            pan_ids, pan_counts = np.unique(pan[..., 2], return_counts=True)
            for class_id, count in zip(pan_ids, pan_counts):
                panoptic_hist[str(int(class_id))] += int(count)
            if np.any(sem > 19) or np.any(pan[..., 2] > 19):
                raise ValueError(f"UrbanSyn class ID outside expected 0..19: {row['sample_id']}")
            decoded_sem = decode_urbansyn_semantic(sem)
            dynamic_map = {i: i for i in DYNAMIC_IDS}
            decoded = decode_urbansyn_panoptic(pan, dynamic_map)
            # Panoptic class-channel agreement against semseg, only where the
            # panoptic class denotes a dynamic object.
            dynamic_pixels = np.isin(pan[..., 2], list(DYNAMIC_IDS))
            agree = float(np.mean(sem[dynamic_pixels] == pan[..., 2][dynamic_pixels])) if dynamic_pixels.any() else None
            bbox_data = json.loads(Path(local["bbox"]).read_text(encoding="utf-8"))
            bbox_count = _bbox_record_count(bbox_data)
            bbox_counts.append(bbox_count)
            agreement.append(agree)
            reports.append({
                "split": split, "sample_id": row["sample_id"], "size": list(size),
                "semantic_ids": [int(x) for x in sem_ids],
                "panoptic_class_ids": [int(x) for x in pan_ids],
                "semantic_panoptic_dynamic_pixel_agreement": agree,
                "decoded_instances": int(len(decoded["labels"])),
                "instance_labels": sorted(int(x) for x in np.unique(decoded["labels"])),
                "bbox_json_type": type(bbox_data).__name__,
                "bbox_record_count": bbox_count,
            })
    return {
        "dataset": "urbansyn", "revision": revision,
        "manifest_counts": {
            s: len(read_jsonl(manifest_dir / f"urbansyn_{s}.jsonl")) for s in ("train", "val", "test")},
        "sampled_per_split": samples_per_split, "samples_audited": len(reports),
        "semantic_pixel_counts_by_source_id": dict(sorted(semantic_hist.items(), key=lambda x: int(x[0]))),
        "panoptic_pixel_counts_by_source_class_id": dict(sorted(panoptic_hist.items(), key=lambda x: int(x[0]))),
        "bbox_record_counts": bbox_counts,
        "mean_dynamic_pixel_class_agreement": float(np.mean([x for x in agreement if x is not None])) if any(x is not None for x in agreement) else None,
        "samples": reports,
        "class_names": "Not assigned: source class-ID-to-name mapping still requires authoritative dataset metadata.",
        "license_status": "REVIEW_REQUIRED_CONFLICTING_DECLARATIONS",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-dir", type=Path, required=True)
    parser.add_argument("--samples-per-split", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path("annotation_audit_report.json"))
    args = parser.parse_args()
    if not 1 <= args.samples_per_split <= 50:
        parser.error("--samples-per-split must be between 1 and 50")
    report = {
        "method": "deterministic sample from each existing manifest split",
        "samples_per_split": args.samples_per_split,
        "a2d2": audit_a2d2(args.manifest_dir, args.samples_per_split),
        "urbansyn": audit_urbansyn(args.manifest_dir, args.samples_per_split),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
