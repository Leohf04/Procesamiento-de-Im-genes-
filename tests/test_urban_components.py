import numpy as np

from scripts.prepare_bdd100k_lane_masks import rasterize_annotation
from src.utils.urban_dataset import CITYSCAPES_ID_TO_TRAIN, CITYSCAPES_CLASSES
from src.utils.cityscapes_instance_dataset import CITYSCAPES_INSTANCE_IDS


def test_cityscapes_semantic_mapping_has_expected_urban_classes():
    assert len(CITYSCAPES_CLASSES) == 11
    assert CITYSCAPES_ID_TO_TRAIN[7] == 0
    assert CITYSCAPES_ID_TO_TRAIN[24] == 2
    assert CITYSCAPES_ID_TO_TRAIN[26] == 4
    assert CITYSCAPES_ID_TO_TRAIN[33] == 8


def test_cityscapes_instance_mapping_excludes_stuff_classes():
    assert CITYSCAPES_INSTANCE_IDS == {
        24: 1, 25: 2, 26: 3, 27: 4, 28: 5, 32: 6, 33: 7
    }


def test_bdd_lane_annotation_is_rasterized_to_binary_mask():
    frame = {"labels": [{"category": "lane", "poly2d": [
        {"vertices": [[5, 5], [20, 20], [35, 5]], "closed": False}
    ]}]}
    mask = rasterize_annotation(frame, width=40, height=30, thickness=3)
    assert mask.shape == (30, 40)
    assert set(np.unique(mask)).issubset({0, 255})
    assert np.count_nonzero(mask) > 0


def test_non_lane_bdd_annotation_is_ignored():
    frame = {"labels": [{"category": "drivable area", "poly2d": [
        {"vertices": [[1, 1], [20, 20]], "closed": False}
    ]}]}
    mask = rasterize_annotation(frame, width=24, height=24)
    assert np.count_nonzero(mask) == 0
