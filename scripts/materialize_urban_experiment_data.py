#!/usr/bin/env python3
"""Safely preflight or materialize train/validation assets for A2D2 and UrbanSyn.

Never accesses test. Dry-run estimates remote bytes without downloading images/masks.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from huggingface_hub import HfApi, hf_hub_download

A2D2_BUCKET = "audi-autonomous-driving-dataset"
HF_REPO = "UrbanSyn/UrbanSyn"
SPLITS = ("train", "val")
ASSET_NAMES = {"a2d2": ("rgb", "semantic"), "urbansyn": ("rgb", "semantic", "panoptic")}


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def select_rows(rows, limit, annotation_map=None, require_instances=False):
    candidates = list(rows)
    if require_instances:
        if annotation_map is None:
            raise ValueError("annotation_map is required when require_instances=True")
        candidates = [row for row in candidates
                      if annotation_map[str(row["sample_id"])].get("instance_counts")]
        if not candidates:
            raise RuntimeError("No samples with positive instance annotations were found.")
    if limit is None:
        return candidates
    if limit < 1:
        raise ValueError("max_samples_per_split must be >= 1")
    return candidates[:limit]


def check_byte_budget(total_bytes, max_total_bytes):
    if max_total_bytes is not None and total_bytes > max_total_bytes:
        raise RuntimeError(
            f"Estimated materialization {total_bytes:,} bytes exceeds "
            f"--max-total-bytes={max_total_bytes:,}; nothing was downloaded."
        )


def _s3_key(uri):
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or parsed.netloc != A2D2_BUCKET:
        raise ValueError(f"Unexpected A2D2 URI: {uri}")
    return parsed.path.lstrip("/")


def _hf_sizes(api, revision, cache):
    if revision not in cache:
        info = api.repo_info(repo_id=HF_REPO, repo_type="dataset",
                             revision=revision, files_metadata=True)
        sizes = {}
        for sibling in info.siblings:
            size = getattr(sibling, "size", None)
            if size is None:
                size = getattr(getattr(sibling, "lfs", None), "size", None)
            if size is not None:
                sizes[sibling.rfilename] = int(size)
        cache[revision] = sizes
    return cache[revision]


def estimate_split(ds, rows, s3, hf_api, hf_cache):
    estimates = []
    for row in rows:
        assets = row.get("assets", {})
        for name in ASSET_NAMES[ds]:
            if name not in assets:
                raise ValueError(f"{ds} {row.get('sample_id')}: missing asset {name}")
            if ds == "a2d2":
                key = _s3_key(assets[name])
                size = int(s3.head_object(Bucket=A2D2_BUCKET, Key=key)["ContentLength"])
            else:
                revision = row.get("revision")
                if not revision:
                    raise ValueError(f"UrbanSyn {row.get('sample_id')}: pinned revision missing")
                size = _hf_sizes(hf_api, revision, hf_cache).get(assets[name])
                if size is None:
                    raise RuntimeError(
                        f"Could not obtain remote size for UrbanSyn file {assets[name]} "
                        f"at revision {revision}; refusing an unbounded download."
                    )
            estimates.append({"sample_id": str(row["sample_id"]), "asset": name,
                              "bytes": size})
    return estimates


def download_s3(client, uri, dest, expected_size):
    key = _s3_key(uri)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size == expected_size:
        return
    if dest.exists():
        dest.unlink()
    client.download_file(A2D2_BUCKET, key, str(dest))
    if not dest.is_file() or dest.stat().st_size != expected_size:
        raise RuntimeError(f"A2D2 downloaded file size mismatch: {dest}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest-dir", type=Path, required=True)
    p.add_argument("--annotation-index-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--dry-run", action="store_true",
                   help="Estimate remote bytes and validate IDs; do not download assets.")
    p.add_argument("--max-samples-per-split", type=int,
                   help="Limit each dataset/split to the first N manifest rows (for smoke validation).")
    p.add_argument("--max-total-bytes", type=int,
                   help="Abort before downloading if selected remote assets exceed this byte budget.")
    p.add_argument("--require-instances", action="store_true",
                   help="Select only samples whose annotation index reports at least one instance.")
    a = p.parse_args()
    if a.max_samples_per_split is not None and a.max_samples_per_split < 1:
        p.error("--max-samples-per-split must be >= 1")
    if a.max_total_bytes is not None and a.max_total_bytes < 1:
        p.error("--max-total-bytes must be >= 1")

    s3 = boto3.client("s3", region_name="eu-central-1",
        config=Config(signature_version=UNSIGNED, retries={"max_attempts": 5}))
    hf_api = HfApi()
    hf_cache = {}
    selected = {}
    selected_annotations = {}
    estimates = []
    validation = []

    for ds in ("a2d2", "urbansyn"):
        for split in SPLITS:
            manifests = read_jsonl(a.manifest_dir / f"{ds}_{split}.jsonl")
            annotations = read_jsonl(a.annotation_index_dir / f"{ds}_{split}.annotations.jsonl")
            ids = [str(x.get("sample_id", "")) for x in manifests]
            ann_ids = [str(x.get("sample_id", "")) for x in annotations]
            if (not ids or any(not x for x in ids + ann_ids)
                or len(ids) != len(set(ids)) or len(ann_ids) != len(set(ann_ids))
                or set(ids) != set(ann_ids)):
                raise RuntimeError(f"{ds}/{split}: manifest/index IDs missing, duplicate or mismatched")
            ann_map = {str(x["sample_id"]): x for x in annotations}
            if any(ann_map[x].get("annotation_status", "ok") != "ok" for x in ids):
                raise RuntimeError(f"{ds}/{split}: annotations contain non-ok rows")
            chosen = select_rows(manifests, a.max_samples_per_split, ann_map, a.require_instances)
            chosen_ids = [str(x["sample_id"]) for x in chosen]
            selected[(ds, split)] = chosen
            selected_annotations[(ds, split)] = [ann_map[x] for x in chosen_ids]
            validation.append({"dataset": ds, "split": split,
                               "manifest_samples": len(manifests),
                               "selected_samples": len(chosen),
                               "ids_unique": True, "manifest_index_ids_match": True})
            estimates.extend({"dataset": ds, "split": split, **x}
                             for x in estimate_split(ds, chosen, s3, hf_api, hf_cache))

    total_bytes = sum(x["bytes"] for x in estimates)
    check_byte_budget(total_bytes, a.max_total_bytes)
    report = {
        "status": "PREFLIGHT_PASS" if a.dry_run else "MATERIALIZED",
        "dry_run": bool(a.dry_run),
        "splits": ["train", "val"],
        "test_touched": False,
        "training_started": False,
        "max_samples_per_split": a.max_samples_per_split,\n        "require_instances": bool(a.require_instances),
        "estimated_remote_asset_bytes": total_bytes,
        "estimated_remote_asset_gib": round(total_bytes / (1024 ** 3), 3),
        "asset_count": len(estimates),
        "selection_validation": validation,
        "asset_estimates": estimates,
        "output_dir": str(a.output_dir),
    }
    if a.dry_run:
        a.output_dir.mkdir(parents=True, exist_ok=True)
        (a.output_dir / "materialization_preflight.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    class_path = a.output_dir / "a2d2" / "class_list.json"
    class_path.parent.mkdir(parents=True, exist_ok=True)
    if not class_path.exists():
        obj = s3.get_object(Bucket=A2D2_BUCKET, Key="camera_lidar_semantic/class_list.json")
        class_path.write_bytes(obj["Body"].read())

    size_map = {(x["dataset"], x["split"], x["sample_id"], x["asset"]): x["bytes"]
                for x in estimates}
    summary = []
    for ds in ("a2d2", "urbansyn"):
        for split in SPLITS:
            local = []
            for row in selected[(ds, split)]:
                sid = str(row["sample_id"])
                key = hashlib.sha256(sid.encode()).hexdigest()[:20]
                folder = a.output_dir / ds / split / key
                assets = row["assets"]
                if ds == "a2d2":
                    image, semantic = folder / "rgb.png", folder / "semantic.png"
                    download_s3(s3, assets["rgb"], image,
                                size_map[(ds, split, sid, "rgb")])
                    download_s3(s3, assets["semantic"], semantic,
                                size_map[(ds, split, sid, "semantic")])
                    record = {"sample_id": sid, "dataset": ds, "image": str(image),
                              "semantic": str(semantic), "instance": str(semantic)}
                else:
                    revision = row["revision"]
                    paths = {}
                    for name in ASSET_NAMES[ds]:
                        path = Path(hf_hub_download(
                            repo_id=HF_REPO, repo_type="dataset", revision=revision,
                            filename=assets[name], local_dir=str(folder / "hf")))
                        expected = size_map[(ds, split, sid, name)]
                        if not path.is_file() or path.stat().st_size != expected:
                            raise RuntimeError(f"UrbanSyn downloaded file size mismatch: {path}")
                        paths[name] = str(path)
                    record = {"sample_id": sid, "dataset": ds, **paths}
                local.append(record)
            write_jsonl(a.output_dir / "local_manifests" / f"{ds}_{split}.jsonl", local)
            write_jsonl(a.output_dir / "local_annotation_index" /
                        f"{ds}_{split}.annotations.jsonl", selected_annotations[(ds, split)])
            summary.append({"dataset": ds, "split": split, "samples": len(local),
                            "materialized_assets": True})
    report.update({"status": "PASS", "datasets": summary,
                   "local_annotation_index_dir": str(a.output_dir / "local_annotation_index")})
    (a.output_dir / "materialization_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
