from scripts.prepare_reproducible_subsets import assign_split, select_subset


def test_split_is_deterministic_and_grouped():
    assert assign_split("sequence-a", 2026) == assign_split("sequence-a", 2026)
    records = [
        {"dataset": "a2d2", "sample_id": "a/1", "group_id": "a", "assets": {"rgb": "x"}},
        {"dataset": "a2d2", "sample_id": "a/2", "group_id": "a", "assets": {"rgb": "y"}},
        {"dataset": "a2d2", "sample_id": "b/1", "group_id": "b", "assets": {"rgb": "z"}},
    ]
    selected = select_subset(records, seed=2026, max_per_split=None)
    locations = {
        record["sample_id"]: split
        for split, values in selected.items()
        for record in values
    }
    assert locations["a/1"] == locations["a/2"]


def test_subset_cap_is_deterministic():
    records = [
        {"dataset": "urbansyn", "sample_id": str(i), "group_id": str(i), "assets": {"rgb": "x"}}
        for i in range(100)
    ]
    first = select_subset(records, seed=7, max_per_split=5)
    second = select_subset(records, seed=7, max_per_split=5)
    assert {
        split: [item["sample_id"] for item in values]
        for split, values in first.items()
    } == {
        split: [item["sample_id"] for item in values]
        for split, values in second.items()
    }
    assert all(len(values) <= 5 for values in first.values())


def test_duplicate_sample_is_rejected():
    record = {"dataset": "x", "sample_id": "1", "group_id": "1", "assets": {}}
    try:
        select_subset([record, record], seed=1, max_per_split=None)
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate sample should fail")
