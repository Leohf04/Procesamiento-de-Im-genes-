#!/usr/bin/env python3
"""Real-data factory/loader smoke, semantic forward, COCOeval and checkpoint resume.

This script performs inference only. It never calls backward(), optimizer.step(),
or the experiment training loop.
"""
import argparse
import gc
import hashlib
import json
import sys
from pathlib import Path

# When executed as `python scripts/smoke_test_urban_experiment_factory.py`,
# Python puts the scripts/ directory (not the repository root) on sys.path.
# Add the repository root so absolute imports such as `scripts.*` and `src.*`
# work consistently in Colab and other subprocess-based environments.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

import torch

from scripts.urban_experiment_factory import create_experiment
from src.urban_experiment_runner import (
    _atomic_save, _loader_rng_state, _rng_state, load_checkpoint,
)


def _config(dataset, task, data_dir, annotation_index_dir, size):
    return {
        "run_training": False,
        "experiment_id": f"SMOKE-{dataset.upper()}-{task.upper()}",
        "dataset": dataset,
        "task": task,
        "data_dir": str(data_dir),
        "annotation_index_dir": str(annotation_index_dir),
        "image_size": size,
        "batch_size": 1,
        "validation_batch_size": 1,
        "num_workers": 0,
        "num_classes": 20,
        "learning_rate": 1e-3,
        "weight_decay": 1e-4,
        "momentum": 0.9,
        "seed": 2026,
    }


def _check_batch(batch, task, split, dataset):
    if task == "semantic":
        images, masks = batch
        if images.ndim != 4 or images.shape[0] != 1 or images.shape[1] != 3:
            raise RuntimeError(f"{dataset}/{split}: unexpected semantic image shape {tuple(images.shape)}")
        if masks.ndim != 3 or masks.shape[0] != 1:
            raise RuntimeError(f"{dataset}/{split}: unexpected semantic mask shape {tuple(masks.shape)}")
        if not torch.isfinite(images).all():
            raise RuntimeError(f"{dataset}/{split}: non-finite RGB tensor")
        valid = (masks != 255) & (masks >= 0) & (masks < 20)
        if not valid.any():
            raise RuntimeError(f"{dataset}/{split}: semantic mask has no valid ontology pixels")
        return {"images_shape": list(images.shape), "targets_shape": list(masks.shape),
                "valid_semantic_pixels": int(valid.sum())}

    images, targets = batch
    if len(images) != 1 or len(targets) != 1:
        raise RuntimeError(f"{dataset}/{split}: expected batch size 1")
    image, target = images[0], targets[0]
    required = {"boxes", "labels", "masks", "image_id"}
    if required - set(target):
        raise RuntimeError(f"{dataset}/{split}: missing target fields {sorted(required-set(target))}")
    boxes, labels, masks = target["boxes"], target["labels"], target["masks"]
    if boxes.ndim != 2 or boxes.shape[1] != 4 or labels.ndim != 1:
        raise RuntimeError(f"{dataset}/{split}: malformed boxes/labels")
    if masks.ndim != 3 or masks.shape[0] != len(labels) or len(boxes) != len(labels):
        raise RuntimeError(f"{dataset}/{split}: boxes/labels/masks count mismatch")
    if len(labels) == 0:
        raise RuntimeError(f"{dataset}/{split}: selected instance sample has no GT instances")
    if not torch.isfinite(image).all() or not torch.isfinite(boxes).all():
        raise RuntimeError(f"{dataset}/{split}: non-finite image/boxes")
    if (boxes[:, 2:] <= boxes[:, :2]).any():
        raise RuntimeError(f"{dataset}/{split}: degenerate boxes")
    return {"image_shape": list(image.shape), "instances": int(len(labels)),
            "boxes_shape": list(boxes.shape), "masks_shape": list(masks.shape),
            "labels": [int(x) for x in labels.tolist()]}


def run_one(dataset, task, data_dir, annotation_index_dir, size, report_dir):
    cfg = _config(dataset, task, data_dir, annotation_index_dir, size)
    bundle = create_experiment(cfg)
    train_loader, val_loader = bundle["train_loader"], bundle["validation_loader"]
    train_batch = next(iter(train_loader))
    val_batch = next(iter(val_loader))
    train_summary = _check_batch(train_batch, task, "train", dataset)
    val_summary = _check_batch(val_batch, task, "val", dataset)

    model = bundle["model"].cpu()
    model.eval()
    if task == "semantic":
        images, _ = val_batch
        with torch.inference_mode():
            logits = model(images.cpu())["out"]
        if logits.shape[:2] != (1, 20) or not torch.isfinite(logits).all():
            raise RuntimeError(f"{dataset}: invalid semantic inference output {tuple(logits.shape)}")
        evaluation = {"forward_status": "PASS", "logits_shape": list(logits.shape),
                      "logits_finite": True}
    else:
        with torch.inference_mode():
            coco = bundle["detection_evaluator"](model, val_loader, torch.device("cpu"))
        required_metrics = ("box_ap", "box_ap50", "box_ap75", "mask_ap", "mask_ap50", "mask_ap75")
        if any(k not in coco or not isinstance(coco[k], (int, float)) for k in required_metrics):
            raise RuntimeError(f"{dataset}: COCOeval did not return all AP metrics")
        evaluation = {"cocoeval_status": "PASS", "metrics": coco}

    # Round-trip a zero-epoch checkpoint using the real factory optimizer,
    # scheduler and train-loader RNG state. No optimizer update is performed.
    config_hash = hashlib.sha256(
        json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    checkpoint = report_dir / f"checkpoint_smoke_{dataset}_{task}.pt"
    loader_rng_before = _loader_rng_state(train_loader)
    payload = {
        "format_version": 1,
        "model": model.state_dict(),
        "optimizer": bundle["optimizer"].state_dict(),
        "scheduler": bundle["scheduler"].state_dict() if bundle.get("scheduler") else None,
        "scaler": None,
        "epoch": 0,
        "global_step": 0,
        "best_metric": None,
        "bad_epochs": 0,
        "rng": _rng_state(),
        "loader_rng": loader_rng_before,
        "config_hash": config_hash,
        "metadata": {"experiment_id": cfg["experiment_id"], "dataset": dataset, "task": task},
    }
    _atomic_save(payload, checkpoint)
    restored = load_checkpoint(
        checkpoint, model, bundle["optimizer"], bundle.get("scheduler"),
        expected_config_hash=config_hash, map_location="cpu", train_loader=train_loader,
    )
    loader_rng_after = _loader_rng_state(train_loader)
    for key, value in loader_rng_before.items():
        if key not in loader_rng_after or not torch.equal(value, loader_rng_after[key]):
            raise RuntimeError(f"{dataset}/{task}: DataLoader RNG state was not restored ({key})")
    if restored["global_step"] != 0 or restored["epoch"] != 0:
        raise RuntimeError(f"{dataset}/{task}: checkpoint smoke unexpectedly contains training progress")
    checkpoint.unlink(missing_ok=True)

    result = {
        "dataset": dataset, "task": task, "status": "PASS",
        "train_batch": train_summary, "validation_batch": val_summary,
        "evaluation": evaluation, "checkpoint_resume": "PASS",
        "optimizer_steps": 0, "backward_calls": 0,
    }
    del bundle, model, train_loader, val_loader, train_batch, val_batch
    gc.collect()
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--annotation-index-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--size", type=int, default=256)
    a = p.parse_args()
    if a.size < 64:
        p.error("--size must be >= 64")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    results = []
    for dataset in ("a2d2", "urbansyn"):
        for task in ("semantic", "instances"):
            print(f"Smoke {dataset}/{task} ...", flush=True)
            results.append(run_one(dataset, task, a.data_dir,
                                   a.annotation_index_dir, a.size, a.output.parent))
    report = {
        "status": "PASS" if all(x["status"] == "PASS" for x in results) else "FAIL",
        "experiments": results,
        "training_started": False,
        "optimizer_steps": 0,
        "backward_calls": 0,
        "test_split_touched": False,
        "image_size": a.size,
        "device": "cpu",
    }
    a.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
