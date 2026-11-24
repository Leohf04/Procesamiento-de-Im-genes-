"""Class-imbalance helpers for the urban-v1 multi-dataset experiments.

Weights are computed from training-split statistics only. Validation/test must
never be passed to these functions.
"""
from __future__ import annotations

from collections import Counter
from typing import Mapping, Sequence

import torch
from torch.utils.data import WeightedRandomSampler


def semantic_class_weights(
    pixel_counts: Mapping[str, int],
    class_to_id: Mapping[str, int],
    *,
    power: float = 0.5,
    min_weight: float = 0.25,
    max_weight: float = 4.0,
    ignore_names: Sequence[str] = (),
) -> torch.Tensor:
    """Return mean-one inverse-frequency pixel weights indexed by class ID.

    Missing classes receive zero (they cannot be learned from this train split).
    """
    if power <= 0 or min_weight <= 0 or max_weight < min_weight:
        raise ValueError("Invalid class-weight parameters")
    if not class_to_id:
        raise ValueError("class_to_id cannot be empty")
    ids = list(class_to_id.values())
    if min(ids) < 0 or len(ids) != len(set(ids)):
        raise ValueError("class IDs must be unique and non-negative")
    weights = torch.zeros(max(ids) + 1, dtype=torch.float32)
    valid = {}
    for name, class_id in class_to_id.items():
        count = int(pixel_counts.get(name, 0))
        if count < 0:
            raise ValueError(f"Negative pixel count for {name}")
        if count > 0 and name not in set(ignore_names):
            valid[class_id] = float(count) ** (-power)
    if not valid:
        raise ValueError("No configured class has positive training pixels")
    mean = sum(valid.values()) / len(valid)
    for class_id, raw in valid.items():
        weights[class_id] = min(max(raw / mean, min_weight), max_weight)
    # Renormalize after clipping so the average active-class weight is one.
    active = weights > 0
    weights[active] /= weights[active].mean()
    return weights


def instance_sample_weights(
    records: Sequence[Mapping],
    class_names: Sequence[str],
    *,
    count_key: str = "instance_counts",
    power: float = 0.5,
    empty_sample_weight: float | None = None,
) -> list[float]:
    """Weight each training image by the rarity of classes present in it.

    A sample's weight is the mean inverse-frequency score of its present
    classes, not the number of objects; this avoids favoring crowded images
    solely because they contain many instances.
    """
    if not records or not class_names or power <= 0:
        raise ValueError("records/classes must be non-empty and power positive")
    names = set(class_names)
    image_frequency = Counter()
    present_per_record = []
    for row in records:
        counts = row.get(count_key, {})
        present = {name for name in names if int(counts.get(name, 0)) > 0}
        if any(int(v) < 0 for v in counts.values()):
            raise ValueError(f"Negative instance count in {row.get('sample_id', '<unknown>')}")
        present_per_record.append(present)
        image_frequency.update(present)
    active = {name: freq ** (-power) for name, freq in image_frequency.items() if freq > 0}
    if not active:
        raise ValueError("No configured instance class occurs in training records")
    fallback = float(empty_sample_weight) if empty_sample_weight is not None else min(active.values())
    if fallback <= 0:
        raise ValueError("empty_sample_weight must be positive")
    weights = [sum(active[n] for n in present) / len(present) if present else fallback
               for present in present_per_record]
    mean = sum(weights) / len(weights)
    return [float(w / mean) for w in weights]


def make_instance_sampler(records, class_names, *, seed: int = 2026,
                          replacement: bool = True) -> WeightedRandomSampler:
    """Create a deterministic weighted sampler for the training split."""
    weights = instance_sample_weights(records, class_names)
    generator = torch.Generator()
    generator.manual_seed(int(seed))
    return WeightedRandomSampler(
        torch.as_tensor(weights, dtype=torch.double),
        num_samples=len(records),
        replacement=replacement,
        generator=generator,
    )
