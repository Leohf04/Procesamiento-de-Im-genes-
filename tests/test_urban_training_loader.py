import pytest
import torch
from torch.utils.data import Dataset

from src.urban_training import build_urban_train_loader


class _DetectionDataset(Dataset):
    def __init__(self, sample_ids):
        self.records = [{"sample_id": sample_id} for sample_id in sample_ids]

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        return torch.tensor([float(index)]), {"labels": torch.tensor([1])}


def _dataset(n=4, sample_ids=None):
    sample_ids = sample_ids or [f"sample-{index}" for index in range(n)]
    return _DetectionDataset(sample_ids)


def test_semantic_train_loader_returns_train_only_pixel_weights():
    rows = [
        {"sample_id": "a", "split": "train", "semantic_pixels": {"road": 100, "car": 1}},
        {"sample_id": "b", "split": "train", "semantic_pixels": {"road": 100, "car": 9}},
        {"sample_id": "c", "split": "train", "semantic_pixels": {"road": 50, "car": 0}},
        {"sample_id": "d", "split": "train", "semantic_pixels": {"road": 50, "car": 0}},
    ]
    loader, weights = build_urban_train_loader(
        _dataset(sample_ids=["a", "b", "c", "d"]), rows, task="semantic", class_to_id={"road": 0, "car": 1},
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
        _dataset(sample_ids=["a", "b", "c", "d"]), rows, task="instances", class_to_id={"car": 3, "bus": 5},
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
            _dataset(sample_ids=["a", "b", "c", "d"]), rows, task="semantic", class_to_id={"road": 0}, batch_size=2
        )
    with pytest.raises(ValueError, match="match dataset length"):
        build_urban_train_loader(
            _dataset(sample_ids=["a", "b", "c", "d"]), rows[:2], task="semantic", class_to_id={"road": 0}, batch_size=2
        )



def test_train_loader_rejects_same_ids_in_different_order():
    rows = [
        {"sample_id": "a", "split": "train", "semantic_pixels": {"road": 1}},
        {"sample_id": "b", "split": "train", "semantic_pixels": {"road": 1}},
        {"sample_id": "c", "split": "train", "semantic_pixels": {"road": 1}},
        {"sample_id": "d", "split": "train", "semantic_pixels": {"road": 1}},
    ]
    dataset = _dataset(sample_ids=["b", "a", "c", "d"])
    with pytest.raises(ValueError, match="not aligned by sample_id/order"):
        build_urban_train_loader(
            dataset, rows, task="semantic", class_to_id={"road": 0}, batch_size=2
        )


def test_train_loader_rejects_missing_or_duplicate_sample_ids():
    rows = [
        {"sample_id": "a", "split": "train", "semantic_pixels": {"road": 1}},
        {"sample_id": "b", "split": "train", "semantic_pixels": {"road": 1}},
        {"sample_id": "c", "split": "train", "semantic_pixels": {"road": 1}},
        {"sample_id": "d", "split": "train", "semantic_pixels": {"road": 1}},
    ]
    with pytest.raises(ValueError, match="duplicate sample_id"):
        build_urban_train_loader(
            _dataset(sample_ids=["a", "b", "b", "d"]), rows,
            task="semantic", class_to_id={"road": 0}, batch_size=2
        )


def test_multidataset_semantic_loaders_compute_weights_independently():
    from src.urban_training import build_urban_train_loaders

    a2d2 = _dataset(sample_ids=["a1", "a2"])
    urbansyn = _dataset(sample_ids=["u1", "u2"])
    for record in a2d2.records:
        record["dataset"] = "a2d2"
    for record in urbansyn.records:
        record["dataset"] = "urbansyn"

    loaders = build_urban_train_loaders(
        {
            "a2d2": {
                "dataset": a2d2,
                "annotation_rows": [
                    {"sample_id": "a1", "dataset": "a2d2", "split": "train",
                     "semantic_pixels": {"road": 1000, "car": 1}},
                    {"sample_id": "a2", "dataset": "a2d2", "split": "train",
                     "semantic_pixels": {"road": 1000, "car": 1}},
                ],
                "class_to_id": {"road": 0, "car": 1},
            },
            "urbansyn": {
                "dataset": urbansyn,
                "annotation_rows": [
                    {"sample_id": "u1", "dataset": "urbansyn", "split": "train",
                     "semantic_pixels": {"road": 1, "car": 1000}},
                    {"sample_id": "u2", "dataset": "urbansyn", "split": "train",
                     "semantic_pixels": {"road": 1, "car": 1000}},
                ],
                "class_to_id": {"road": 0, "car": 1},
            },
        },
        task="semantic",
        batch_size=2,
    )

    a2d2_loader, a2d2_weights = loaders["a2d2"]
    urban_loader, urban_weights = loaders["urbansyn"]
    assert a2d2_loader.dataset is a2d2
    assert urban_loader.dataset is urbansyn
    assert a2d2_weights[1] > a2d2_weights[0]
    assert urban_weights[0] > urban_weights[1]
    assert not torch.allclose(a2d2_weights, urban_weights)


def test_multidataset_instance_samplers_use_domain_local_frequencies():
    from src.urban_training import build_urban_train_loaders

    a2d2 = _dataset(sample_ids=["a1", "a2"])
    urbansyn = _dataset(sample_ids=["u1", "u2"])
    specs = {
        "a2d2": {
            "dataset": a2d2,
            "annotation_rows": [
                {"sample_id": "a1", "dataset": "a2d2", "split": "train",
                 "instance_counts": {"car": 1}},
                {"sample_id": "a2", "dataset": "a2d2", "split": "train",
                 "instance_counts": {"car": 1, "bus": 1}},
            ],
            "class_to_id": {"car": 1, "bus": 2},
        },
        "urbansyn": {
            "dataset": urbansyn,
            "annotation_rows": [
                {"sample_id": "u1", "dataset": "urbansyn", "split": "train",
                 "instance_counts": {"car": 1, "bus": 1}},
                {"sample_id": "u2", "dataset": "urbansyn", "split": "train",
                 "instance_counts": {"bus": 1}},
            ],
            "class_to_id": {"car": 1, "bus": 2},
        },
    }
    loaders = build_urban_train_loaders(
        specs, task="instances", batch_size=2, seed=23
    )
    a2d2_sampler = loaders["a2d2"][0].sampler
    urban_sampler = loaders["urbansyn"][0].sampler
    assert isinstance(a2d2_sampler, torch.utils.data.WeightedRandomSampler)
    assert isinstance(urban_sampler, torch.utils.data.WeightedRandomSampler)
    assert not torch.allclose(a2d2_sampler.weights, urban_sampler.weights)


def test_multidataset_loader_rejects_foreign_rows_and_reused_dataset():
    from src.urban_training import build_urban_train_loaders

    dataset = _dataset(sample_ids=["a", "b", "c", "d"])
    rows = [
        {"sample_id": sample_id, "dataset": "urbansyn", "split": "train",
         "semantic_pixels": {"road": 1}}
        for sample_id in ["a", "b", "c", "d"]
    ]
    with pytest.raises(ValueError, match="foreign dataset tags"):
        build_urban_train_loaders(
            {"a2d2": {
                "dataset": dataset,
                "annotation_rows": rows,
                "class_to_id": {"road": 0},
            }},
            task="semantic", batch_size=2,
        )

    clean_rows = [
        {"sample_id": sample_id, "split": "train", "semantic_pixels": {"road": 1}}
        for sample_id in ["a", "b", "c", "d"]
    ]
    with pytest.raises(ValueError, match="distinct dataset object"):
        build_urban_train_loaders(
            {
                "a2d2": {"dataset": dataset, "annotation_rows": clean_rows,
                         "class_to_id": {"road": 0}},
                "urbansyn": {"dataset": dataset, "annotation_rows": clean_rows,
                             "class_to_id": {"road": 0}},
            },
            task="semantic", batch_size=2,
        )

