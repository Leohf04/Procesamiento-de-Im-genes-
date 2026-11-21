import numpy as np
import pytest

from src.evaluation.metrics import (
    compute_average_precision_per_image,
    compute_box_iou,
    compute_semantic_miou,
    match_predictions_to_ground_truth,
)


def test_box_iou():
    box = np.array([0, 0, 10, 10], dtype=np.float32)
    assert compute_box_iou(box, box) == pytest.approx(1.0)


def test_matching_requires_same_class_and_is_one_to_one():
    pred = np.array([[0, 0, 10, 10], [0, 0, 10, 10]], dtype=np.float32)
    gt = np.array([[0, 0, 10, 10]], dtype=np.float32)
    tp, fn, fp = match_predictions_to_ground_truth(
        pred, gt, 0.5, ["bus", "car"], ["car"]
    )
    assert (tp, fn, fp) == (1, 0, 1)


def test_multiclass_miou_detects_class_confusion():
    gt = np.array([[0, 1], [2, 2]], dtype=np.uint8)
    pred = np.array([[0, 2], [2, 2]], dtype=np.uint8)
    assert compute_semantic_miou(gt, gt) == pytest.approx(1.0)
    assert compute_semantic_miou(pred, gt) < 1.0


def test_ap_uses_global_confidence_ranking_and_class_labels():
    predictions = [
        {"boxes": [[0, 0, 10, 10]], "class_names": ["car"], "scores": [0.9]},
        {"boxes": [[20, 20, 30, 30], [0, 0, 10, 10]],
         "class_names": ["car", "car"], "scores": [0.8, 0.1]},
    ]
    ground_truth = [
        {"boxes": [[0, 0, 10, 10]], "class_names": ["car"]},
        {"boxes": [[0, 0, 10, 10]], "class_names": ["car"]},
    ]
    ap = compute_average_precision_per_image(predictions, ground_truth, ["car"])
    assert ap["car"] == pytest.approx(0.8333333333, rel=1e-5)


def test_ap_is_nan_for_class_without_ground_truth():
    ap = compute_average_precision_per_image(
        [{"boxes": [], "class_names": [], "scores": []}],
        [{"boxes": [], "class_names": []}],
        ["person"],
    )
    assert np.isnan(ap["person"])
