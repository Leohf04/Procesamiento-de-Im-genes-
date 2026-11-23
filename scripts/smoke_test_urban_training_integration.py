#!/usr/bin/env python3
"""Bounded real-data integration smoke test for per-domain urban train loaders.

Downloads one train sample per dataset into temporary storage, builds semantic
and instance datasets with the versioned ontology, and exercises
build_urban_train_loaders with the matching train-only annotation rows.
No full dataset download, optimization, or checkpoint write. Optional --model-forward
runs untrained DeepLabV3+ and Mask R-CNN inference on the same two real samples.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import time
import resource
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
from src.models.deeplabv3plus import DeepLabV3Plus

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



def run_model_forward_checks(semantic_loaders, instance_loaders, num_semantic_classes: int,
                             num_instance_classes: int, size: int) -> dict:
    """Run inference-only forward passes on the already loaded real samples."""
    import torchvision
    from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
    from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results = {"device": str(device), "weights": "random_initialization_no_pretrained_weights",
               "training_or_backward": False, "deeplabv3plus": {}, "mask_rcnn": {}}

    semantic_model = DeepLabV3Plus(
        num_classes=num_semantic_classes, pretrained_backbone=False
    ).to(device).eval()
    with torch.inference_mode():
        for dataset_name, (loader, _) in semantic_loaders.items():
            images, masks = next(iter(loader))
            logits = semantic_model(images.to(device))["out"]
            assert tuple(logits.shape) == (1, num_semantic_classes, size, size), tuple(logits.shape)
            assert torch.isfinite(logits).all()
            predictions = logits.argmax(dim=1)
            results["deeplabv3plus"][dataset_name] = {
                "input_shape": list(images.shape),
                "logits_shape": list(logits.shape),
                "prediction_shape": list(predictions.shape),
                "finite_logits": True,
            }
            del images, masks, logits, predictions
    del semantic_model
    if device.type == "cuda":
        torch.cuda.empty_cache()

    detector = torchvision.models.detection.maskrcnn_resnet50_fpn(
        weights=None, weights_backbone=None, min_size=size, max_size=size
    )
    box_features = detector.roi_heads.box_predictor.cls_score.in_features
    detector.roi_heads.box_predictor = FastRCNNPredictor(box_features, num_instance_classes)
    mask_features = detector.roi_heads.mask_predictor.conv5_mask.in_channels
    detector.roi_heads.mask_predictor = MaskRCNNPredictor(mask_features, 256, num_instance_classes)
    detector.to(device).eval()

    with torch.inference_mode():
        for dataset_name, (loader, _) in instance_loaders.items():
            images, targets = next(iter(loader))
            outputs = detector([image.to(device) for image in images])
            assert len(outputs) == len(images) == 1
            output = outputs[0]
            boxes, labels = output["boxes"], output["labels"]
            scores, masks = output["scores"], output["masks"]
            assert boxes.ndim == 2 and boxes.shape[1] == 4
            assert masks.ndim == 4 and masks.shape[1] == 1
            assert masks.shape[-2:] == (size, size), tuple(masks.shape)
            assert len(boxes) == len(labels) == len(scores) == len(masks)
            assert torch.isfinite(boxes).all() and torch.isfinite(scores).all()
            assert torch.isfinite(masks).all()
            results["mask_rcnn"][dataset_name] = {
                "input_shape": list(images[0].shape),
                "ground_truth_instances": int(len(targets[0]["labels"])),
                "predicted_boxes_shape": list(boxes.shape),
                "predicted_masks_shape": list(masks.shape),
                "predictions_finite": True,
            }
            del images, targets, outputs, output, boxes, labels, scores, masks
    del detector
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return results



def _assert_finite_gradients(model, model_name: str) -> dict:
    gradients = [parameter.grad for parameter in model.parameters()
                 if parameter.requires_grad and parameter.grad is not None]
    if not gradients:
        raise RuntimeError(f"{model_name}: backward no produjo gradientes")
    finite = all(bool(torch.isfinite(gradient).all()) for gradient in gradients)
    if not finite:
        raise RuntimeError(f"{model_name}: se detectaron gradientes NaN/Inf")
    nonzero = sum(int(torch.count_nonzero(gradient).item() > 0) for gradient in gradients)
    if nonzero == 0:
        raise RuntimeError(f"{model_name}: todos los gradientes son cero")
    return {"gradient_tensors": len(gradients), "nonzero_gradient_tensors": nonzero,
            "finite_gradients": True}


def _optimizer_step(model, loss: torch.Tensor, model_name: str, learning_rate: float) -> dict:
    if loss.ndim != 0 or not bool(torch.isfinite(loss)):
        raise RuntimeError(f"{model_name}: loss no escalar o no finita")
    optimizer = torch.optim.SGD(
        (parameter for parameter in model.parameters() if parameter.requires_grad),
        lr=learning_rate, momentum=0.0,
    )
    optimizer.zero_grad(set_to_none=True)
    before = next(parameter.detach().clone() for parameter in model.parameters()
                  if parameter.requires_grad)
    loss.backward()
    gradient_report = _assert_finite_gradients(model, model_name)
    optimizer.step()
    after = next(parameter.detach() for parameter in model.parameters()
                 if parameter.requires_grad)
    changed = not torch.equal(before, after)
    if not changed:
        raise RuntimeError(f"{model_name}: el optimizador no modificó el parámetro inspeccionado")
    return {
        "loss": float(loss.detach().cpu()),
        "optimizer": "SGD",
        "learning_rate": learning_rate,
        "parameter_updated": True,
        **gradient_report,
    }


def run_controlled_learning_steps(semantic_loaders, instance_loaders,
                                  num_semantic_classes: int, num_instance_classes: int,
                                  size: int, learning_rate: float = 1e-4) -> dict:
    """One real-data loss/backward/SGD step per model and dataset, no checkpoint."""
    import torchvision
    from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
    from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    report = {
        "status": "running", "device": str(device), "image_size": size,
        "initialization": "random_no_pretrained_weights",
        "optimizer_steps_expected": 4, "optimizer_steps_completed": 0,
        "full_training": False, "checkpoint_saved": False,
        "deeplabv3plus": {}, "mask_rcnn": {},
    }

    for dataset_name, (loader, class_weights) in semantic_loaders.items():
        step_started = time.perf_counter()
        if device.type == "cuda": torch.cuda.reset_peak_memory_stats(device)
        torch.manual_seed(2026)
        model = DeepLabV3Plus(
            num_classes=num_semantic_classes, pretrained_backbone=False
        ).to(device).train()
        images, masks = next(iter(loader))
        images, masks = images.to(device), masks.to(device)
        weights = class_weights.to(device=device, dtype=torch.float32)
        optimizer_report = None
        try:
            logits = model(images)["out"]
            if tuple(logits.shape) != (1, num_semantic_classes, size, size):
                raise RuntimeError(f"{dataset_name}: logits shape inesperada {tuple(logits.shape)}")
            loss = torch.nn.functional.cross_entropy(
                logits, masks, weight=weights, ignore_index=255
            )
            optimizer_report = _optimizer_step(
                model, loss, f"DeepLabV3+/{dataset_name}", learning_rate
            )
            report["deeplabv3plus"][dataset_name] = {
                "input_shape": list(images.shape), "target_shape": list(masks.shape),
                "logits_shape": list(logits.shape),
                "elapsed_seconds": round(time.perf_counter() - step_started, 3),
                "peak_cuda_memory_mb": (round(torch.cuda.max_memory_allocated(device) / (1024 ** 2), 2) if device.type == "cuda" else None),
                **optimizer_report,
            }
            report["optimizer_steps_completed"] += 1
        finally:
            del model, images, masks
            if "logits" in locals(): del logits
            if "loss" in locals(): del loss
            if device.type == "cuda": torch.cuda.empty_cache()

    for dataset_name, (loader, _) in instance_loaders.items():
        step_started = time.perf_counter()
        if device.type == "cuda": torch.cuda.reset_peak_memory_stats(device)
        torch.manual_seed(2026)
        detector = torchvision.models.detection.maskrcnn_resnet50_fpn(
            weights=None, weights_backbone=None, min_size=size, max_size=size
        )
        box_features = detector.roi_heads.box_predictor.cls_score.in_features
        detector.roi_heads.box_predictor = FastRCNNPredictor(box_features, num_instance_classes)
        mask_features = detector.roi_heads.mask_predictor.conv5_mask.in_channels
        detector.roi_heads.mask_predictor = MaskRCNNPredictor(
            mask_features, 256, num_instance_classes
        )
        detector.to(device).train()
        images, targets = next(iter(loader))
        images = [image.to(device) for image in images]
        targets = [{key: value.to(device) if torch.is_tensor(value) else value
                    for key, value in target.items()} for target in targets]
        if not targets or any(len(target["labels"]) == 0 for target in targets):
            raise RuntimeError(f"{dataset_name}: Mask R-CNN requiere al menos una instancia GT")
        try:
            losses = detector(images, targets)
            if not losses:
                raise RuntimeError(f"{dataset_name}: Mask R-CNN no devolvió componentes de loss")
            bad = [name for name, value in losses.items()
                   if value.ndim != 0 or not bool(torch.isfinite(value))]
            if bad:
                raise RuntimeError(f"{dataset_name}: losses no finitas/no escalares: {bad}")
            total_loss = sum(losses.values())
            optimizer_report = _optimizer_step(
                detector, total_loss, f"Mask R-CNN/{dataset_name}", learning_rate
            )
            report["mask_rcnn"][dataset_name] = {
                "input_shape": list(images[0].shape),
                "ground_truth_instances": int(len(targets[0]["labels"])),
                "loss_components": {name: float(value.detach().cpu())
                                    for name, value in losses.items()},
                "elapsed_seconds": round(time.perf_counter() - step_started, 3),
                "peak_cuda_memory_mb": (round(torch.cuda.max_memory_allocated(device) / (1024 ** 2), 2) if device.type == "cuda" else None),
                **optimizer_report,
            }
            report["optimizer_steps_completed"] += 1
        finally:
            del detector, images, targets
            if "losses" in locals(): del losses
            if "total_loss" in locals(): del total_loss
            if device.type == "cuda": torch.cuda.empty_cache()

    if report["optimizer_steps_completed"] != report["optimizer_steps_expected"]:
        raise RuntimeError("No se completaron los cuatro pasos de optimizador.")
    report["process_max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2)
    report["status"] = "PASS"
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-dir", type=Path, required=True)
    parser.add_argument("--annotation-index-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--model-forward", action="store_true", help="Run inference-only DeepLabV3+ and Mask R-CNN forward passes on the real samples.")
    parser.add_argument("--learning-step", action="store_true", help="Run one loss/backward/SGD update for each model and dataset (four bounded steps).")
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    if "--learning-step" in __import__("sys").argv and "--model-forward" in __import__("sys").argv:
        parser.error("--learning-step and --model-forward are mutually exclusive")
    args = parser.parse_args()
    if args.size < 32:
        parser.error("--size must be >= 32")
    if not (0 < args.learning_rate <= 1e-2):
        parser.error("--learning-rate must be in (0, 1e-2]")

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
        "training_started": bool(args.learning_step),
        "controlled_learning_step": bool(args.learning_step),
        "full_training_started": False,
        "full_dataset_downloaded": False,
        "model_forward": {"status": "NOT_REQUESTED"},
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
                    size=(args.size, args.size), min_component_area=(1 if args.learning_step else 8),
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


        if args.learning_step:
            report["controlled_learning"] = run_controlled_learning_steps(
                semantic_loaders, instance_loaders,
                num_semantic_classes=len(semantic_ids),
                num_instance_classes=len(instance_ids) + 1,
                size=args.size, learning_rate=args.learning_rate,
            )
        if args.model_forward:
            report["model_forward"] = {
                "status": "PASS",
                **run_model_forward_checks(
                    semantic_loaders, instance_loaders,
                    num_semantic_classes=len(semantic_ids),
                    num_instance_classes=len(instance_ids) + 1,
                    size=args.size,
                ),
            }

    report["status"] = "PASS"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("RESULT: REAL MULTIDATASET TRAIN-LOADER INTEGRATION PASSED")
    if args.learning_step:
        print("RESULT: CONTROLLED REAL-DATA LEARNING STEPS PASSED (4 optimizer updates)")


if __name__ == "__main__":
    main()
