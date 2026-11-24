"""Versioned shared ontology for A2D2 and UrbanSyn.

The semantic and instance heads intentionally have different contiguous IDs.
Unknown semantic classes map to ignore_index; instance background is 0.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_ONTOLOGY_PATH = Path(__file__).resolve().parents[1] / "configs" / "urban_ontology_v1.json"


def load_urban_ontology(path: str | Path = DEFAULT_ONTOLOGY_PATH) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("ontology_version") != "urban-v1":
        raise ValueError("Unsupported urban ontology version")
    ignore = int(data["ignore_index"])
    semantic = data["semantic"]["classes"]
    instances = data["instances"]["classes"]
    _validate_classes(semantic, "semantic", allowed_ignore=ignore)
    _validate_classes(instances, "instances", allowed_ignore=0)
    if int(data["instances"]["background_id"]) != 0:
        raise ValueError("Instance background ID must be 0")
    return data


def _validate_classes(classes: list[dict], name: str, allowed_ignore: int) -> None:
    ids = [int(item["id"]) for item in classes]
    names = [str(item["name"]) for item in classes]
    if len(ids) != len(set(ids)) or len(names) != len(set(names)):
        raise ValueError(f"Duplicate {name} class IDs or names")
    if allowed_ignore in ids:
        raise ValueError(f"{name} class IDs must not use reserved ID {allowed_ignore}")


def semantic_name_to_id(ontology: dict | None = None) -> dict[str, int]:
    ontology = ontology or load_urban_ontology()
    return {item["name"]: int(item["id"]) for item in ontology["semantic"]["classes"]}


def instance_name_to_id(ontology: dict | None = None) -> dict[str, int]:
    ontology = ontology or load_urban_ontology()
    return {item["name"]: int(item["id"]) for item in ontology["instances"]["classes"]}


def source_semantic_map(dataset: str, ontology: dict | None = None) -> dict[int, int] | dict[str, int]:
    ontology = ontology or load_urban_ontology()
    normalized = dataset.lower()
    if normalized not in {"urbansyn", "a2d2"}:
        raise ValueError(f"Unsupported dataset: {dataset}")
    key = ("urbansyn_train_id_to_semantic_id" if normalized == "urbansyn"
           else "a2d2_normalized_name_to_semantic_id")
    mapping = ontology["semantic"]["sources"][key]
    return ({int(source_id): int(target_id) for source_id, target_id in mapping.items()}
            if normalized == "urbansyn" else {str(k): int(v) for k, v in mapping.items()})


def source_instance_map(dataset: str, ontology: dict | None = None) -> dict[int, int] | dict[str, int]:
    ontology = ontology or load_urban_ontology()
    normalized = dataset.lower()
    if normalized not in {"urbansyn", "a2d2"}:
        raise ValueError(f"Unsupported dataset: {dataset}")
    key = ("urbansyn_train_id_to_instance_id" if normalized == "urbansyn"
           else "a2d2_normalized_name_to_instance_id")
    mapping = ontology["instances"]["sources"][key]
    return ({int(source_id): int(target_id) for source_id, target_id in mapping.items()}
            if normalized == "urbansyn" else {str(k): int(v) for k, v in mapping.items()})
