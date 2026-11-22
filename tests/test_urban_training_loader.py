import pytest
import torch
from torch.utils.data import TensorDataset

from src.urban_training import build_urban_train_loader


def _dataset(n=4):
    return TensorDataset(torch.arange(n).float().unsqueeze(1))


def test_semantic_train_loader_returns_train_only_pixel_weights():
    rows = [
        {"sample_id": "a", "split": "train", "semantic_pixels": {"road": 100, "car": 1}},
        {"sample_id": "b", "split": "train", "semantic_pixels": {"road": 100, "car": 9}},
        {"sample_id": "c", "split": "train", "semantic_pixels": {"road": 50, "car": 0}},
        {"sample_id": "d", "split": "train", "semantic_pixels": {"road": 50, "car": 0}},
    ]
    loader, weights = build_urban_train_loader(
        _dataset(), rows, task="semantic", class_to_id={"road": 0, "car": 1},
        batch_size=2, seed=11,
    )
    assert len(loader) == 2
    assert weights.shape == (2,)
    assert torch.isfinite(weights).all()
    assert weights[1] > weights[0]


def test_instance_train_loader_uses_weighted_sampler_and_detection_collate():
    rows = [
        {"sample_id": "a", "split": "train", "instance_counts": {"car": 3}},
        {"sample_id": "b", "split": "train", "instance_counts": {"car": 2}},
        {"sample_id": "c", "split": "train", "instance_counts": {"bus": 1}},
        {"sample_id": "d", "split": "train", "instance_counts": {"car": 1, "bus": 1}},
    ]
    loader, weights = build_urban_train_loader(
        _dataset(), rows, task="instances", class_to_id={"car": 3, "bus": 5},
        batch_size=2, seed=19,
    )
    assert loader.sampler is not None
    assert loader.batch_size == 2
    assert weights is None
    images, targets = next(iter(loader))
    assert len(images) == len(targets) == 2


def test_train_loader_rejects_validation_or_misaligned_statistics():
    rows = [
        {"sample_id": "a", "split": "train", "semantic_pixels": {"road": 1}},
        {"sample_id": "b", "split": "val", "semantic_pixels": {"road": 1}},
        {"sample_id": "c", "split": "train", "semantic_pixels": {"road": 1}},
        {"sample_id": "d", "split": "train", "semantic_pixels": {"road": 1}},
    ]
    with pytest.raises(ValueError, match="Only train"):
        build_urban_train_loader(
            _dataset(), rows, task="semantic", class_to_id={"road": 0}, batch_size=2
        )
    with pytest.raises(ValueError, match="match dataset length"):
        build_urban_train_loader(
            _dataset(), rows[:2], task="semantic", class_to_id={"road": 0}, batch_size=2
        )
