import json

import pytest

from src.urban_ontology import (
    instance_name_to_id, load_urban_ontology, semantic_name_to_id,
    source_instance_map, source_semantic_map,
)
from scripts.build_balanced_training_plan import (
    attach_annotation_stats, greedy_balanced_select,
)


def test_ontology_has_separate_semantic_and_instance_heads():
    ontology = load_urban_ontology()
    semantic = semantic_name_to_id(ontology)
    instances = instance_name_to_id(ontology)
    assert semantic["road"] == 0
    assert semantic["lane marking"] == 19
    assert instances["person"] == 1
    assert instances["bicycle"] == 8
    assert "lane marking" not in instances
    assert ontology["policy"]["rider_is_not_bicycle"] is True


def test_urbansyn_unlabeled_is_ignore_and_rider_is_separate():
    semantic = source_semantic_map("urbansyn")
    instance = source_instance_map("urbansyn")
    assert semantic[19] == 255
    assert semantic[12] == 12
    assert instance[12] == 2
    assert instance[18] == 8


def test_a2d2_aliases_keep_cyclist_and_bicycle_distinct():
    semantic = source_semantic_map("a2d2")
    instance = source_instance_map("a2d2")
    assert semantic["pedestrian"] == 11
    assert semantic["cyclist"] == 12
    assert semantic["bicycle"] == 18
    assert instance["cyclist"] == 2
    assert instance["bicycle"] == 8


def test_attach_annotation_stats_requires_complete_index():
    manifest = [{"dataset": "urbansyn", "sample_id": "001", "assets": {"rgb": "x"}}]
    annotations = [{"sample_id": "001", "semantic_pixels": {"car": 20},
                    "instance_counts": {"car": 2}}]
    attached = attach_annotation_stats(manifest, annotations)
    assert attached[0]["semantic_pixels"] == {"car": 20}
    with pytest.raises(ValueError, match="No annotation statistics"):
        attach_annotation_stats(manifest, [])


def test_greedy_balancer_prefers_rare_classes_and_is_deterministic():
    rows = [
        {"sample_id": "common-1", "instance_counts": {"car": 10}},
        {"sample_id": "common-2", "instance_counts": {"car": 8}},
        {"sample_id": "rare", "instance_counts": {"bicycle": 1, "person": 1}},
        {"sample_id": "mixed", "instance_counts": {"car": 3, "person": 2}},
    ]
    first, summary = greedy_balanced_select(
        rows, count_key="instance_counts", seed=2026, max_samples=2
    )
    second, _ = greedy_balanced_select(
        rows, count_key="instance_counts", seed=2026, max_samples=2
    )
    assert [r["sample_id"] for r in first] == [r["sample_id"] for r in second]
    assert {r["sample_id"] for r in first} == {"rare", "mixed"}
    assert summary["selected_samples_per_class"]["person"] == 2


def test_greedy_balancer_reports_uncovered_classes():
    rows = [
        {"sample_id": "a", "semantic_pixels": {"road": 100}},
        {"sample_id": "b", "semantic_pixels": {"car": 20}},
    ]
    selected, summary = greedy_balanced_select(
        rows, count_key="semantic_pixels", seed=3, max_samples=1
    )
    assert len(selected) == 1
    assert len(summary["uncovered_classes"]) == 1
