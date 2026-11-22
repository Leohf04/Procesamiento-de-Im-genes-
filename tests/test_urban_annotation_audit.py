from collections import Counter

import numpy as np

from scripts.audit_urban_annotations import color_histogram, deterministic_sample, _bbox_record_count


def test_deterministic_sample_is_stable_and_bounded():
    rows = [{"sample_id": f"id-{i}"} for i in range(20)]
    assert deterministic_sample(rows, 5, 2026) == deterministic_sample(rows, 5, 2026)
    assert len(deterministic_sample(rows, 5, 2026)) == 5


def test_color_histogram_counts_pixels():
    image = np.array([[[1, 2, 3], [1, 2, 3]], [[4, 5, 6], [1, 2, 3]]], dtype=np.uint8)
    counts = color_histogram(image)
    assert counts[(1, 2, 3)] == 3
    assert counts[(4, 5, 6)] == 1


def test_bbox_record_count_handles_common_shapes():
    assert _bbox_record_count([{}, {}]) == 2
    assert _bbox_record_count({"objects": [{}, {}, {}]}) == 3
    assert _bbox_record_count({"metadata": {}}) is None
