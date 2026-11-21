"""BDD100K datasets backed by the official 8-bit semantic and RGBA instance masks.

Expected roots:
  images/10k/{train,val}/*.jpg
  labels/sem_seg/masks/{train,val}/*.png
  labels/ins_seg/bitmasks/{train,val}/*.png

The mask encodings follow bdd100k/doc/source/format.rst. No label files are
silently synthesized: image/mask pairs must match by filename stem.
"""
from pathlib import Path
import json

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
BDD100K_DETECTION_CLASSES = (
    "pedestrian", "rider", "car", "truck", "bus", "train",
    "motorcycle", "bicycle", "traffic light", "traffic sign",
)
_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
_MEAN = np.asarray([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.asarray([0.229, 0.224, 0.225], dtype=np.float32)


def _image_tensor(path, size, normalize=True):
    """Load RGB as CHW float32; normalize only for semantic segmentation.

    Torchvision detection models (including Mask R-CNN) normalize internally,
    so their input must remain in [0, 1].
    """
    image = Image.open(path).convert("RGB").resize(
        (size[1], size[0]), Image.Resampling.BILINEAR
    )
    array = np.asarray(image, dtype=np.float32) / 255.0
    if normalize:
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
        return _image_tensor(image_path, self.size, normalize=False), target


class BDD100KDetectionDataset(Dataset):
    """BDD100K 2D detection adapter for the official det_20 frame JSON.

    Images are returned in [0, 1] because torchvision detection models perform
    their own normalization. Category IDs in targets are 1..10 (0 is background).
    """
    def __init__(self, images_dir, labels_json, size=(512, 1024)):
        self.images_dir = Path(images_dir)
        self.labels_json = Path(labels_json)
        self.size = tuple(size)
        if not self.images_dir.is_dir():
            raise FileNotFoundError(f"No existe el directorio de imágenes: {self.images_dir}")
        if not self.labels_json.is_file():
            raise FileNotFoundError(f"No existe el JSON de detección: {self.labels_json}")
        frames = json.loads(self.labels_json.read_text(encoding="utf-8"))
        if not isinstance(frames, list):
            raise ValueError("El JSON de detección BDD100K debe contener una lista de frames.")
        self.frames = []
        missing = []
        for frame in frames:
            name = frame.get("name")
            if not isinstance(name, str) or Path(name).name != name:
                raise ValueError(f"Nombre de imagen BDD100K no permitido: {name!r}")
            image_path = self.images_dir / name
            if not image_path.is_file():
                missing.append(name)
            else:
                self.frames.append(frame)
        if missing:
            raise FileNotFoundError(
                f"Faltan {len(missing)} imágenes de detección; ejemplos: {', '.join(missing[:3])}"
            )
        if not self.frames:
            raise ValueError("El JSON de detección no contiene imágenes disponibles.")

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, index):
        frame = self.frames[index]
        image_path = self.images_dir / frame["name"]
        with Image.open(image_path) as source:
            original_width, original_height = source.size
        scale_x = self.size[1] / original_width
        scale_y = self.size[0] / original_height
        boxes, labels = [], []
        for annotation in frame.get("labels", []):
            category = annotation.get("category")
            if category not in BDD100K_DETECTION_CLASSES:
                continue
            box = annotation.get("box2d")
            if not isinstance(box, dict):
                continue
            try:
                x1, y1 = float(box["x1"]), float(box["y1"])
                x2, y2 = float(box["x2"]), float(box["y2"])
            except (KeyError, TypeError, ValueError):
                continue
            x1, x2 = np.clip([x1 * scale_x, x2 * scale_x], 0, self.size[1])
            y1, y2 = np.clip([y1 * scale_y, y2 * scale_y], 0, self.size[0])
            if x2 <= x1 or y2 <= y1:
                continue
            boxes.append([x1, y1, x2, y2])
            labels.append(BDD100K_DETECTION_CLASSES.index(category) + 1)
        target = {
            "boxes": torch.as_tensor(boxes, dtype=torch.float32).reshape(-1, 4),
            "labels": torch.as_tensor(labels, dtype=torch.int64),
            "image_id": torch.tensor([index], dtype=torch.int64),
            "area": torch.as_tensor(
                [(box[2] - box[0]) * (box[3] - box[1]) for box in boxes],
                dtype=torch.float32,
            ),
            "iscrowd": torch.zeros((len(labels),), dtype=torch.int64),
        }
        return _image_tensor(image_path, self.size, normalize=False), target
