"""Training-loader integration for the urban-v1 datasets.

This module consumes already materialized local datasets plus annotation-index
rows from the TRAIN split only. It never reads validation/test statistics.
"""
from __future__ import annotations

from typing import Mapping, Sequence

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
            generator=__import__("torch").Generator().manual_seed(int(seed)),
        )
        return loader, weights

    sampler = make_instance_sampler(rows, list(class_to_id), seed=seed)
    loader = DataLoader(
        dataset, batch_size=batch_size, sampler=sampler, num_workers=num_workers,
        pin_memory=pin_memory, drop_last=drop_last, collate_fn=detection_collate_fn,
    )
    return loader, None
