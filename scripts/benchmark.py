"""Reproducible inference benchmark with warm-up, CUDA sync and latency percentiles."""
import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import time
from pathlib import Path
import cv2
import numpy as np
import torch
from src.pipeline import UrbanPerceptionPipeline
from src.utils.config_utils import load_config, resolve_backend, set_global_seed


def sync(device):
    if str(device).startswith("cuda") and torch.cuda.is_available():
        torch.cuda.synchronize()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Video file or camera index")
    parser.add_argument("--approach", choices=["instance", "hybrid"], default="instance")
    parser.add_argument("--backend", choices=["auto", "torch"], default="torch")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--warmup", type=int, default=30)
    parser.add_argument("--frames", type=int, default=300)
    parser.add_argument("--output", default="data/outputs/benchmark.json")
    args = parser.parse_args()
    cfg = load_config(args.config)
    seed = int(cfg.get("system", {}).get("seed", 42))
    set_global_seed(seed)
    backend = resolve_backend(args.backend)
    pipeline = UrbanPerceptionPipeline(args.approach, args.config, backend)
    cap = cv2.VideoCapture(int(args.source) if args.source.isdigit() else args.source)
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir {args.source}")
    latencies = []
    frame_shape = None
    try:
        for index in range(args.warmup + args.frames):
            ok, frame = cap.read()
            if not ok:
                break
            frame_shape = list(frame.shape)
            sync(getattr(pipeline.model, "device", "cpu"))
            start = time.perf_counter()
            pipeline.run_frame(frame)
            sync(getattr(pipeline.model, "device", "cpu"))
            elapsed = (time.perf_counter() - start) * 1000.0
            if index >= args.warmup:
                latencies.append(elapsed)
    finally:
        cap.release()
    if not latencies:
        raise RuntimeError("No se midieron frames; verifica la fuente.")
    values = np.asarray(latencies)
    model_cfg = cfg.get("models", {}).get(args.approach if args.approach == "instance" else "semantic_hybrid", {})
    checkpoint_paths = [model_cfg.get("urban_checkpoint")] if args.approach == "instance" else [
        model_cfg.get("checkpoint_path"), model_cfg.get("lane_checkpoint")
    ]
    checkpoint_hashes = {}
    for checkpoint_path in checkpoint_paths:
        if checkpoint_path and Path(checkpoint_path).is_file():
            digest = hashlib.sha256(Path(checkpoint_path).read_bytes()).hexdigest()
            checkpoint_hashes[checkpoint_path] = digest
    report = {
        "checkpoint_sha256": checkpoint_hashes,
        "protocol": "single-stream model pipeline; excludes decode, display and output encoding",
        "approach": args.approach, "backend": backend, "warmup_frames": args.warmup,
        "measured_frames": len(latencies), "input_shape_bgr": frame_shape,
        "latency_ms_mean": float(values.mean()), "latency_ms_median": float(np.percentile(values, 50)),
        "latency_ms_p95": float(np.percentile(values, 95)), "latency_ms_p99": float(np.percentile(values, 99)),
        "fps_from_mean_latency": float(1000.0 / values.mean()),
        "hardware": {"platform": platform.platform(), "processor": platform.processor(),
                     "torch": torch.__version__, "opencv": cv2.__version__,
                     "cuda_available": torch.cuda.is_available(),
                     "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None},
        "seed": seed, "python": platform.python_version(),
    }
    try:
        report["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        report["git_commit"] = None
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
