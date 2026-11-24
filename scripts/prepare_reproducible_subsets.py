#!/usr/bin/env python3
"""Create deterministic, remote-reference manifests for bounded urban subsets.

No image or annotation payload is downloaded. Splits are experimental hash splits,
not official dataset splits. A2D2 is grouped by sequence; UrbanSyn currently has
no verified sequence metadata in the public file index, so IDs are grouped alone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Iterable

SPLITS = ("train", "val", "test")
DEFAULT_RATIOS = (0.8, 0.1, 0.1)


def stable_digest(seed: int, group_id: str) -> str:
    return hashlib.sha256(f"{seed}:{group_id}".encode("utf-8")).hexdigest()


def assign_split(group_id: str, seed: int = 2026,
                 ratios: tuple[float, float, float] = DEFAULT_RATIOS) -> str:
    if len(ratios) != 3 or any(x <= 0 for x in ratios) or abs(sum(ratios) - 1.0) > 1e-9:
        raise ValueError("ratios must be three positive values summing to 1")
    value = int(stable_digest(seed, group_id)[:16], 16) / float(16**16)
    if value < ratios[0]:
        return "train"
    if value < ratios[0] + ratios[1]:
        return "val"
    return "test"


def select_subset(records: Iterable[dict], *, seed: int, max_per_split: int | None):
    grouped: dict[str, list[dict]] = {name: [] for name in SPLITS}
    seen: set[tuple[str, str]] = set()
    for record in records:
        required = ("dataset", "sample_id", "group_id", "assets")
        if any(key not in record for key in required):
            raise ValueError(f"record missing required keys: {record}")
        key = (str(record["dataset"]), str(record["sample_id"]))
        if key in seen:
            raise ValueError(f"duplicate sample: {key}")
        seen.add(key)
        split = assign_split(str(record["group_id"]), seed)
        grouped[split].append(record)
    selected = {}
    for split, items in grouped.items():
        items.sort(key=lambda r: stable_digest(seed, str(r["sample_id"])))
        selected[split] = items[:max_per_split] if max_per_split else items
    return selected


def urban_syn_inventory(revision: str) -> tuple[list[dict], str]:
    from huggingface_hub import HfApi
    repo_id = "UrbanSyn/UrbanSyn"
    api = HfApi()
    info = api.dataset_info(repo_id, revision=revision, files_metadata=False)
    files = api.list_repo_files(repo_id, repo_type="dataset", revision=revision)
    prefixes = {"rgb": "rgb_", "semantic": "ss_", "panoptic": "panoptic_", "bbox": "bbox2d_"}
    index: dict[str, dict[str, str]] = {}
    for path in files:
        parts = {p.lower() for p in PurePosixPath(path).parts[:-1]}
        kind = next((k for folder, k in (("rgb", "rgb"), ("ss", "semantic"),
                    ("panoptic", "panoptic"), ("bbox2d", "bbox")) if folder in parts), None)
        if kind is None:
            continue
        stem = PurePosixPath(path).stem
        prefix = prefixes[kind]
        sample_id = stem[len(prefix):] if stem.startswith(prefix) else stem
        index.setdefault(sample_id, {})[kind] = path
    records = []
    for sample_id, assets in sorted(index.items()):
        if set(assets) == set(prefixes):
            records.append({
                "dataset": "urbansyn", "sample_id": sample_id,
                "group_id": sample_id,
                "source": f"hf://datasets/{repo_id}@{info.sha}",
                "revision": info.sha, "assets": assets,
            })
    if not records:
        raise RuntimeError("No complete UrbanSyn RGB/semantic/panoptic/bbox2D records found")
    return records, str(info.sha)


def a2d2_inventory() -> tuple[list[dict], str]:
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config
    bucket, region = "audi-autonomous-driving-dataset", "eu-central-1"
    s3 = boto3.client("s3", region_name=region,
        config=Config(signature_version=UNSIGNED, retries={"max_attempts": 5}))
    paginator = s3.get_paginator("list_objects_v2")
    records = []
    sequence_pages = s3.get_paginator("list_objects_v2").paginate(
        Bucket=bucket, Prefix="camera_lidar_semantic/", Delimiter="/")
    sequences = (entry for page in sequence_pages
                 for entry in page.get("CommonPrefixes", []))
    for sequence_index, entry in enumerate(sequences, start=1):
        seq_prefix = entry["Prefix"]
        group_id = seq_prefix.rstrip("/").split("/")[-1]
        camera_prefix = seq_prefix + "camera/cam_front_center/"
        label_prefix = seq_prefix + "label/cam_front_center/"
        # List each sequence's masks once. This replaces one S3 HEAD request
        # per RGB frame, which made the original inventory exceed the job limit.
        label_objects = {}
        for page in paginator.paginate(Bucket=bucket, Prefix=label_prefix):
            for label_obj in page.get("Contents", []):
                label_name = PurePosixPath(label_obj["Key"]).name
                if label_name.lower().endswith(".png"):
                    label_objects[label_name] = label_obj
        print(f"A2D2 sequence {sequence_index}: {group_id}; "
              f"{len(label_objects)} semantic masks indexed", flush=True)
        for page in paginator.paginate(Bucket=bucket, Prefix=camera_prefix):
            for obj in page.get("Contents", []):
                image_key = obj["Key"]
                if not image_key.lower().endswith(".png"):
                    continue
                filename = PurePosixPath(image_key).name
                label_name = filename.replace("_camera_frontcenter_", "_label_frontcenter_")
                mask_obj = label_objects.get(label_name)
                if mask_obj is None:
                    continue
                mask_key = mask_obj["Key"]
                sample_id = f"{group_id}/{filename}"
                records.append({
                    "dataset": "a2d2", "sample_id": sample_id,
                    "group_id": group_id,
                    "source": f"s3://{bucket}/{seq_prefix}",
                    "assets": {"rgb": f"s3://{bucket}/{image_key}",
                               "semantic": f"s3://{bucket}/{mask_key}"},
                    "asset_metadata": {
                        "rgb": {"size": int(obj["Size"]), "etag": obj.get("ETag", "").strip('"')},
                        "semantic": {"size": int(mask_obj["Size"]),
                                     "etag": mask_obj.get("ETag", "").strip('"')},
                    },
                })
    if not records:
        raise RuntimeError("No complete A2D2 front-camera RGB/semantic pairs found")
    return records, "s3-anonymous-current-index"


def write_manifests(dataset: str, records: list[dict], revision: str,
                    output: Path, seed: int, max_per_split: int | None) -> dict:
    selected = select_subset(records, seed=seed, max_per_split=max_per_split)
    output.mkdir(parents=True, exist_ok=True)
    summary = {
        "schema_version": 1, "dataset": dataset, "source_revision": revision,
        "seed": seed, "split_policy": "sha256(seed:group_id), 80/10/10",
        "grouping": "A2D2 sequence-level" if dataset == "a2d2" else
                    "sample-ID-level; no verified sequence metadata",
        "max_per_split": max_per_split, "counts": {},
        "warning": "Experimental reproducible split; not an official dataset split.",
    }
    for split in SPLITS:
        path = output / f"{dataset}_{split}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for record in selected[split]:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
        summary["counts"][split] = len(selected[split])
    summary["total_selected"] = sum(summary["counts"].values())
    (output / f"{dataset}_manifest_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("a2d2", "urbansyn", "both"), default="both")
    parser.add_argument("--output", type=Path, default=Path("data/manifests"))
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-per-split", type=int, default=1000,
                        help="Bound each split; use 0 for all indexed records.")
    parser.add_argument("--urbansyn-revision", default="main")
    args = parser.parse_args()
    cap = args.max_per_split or None
    datasets = ("a2d2", "urbansyn") if args.dataset == "both" else (args.dataset,)
    for dataset in datasets:
        records, revision = a2d2_inventory() if dataset == "a2d2" else urban_syn_inventory(args.urbansyn_revision)
        summary = write_manifests(dataset, records, revision, args.output,
                                  args.seed, cap)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
