"""BDD100K datasets backed by the official 8-bit semantic and RGBA instance masks.

Expected roots:
  images/10k/{train,val}/*.jpg
  labels/sem_seg/masks/{train,val}/*.png
  labels/ins_seg/bitmasks/{train,val}/*.png

The mask encodings follow bdd100k/doc/source/format.rst. No label files are
silently synthesized: image/mask pairs must match by filename stem.
"""
from pathlib import Path

import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset


BDD100K_SEMANTIC_CLASSES = (
    "road", "sidewalk", "building", "wall", "fence", "pole",
    "traffic_light", "traffic_sign", "vegetation", "terrain", "sky",
    "person", "rider", "car", "truck", "bus", "train", "motorcycle",
    "bicycle",
)
BDD100K_INSTANCE_CLASSES = (
    "pedestrian", "rider", "car", "truck", "bus", "train",
    "motorcycle", "bicycle",
)
_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
_MEAN = np.asarray([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.asarray([0.229, 0.224, 0.225], dtype=np.float32)


def _image_tensor(path, size):
    image = Image.open(path).convert("RGB").resize(
        (size[1], size[0]), Image.Resampling.BILINEAR
    )
    array = np.asarray(image, dtype=np.float32) / 255.0
    array = (array - _MEAN) / _STD
    return torch.from_numpy(array.transpose(2, 0, 1).copy())


def _paired_files(images_dir, masks_dir):
    images_dir, masks_dir = Path(images_dir), Path(masks_dir)
    if not images_dir.is_dir():
        raise FileNotFoundError(f"No existe el directorio de imágenes: {images_dir}")
    if not masks_dir.is_dir():
        raise FileNotFoundError(f"No existe el directorio de máscaras: {masks_dir}")
    images = sorted(p for p in images_dir.iterdir()
                    if p.is_file() and p.suffix.lower() in _IMAGE_SUFFIXES)
    if not images:
        raise FileNotFoundError(f"No hay imágenes en {images_dir}")
    pairs = []
    missing = []
    for image in images:
        mask = masks_dir / f"{image.stem}.png"
        if mask.is_file():
            pairs.append((image, mask))
        else:
            missing.append(image.name)
    if missing:
        sample = ", ".join(missing[:3])
        raise FileNotFoundError(
            f"Faltan {len(missing)} máscaras en {masks_dir}; ejemplos: {sample}"
        )
    return pairs


class BDD100KSemanticDataset(Dataset):
    """19-class semantic segmentation; mask pixel values are train IDs 0..18/255."""

    def __init__(self, images_dir, masks_dir, size=(512, 1024)):
        self.pairs = _paired_files(images_dir, masks_dir)
        self.size = tuple(size)

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        image_path, mask_path = self.pairs[index]
        mask = Image.open(mask_path).convert("L").resize(
            (self.size[1], self.size[0]), Image.Resampling.NEAREST
        )
        target = np.asarray(mask, dtype=np.uint8).copy()
        valid = (target == 255) | (target < len(BDD100K_SEMANTIC_CLASSES))
        if not bool(valid.all()):
            values = np.unique(target[~valid]).tolist()
            raise ValueError(f"IDs semánticos BDD100K fuera de rango en {mask_path}: {values}")
        return _image_tensor(image_path, self.size), torch.from_numpy(target.astype(np.int64))


class BDD100KInstanceDataset(Dataset):
    """Eight-class Mask R-CNN dataset decoded from official RGBA bitmask PNGs.

    R stores category ID (1..8), G stores flags (ignore/crowd in bits 0/1),
    and B stores the instance ID for instance segmentation (A is reserved for tracking). Instances with ignore/crowd flags
    are excluded, as required by the official evaluation convention.
    """

    def __init__(self, images_dir, bitmasks_dir, size=(512, 1024)):
        self.pairs = _paired_files(images_dir, bitmasks_dir)
        self.size = tuple(size)

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        image_path, mask_path = self.pairs[index]
        rgba = Image.open(mask_path).convert("RGBA").resize(
            (self.size[1], self.size[0]), Image.Resampling.NEAREST
        )
        encoded = np.asarray(rgba, dtype=np.uint8)
        category = encoded[..., 0]
        flags = encoded[..., 1]
        instance_id = encoded[..., 2].astype(np.uint16)

        masks, labels = [], []
        for ann_id in np.unique(instance_id):
            if ann_id == 0:
                continue
            pixels = instance_id == ann_id
            category_ids = np.unique(category[pixels])
            category_ids = category_ids[category_ids > 0]
            if category_ids.size != 1:
                continue
            category_id = int(category_ids[0])
            if category_id > len(BDD100K_INSTANCE_CLASSES):
                continue
            # Official G bits: ignore=bit0, crowd=bit1.
            instance_flags = flags[pixels]
            if np.any((instance_flags & 0b00000011) != 0):
                continue
            mask = pixels & (category == category_id)
            if not mask.any():
                continue
            masks.append(mask.astype(np.uint8))
            labels.append(category_id)

        height, width = self.size
        if masks:
            masks_array = np.stack(masks)
            boxes = []
            for mask in masks_array:
                ys, xs = np.where(mask)
                boxes.append([xs.min(), ys.min(), xs.max() + 1, ys.max() + 1])
        else:
            masks_array = np.zeros((0, height, width), dtype=np.uint8)
            boxes = []

        target = {
            "boxes": torch.as_tensor(boxes, dtype=torch.float32).reshape(-1, 4),
            "labels": torch.as_tensor(labels, dtype=torch.int64),
            "masks": torch.as_tensor(masks_array, dtype=torch.uint8),
            "image_id": torch.tensor([index], dtype=torch.int64),
            "area": torch.as_tensor([float(mask.sum()) for mask in masks_array], dtype=torch.float32),
            "iscrowd": torch.zeros((len(labels),), dtype=torch.int64),
        }
        return _image_tensor(image_path, self.size), target
