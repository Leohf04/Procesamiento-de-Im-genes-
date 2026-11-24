#!/usr/bin/env python3
"""Audit materialized train/val capacity by decoding every selected sample.

No model forward, backward, optimizer step, checkpoint, or test access.
"""
import argparse
import gc
import json
import resource
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch
from scripts.urban_experiment_factory import create_experiment


def tree_bytes(path):
    return sum(p.stat().st_size for p in Path(path).rglob("*") if p.is_file())


def peak_rss_mib():
    # Linux reports ru_maxrss in KiB.
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0


def config(dataset, task, data_dir, index_dir, size):
    return {
        "run_training": False, "experiment_id": f"CAPACITY-{dataset}-{task}",
        "dataset": dataset, "task": task, "data_dir": str(data_dir),
        "annotation_index_dir": str(index_dir), "image_size": size,
        "batch_size": 1, "validation_batch_size": 1, "num_workers": 0,
        "num_classes": 20, "learning_rate": 1e-3, "weight_decay": 1e-4,
        "momentum": 0.9, "seed": 2026,
    }


def scan_dataset(dataset_obj, task, dataset_name, split):
    start = time.perf_counter()
    images_seen = 0
    semantic_valid_pixels = 0
    instances_seen = 0
    for i in range(len(dataset_obj)):
        item = dataset_obj[i]
        if task == "semantic":
            image, mask = item
            if image.ndim != 3 or image.shape[0] != 3:
                raise RuntimeError(f"{dataset_name}/{split}/{i}: invalid image shape {tuple(image.shape)}")
            if mask.ndim != 2:
                raise RuntimeError(f"{dataset_name}/{split}/{i}: invalid mask shape {tuple(mask.shape)}")
            if not torch.isfinite(image).all():
                raise RuntimeError(f"{dataset_name}/{split}/{i}: non-finite image")
            valid = (mask != 255) & (mask >= 0) & (mask < 20)
            semantic_valid_pixels += int(valid.sum())
        else:
            image, target = item
            boxes, labels, masks = target["boxes"], target["labels"], target["masks"]
            if image.ndim != 3 or image.shape[0] != 3:
                raise RuntimeError(f"{dataset_name}/{split}/{i}: invalid image shape {tuple(image.shape)}")
            if boxes.ndim != 2 or boxes.shape[1] != 4 or len(boxes) != len(labels):
                raise RuntimeError(f"{dataset_name}/{split}/{i}: invalid boxes/labels")
            if masks.ndim != 3 or masks.shape[0] != len(labels):
                raise RuntimeError(f"{dataset_name}/{split}/{i}: invalid masks")
            if not torch.isfinite(image).all() or not torch.isfinite(boxes).all():
                raise RuntimeError(f"{dataset_name}/{split}/{i}: non-finite tensor")
            if len(boxes) and (boxes[:, 2:] <= boxes[:, :2]).any():
                raise RuntimeError(f"{dataset_name}/{split}/{i}: degenerate boxes")
            instances_seen += int(len(labels))
        images_seen += 1
    return {
        "samples_expected": len(dataset_obj), "samples_decoded": images_seen,
        "semantic_valid_pixels": semantic_valid_pixels if task == "semantic" else None,
        "ground_truth_instances": instances_seen if task == "instances" else None,
        "decode_seconds": round(time.perf_counter() - start, 3),
        "samples_per_second": round(images_seen / max(time.perf_counter() - start, 1e-9), 3),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--annotation-index-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--size", type=int, default=256)
    a = p.parse_args()
    if a.size < 64:
        p.error("--size must be >= 64")
    if not a.data_dir.is_dir() or not a.annotation_index_dir.is_dir():
        raise RuntimeError("Materialized data or local annotation index directory is missing.")
    disk_before = shutil.disk_usage(a.data_dir)
    results = []
    rss_start = peak_rss_mib()
    for ds in ("a2d2", "urbansyn"):
        for task in ("semantic", "instances"):
            print(f"Capacity scan {ds}/{task} ...", flush=True)
            bundle = create_experiment(config(ds, task, a.data_dir,
                                               a.annotation_index_dir, a.size))
            train_ds = bundle["train_loader"].dataset
            val_ds = bundle["validation_loader"].dataset
            train = scan_dataset(train_ds, task, ds, "train")
            val = scan_dataset(val_ds, task, ds, "val")
            results.append({"dataset": ds, "task": task,
                            "train": train, "val": val, "status": "PASS"})
            del bundle, train_ds, val_ds
            gc.collect()
    disk_after = shutil.disk_usage(a.data_dir)
    report = {
        "status": "PASS",
        "image_size": a.size,
        "device": "cpu",
        "datasets": ["a2d2", "urbansyn"],
        "splits": ["train", "val"],
        "test_split_touched": False,
        "training_started": False,
        "optimizer_steps": 0,
        "backward_calls": 0,
        "model_forward_calls": 0,
        "materialized_bytes": tree_bytes(a.data_dir),
        "disk_free_before_bytes": disk_before.free,
        "disk_free_after_bytes": disk_after.free,
        "disk_total_bytes": disk_after.total,
        "process_peak_rss_start_mib": rss_start,
        "process_peak_rss_end_mib": peak_rss_mib(),
        "experiments": results,
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                        encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    if not all(x["status"] == "PASS" for x in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
