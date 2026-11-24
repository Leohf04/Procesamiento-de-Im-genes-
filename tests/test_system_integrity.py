import json
import os

import cv2
import numpy as np
import pytest

from src.evaluation.error_analysis import save_failure_case
from src.evaluation.metrics import compute_box_iou, compute_semantic_miou
from src.features.fine_classifier import FineGrainedClassifier
from src.utils.coco_loader import decode_segmentation_mask, load_coco_val2017_samples
from src.utils.config_utils import HAS_TORCH, load_config, resolve_backend

SHARED_VOC_LABELS = ["person", "bicycle", "car", "motorcycle", "bus"]


class MockDetectorModel:
    def __init__(self):
        self.calls = 0

    def predict(self, image_bgr: np.ndarray) -> dict:
        self.calls += 1
        h, w = image_bgr.shape[:2]
        box = np.array([[10, 20, 90, 140]], dtype=np.float32)
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[20:140, 10:90] = 1
        return {
            "boxes": box,
            "labels": np.array([1], dtype=np.int64),
            "class_names": ["person"],
            "scores": np.array([0.91], dtype=np.float32),
            "instance_masks": mask[np.newaxis, :, :],
            "urban_semantic_mask": mask,
            "urban_semantic_mask_all8": mask,
        }


def test_config_loads_and_backend_resolves():
    config = load_config("configs/config.yaml")
    assert config["dataset"]["name"] == "cityscapes"
    assert config["dataset"]["root"] == "data/cityscapes"
    assert config["evaluation"]["iou_threshold"] == 0.5
    assert resolve_backend("auto") in {"torch", "onnx_cv2"}


def test_coco_loader_missing_dataset_raises():
    with pytest.raises(FileNotFoundError):
        load_coco_val2017_samples(
            images_dir="ruta/inexistente",
            annotations_file="ruta/inexistente.json",
            max_samples=1,
        )


def test_coco_loader_builds_shared5_and_all8_masks(tmp_path):
    images_dir = tmp_path / "val2017"
    ann_dir = tmp_path / "annotations"
    images_dir.mkdir()
    ann_dir.mkdir()

    image = (np.ones((100, 100, 3), dtype=np.uint8) * 128)
    cv2.imwrite(str(images_dir / "000000000001.jpg"), image)

    annotations = {
        "images": [
            {"id": 1, "file_name": "000000000001.jpg", "height": 100, "width": 100}
        ],
        "annotations": [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "bbox": [10.0, 10.0, 20.0, 20.0],
                "segmentation": [[10, 10, 30, 10, 30, 30, 10, 30]],
                "iscrowd": 0,
            },
            {
                "id": 2,
                "image_id": 1,
                "category_id": 13,
                "bbox": [50.0, 50.0, 20.0, 20.0],
                "segmentation": [[50, 50, 70, 50, 70, 70, 50, 70]],
                "iscrowd": 0,
            },
        ],
        "categories": [],
    }
    ann_file = ann_dir / "instances_val2017.json"
    ann_file.write_text(json.dumps(annotations), encoding="utf-8")

    samples = load_coco_val2017_samples(
        images_dir=str(images_dir),
        annotations_file=str(ann_file),
        max_samples=5,
        only_urban_images=True,
        shared_mask_labels=set(SHARED_VOC_LABELS),
    )

    assert len(samples) == 1
    sample = samples[0]
    assert set(sample["gt_labels"]) == {"person", "stop sign"}
    assert int(sample["gt_semantic_mask"].sum()) == 400
    assert int(np.count_nonzero(sample["gt_semantic_mask_all8"])) == 800
    assert int(np.count_nonzero(sample["gt_semantic_mask_all8"] == 1)) == 400
    assert int(np.count_nonzero(sample["gt_semantic_mask_all8"] == 13)) == 400


def test_decode_segmentation_mask_polygon_fallback():
    mask = decode_segmentation_mask(
        [[0, 0, 10, 0, 10, 10, 0, 10]], height=20, width=20
    )
    assert mask.shape == (20, 20)
    assert int(mask.sum()) == 100


def test_box_iou_and_semantic_miou():
    box = np.array([0, 0, 10, 10], dtype=np.float32)
    assert compute_box_iou(box, box) == pytest.approx(1.0)

    gt = np.zeros((20, 20), dtype=np.uint8)
    gt[:10, :10] = 1
    pred = gt.copy()
    assert compute_semantic_miou(pred, gt, num_classes=2) == pytest.approx(1.0)


def test_fine_classifier_untrained_and_training(tmp_path):
    model_path = tmp_path / "svm.joblib"
    classifier = FineGrainedClassifier(model_path=str(model_path))
    assert not classifier.is_trained()

    dummy = (np.ones((128, 128, 3), dtype=np.uint8) * 90)
    label, score = classifier.predict_roi(
        dummy, (10, 10, 60, 110), "person", 0.9, subclasses_map={"person": "peaton"}
    )
    assert label == "peatonsvm_untrained"
    assert score == 0.0

    samples = []
    for image_idx, intensity in enumerate([70, 90, 120, 150, 180, 210]):
        image = np.full((160, 160, 3), intensity, dtype=np.uint8)
        samples.append({
            "image_id": image_idx,
            "image": image,
            "gt_boxes": [[10, 10, 60, 130], [70, 10, 130, 130]],
            "gt_labels": ["person", "car"],
        })
    class_names, confusion = classifier.train(samples, max_rois_per_class=10)
    assert len(class_names) >= 2
    assert confusion.shape[0] == confusion.shape[1]
    classifier.save()
    assert os.path.isfile(model_path)


def test_headless_video_writer_end_to_end(tmp_path):
    from main import process_video_source
    from src.pipeline import UrbanPerceptionPipeline

    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(input_path), fourcc, 10.0, (96, 96))

    assert writer.isOpened(), "No se pudo crear el video sintético de prueba."
    for _ in range(4):
        writer.write(np.full((96, 96, 3), 60, dtype=np.uint8))
    writer.release()
    assert os.path.isfile(input_path)

    pipeline = UrbanPerceptionPipeline(
        approach="instance",
        config_path="configs/config.yaml",
        backend="onnx_cv2",
        model_override=MockDetectorModel(),
    )
    stats = pipeline.process_video_stream(
        source=str(input_path), output_video_path=str(output_path), max_frames=4
    )

    assert os.path.isfile(output_path)
    assert stats["frames_written"] >= 3


def test_save_failure_case_writes_image(tmp_path):
    image = np.zeros((80, 80, 3), dtype=np.uint8)
    gt = np.array([[10, 10, 40, 40]], dtype=np.float32)
    pred = np.array([[12, 12, 42, 42]], dtype=np.float32)
    out_path = tmp_path / "failure.png"

    save_failure_case(image, gt, pred, np.array([0.8]), str(out_path))
    saved = cv2.imread(str(out_path))
    assert saved is not None
    assert saved.shape == (80, 80, 3)


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch no disponible en este entorno")
def test_instance_seg_torch_predict_path():
    from src.models.instance_seg import InstanceSegmentationModel

    model = InstanceSegmentationModel(
        backend="torch",
        device="cpu",
        confidence_threshold=0.5,
        allowed_labels={"person", "car", "bicycle", "motorcycle", "bus"},
    )
    output = model.predict(np.full((320, 320, 3), 120, dtype=np.uint8))
    assert "boxes" in output
    assert "urban_semantic_mask" in output
