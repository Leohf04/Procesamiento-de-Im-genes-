#!/usr/bin/env python3
"""Build class-aware manifests from per-sample annotation statistics.

Input manifests are the remote-reference JSONL files produced by
prepare_reproducible_subsets.py. For each split, a matching annotation index
must contain one row per sample with semantic_pixels and instance_counts maps.
The planner never moves samples between splits and never merges dataset domains.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


TASKS = {
    "semantic": ("semantic_pixels", ("a2d2", "urbansyn")),
    "instances": ("instance_counts", ("urbansyn", "a2d2")),
}


def _tie_key(seed: int, sample_id: str) -> str:
    return hashlib.sha256(f"{seed}:{sample_id}".encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(path)
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def attach_annotation_stats(manifest: list[dict], annotation_rows: list[dict]) -> list[dict]:
    index = {}
    for row in annotation_rows:
        sample_id = str(row.get("sample_id", ""))
        if not sample_id or sample_id in index:
            raise ValueError(f"Missing or duplicate annotation sample_id: {sample_id!r}")
        if row.get("annotation_status", "ok") != "ok":
            raise ValueError(f"Annotation index contains non-ok sample: {sample_id}")
        if "semantic_pixels" not in row or "instance_counts" not in row:
            raise ValueError(f"Annotation row {sample_id} lacks semantic_pixels/instance_counts")
        index[sample_id] = row
    attached = []
    for record in manifest:
        sample_id = str(record["sample_id"])
        if sample_id not in index:
            raise ValueError(f"No annotation statistics for {record['dataset']}:{sample_id}")
        enriched = dict(record)
        stats = index[sample_id]
        enriched["semantic_pixels"] = {str(k): int(v) for k, v in stats["semantic_pixels"].items() if int(v) > 0}
        enriched["instance_counts"] = {str(k): int(v) for k, v in stats["instance_counts"].items() if int(v) > 0}
        if any(v < 0 for v in [*enriched["semantic_pixels"].values(), *enriched["instance_counts"].values()]):
            raise ValueError(f"Negative annotation count for {sample_id}")
        attached.append(enriched)
    return attached


def greedy_balanced_select(records: list[dict], *, count_key: str, seed: int,
                           max_samples: int, per_class_cap: int | None = None) -> tuple[list[dict], dict]:
    """Greedy deterministic multilabel balancing by sample presence/count.

    Selection is confined to the supplied split. The objective first covers
    classes with the fewest available samples, then reduces count imbalance.
    """
    if max_samples < 1:
        raise ValueError("max_samples must be >= 1")
    available = Counter()
    totals = Counter()
    normalized = []
    seen = set()
    for row in records:
        sample_id = str(row["sample_id"])
        if sample_id in seen:
            raise ValueError(f"Duplicate sample in split: {sample_id}")
        seen.add(sample_id)
        raw_counts = {str(k): int(v) for k, v in row.get(count_key, {}).items()}
        if any(value < 0 for value in raw_counts.values()):
            raise ValueError(f"Negative class count in {sample_id}")
        counts = {label: value for label, value in raw_counts.items() if value > 0}
        normalized.append((row, counts))
        for label, value in counts.items():
            available[label] += 1
            totals[label] += value
    if not normalized:
        raise ValueError("Cannot balance an empty split")
    selected = []
    remaining = list(normalized)
    selected_presence = Counter()
    selected_counts = Counter()
    target_size = min(max_samples, len(remaining))
    while remaining and len(selected) < target_size:
        def score(item):
            row, counts = item
            gains = []
            for label, value in counts.items():
                if per_class_cap is not None and selected_presence[label] >= per_class_cap:
                    continue
                # Rare classes receive greater weight; counts distinguish dense examples.
                rarity = 1.0 / max(available[label], 1)
                deficit = 1.0 / (1 + selected_presence[label])
                gains.append(rarity * deficit * (1.0 + min(value, 20) / 20.0))
            return (sum(gains), _tie_key(seed, str(row["sample_id"])))
        best = max(remaining, key=score)
        remaining.remove(best)
        row, counts = best
        selected.append(row)
        for label, value in counts.items():
            selected_presence[label] += 1
            selected_counts[label] += value
    summary = {
        "available_samples": len(records),
        "selected_samples": len(selected),
        "available_samples_per_class": dict(sorted(available.items())),
        "selected_samples_per_class": dict(sorted(selected_presence.items())),
        "selected_annotation_counts_per_class": dict(sorted(selected_counts.items())),
        "uncovered_classes": sorted(set(available) - set(selected_presence)),
        "seed": seed,
        "selection": "deterministic greedy multilabel; split-preserving",
    }
    return selected, summary


def build_plan(manifest_dir: Path, annotation_dir: Path, output_dir: Path, *,
               seed: int = 2026, max_samples_per_split: int = 1000,
               per_class_cap: int | None = None) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "ontology_version": "urban-v1",
        "seed": seed,
        "max_samples_per_split": max_samples_per_split,
        "per_class_cap": per_class_cap,
        "dataset_roles": {
            "semantic": {"a2d2": "real-domain semantic source", "urbansyn": "synthetic semantic source"},
            "instances": {"urbansyn": "primary synthetic instance source", "a2d2": "real-domain complementary ablation"}
        },
        "plans": {},
        "warning": "No cross-domain concatenation: dataset manifests remain separate. Experimental hash splits are not official splits."
    }
    for dataset in ("a2d2", "urbansyn"):
        report["plans"][dataset] = {}
        for split in ("train", "val", "test"):
            manifest_path = manifest_dir / f"{dataset}_{split}.jsonl"
            annotation_path = annotation_dir / f"{dataset}_{split}.annotations.jsonl"
            manifest = read_jsonl(manifest_path)
            annotations = read_jsonl(annotation_path)
            enriched = attach_annotation_stats(manifest, annotations)
            report["plans"][dataset][split] = {}
            for task, (count_key, _) in TASKS.items():
                # A2D2 instance targets are an auxiliary experiment, not pooled into UrbanSyn.
                if task == "instances" and dataset == "a2d2":
                    role = "complementary_ablation"
                elif task == "instances":
                    role = "primary"
                else:
                    role = "separate_domain_source"
                if split == "train":
                    selected, summary = greedy_balanced_select(
                        enriched, count_key=count_key, seed=seed,
                        max_samples=max_samples_per_split, per_class_cap=per_class_cap
                    )
                else:
                    # Keep validation and test complete and in manifest order.
                    selected = enriched
                    _, summary = greedy_balanced_select(
                        enriched, count_key=count_key, seed=seed,
                        max_samples=len(enriched), per_class_cap=None
                    )
                    summary["selection"] = "complete split; no downsampling or reordering"
                out_path = output_dir / f"{dataset}_{task}_{split}.jsonl"
                write_jsonl(out_path, selected)
                report["plans"][dataset][split][task] = {
                    "role": role, "manifest": out_path.name, **summary
                }
    (output_dir / "balanced_training_plan.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifests-dir", type=Path, required=True)
    parser.add_argument("--annotation-index-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/balanced"))
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-samples-per-split", type=int, default=1000)
    parser.add_argument("--per-class-cap", type=int, default=0,
                        help="Maximum selected samples containing each class; 0 disables the cap.")
    args = parser.parse_args()
    report = build_plan(
        args.manifests_dir, args.annotation_index_dir, args.output_dir,
        seed=args.seed, max_samples_per_split=args.max_samples_per_split,
        per_class_cap=args.per_class_cap or None,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
