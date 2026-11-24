import json

import numpy as np
from PIL import Image
import pytest

torch = pytest.importorskip("torch")

from src.utils.bdd100k_github_sample import BDD100KGitHubInstanceSampleDataset


def test_github_sample_adapter_builds_maskrcnn_targets(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "labels").mkdir()
    (tmp_path / "masks" / "frame").mkdir(parents=True)
    Image.fromarray(np.full((8, 12, 3), 128, dtype=np.uint8)).save(tmp_path / "images/frame.jpg")
    mask = np.zeros((8, 12), dtype=np.uint8)
    mask[2:6, 3:9] = 255
    Image.fromarray(mask).save(tmp_path / "masks/frame/car_1.png")
    (tmp_path / "labels/frame.json").write_text(json.dumps([
        {"class": "car", "mask": "masks/frame/car_1.png"}
    ]), encoding="utf-8")

    image, target = BDD100KGitHubInstanceSampleDataset(tmp_path, size=(4, 6))[0]

    assert tuple(image.shape) == (3, 4, 6)
    assert image.dtype == torch.float32
    assert target["labels"].tolist() == [3]
    assert target["boxes"].tolist() == [[1.0, 1.0, 4.0, 3.0]]
    assert tuple(target["masks"].shape) == (1, 4, 6)
    assert int(target["masks"].sum()) == 6


def test_github_sample_adapter_rejects_path_traversal(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "labels").mkdir()
    (tmp_path / "masks").mkdir()
    Image.fromarray(np.zeros((4, 4, 3), dtype=np.uint8)).save(tmp_path / "images/frame.jpg")
    (tmp_path / "labels/frame.json").write_text(json.dumps([
        {"class": "car", "mask": "../outside.png"}
    ]), encoding="utf-8")

    with pytest.raises(ValueError, match="Ruta de máscara no permitida"):
        BDD100KGitHubInstanceSampleDataset(tmp_path, size=(4, 4))[0]
