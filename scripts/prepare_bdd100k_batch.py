"""Validate and rasterize one bounded BDD100K lane-marking batch."""
import argparse
import json
from pathlib import Path, PurePosixPath

import cv2
import numpy as np

from prepare_bdd100k_lane_masks import rasterize_annotation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", required=True, type=Path, help="JSON for the selected batch")
    parser.add_argument("--images-dir", required=True, type=Path)
    parser.add_argument("--masks-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--split", choices=("train", "val"), required=True)
    parser.add_argument("--offset", type=int, required=True)
    parser.add_argument("--thickness", type=int, default=8)
    args = parser.parse_args()
    if args.thickness < 1:
        parser.error("--thickness debe ser >= 1")

    frames = json.loads(args.labels.read_text(encoding="utf-8"))
    if not isinstance(frames, list) or not frames:
        raise ValueError("Lote de anotaciones vacío o inválido")
    args.masks_dir.mkdir(parents=True, exist_ok=True)
    missing, corrupt, written = [], [], 0

    for frame in frames:
        name = frame.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("Frame sin nombre válido")
        rel = PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"Ruta de imagen no permitida: {name}")
        image_path = args.images_dir.joinpath(*rel.parts)
        image = cv2.imread(str(image_path))
        if image is None:
            if not image_path.is_file():
                missing.append(name)
            else:
                corrupt.append(name)
            continue
        height, width = image.shape[:2]
        mask = rasterize_annotation(frame, width, height, args.thickness)
        output = args.masks_dir / (Path(name).stem + ".png")
        if not cv2.imwrite(str(output), mask):
            raise OSError(f"No se pudo escribir {output}")
        written += 1

    if missing or corrupt or written != len(frames):
        raise RuntimeError(
            f"Lote incompleto: {written}/{len(frames)} máscaras; "
            f"faltantes={missing[:5]}, corruptas={corrupt[:5]}"
        )
    manifest = {
        "dataset": "bdd100k_lane_markings",
        "split": args.split,
        "offset": args.offset,
        "frames": len(frames),
        "masks": written,
        "lane_thickness_px": args.thickness,
        "status": "validated_and_prepared",
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
