"""Validate urban datasets and generate BDD100K lane masks for CI preparation.

Expected Drive folder layout:
  bdd100k/images/100k/{train,val}/...
  bdd100k/labels/lane/{train,val}.json
  cityscapes/leftImg8bit/{train,val}/...
  cityscapes/gtFine/{train,val}/...
The script never downloads datasets and never modifies source files.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import cv2


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_bdd(root: Path, output: Path, thickness: int) -> dict:
    splits = {}
    for split in ("train", "val"):
        image_dir = root / "images" / "100k" / split
        labels_file = root / "labels" / "lane" / f"{split}.json"
        if not image_dir.is_dir():
            raise FileNotFoundError(f"Falta directorio BDD100K: {image_dir}")
        if not labels_file.is_file():
            raise FileNotFoundError(f"Falta JSON de lane markings: {labels_file}")
        frames = json.loads(labels_file.read_text(encoding="utf-8"))
        if not isinstance(frames, list) or not frames:
            raise ValueError(f"Anotaciones vacías o formato inválido: {labels_file}")
        missing, corrupt = [], []
        for frame in frames:
            name = frame.get("name")
            if not name:
                raise ValueError(f"Frame sin campo 'name' en {labels_file}")
            image_path = image_dir / name
            if not image_path.is_file():
                missing.append(name)
                continue
            image = cv2.imread(str(image_path))
            if image is None:
                corrupt.append(name)
        if missing or corrupt:
            raise ValueError(
                f"{split}: {len(missing)} imágenes faltantes y {len(corrupt)} corruptas; "
                f"ejemplos faltantes={missing[:3]}, corruptas={corrupt[:3]}"
            )
        masks_dir = output / "lane_masks" / split
        command = [
            sys.executable, "scripts/prepare_bdd100k_lane_masks.py",
            "--labels", str(labels_file),
            "--images-dir", str(image_dir),
            "--masks-dir", str(masks_dir),
            "--thickness", str(thickness),
        ]
        subprocess.run(command, check=True)
        masks = sorted(masks_dir.glob("*.png"))
        if len(masks) != len(frames):
            raise RuntimeError(
                f"{split}: se esperaban {len(frames)} máscaras y se generaron {len(masks)}"
            )
        splits[split] = {
            "frames": len(frames),
            "masks": len(masks),
            "labels_json": str(labels_file.relative_to(root)),
        }
    return {"dataset": "bdd100k_lane_markings", "splits": splits}


def validate_cityscapes(root: Path) -> dict:
    splits = {}
    for split in ("train", "val"):
        image_root = root / "leftImg8bit" / split
        label_root = root / "gtFine" / split
        if not image_root.is_dir() or not label_root.is_dir():
            raise FileNotFoundError(
                f"Cityscapes requiere {image_root} y {label_root}"
            )
        images = sorted(image_root.glob("*/*_leftImg8bit.png"))
        labels = sorted(label_root.glob("*/*_gtFine_labelIds.png"))
        if not images or not labels:
            raise ValueError(f"Cityscapes {split}: no se encontraron imágenes o labelIds")
        label_by_key = {
            p.name.replace("_gtFine_labelIds.png", ""): p for p in labels
        }
        missing = [
            p.name.replace("_leftImg8bit.png", "")
            for p in images
            if p.name.replace("_leftImg8bit.png", "") not in label_by_key
        ]
        if missing:
            raise ValueError(f"Cityscapes {split}: {len(missing)} imágenes sin labelIds; {missing[:3]}")
        splits[split] = {"images": len(images), "semantic_labels": len(labels)}
    return {"dataset": "cityscapes_fine", "splits": splits}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=("bdd100k", "cityscapes"), required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--lane-thickness", type=int, default=8)
    args = parser.parse_args()
    if not args.source_root.is_dir():
        raise FileNotFoundError(f"No existe el dataset: {args.source_root}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.dataset == "bdd100k":
        report = validate_bdd(args.source_root, args.output_dir, args.lane_thickness)
    else:
        report = validate_cityscapes(args.source_root)
    report.update({
        "source_root": str(args.source_root),
        "lane_thickness": args.lane_thickness if args.dataset == "bdd100k" else None,
        "status": "validated_and_prepared",
    })
    report_path = args.output_dir / "dataset_manifest.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
