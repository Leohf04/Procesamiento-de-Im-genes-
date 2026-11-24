#!/usr/bin/env python3
"""Run exactly one real-data optimizer update for one urban dataset/task.

This is a bounded preflight, NOT the multi-epoch experiment runner. It reads
only the selected TRAIN split, performs one backward + optimizer.step(), does
not iterate validation, never opens test, and writes no model checkpoint.
"""
from __future__ import annotations

import argparse
import gc
import json
import math
import sys
import time
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

import torch
from scripts.urban_experiment_factory import create_experiment


def _finite_gradients(model):
    tensors = [p.grad for p in model.parameters() if p.grad is not None]
    if not tensors:
        raise RuntimeError("No parameter received a gradient")
    if any(not torch.isfinite(g).all() for g in tensors):
        raise FloatingPointError("Non-finite gradient detected")
    norm_sq = sum(float(torch.sum(g.detach().float() ** 2).cpu()) for g in tensors)
    return len(tensors), math.sqrt(norm_sq)


def run_one(dataset: str, task: str, data_dir: Path, index_dir: Path,
            image_size: int, output: Path) -> dict:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; refusing to run the real-data GPU preflight")
    if image_size != 512:
        raise ValueError("This preflight is frozen to image_size=512")
    cfg = {
        "run_training": False,
        "run_single_step_preflight": True,
        "experiment_id": f"ONE-STEP-{dataset.upper()}-{task.upper()}",
        "dataset": dataset,
        "task": task,
        "data_dir": str(data_dir),
        "annotation_index_dir": str(index_dir),
        "image_size": image_size,
        "batch_size": 1,
        "validation_batch_size": 1,
        "num_workers": 0,
        "num_classes": 20,
        "learning_rate": 1e-4,
        "weight_decay": 1e-4 if task == "semantic" else 5e-4,
        "momentum": 0.9,
        "seed": 2026,
        "amp": False,
        "max_grad_norm": 1.0,
    }
    if not data_dir.is_dir() or not index_dir.is_dir():
        raise FileNotFoundError("Materialized data/index directories are missing; this script never downloads data")
    materialization = data_dir / "materialization_report.json"
    if not materialization.is_file():
        raise FileNotFoundError(f"Missing materialization report: {materialization}")
    mat = json.loads(materialization.read_text(encoding="utf-8"))
    if mat.get("status") != "PASS" or mat.get("test_touched") is not False:
        raise RuntimeError("Materialization report is not PASS or does not explicitly exclude test")

    torch.manual_seed(2026)
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    bundle = create_experiment(cfg)
    model = bundle["model"].cuda()
    optimizer = bundle["optimizer"]
    loader = bundle["train_loader"]
    # Only the first selected TRAIN batch is requested. Validation loader is
    # constructed by the existing factory but is never iterated.
    batch = next(iter(loader))
    optimizer.zero_grad(set_to_none=True)

    if task == "semantic":
        images, masks = batch
        images = images.cuda(non_blocking=True)
        masks = masks.cuda(non_blocking=True, dtype=torch.long)
        logits = model(images)["out"]
        if logits.ndim != 4 or logits.shape[0] != 1 or logits.shape[1] != 20:
            raise RuntimeError(f"Unexpected semantic logits shape: {tuple(logits.shape)}")
        weights = bundle["class_weights"]
        loss = torch.nn.functional.cross_entropy(
            logits, masks,
            weight=weights.cuda() if weights is not None else None,
            ignore_index=255,
        )
        batch_summary = {
            "images_shape": list(images.shape),
            "masks_shape": list(masks.shape),
            "valid_pixels": int(((masks != 255) & (masks >= 0) & (masks < 20)).sum().item()),
        }
        if batch_summary["valid_pixels"] == 0:
            raise RuntimeError("Selected semantic training sample has no valid ontology pixels")
    else:
        images, targets = batch
        if len(images) != 1 or len(targets) != 1:
            raise RuntimeError("Instance preflight requires exactly one image/target")
        images = [image.cuda(non_blocking=True) for image in images]
        targets = [{
            key: value.cuda(non_blocking=True) if torch.is_tensor(value) else value
            for key, value in target.items()
        } for target in targets]
        target = targets[0]
        if len(target["labels"]) < 1:
            raise RuntimeError("Selected instance training sample has no GT instances")
        losses = model(images, targets)
        if not isinstance(losses, dict) or not losses:
            raise RuntimeError("Mask R-CNN returned no loss components")
        if any(value.ndim != 0 or not torch.isfinite(value).all() for value in losses.values()):
            raise FloatingPointError("Non-finite or non-scalar Mask R-CNN loss")
        loss = sum(losses.values())
        batch_summary = {
            "image_shape": list(images[0].shape),
            "instances": int(len(target["labels"])),
            "boxes_shape": list(target["boxes"].shape),
            "masks_shape": list(target["masks"].shape),
            "loss_components": {key: float(value.detach().cpu()) for key, value in losses.items()},
        }

    if loss.ndim != 0 or not torch.isfinite(loss).all():
        raise FloatingPointError("Training loss is not a finite scalar")
    loss_value = float(loss.detach().cpu())
    loss.backward()
    gradient_tensors, gradient_norm = _finite_gradients(model)
    if not math.isfinite(gradient_norm) or gradient_norm <= 0:
        raise RuntimeError(f"Gradient norm is not positive and finite: {gradient_norm}")
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    before = next(model.parameters()).detach().clone()
    optimizer.step()
    parameter_changed = not torch.equal(before, next(model.parameters()).detach())
    if not parameter_changed:
        raise RuntimeError("The optimizer step completed but the sampled parameter did not change")

    torch.cuda.synchronize()
    elapsed = round(time.monotonic() - started, 3)
    report = {
        "status": "PASS",
        "dataset": dataset,
        "task": task,
        "experiment_id": cfg["experiment_id"],
        "device": torch.cuda.get_device_name(0),
        "torch": str(torch.__version__),
        "cuda": torch.version.cuda,
        "image_size": image_size,
        "batch_size": 1,
        "amp": False,
        "initialization": "random_weights_no_pretraining",
        "learning_rate_probe_only": cfg["learning_rate"],
        "train_batch": batch_summary,
        "loss": loss_value,
        "gradient_tensors": gradient_tensors,
        "gradient_l2_norm_before_clip": gradient_norm,
        "optimizer_steps": 1,
        "parameter_changed": parameter_changed,
        "elapsed_seconds": elapsed,
        "peak_allocated_bytes": int(torch.cuda.max_memory_allocated()),
        "peak_reserved_bytes": int(torch.cuda.max_memory_reserved()),
        "validation_batches_iterated": 0,
        "test_split_touched": False,
        "pilot_training_started": False,
        "checkpoint_written": False,
        "dataset_downloaded_by_script": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    del bundle, model, optimizer, loader, batch
    gc.collect()
    torch.cuda.empty_cache()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("a2d2", "urbansyn"), required=True)
    parser.add_argument("--task", choices=("semantic", "instances"), required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--annotation-index-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=512)
    parser.add_argument("--execute-single-step", action="store_true")
    args = parser.parse_args()
    if not args.execute_single_step:
        raise SystemExit("BLOCKED: pass --execute-single-step to permit exactly one optimizer update")
    try:
        report = run_one(args.dataset, args.task, args.data_dir,
                         args.annotation_index_dir, args.image_size, args.output)
    except Exception as exc:
        failure = {
            "status": "FAIL",
            "dataset": args.dataset,
            "task": args.task,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "optimizer_steps": 0,
            "test_split_touched": False,
            "pilot_training_started": False,
            "checkpoint_written": False,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure, indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
