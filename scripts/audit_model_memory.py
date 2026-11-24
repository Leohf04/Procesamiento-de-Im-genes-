#!/usr/bin/env python3
"""Isolated CUDA memory probe for urban semantic/instance architectures.

Synthetic tensors only. Performs forward + backward to measure training-like
activation memory, but never calls optimizer.step(), loads datasets, or writes
model checkpoints.
"""
import argparse
import gc
import json
import sys
import time
from pathlib import Path

# Ejecutado como script, sys.path[0] apunta a scripts/. Añadimos la raíz
# del repositorio para que los imports del paquete src sean independientes
# del directorio de trabajo desde el que se invoque.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--task", choices=("semantic", "instances"), required=True)
    p.add_argument("--batch-size", type=int, required=True)
    p.add_argument("--image-size", type=int, default=512)
    p.add_argument("--amp", action="store_true")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--output", type=Path, required=True)
    return p.parse_args()


def main():
    args = parse_args()
    result = {
        "task": args.task, "batch_size": args.batch_size,
        "image_size": args.image_size, "amp": args.amp,
        "seed": args.seed, "training_dataset_loaded": False,
        "optimizer_steps": 0, "test_split_touched": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is unavailable; select a GPU runtime.")
        torch.manual_seed(args.seed)
        torch.cuda.manual_seed_all(args.seed)
        device = torch.device("cuda:0")
        props = torch.cuda.get_device_properties(device)
        result.update({
            "torch": str(torch.__version__), "cuda": str(torch.version.cuda),
            "gpu": props.name, "vram_total_bytes": props.total_memory,
        })

        if args.task == "semantic":
            from src.models.deeplabv3plus import DeepLabV3Plus
            model = DeepLabV3Plus(num_classes=20, pretrained_backbone=False)
        else:
            import torchvision
            from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
            from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
            model = torchvision.models.detection.maskrcnn_resnet50_fpn(
                weights=None, weights_backbone=None,
                min_size=args.image_size, max_size=args.image_size,
            )
            box_features = model.roi_heads.box_predictor.cls_score.in_features
            model.roi_heads.box_predictor = FastRCNNPredictor(box_features, 9)
            mask_features = model.roi_heads.mask_predictor.conv5_mask.in_channels
            model.roi_heads.mask_predictor = MaskRCNNPredictor(mask_features, 256, 9)

        model = model.to(device).train()
        baseline = torch.cuda.memory_allocated(device)
        torch.cuda.reset_peak_memory_stats(device)
        images = torch.rand(args.batch_size, 3, args.image_size, args.image_size, device=device)
        started = time.perf_counter()
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=args.amp):
            if args.task == "semantic":
                target = torch.randint(
                    0, 20, (args.batch_size, args.image_size, args.image_size),
                    dtype=torch.long, device=device,
                )
                logits = model(images)["out"]
                loss = torch.nn.functional.cross_entropy(logits, target)
            else:
                image_list = [images[i] for i in range(args.batch_size)]
                targets = []
                for _ in range(args.batch_size):
                    mask = torch.zeros((1, args.image_size, args.image_size),
                                       dtype=torch.uint8, device=device)
                    lo = max(8, args.image_size // 8)
                    hi = max(lo + 1, args.image_size - lo)
                    mask[:, lo:hi, lo:hi] = 1
                    targets.append({
                        "boxes": torch.tensor([[lo, lo, hi, hi]], dtype=torch.float32, device=device),
                        "labels": torch.ones((1,), dtype=torch.int64, device=device),
                        "masks": mask,
                        "image_id": torch.zeros((1,), dtype=torch.int64, device=device),
                        "area": torch.tensor([(hi-lo)*(hi-lo)], dtype=torch.float32, device=device),
                        "iscrowd": torch.zeros((1,), dtype=torch.int64, device=device),
                    })
                losses = model(image_list, targets)
                loss = sum(losses.values())
        if loss.ndim != 0 or not bool(torch.isfinite(loss)):
            raise FloatingPointError("Non-finite scalar loss")
        loss.backward()
        torch.cuda.synchronize(device)
        elapsed = time.perf_counter() - started
        result.update({
            "status": "PASS", "loss": float(loss.detach().cpu()),
            "elapsed_seconds": round(elapsed, 3),
            "baseline_allocated_bytes": baseline,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(device),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(device),
            "peak_increment_over_model_bytes": max(0, torch.cuda.max_memory_allocated(device)-baseline),
            "backward_calls": 1, "optimizer_steps": 0,
        })
    except torch.cuda.OutOfMemoryError as exc:
        result.update({"status": "OOM", "error": str(exc)[:1200]})
    except Exception as exc:
        result.update({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"[:2000]})
    finally:
        for name in ("model", "images", "target", "image_list", "targets", "loss", "losses", "logits"):
            if name in locals():
                try: del locals()[name]
                except Exception: pass
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            try:
                result["allocated_after_cleanup_bytes"] = torch.cuda.memory_allocated()
                result["reserved_after_cleanup_bytes"] = torch.cuda.memory_reserved()
            except Exception:
                pass
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
