import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def test_bdd_batch_selection_and_mask_preparation(tmp_path):
    labels = tmp_path / "train.json"
    frame = {
        "name": "frame_000.jpg",
        "labels": [{
            "category": "lane",
            "poly2d": [{"vertices": [[2, 2], [12, 12]], "closed": False}],
        }],
    }
    labels.write_text(json.dumps([frame]), encoding="utf-8")

    batch_json = tmp_path / "batch.json"
    files_list = tmp_path / "files.txt"
    selection_manifest = tmp_path / "selection.json"
    subprocess.run([
        sys.executable, str(ROOT / "scripts/select_bdd100k_batch.py"),
        "--labels", str(labels), "--split", "train", "--offset", "0", "--limit", "1",
        "--output-json", str(batch_json), "--files-list", str(files_list),
        "--manifest", str(selection_manifest),
    ], check=True, cwd=ROOT)

    selection = json.loads(selection_manifest.read_text(encoding="utf-8"))
    assert selection["selected_frames"] == 1
    assert selection["next_offset"] == 1
    assert selection["complete"] is True
    assert files_list.read_text(encoding="utf-8").strip() == "frame_000.jpg"

    images_dir = tmp_path / "images"
    images_dir.mkdir()
    image = np.zeros((16, 16, 3), dtype=np.uint8)
    assert cv2.imwrite(str(images_dir / "frame_000.jpg"), image)

    masks_dir = tmp_path / "masks"
    manifest = tmp_path / "prepared.json"
    subprocess.run([
        sys.executable, str(ROOT / "scripts/prepare_bdd100k_batch.py"),
        "--labels", str(batch_json), "--images-dir", str(images_dir),
        "--masks-dir", str(masks_dir), "--manifest", str(manifest),
        "--split", "train", "--offset", "0", "--thickness", "2",
    ], check=True, cwd=ROOT)

    mask = cv2.imread(str(masks_dir / "frame_000.png"), cv2.IMREAD_GRAYSCALE)
    assert mask is not None
    assert mask.shape == (16, 16)
    assert set(np.unique(mask)).issubset({0, 255})
    prepared = json.loads(manifest.read_text(encoding="utf-8"))
    assert prepared["frames"] == prepared["masks"] == 1
    assert prepared["status"] == "validated_and_prepared"


def test_bdd_batch_selector_rejects_path_traversal(tmp_path):
    labels = tmp_path / "train.json"
    labels.write_text(json.dumps([{"name": "../outside.jpg", "labels": []}]), encoding="utf-8")
    result = subprocess.run([
        sys.executable, str(ROOT / "scripts/select_bdd100k_batch.py"),
        "--labels", str(labels), "--split", "train", "--offset", "0", "--limit", "1",
        "--output-json", str(tmp_path / "batch.json"),
        "--files-list", str(tmp_path / "files.txt"),
        "--manifest", str(tmp_path / "selection.json"),
    ], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Ruta de imagen no permitida" in result.stderr
