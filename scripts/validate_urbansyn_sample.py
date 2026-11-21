"""Remote, bounded UrbanSyn preflight against the public Hugging Face dataset.

Downloads only a few matched files into a temporary directory; never snapshots
or clones the full 86 GB repository. The report records actual file sizes,
dimensions, annotation modes/classes and JSON structure.
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from collections import Counter
from pathlib import PurePosixPath

import numpy as np
from PIL import Image
from huggingface_hub import HfApi, hf_hub_download

REPO_ID = "UrbanSyn/UrbanSyn"
REVISION = "main"
DYNAMIC_IDS = {11, 12, 13, 14, 15, 16, 17, 18}


def modality(path: str) -> str | None:
    parts = {p.lower() for p in PurePosixPath(path).parts[:-1]}
    for folder, name in (("rgb", "rgb"), ("ss", "semantic"),
                         ("panoptic", "panoptic"), ("bbox2d", "bbox")):
        if folder in parts:
            return name
    return None


def index_files(paths: list[str]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for path in paths:
        kind = modality(path)
        if not kind:
            continue
        stem = PurePosixPath(path).stem
        index.setdefault(stem, {})[kind] = path
    return index


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.samples <= 4:
        parser.error("--samples must be between 1 and 4")

    api = HfApi()
    info = api.dataset_info(REPO_ID, revision=REVISION, files_metadata=True)
    files = api.list_repo_files(REPO_ID, repo_type="dataset", revision=REVISION)
    indexed = index_files(files)
    complete = [(stem, record) for stem, record in sorted(indexed.items())
                if all(k in record for k in ("rgb", "semantic", "panoptic", "bbox"))]
    if len(complete) < args.samples:
        counts = Counter(k for rec in indexed.values() for k in rec)
        raise RuntimeError(
            f"Insufficient complete RGB/SS/panoptic/bbox2D matches: "
            f"{len(complete)}; modality counts={dict(counts)}"
        )

    report = {
        "dataset": REPO_ID, "revision": REVISION,
        "commit": getattr(info, "sha", None),
        "total_repository_files": len(files),
        "indexed_stems": len(indexed), "complete_stems": len(complete),
        "samples": [], "license": "cc-by-sa-4.0 (verify current terms before reuse)",
    }
    with tempfile.TemporaryDirectory(prefix="urbansyn-preflight-") as tmp:
        for stem, record in complete[:args.samples]:
            local = {}
            for kind, remote in record.items():
                local[kind] = hf_hub_download(
                    repo_id=REPO_ID, repo_type="dataset", revision=REVISION,
                    filename=remote, cache_dir=tmp,
                )
            with Image.open(local["rgb"]) as im:
                if im.mode != "RGB":
                    raise ValueError(f"{stem}: RGB mode is {im.mode}")
                rgb_size = im.size
            with Image.open(local["semantic"]) as im:
                sem = np.asarray(im)
                if sem.ndim != 2:
                    raise ValueError(f"{stem}: semantic mask is not grayscale: {sem.shape}")
                if im.size != rgb_size:
                    raise ValueError(f"{stem}: RGB/semantic dimensions mismatch")
                sem_ids = sorted(int(x) for x in np.unique(sem))
                if any(x < 0 or x > 19 for x in sem_ids):
                    raise ValueError(f"{stem}: unexpected semantic IDs {sem_ids}")
            with Image.open(local["panoptic"]) as im:
                pan = np.asarray(im)
                if pan.ndim != 3 or pan.shape[2] != 3:
                    raise ValueError(f"{stem}: panoptic mask is not RGB: {pan.shape}")
                if im.size != rgb_size:
                    raise ValueError(f"{stem}: RGB/panoptic dimensions mismatch")
                panoptic_class_ids = sorted(int(x) for x in np.unique(pan[:, :, 2]))
            with open(local["bbox"], encoding="utf-8") as f:
                bbox = json.load(f)
            if not isinstance(bbox, (dict, list)):
                raise ValueError(f"{stem}: bbox2D JSON root must be object/list")
            report["samples"].append({
                "stem": stem, "size": list(rgb_size),
                "semantic_ids": sem_ids,
                "panoptic_blue_channel_ids": panoptic_class_ids,
                "bbox_json_root": type(bbox).__name__,
                "bbox_json_keys": sorted(bbox.keys()) if isinstance(bbox, dict) else None,
                "remote_files": record,
            })

    report["result"] = "PASS"
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("RESULT: UrbanSyn bounded remote preflight PASSED")


if __name__ == "__main__":
    main()
