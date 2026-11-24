"""Remote, bounded UrbanSyn preflight against the public Hugging Face dataset.

Downloads only a few matched files into a temporary directory; never snapshots
or clones the full dataset. UrbanSyn modality filenames have different prefixes
(rgb_0001, ss_0001, panoptic_0001, bbox2d_0001), so matching uses the numeric ID.
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from collections import Counter
from pathlib import Path, PurePosixPath
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from PIL import Image

from src.data_adapters import decode_urbansyn_panoptic, decode_urbansyn_semantic
from huggingface_hub import HfApi, hf_hub_download

REPO_ID = "UrbanSyn/UrbanSyn"
REVISION = "main"
DYNAMIC_IDS = {11, 12, 13, 14, 15, 16, 17, 18}
MODALITY_PREFIXES = {"rgb": "rgb_", "semantic": "ss_", "panoptic": "panoptic_", "bbox": "bbox2d_"}


def modality(path: str) -> str | None:
    parts = {p.lower() for p in PurePosixPath(path).parts[:-1]}
    for folder, name in (("rgb", "rgb"), ("ss", "semantic"),
                         ("panoptic", "panoptic"), ("bbox2d", "bbox")):
        if folder in parts:
            return name
    return None


def sample_id(path: str, kind: str) -> str:
    stem = PurePosixPath(path).stem
    prefix = MODALITY_PREFIXES[kind]
    if stem.startswith(prefix):
        return stem[len(prefix):]
    match = re.search(r"(\d+)$", stem)
    return match.group(1) if match else stem


def index_files(paths: list[str]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for path in paths:
        kind = modality(path)
        if not kind:
            continue
        identifier = sample_id(path, kind)
        index.setdefault(identifier, {})[kind] = path
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
    complete = [(identifier, record) for identifier, record in sorted(indexed.items())
                if all(k in record for k in ("rgb", "semantic", "panoptic", "bbox"))]
    if len(complete) < args.samples:
        counts = Counter(k for rec in indexed.values() for k in rec)
        raise RuntimeError(
            f"Insufficient complete RGB/SS/panoptic/bbox2D matches: "
            f"{len(complete)}; modality counts={dict(counts)}; "
            f"sample index={list(indexed.items())[:3]}"
        )

    report = {
        "dataset": REPO_ID, "revision": REVISION,
        "commit": getattr(info, "sha", None),
        "total_repository_files": len(files),
        "indexed_sample_ids": len(indexed), "complete_sample_ids": len(complete),
        "samples": [],
        "license_review": {
            "huggingface_metadata": "cc-by-sa-4.0",
            "official_website_terms": "CC BY-NC-SA 4.0",
            "status": "REVIEW_REQUIRED_CONFLICTING_DECLARATIONS",
        },
    }
    with tempfile.TemporaryDirectory(prefix="urbansyn-preflight-") as tmp:
        for identifier, record in complete[:args.samples]:
            local = {}
            for kind, remote in record.items():
                local[kind] = hf_hub_download(
                    repo_id=REPO_ID, repo_type="dataset", revision=REVISION,
                    filename=remote, cache_dir=tmp,
                )
            with Image.open(local["rgb"]) as im:
                if im.mode != "RGB":
                    raise ValueError(f"{identifier}: RGB mode is {im.mode}")
                rgb_size = im.size
            with Image.open(local["semantic"]) as im:
                sem = np.asarray(im)
                semantic_storage_shape = list(sem.shape)
                if sem.ndim == 3 and sem.shape[2] == 3 and np.array_equal(sem[:, :, 0], sem[:, :, 1]) and np.array_equal(sem[:, :, 0], sem[:, :, 2]):
                    sem = sem[:, :, 0]
                if sem.ndim != 2:
                    raise ValueError(
                        f"{identifier}: semantic mask is not a grayscale class-ID image "
                        f"(or RGB triplicate): {sem.shape}"
                    )
                if im.size != rgb_size:
                    raise ValueError(f"{identifier}: RGB/semantic dimensions mismatch")
                sem_ids = sorted(int(x) for x in np.unique(sem))
                if any(x < 0 or x > 19 for x in sem_ids):
                    raise ValueError(f"{identifier}: unexpected semantic IDs {sem_ids}")
            with Image.open(local["panoptic"]) as im:
                pan = np.asarray(im)
                if pan.ndim != 3 or pan.shape[2] != 3:
                    raise ValueError(f"{identifier}: panoptic mask is not RGB: {pan.shape}")
                if im.size != rgb_size:
                    raise ValueError(f"{identifier}: RGB/panoptic dimensions mismatch")
                panoptic_class_ids = sorted(int(x) for x in np.unique(pan[:, :, 2]))
                observed = set(panoptic_class_ids) - {0}
                if not observed.issubset(DYNAMIC_IDS):
                    raise ValueError(
                        f"{identifier}: unexpected panoptic class IDs {sorted(observed)}"
                    )
            # Exercise the project's real adapters on the downloaded files.
            decoded_semantic = decode_urbansyn_semantic(sem)
            if decoded_semantic.shape != sem.shape[:2] and decoded_semantic.shape != sem.shape:
                raise ValueError(f"{identifier}: semantic adapter changed spatial dimensions")
            dynamic_map = {class_id: class_id for class_id in DYNAMIC_IDS}
            decoded_panoptic = decode_urbansyn_panoptic(pan, dynamic_map)
            if decoded_panoptic["masks"].ndim != 3 or decoded_panoptic["boxes"].shape != (len(decoded_panoptic["labels"]), 4):
                raise ValueError(f"{identifier}: invalid instance target array shapes")
            if len(decoded_panoptic["labels"]) and decoded_panoptic["masks"].shape[1:] != (rgb_size[1], rgb_size[0]):
                raise ValueError(f"{identifier}: instance target dimensions mismatch")
            with open(local["bbox"], encoding="utf-8") as f:
                bbox = json.load(f)
            if not isinstance(bbox, (dict, list)):
                raise ValueError(f"{identifier}: bbox2D JSON root must be object/list")
            report["samples"].append({
                "sample_id": identifier,
                "size": list(rgb_size),
                "semantic_ids": sem_ids,
                "semantic_storage_shape": semantic_storage_shape,
                "panoptic_blue_channel_ids": panoptic_class_ids,
                "adapter_validation": {
                    "semantic_output_shape": list(decoded_semantic.shape),
                    "semantic_unique_ids": sorted(int(x) for x in np.unique(decoded_semantic)),
                    "panoptic_instance_count": int(len(decoded_panoptic["labels"])),
                    "mask_array_shape": list(decoded_panoptic["masks"].shape),
                    "box_array_shape": list(decoded_panoptic["boxes"].shape),
                    "target_labels": sorted(int(x) for x in np.unique(decoded_panoptic["labels"])),
                },
                "bbox_json_root": type(bbox).__name__,
                "bbox_json_keys": sorted(bbox.keys()) if isinstance(bbox, dict) else None,
                "remote_files": record,
            })

    report["result"] = "PASS"
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("RESULT: UrbanSyn remote sample + project adapters PASSED")
    print("Validated adapters against", len(report["samples"]), "real remote samples")


if __name__ == "__main__":
    main()
