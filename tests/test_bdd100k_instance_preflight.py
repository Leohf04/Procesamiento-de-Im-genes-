import importlib.util
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_bdd100k_instance_splits.py"
SPEC = importlib.util.spec_from_file_location("audit_bdd100k_instance_splits", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def _write_pair(images, masks, stem="frame-001", mode="RGBA"):
    images.mkdir(parents=True, exist_ok=True)
    masks.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 6)).save(images / f"{stem}.jpg")
    encoded = np.zeros((6, 8, 4), dtype=np.uint8)
    encoded[1:4, 2:6, 0] = 3  # car
    encoded[1:4, 2:6, 2] = 0
    encoded[1:4, 2:6, 3] = 1  # annotation ID 1
    Image.fromarray(encoded, mode="RGBA").convert(mode).save(masks / f"{stem}.png")


def test_audit_counts_official_rgba_instance(tmp_path):
    images, masks = tmp_path / "images", tmp_path / "masks"
    _write_pair(images, masks)
    report, stems = AUDIT.audit_split("train", images, masks)
    assert report["images"] == report["bitmasks"] == 1
    assert report["instances"] == 1
    assert report["instances_per_class"]["car"] == 1
    assert stems == {"frame-001"}


def test_audit_rejects_non_rgba_mask(tmp_path):
    images, masks = tmp_path / "images", tmp_path / "masks"
    _write_pair(images, masks, mode="RGB")
    with pytest.raises(ValueError, match="original RGBA"):
        AUDIT.audit_split("train", images, masks)


def test_audit_rejects_missing_mask(tmp_path):
    images, masks = tmp_path / "images", tmp_path / "masks"
    images.mkdir()
    masks.mkdir()
    Image.new("RGB", (8, 6)).save(images / "unpaired.jpg")
    with pytest.raises(ValueError, match="image/mask mismatch"):
        AUDIT.audit_split("train", images, masks)
