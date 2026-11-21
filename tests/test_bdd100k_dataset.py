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


def test_instance_loader_returns_torchvision_range_without_imagenet_normalization(tmp_path):
    images, masks = tmp_path / "images", tmp_path / "masks"
    images.mkdir()
    masks.mkdir()
    pixels = np.full((4, 4, 3), 128, dtype=np.uint8)
    Image.fromarray(pixels).save(images / "frame.jpg")
    rgba = np.zeros((4, 4, 4), dtype=np.uint8)
    rgba[1:3, 1:3, 0] = 1
    rgba[1:3, 1:3, 2] = 1
    Image.fromarray(rgba, mode="RGBA").save(masks / "frame.png")

    image, _ = BDD100KInstanceDataset(images, masks, size=(4, 4))[0]

    assert image.dtype == torch.float32
    assert float(image.min()) >= 0.0
    assert float(image.max()) <= 1.0
    assert 0.45 < float(image.mean()) < 0.56


def test_semantic_loader_keeps_imagenet_normalization(tmp_path):
    images, masks = tmp_path / "images", tmp_path / "masks"
    images.mkdir()
    masks.mkdir()
    Image.fromarray(np.full((4, 4, 3), 128, dtype=np.uint8)).save(images / "frame.jpg")
    Image.fromarray(np.zeros((4, 4), dtype=np.uint8)).save(masks / "frame.png")

    image, _ = BDD100KSemanticDataset(images, masks, size=(4, 4))[0]

    assert float(image.min()) < 0.0


def test_detection_loader_maps_categories_and_scales_boxes(tmp_path):
    import json
    from src.utils.bdd100k_dataset import BDD100KDetectionDataset

    images = tmp_path / "images"
    images.mkdir()
    Image.fromarray(np.zeros((8, 16, 3), dtype=np.uint8)).save(images / "frame.jpg")
    labels = tmp_path / "det.json"
    labels.write_text(json.dumps([{
        "name": "frame.jpg",
        "labels": [
            {"category": "car", "box2d": {"x1": 2, "y1": 1, "x2": 10, "y2": 7}},
            {"category": "traffic sign", "box2d": {"x1": 0, "y1": 0, "x2": 4, "y2": 4}},
            {"category": "unknown", "box2d": {"x1": 1, "y1": 1, "x2": 2, "y2": 2}},
        ],
    }]), encoding="utf-8")

    image, target = BDD100KDetectionDataset(images, labels, size=(4, 8))[0]

    assert float(image.min()) >= 0.0 and float(image.max()) <= 1.0
    assert target["labels"].tolist() == [3, 8]
    assert target["boxes"].tolist() == [[1.0, 0.5, 5.0, 3.5], [0.0, 0.0, 2.0, 2.0]]


def test_lane_dataset_decodes_three_packed_targets_and_background(tmp_path):
    from src.utils.bdd100k_dataset import BDD100KLaneDataset

    images, masks = tmp_path / "images", tmp_path / "masks"
    images.mkdir()
    masks.mkdir()
    _write_image(images / "frame.jpg", size=(2, 3))
    # category=6, style=1, direction=1 -> 6 + (1<<4) + (1<<5) = 54
    # background bit set on last pixel; its task targets must be ignored.
    packed = np.array([[54, 0, 255], [54, 54, 54]], dtype=np.uint8)
    Image.fromarray(packed).save(masks / "frame.png")

    image, targets = BDD100KLaneDataset(images, masks, size=(2, 3))[0]

    assert tuple(image.shape) == (3, 2, 3)
    assert targets["category"].tolist() == [[6, 0, 7], [6, 6, 6]]
    assert targets["style"].tolist() == [[1, 0, 1], [1, 1, 1]]
    assert targets["direction"].tolist() == [[1, 0, 1], [1, 1, 1]]
    # 255 has background bit 1; ignore it in all three heads.
    assert targets["category"][0, 2].item() == 255
    assert targets["style"][0, 2].item() == 255
    assert targets["direction"][0, 2].item() == 255
