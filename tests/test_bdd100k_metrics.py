import numpy as np

from src.evaluation.metrics import (
    compute_average_precision_per_image,
    compute_mask_average_precision_per_image,
)


def test_mask_average_precision_matches_exact_instance_mask():
    gt_mask = np.zeros((8, 8), dtype=np.uint8)
    gt_mask[2:5, 3:6] = 1
    predictions = [{
        "masks": [gt_mask.copy()],
        "class_names": ["car"],
        "scores": [0.95],
    }]
    ground_truth = [{
        "masks": [gt_mask.copy()],
        "class_names": ["car"],
    }]

    result = compute_mask_average_precision_per_image(
        predictions, ground_truth, ["car"], iou_threshold=0.5
    )

    assert result["car"] == 1.0


def test_mask_average_precision_rejects_shape_mismatch():
    predictions = [{
        "masks": [np.ones((4, 4), dtype=np.uint8)],
        "class_names": ["car"],
        "scores": [0.9],
    }]
    ground_truth = [{
        "masks": [np.ones((5, 5), dtype=np.uint8)],
        "class_names": ["car"],
    }]

    import pytest
    with pytest.raises(ValueError, match="incompatibles"):
        compute_mask_average_precision_per_image(
            predictions, ground_truth, ["car"], iou_threshold=0.5
        )


def test_box_average_precision_remains_available():
    predictions = [{
        "boxes": [[1, 1, 5, 5]],
        "class_names": ["car"],
        "scores": [0.9],
    }]
    ground_truth = [{
        "boxes": [[1, 1, 5, 5]],
        "class_names": ["car"],
    }]
    result = compute_average_precision_per_image(
        predictions, ground_truth, ["car"], iou_threshold=0.5
    )
    assert result["car"] == 1.0


def test_mask_average_precision_accepts_compact_bitpacked_masks():
    gt_mask = np.zeros((5, 7), dtype=np.uint8)
    gt_mask[1:4, 2:6] = 1
    packed = (np.packbits(gt_mask.reshape(-1)), gt_mask.shape)
    predictions = [{"masks": [packed], "class_names": ["car"], "scores": [0.8]}]
    ground_truth = [{"masks": [packed], "class_names": ["car"]}]
    result = compute_mask_average_precision_per_image(
        predictions, ground_truth, ["car"], iou_threshold=0.5
    )
    assert result["car"] == 1.0
