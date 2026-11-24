"""Adapter for the small third-party BDD100K instance-mask sample on GitHub.

This is deliberately separate from BDD100KInstanceDataset: the source stores
one binary PNG per object, not the official packed RGBA bitmasks.
"""
from pathlib import Path, PurePosixPath
import json

import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset

GITHUB_SAMPLE_CLASSES = {
    "car": 3,
    "truck": 4,
    "bus": 5,
    "motorcycle": 7,
}


class BDD100KGitHubInstanceSampleDataset(Dataset):
    """Read per-object binary masks from the limited public GitHub sample."""

    def __init__(self, root, size=(256, 512)):
        self.root = Path(root)
        self.images_dir = self.root / "images"
        self.labels_dir = self.root / "labels"
        self.size = tuple(size)
        if not self.images_dir.is_dir() or not self.labels_dir.is_dir():
            raise FileNotFoundError("Se esperan los directorios images/ y labels/")
        self.images = sorted(self.images_dir.glob("*.jpg"))
        if not self.images:
            raise FileNotFoundError(f"No hay JPG en {self.images_dir}")
        missing = [p.stem for p in self.images if not (self.labels_dir / f"{p.stem}.json").is_file()]
        if missing:
            raise FileNotFoundError(f"Faltan JSON para {len(missing)} imágenes: {missing[:3]}")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        image_path = self.images[index]
        annotation_path = self.labels_dir / f"{image_path.stem}.json"
        annotations = json.loads(annotation_path.read_text(encoding="utf-8"))
        if not isinstance(annotations, list):
            raise ValueError(f"Anotaciones inválidas en {annotation_path}")

        with Image.open(image_path) as source:
            original = source.convert("RGB")
            image = original.resize((self.size[1], self.size[0]), Image.Resampling.BILINEAR)
        image_array = np.asarray(image, dtype=np.float32) / 255.0

        masks, labels, boxes = [], [], []
        for annotation in annotations:
            if not isinstance(annotation, dict):
                raise ValueError(f"Anotación no válida en {annotation_path}")
            class_name = annotation.get("class")
            if class_name not in GITHUB_SAMPLE_CLASSES:
                raise ValueError(f"Clase no soportada en muestra GitHub: {class_name!r}")
            relative = annotation.get("mask")
            if not isinstance(relative, str):
                raise ValueError(f"Ruta de máscara ausente en {annotation_path}")
            rel_path = PurePosixPath(relative)
            if rel_path.is_absolute() or ".." in rel_path.parts:
                raise ValueError(f"Ruta de máscara no permitida: {relative}")
            mask_path = self.root / Path(*rel_path.parts)
            if not mask_path.is_file():
                raise FileNotFoundError(f"Falta máscara de instancia: {mask_path}")
            with Image.open(mask_path) as source_mask:
                raw_mask = source_mask.convert("L")
                if raw_mask.size != original.size:
                    raise ValueError(
                        f"Dimensiones incompatibles {mask_path}: {raw_mask.size} != {original.size}"
                    )
                resized = raw_mask.resize(
                    (self.size[1], self.size[0]), Image.Resampling.NEAREST
                )
                binary = np.asarray(resized, dtype=np.uint8) > 0
            if not binary.any():
                raise ValueError(f"Máscara vacía: {mask_path}")
            ys, xs = np.where(binary)
            masks.append(binary.astype(np.uint8))
            labels.append(GITHUB_SAMPLE_CLASSES[class_name])
            boxes.append([xs.min(), ys.min(), xs.max() + 1, ys.max() + 1])

        height, width = self.size
        masks_array = (np.stack(masks) if masks else np.zeros((0, height, width), dtype=np.uint8))
        target = {
            "boxes": torch.as_tensor(boxes, dtype=torch.float32).reshape(-1, 4),
            "labels": torch.as_tensor(labels, dtype=torch.int64),
            "masks": torch.as_tensor(masks_array, dtype=torch.uint8),
            "image_id": torch.tensor([index], dtype=torch.int64),
            "area": torch.as_tensor([float(mask.sum()) for mask in masks_array], dtype=torch.float32),
            "iscrowd": torch.zeros((len(labels),), dtype=torch.int64),
        }
        return torch.from_numpy(image_array.transpose(2, 0, 1).copy()), target
