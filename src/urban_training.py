"""Training-loader integration for the urban-v1 datasets.

This module consumes already materialized local datasets plus annotation-index
rows from the TRAIN split only. It never reads validation/test statistics.
"""
from __future__ import annotations

from typing import Mapping, Sequence

import torch
from torch.utils.data import DataLoader

from src.class_balancing import make_instance_sampler, semantic_class_weights
from src.data_adapters import detection_collate_fn


def build_urban_train_loader(
    dataset,
    training_annotation_rows: Sequence[Mapping],
    *,
    task: str,
    class_to_id: Mapping[str, int],
    batch_size: int,
    num_workers: int = 0,
    seed: int = 2026,
    pin_memory: bool = False,
    drop_last: bool = False,
):
    """Build a train DataLoader and return (loader, loss_class_weights).

    For semantic segmentation, sampling remains uniform and pixel-level class
    weights are returned for CrossEntropyLoss(weight=...). For instances, a
    WeightedRandomSampler reweights images by the rarity of classes present.
    The caller must pass the annotation rows paired with this dataset's train
    manifest; validation/test rows are rejected when their split is declared.
    """
    if task not in {"semantic", "instances"}:
        raise ValueError("task must be 'semantic' or 'instances'")
    if batch_size < 1 or num_workers < 0:
        raise ValueError("batch_size must be >= 1 and num_workers >= 0")
    rows = [dict(row) for row in training_annotation_rows]
    if len(rows) != len(dataset):
        raise ValueError(
            f"Training annotation rows ({len(rows)}) must match dataset length ({len(dataset)})"
        )

    # Dataset adapters retain the source manifest records. Validate identity and
    # order, not only length: two manifests can contain the same IDs in different
    # orders, which would silently attach the wrong class statistics to images.
    dataset_records = getattr(dataset, "records", None)
    if dataset_records is None:
        raise ValueError(
            "Dataset must expose manifest records with sample_id to validate annotation alignment"
        )
    dataset_ids = [str(record.get("sample_id", "")) for record in dataset_records]
    annotation_ids = [str(row.get("sample_id", "")) for row in rows]
    if any(not sample_id for sample_id in dataset_ids + annotation_ids):
        raise ValueError("Dataset and annotation rows must all contain non-empty sample_id values")
    if len(set(dataset_ids)) != len(dataset_ids):
        raise ValueError("Dataset manifest contains duplicate sample_id values")
    if len(set(annotation_ids)) != len(annotation_ids):
        raise ValueError("Training annotation rows contain duplicate sample_id values")
    if dataset_ids != annotation_ids:
        mismatch = next(
            index for index, (dataset_id, annotation_id)
            in enumerate(zip(dataset_ids, annotation_ids))
            if dataset_id != annotation_id
        )
        raise ValueError(
            "Dataset and annotation rows are not aligned by sample_id/order "
            f"at index {mismatch}: dataset={dataset_ids[mismatch]!r}, "
            f"annotations={annotation_ids[mismatch]!r}"
        )

    wrong_split = [
        str(row.get("sample_id", index))
        for index, row in enumerate(rows)
        if row.get("split", "train") != "train"
    ]
    if wrong_split:
        raise ValueError(f"Only train annotation rows are allowed; found: {wrong_split[:5]}")
    if any(row.get("annotation_status", "ok") != "ok" for row in rows):
        raise ValueError("Training annotation rows must all have annotation_status='ok'")

    if task == "semantic":
        pixel_totals = {}
        for row in rows:
            for name, count in row.get("semantic_pixels", {}).items():
                pixel_totals[name] = pixel_totals.get(name, 0) + int(count)
        weights = semantic_class_weights(pixel_totals, class_to_id)
        loader = DataLoader(
            dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers,
            pin_memory=pin_memory, drop_last=drop_last,
            generator=torch.Generator().manual_seed(int(seed)),
        )
        return loader, weights

    sampler = make_instance_sampler(rows, list(class_to_id), seed=seed)
    loader = DataLoader(
        dataset, batch_size=batch_size, sampler=sampler, num_workers=num_workers,
        pin_memory=pin_memory, drop_last=drop_last, collate_fn=detection_collate_fn,
    )
    return loader, None


def build_urban_train_loaders(
    dataset_specs: Mapping[str, Mapping],
    *,
    task: str,
    batch_size: int,
    num_workers: int = 0,
    seed: int = 2026,
    pin_memory: bool = False,
    drop_last: bool = False,
):
    """Build independent train loaders for multiple dataset domains.

    dataset_specs maps each domain name (for example a2d2 or urbansyn) to
    its own dataset, annotation_rows and class_to_id. Each domain is passed
    separately through build_urban_train_loader; pixel totals and image
    frequencies are never pooled across domains. Returns
    {name: (loader, class_weights)}.
    """
    if not dataset_specs:
        raise ValueError("dataset_specs cannot be empty")

    loaders = {}
    seen_dataset_objects = set()
    for dataset_name, spec in dataset_specs.items():
        if not isinstance(dataset_name, str) or not dataset_name.strip():
            raise ValueError("Dataset names must be non-empty strings")
        if not isinstance(spec, Mapping):
            raise ValueError(f"Dataset spec for {dataset_name!r} must be a mapping")
        required = {"dataset", "annotation_rows", "class_to_id"}
        missing = required - set(spec)
        if missing:
            raise ValueError(
                f"Dataset spec for {dataset_name!r} is missing: {sorted(missing)}"
            )

        dataset = spec["dataset"]
        if id(dataset) in seen_dataset_objects:
            raise ValueError(
                "Each domain must use a distinct dataset object; do not concatenate or reuse datasets"
            )
        seen_dataset_objects.add(id(dataset))

        rows = spec["annotation_rows"]
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
            raise ValueError(f"Annotation rows for {dataset_name!r} must be a sequence")
        if not isinstance(spec["class_to_id"], Mapping):
            raise ValueError(f"class_to_id for {dataset_name!r} must be a mapping")
        records = getattr(dataset, "records", None)
        if records is not None:
            tagged = {
                str(record["dataset"]).strip().lower()
                for record in records
                if record.get("dataset") not in (None, "")
            }
            if tagged and tagged != {dataset_name.strip().lower()}:
                raise ValueError(
                    f"Dataset records for {dataset_name!r} contain foreign dataset tags: {sorted(tagged)}"
                )
        row_tags = {
            str(row["dataset"]).strip().lower()
            for row in rows
            if row.get("dataset") not in (None, "")
        }
        if row_tags and row_tags != {dataset_name.strip().lower()}:
            raise ValueError(
                f"Annotation rows for {dataset_name!r} contain foreign dataset tags: {sorted(row_tags)}"
            )

        loaders[dataset_name] = build_urban_train_loader(
            dataset,
            rows,
            task=task,
            class_to_id=spec["class_to_id"],
            batch_size=batch_size,
            num_workers=num_workers,
            seed=seed,
            pin_memory=pin_memory,
            drop_last=drop_last,
        )
    return loaders
