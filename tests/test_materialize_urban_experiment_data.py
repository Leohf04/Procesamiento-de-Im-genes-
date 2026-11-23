from scripts.materialize_urban_experiment_data import select_rows, check_byte_budget
import pytest


def test_select_rows_limits_deterministically_without_mutating_source():
    rows = [{"sample_id": str(i)} for i in range(4)]
    selected = select_rows(rows, 2)
    assert [x["sample_id"] for x in selected] == ["0", "1"]
    assert len(rows) == 4


def test_select_rows_without_limit_keeps_all_rows():
    rows = [{"sample_id": "a"}, {"sample_id": "b"}]
    assert select_rows(rows, None) == rows


def test_select_rows_rejects_nonpositive_limit():
    with pytest.raises(ValueError, match=">= 1"):
        select_rows([{"sample_id": "a"}], 0)


def test_byte_budget_accepts_equal_or_lower_estimate():
    check_byte_budget(100, 100)
    check_byte_budget(99, 100)


def test_byte_budget_rejects_over_budget_before_download():
    with pytest.raises(RuntimeError, match="nothing was downloaded"):
        check_byte_budget(101, 100)


def test_byte_budget_without_limit_is_unrestricted():
    check_byte_budget(10**12, None)


def test_select_rows_can_require_instance_positive_annotations():
    rows = [{"sample_id": "empty"}, {"sample_id": "has-instance"}]
    annotations = {
        "empty": {"instance_counts": {}},
        "has-instance": {"instance_counts": {"car": 1}},
    }
    assert select_rows(rows, 1, annotations, require_instances=True) == [rows[1]]


def test_select_rows_rejects_empty_instance_positive_pool():
    with pytest.raises(RuntimeError, match="No samples with positive instance"):
        select_rows([{"sample_id": "empty"}], 1,
                    {"empty": {"instance_counts": {}}}, require_instances=True)
