#!/usr/bin/env python3
"""Non-training audit of Colab GPU, RAM, disk, and mounted Drive checkpoint I/O."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import tempfile
import time
from pathlib import Path

import torch


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def memory_info():
    result = {}
    try:
        import psutil
        vm = psutil.virtual_memory()
        result = {
            "ram_total_bytes": int(vm.total),
            "ram_available_bytes": int(vm.available),
            "ram_used_bytes": int(vm.used),
        }
    except Exception:
        try:
            values = {}
            for line in Path("/proc/meminfo").read_text().splitlines():
                key, raw = line.split(":", 1)
                values[key] = int(raw.strip().split()[0]) * 1024
            result = {
                "ram_total_bytes": values.get("MemTotal"),
                "ram_available_bytes": values.get("MemAvailable"),
            }
        except Exception:
            result = {"ram_status": "unavailable"}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Persistent destination, normally a mounted Google Drive folder.")
    parser.add_argument("--gpu-probe-mib", type=int, default=64)
    args = parser.parse_args()
    if args.gpu_probe_mib < 1 or args.gpu_probe_mib > 256:
        raise SystemExit("--gpu-probe-mib must be between 1 and 256 MiB")

    out = args.output_dir.expanduser().resolve()
    if not out.is_dir():
        raise SystemExit(f"Output directory does not exist or is not mounted: {out}")
    report = {
        "status": "RUNNING",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_version": torch.version.cuda,
        "device_count": torch.cuda.device_count(),
        "devices": [],
        "memory": memory_info(),
        "disk": {},
        "drive_checkpoint_io": {},
        "training_started": False,
        "dataset_downloaded": False,
        "test_split_touched": False,
        "forward_calls": 0,
        "backward_calls": 0,
        "optimizer_steps": 0,
    }

    for path_name, path in {
        "runtime": Path("/content"),
        "drive_output": out,
    }.items():
        usage = shutil.disk_usage(path)
        report["disk"][path_name] = {
            "path": str(path),
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
        }

    if torch.cuda.is_available():
        for index in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(index)
            free_bytes, total_bytes = torch.cuda.mem_get_info(index)
            report["devices"].append({
                "index": index,
                "name": props.name,
                "total_memory_bytes": int(props.total_memory),
                "free_memory_before_probe_bytes": int(free_bytes),
                "memory_total_from_mem_get_info_bytes": int(total_bytes),
                "compute_capability": [props.major, props.minor],
            })
        try:
            device = torch.device("cuda:0")
            torch.cuda.reset_peak_memory_stats(device)
            n = args.gpu_probe_mib * 1024 * 1024 // 4
            probe = torch.empty(n, dtype=torch.float32, device=device)
            probe.fill_(1.0)
            torch.cuda.synchronize(device)
            report["gpu_allocation_probe"] = {
                "status": "PASS",
                "allocated_mib": args.gpu_probe_mib,
                "tensor_sum": float(probe.sum().item()),
                "peak_allocated_bytes": int(torch.cuda.max_memory_allocated(device)),
                "peak_reserved_bytes": int(torch.cuda.max_memory_reserved(device)),
            }
            del probe
            torch.cuda.empty_cache()
        except Exception as exc:
            report["gpu_allocation_probe"] = {
                "status": "FAIL",
                "error": f"{type(exc).__name__}: {exc}",
            }
    else:
        report["gpu_allocation_probe"] = {
            "status": "CPU_ONLY",
            "detail": "No CUDA device was assigned to this runtime.",
        }

    # Round-trip a small synthetic checkpoint on the mounted Drive filesystem.
    # This validates write/read through the current mount, not persistence after
    # VM destruction or a future session.
    checkpoint_path = out / ".runtime_checkpoint_io_probe.pt"
    temp_path = out / (checkpoint_path.name + ".tmp")
    expected = torch.arange(256 * 1024, dtype=torch.float32).reshape(256, 1024)
    payload = {
        "probe": "drive-checkpoint-io-v1",
        "tensor": expected,
        "torch_version": torch.__version__,
    }
    try:
        torch.save(payload, temp_path)
        with temp_path.open("rb") as f:
            os.fsync(f.fileno())
        digest_before = sha256(temp_path)
        os.replace(temp_path, checkpoint_path)
        loaded = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        equal = torch.equal(loaded["tensor"], expected)
        digest_after = sha256(checkpoint_path)
        report["drive_checkpoint_io"] = {
            "status": "PASS" if equal and digest_before == digest_after else "FAIL",
            "path": str(checkpoint_path),
            "bytes": checkpoint_path.stat().st_size,
            "sha256_before_rename": digest_before,
            "sha256_after_read": digest_after,
            "tensor_equal": bool(equal),
            "read_after_write": True,
            "note": "Validates write/read on the current mounted Drive filesystem only; it does not prove survival after runtime teardown.",
        }
    except Exception as exc:
        report["drive_checkpoint_io"] = {
            "status": "FAIL",
            "error": f"{type(exc).__name__}: {exc}",
        }
    finally:
        for path in (temp_path, checkpoint_path):
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass

    report["status"] = (
        "PASS" if report["drive_checkpoint_io"].get("status") == "PASS"
        and (not report["cuda_available"]
             or report.get("gpu_allocation_probe", {}).get("status") == "PASS")
        else "FAIL"
    )
    report_path = out / "training_runtime_preflight.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"REPORT_PATH={report_path}")
    if report["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
