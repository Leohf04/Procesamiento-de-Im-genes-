"""Download and validate a tiny, pinned BDD100K instance sample from GitHub.

The source uses one binary PNG per object. It is NOT the official BDD100K RGBA
bitmask format and this script never feeds it to the official RGBA loader.
"""
from __future__ import annotations

import argparse
import csv
import json
import tempfile
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen

from PIL import Image
import torch

from src.utils.bdd100k_github_sample import (
    BDD100KGitHubInstanceSampleDataset,
    GITHUB_SAMPLE_CLASSES,
)

REPO = "PETER-nguyen7506/yolo11"
REVISION = "af057234c8f010302c7fbb9807e263167693fb25"
BASE = f"https://raw.githubusercontent.com/{REPO}/{REVISION}/datasets/bdd100k-seg-100"


def fetch(relative: str, destination: Path) -> None:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Ruta remota no permitida: {relative}")
    url = f"{BASE}/{relative}"
    request = Request(url, headers={"User-Agent": "BDD100K-sample-validator/1.0"})
    with urlopen(request, timeout=45) as response, destination.open("wb") as output:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} descargando {relative}")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)


def select_rows(manifest_path: Path, limit: int):
    with manifest_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    selected, covered = [], set()
    # Greedy coverage: prefer images adding a class not already represented.
    while rows and len(selected) < limit:
        best = None
        best_gain = -1
        for row in rows:
            present = {name for name in GITHUB_SAMPLE_CLASSES if int(row.get(name, 0) or 0) > 0}
            gain = len(present - covered)
            if best is None or gain > best_gain:
                best, best_gain = row, gain
        if best is None:
            break
        selected.append(best)
        covered.update(name for name in GITHUB_SAMPLE_CLASSES if int(best.get(name, 0) or 0) > 0)
        rows.remove(best)
        if covered == set(GITHUB_SAMPLE_CLASSES):
            break
    return selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=4, choices=range(1, 9))
    parser.add_argument("--height", type=int, default=256)
    parser.add_argument("--width", type=int, default=512)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="bdd100k-github-sample-") as tmp:
        root = Path(tmp)
        for folder in ("images", "labels", "masks"):
            (root / folder).mkdir()
        manifest = root / "manifest.csv"
        fetch("manifest.csv", manifest)
        rows = select_rows(manifest, args.samples)
        if not rows:
            raise RuntimeError("El manifiesto no contiene muestras.")

        expected_classes = set()
        expected_instances = 0
        for row in rows:
            filename = row["filename"]
            stem = Path(filename).stem
            fetch(row["image_path"], root / "images" / filename)
            label_path = root / "labels" / f"{stem}.json"
            fetch(row["label_path"], label_path)
            annotations = json.loads(label_path.read_text(encoding="utf-8"))
            if not isinstance(annotations, list) or not annotations:
                raise RuntimeError(f"Anotaciones vacías o inválidas: {stem}")
            for annotation in annotations:
                class_name = annotation.get("class")
                if class_name not in GITHUB_SAMPLE_CLASSES:
                    raise RuntimeError(f"Clase inesperada: {class_name!r}")
                relative = annotation.get("mask")
                if not isinstance(relative, str):
                    raise RuntimeError(f"Máscara sin ruta: {stem}")
                rel = PurePosixPath(relative)
                if rel.is_absolute() or ".." in rel.parts or not relative.startswith("masks/"):
                    raise RuntimeError(f"Ruta de máscara insegura: {relative}")
                destination = root / Path(*rel.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                if not destination.exists():
                    fetch(relative, destination)
                with Image.open(destination) as mask:
                    if mask.size == (0, 0) or mask.mode not in {"1", "L", "P", "RGB", "RGBA"}:
                        raise RuntimeError(f"Máscara PNG no válida: {relative}")
                    if not (mask.convert("L").getbbox()):
                        raise RuntimeError(f"Máscara vacía: {relative}")
                expected_classes.add(class_name)
                expected_instances += 1
            print(f"DOWNLOADED {stem}: {len(annotations)} object masks")

        dataset = BDD100KGitHubInstanceSampleDataset(
            root, size=(args.height, args.width)
        )
        total_instances = 0
        observed_classes = set()
        for index in range(len(dataset)):
            image, target = dataset[index]
            assert tuple(image.shape) == (3, args.height, args.width)
            assert image.dtype == torch.float32
            assert image.min().item() >= 0.0 and image.max().item() <= 1.0
            assert target["boxes"].shape == (len(target["labels"]), 4)
            assert target["masks"].shape == (len(target["labels"]), args.height, args.width)
            assert target["labels"].dtype == torch.int64
            assert target["masks"].dtype == torch.uint8
            assert torch.all(target["boxes"][:, 2] > target["boxes"][:, 0])
            assert torch.all(target["boxes"][:, 3] > target["boxes"][:, 1])
            total_instances += len(target["labels"])
            observed_classes.update(
                name for name, class_id in GITHUB_SAMPLE_CLASSES.items()
                if bool((target["labels"] == class_id).any())
            )
            print(
                f"LOADER sample={index} image={tuple(image.shape)} "
                f"instances={len(target['labels'])} boxes={tuple(target['boxes'].shape)} "
                f"masks={tuple(target['masks'].shape)}"
            )

        if total_instances != expected_instances:
            raise RuntimeError(
                f"Instancias inconsistentes: descargadas={expected_instances}, loader={total_instances}"
            )
        if not expected_classes.issubset(observed_classes):
            raise RuntimeError("El loader perdió clases presentes en las anotaciones.")
        print(
            f"SUMMARY images={len(dataset)} instances={total_instances} "
            f"classes={','.join(sorted(observed_classes))}"
        )
        print("FORMAT: third-party per-object binary PNG; NOT official BDD100K RGBA")
        print("RESULT: BDD100K GITHUB INSTANCE SAMPLE VALIDATION PASSED")


if __name__ == "__main__":
    main()
