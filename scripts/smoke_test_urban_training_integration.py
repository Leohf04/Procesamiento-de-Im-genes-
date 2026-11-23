#!/usr/bin/env python3
"""Bounded real-data integration smoke test for per-domain urban train loaders.

Downloads one train sample per dataset into temporary storage, builds semantic
and instance datasets with the versioned ontology, and exercises
build_urban_train_loaders with the matching train-only annotation rows.
No full dataset download, model forward pass, optimization, or checkpoint write.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from huggingface_hub import hf_hub_download
import numpy as np
from PIL import Image
import torch
from torch.utils.data import WeightedRandomSampler

from src.data_adapters import (
    A2D2InstanceDataset,
    A2D2SemanticDataset,
    UrbanSynInstanceDataset,
    UrbanSynSemanticDataset,
    load_a2d2_class_list,
)
from src.urban_ontology import (
    instance_name_to_id,
    load_urban_ontology,
    semantic_name_to_id,
    source_instance_map,
    source_semantic_map,
)
from src.urban_training import build_urban_train_loaders

A2D2_BUCKET = "audi-autonomous-driving-dataset"
A2D2_REGION = "eu-central-1"
URBANSYN_REPO = "UrbanSyn/UrbanSyn"


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
    ids = [str(row.get("sample_id", "")) for row in rows]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError(f"{path}: sample_id missing or duplicated")
    return rows


def choose_train_record(manifest_rows: list[dict], annotation_rows: list[dict]) -> tuple[dict, dict]:
    annotations = {str(row["sample_id"]): row for row in annotation_rows}
    candidates = []
    for record in manifest_rows:
        sample_id = str(record["sample_id"])
        stats = annotations.get(sample_id)
        if stats is None:
            continue
        if stats.get("annotation_status", "ok") != "ok":
            continue
        if stats.get("semantic_pixels") and stats.get("instance_counts"):
            candidates.append((record, stats))
    if not candidates:
        raise RuntimeError("No train sample has both semantic_pixels and instance_counts")
    return min(
        candidates,
        key=lambda pair: hashlib.sha256(
            f"urban-loader-integration-v1:{pair[0]['sample_id']}".encode()
        ).hexdigest(),
    )


def download_a2d2(s3, uri: str, destination: Path) -> None:
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or parsed.netloc != A2D2_BUCKET:
        raise ValueError(f"Unexpected A2D2 asset URI: {uri}")
    s3.download_file(parsed.netloc, parsed.path.lstrip("/"), str(destination))


def verify_semantic_batch(batch, valid_ids: set[int], ignore_index: int) -> dict:
    images, masks = batch
    assert images.ndim == 4 and images.shape[0] == 1
    assert masks.ndim == 3 and masks.shape[0] == 1
    assert torch.isfinite(images).all()
    observed = {int(value) for value in torch.unique(masks).tolist()}
    assert observed.issubset(valid_ids | {ignore_index}), observed
    return {
        "image_shape": list(images.shape),
        "mask_shape": list(masks.shape),
        "observed_semantic_ids": sorted(observed),
    }


def verify_instance_batch(batch, valid_ids: set[int]) -> dict:
    images, targets = batch
    assert len(images) == len(targets) == 1
    target = targets[0]
    assert set(target) == {"boxes", "labels", "masks", "image_id", "area", "iscrowd"}
    assert target["boxes"].ndim == 2 and target["boxes"].shape[1] == 4
    assert target["masks"].ndim == 3
    assert len(target["boxes"]) == len(target["masks"]) == len(target["labels"])
    assert torch.isfinite(target["boxes"]).all()
    labels = {int(value) for value in torch.unique(target["labels"]).tolist()}
    assert labels.issubset(valid_ids), labels
    return {
        "image_shape": list(images[0].shape),
        "boxes_shape": list(target["boxes"].shape),
        "masks_shape": list(target["masks"].shape),
        "observed_instance_ids": sorted(labels),
        "instance_count": int(len(target["labels"])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-dir", type=Path, required=True)
    parser.add_argument("--annotation-index-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=512)
    args = parser.parse_args()
    if args.size < 32:
        parser.error("--size must be >= 32")

    ontology = load_urban_ontology()
    semantic_ids = semantic_name_to_id(ontology)
    instance_ids = instance_name_to_id(ontology)
    semantic_valid = set(semantic_ids.values())
    instance_valid = set(instance_ids.values())
    ignore_index = int(ontology["ignore_index"])

    selected = {}
    annotation_by_dataset = {}
    for dataset_name in ("a2d2", "urbansyn"):
        manifest_rows = read_jsonl(args.manifest_dir / f"{dataset_name}_train.jsonl")
        annotation_rows = read_jsonl(
            args.annotation_index_dir / f"{dataset_name}_train.annotations.jsonl"
        )
        record, stats = choose_train_record(manifest_rows, annotation_rows)
        selected[dataset_name] = record
        annotation = dict(stats)
        annotation["dataset"] = dataset_name
        annotation["split"] = "train"
        annotation_by_dataset[dataset_name] = [annotation]

    report = {
        "status": "running",
        "ontology_version": ontology["ontology_version"],
        "sampled_per_dataset": 1,
        "datasets": {},
        "tasks": {},
        "training_started": False,
        "full_dataset_downloaded": False,
    }

    s3 = boto3.client(
        "s3",
        region_name=A2D2_REGION,
        config=Config(signature_version=UNSIGNED, retries={"max_attempts": 5}),
    )
    class_response = s3.get_object(
        Bucket=A2D2_BUCKET, Key="camera_lidar_semantic/class_list.json"
    )
    color_map = load_a2d2_class_list(json.loads(class_response["Body"].read()))

    with tempfile.TemporaryDirectory(prefix="urban-loader-integration-") as temp_dir:
        root = Path(temp_dir)
        semantic_datasets = {}
        instance_datasets = {}

        for dataset_name in ("a2d2", "urbansyn"):
            record = selected[dataset_name]
            local = root / dataset_name
            local.mkdir(parents=True)
            if dataset_name == "a2d2":
                image_path, semantic_path = local / "rgb.png", local / "semantic.png"
                download_a2d2(s3, record["assets"]["rgb"], image_path)
                download_a2d2(s3, record["assets"]["semantic"], semantic_path)
                semantic_records = [{
                    "sample_id": record["sample_id"], "dataset": dataset_name,
                    "image": str(image_path), "semantic": str(semantic_path),
                }]
                instance_records = [{
                    "sample_id": record["sample_id"], "dataset": dataset_name,
                    "image": str(image_path), "instance": str(semantic_path),
                }]
                semantic_datasets[dataset_name] = A2D2SemanticDataset(
                    semantic_records, color_map, semantic_ids, size=(args.size, args.size)
                )
                instance_datasets[dataset_name] = A2D2InstanceDataset(
                    instance_records, color_map, instance_ids,
                    size=(args.size, args.size), min_component_area=8,
                )
            else:
                paths = {}
                for key in ("rgb", "semantic", "panoptic"):
                    paths[key] = Path(hf_hub_download(
                        repo_id=URBANSYN_REPO,
                        repo_type="dataset",
                        revision=record["revision"],
                        filename=record["assets"][key],
                        local_dir=str(local / "hf"),
                    ))
                semantic_records = [{
                    "sample_id": record["sample_id"], "dataset": dataset_name,
                    "image": str(paths["rgb"]), "semantic": str(paths["semantic"]),
                }]
                instance_records = [{
                    "sample_id": record["sample_id"], "dataset": dataset_name,
                    "image": str(paths["rgb"]), "panoptic": str(paths["panoptic"]),
                }]
                semantic_datasets[dataset_name] = UrbanSynSemanticDataset(
                    semantic_records, source_semantic_map("urbansyn", ontology),
                    size=(args.size, args.size),
                )
                instance_datasets[dataset_name] = UrbanSynInstanceDataset(
                    instance_records, source_instance_map("urbansyn", ontology),
                    size=(args.size, args.size), min_instance_area=1,
                )

            report["datasets"][dataset_name] = {
                "sample_id": record["sample_id"],
                "train_manifest_rows": len(read_jsonl(
                    args.manifest_dir / f"{dataset_name}_train.jsonl"
                )),
                "annotation_status": annotation_by_dataset[dataset_name][0].get(
                    "annotation_status", "ok"
                ),
            }

        semantic_specs = {
            name: {
                "dataset": semantic_datasets[name],
                "annotation_rows": annotation_by_dataset[name],
                "class_to_id": semantic_ids,
            }
            for name in ("a2d2", "urbansyn")
        }
        semantic_loaders = build_urban_train_loaders(
            semantic_specs, task="semantic", batch_size=1, seed=2026
        )
        semantic_results = {}
        for name, (loader, weights) in semantic_loaders.items():
            semantic_results[name] = verify_semantic_batch(
                next(iter(loader)), semantic_valid, ignore_index
            )
            assert weights is not None and weights.shape[0] == len(semantic_ids)
            assert torch.isfinite(weights).all()
            semantic_results[name]["class_weight_count"] = int(weights.numel())
        report["tasks"]["semantic"] = semantic_results

        instance_specs = {
            name: {
                "dataset": instance_datasets[name],
                "annotation_rows": annotation_by_dataset[name],
                "class_to_id": instance_ids,
            }
            for name in ("a2d2", "urbansyn")
        }
        instance_loaders = build_urban_train_loaders(
            instance_specs, task="instances", batch_size=1, seed=2026
        )
        instance_results = {}
        for name, (loader, weights) in instance_loaders.items():
            assert isinstance(loader.sampler, WeightedRandomSampler)
            assert weights is None
            instance_results[name] = verify_instance_batch(
                next(iter(loader)), instance_valid
            )
        report["tasks"]["instances"] = instance_results

    report["status"] = "PASS"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("RESULT: REAL MULTIDATASET TRAIN-LOADER INTEGRATION PASSED")


if __name__ == "__main__":
    main()
