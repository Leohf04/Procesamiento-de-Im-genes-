"""LEGACY/DEPRECATED: los polígonos BDD100K no deben rasterizarse a una máscara binaria.

Use las máscaras oficiales empaquetadas y BDD100KLaneDataset.

This script is retained only for reproducing an earlier experiment. It discards
lane category, direction, style, and Bezier control-point semantics. Do not use
its output for BDD100K training or academic metrics.
"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np


def rasterize_annotation(frame, width, height, thickness=8):
    mask = np.zeros((height, width), dtype=np.uint8)
    for label in frame.get("labels", []):
        if label.get("category") != "lane":
            continue
        for line in label.get("poly2d", []):
            vertices = line.get("vertices", [])
            if len(vertices) < 2:
                continue
            points = np.asarray([[round(x), round(y)] for x, y in vertices], dtype=np.int32)
            cv2.polylines(mask, [points], bool(line.get("closed", False)), 255,
                          thickness=max(1, int(thickness)), lineType=cv2.LINE_8)
    return mask


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", required=True, help="BDD100K lane-marking JSON")
    parser.add_argument("--images-dir", required=True, help="Directory containing source images")
    parser.add_argument("--masks-dir", required=True, help="Output directory for binary lane masks")
    parser.add_argument("--thickness", type=int, default=8)
    args = parser.parse_args()
    images_dir, masks_dir = Path(args.images_dir), Path(args.masks_dir)
    masks_dir.mkdir(parents=True, exist_ok=True)
    frames = json.loads(Path(args.labels).read_text(encoding="utf-8"))
    written = missing = 0
    for frame in frames:
        name = frame.get("name")
        image_path = images_dir / name
        image = cv2.imread(str(image_path))
        if image is None:
            missing += 1
            continue
        height, width = image.shape[:2]
        mask = rasterize_annotation(frame, width, height, args.thickness)
        if not cv2.imwrite(str(masks_dir / (Path(name).stem + ".png")), mask):
            raise OSError(f"No se pudo guardar máscara para {name}")
        written += 1
    print(f"Máscaras escritas: {written}; imágenes faltantes: {missing}; salida: {masks_dir}")


if __name__ == "__main__":
    main()
