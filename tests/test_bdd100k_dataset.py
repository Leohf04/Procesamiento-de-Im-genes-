"""Unit tests for BDD100K mask adapters; fixtures are synthetic, no dataset download."""
import numpy as np
from PIL import Image
import pytest

torch = pytest.importorskip("torch")

from src.utils.bdd100k_dataset import BDD100KInstanceDataset, BDD100KSemanticDataset


def _write_image(path, size=(4, 4)):
    Image.fromarray(np.zeros((size[0], size[1], 3), dtype=np.uint8)).save(path)


def test_semantic_loader_preserves_train_ids_and_ignore(tmp_path):
    images, masks = tmp_path / "images", tmp_path / "masks"
    images.mkdir()
    masks.mkdir()
    _write_image(images / "frame.jpg")
    labels = np.array([[0, 1, 2, 3], [4, 5, 6, 7],
                       [8, 9, 10, 11], [12, 13, 18, 255]], dtype=np.uint8)
    Image.fromarray(labels).save(masks / "frame.png")

    image, target = BDD100KSemanticDataset(images, masks, size=(4, 4))[0]

    assert tuple(image.shape) == (3, 4, 4)
    assert target.dtype == torch.int64
    assert target.tolist() == labels.tolist()


def test_instance_loader_decodes_rgba_instance_ids_and_flags(tmp_path):
    images, masks = tmp_path / "images", tmp_path / "masks"
    images.mkdir()
    masks.mkdir()
    _write_image(images / "frame.jpg")

    # Instance 1: category 1, valid. Instance 2: category 3, ignore flag.
    rgba = np.zeros((4, 4, 4), dtype=np.uint8)
    rgba[0:2, 0:2, 0] = 1
    rgba[0:2, 0:2, 2] = 1
    rgba[2:4, 2:4, 0] = 3
    rgba[2:4, 2:4, 1] = 1
    rgba[2:4, 2:4, 2] = 2
    Image.fromarray(rgba, mode="RGBA").save(masks / "frame.png")

    image, target = BDD100KInstanceDataset(images, masks, size=(4, 4))[0]

    assert tuple(image.shape) == (3, 4, 4)
    assert target["labels"].tolist() == [1]
    assert target["boxes"].tolist() == [[0.0, 0.0, 2.0, 2.0]]
    assert tuple(target["masks"].shape) == (1, 4, 4)
    assert int(target["masks"].sum()) == 4


def test_loader_fails_when_a_mask_is_missing(tmp_path):
    images, masks = tmp_path / "images", tmp_path / "masks"
    images.mkdir()
    masks.mkdir()
    _write_image(images / "orphan.jpg")

    with pytest.raises(FileNotFoundError, match="Faltan"):
        BDD100KSemanticDataset(images, masks, size=(4, 4))
