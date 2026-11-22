"""Adapters for A2D2 and UrbanSyn annotations into a common urban schema.

Canonical semantic IDs are supplied by the caller; source IDs are never silently
assumed to be equivalent. Instance labels are 1-based and 0 is reserved for
background. 255 is the semantic ignore index.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Mapping

import numpy as np

IGNORE_INDEX = 255
DEFAULT_CANONICAL_CLASSES = {
    "road": 1, "sidewalk": 2, "person": 3, "rider": 4, "bicycle": 5,
    "car": 6, "truck": 7, "bus": 8, "motorcycle": 9,
    "traffic light": 10, "traffic sign": 11, "lane marking": 12,
}
A2D2_INSTANCE_PATTERN = re.compile(
    r"^(car|truck|bus|person|pedestrian|rider|bicycle|cyclist|motor biker|motorcycle)\s+[1-4]$",
    re.IGNORECASE,
)


def _rgb_array(mask: np.ndarray) -> np.ndarray:
    arr = np.asarray(mask)
    if arr.ndim != 3 or arr.shape[2] < 3:
        raise ValueError(f"Expected RGB mask [H,W,3], got {arr.shape}")
    return arr[..., :3].astype(np.uint8, copy=False)


def load_a2d2_class_list(source) -> dict[tuple[int, int, int], str]:
    """Load A2D2 class_list.json (color-key -> class-name)."""
    if isinstance(source, (str, Path)):
        with open(source, encoding="utf-8") as handle:
            source = json.load(handle)
    if not isinstance(source, Mapping):
        raise ValueError("A2D2 class list must be a JSON object")
    result = {}
    for color, name in source.items():
        if not isinstance(color, str) or not isinstance(name, str):
            continue
        token = color.lstrip("#")
        if len(token) != 6:
            continue
        try:
            result[tuple(bytes.fromhex(token))] = name.strip()
        except ValueError:
            continue
    if not result:
        raise ValueError("No valid #RRGGBB -> class entries found in A2D2 class list")
    return result


def normalize_class_name(name: str) -> str | None:
    value = re.sub(r"\s+[1-4]$", "", name.strip().lower())
    aliases = {
        "pedestrian": "person", "person": "person", "cyclist": "rider",
        "motor biker": "rider", "bicycle": "bicycle", "car": "car",
        "truck": "truck", "bus": "bus", "motorcycle": "motorcycle",
        "traffic sign": "traffic sign", "traffic light": "traffic light",
        "road": "road", "sidewalk": "sidewalk", "building": "building",
        "wall": "wall", "fence": "fence", "pole": "pole",
        "vegetation": "vegetation", "terrain": "terrain", "sky": "sky",
        "solid line": "lane marking", "dashed line": "lane marking",
        "road marking": "lane marking", "crosswalk": "lane marking",
    }
    return aliases.get(value)


def decode_a2d2_semantic(
    rgb_mask: np.ndarray,
    color_to_name: Mapping[tuple[int, int, int], str],
    canonical_classes: Mapping[str, int] = DEFAULT_CANONICAL_CLASSES,
    ignore_index: int = IGNORE_INDEX,
) -> np.ndarray:
    """Map exact A2D2 RGB colors to canonical IDs; unknown colors stay ignored."""
    rgb = _rgb_array(rgb_mask)
    out = np.full(rgb.shape[:2], ignore_index, dtype=np.uint8)
    for color, source_name in color_to_name.items():
        canonical = normalize_class_name(source_name)
        if canonical in canonical_classes:
            out[np.all(rgb == np.asarray(color, dtype=np.uint8), axis=-1)] = canonical_classes[canonical]
    return out


def _boxes_from_masks(masks: np.ndarray) -> np.ndarray:
    boxes = []
    for mask in masks:
        ys, xs = np.where(mask)
        if len(xs) == 0:
            boxes.append([0, 0, 0, 0])
        else:
            boxes.append([int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1])
    return np.asarray(boxes, dtype=np.float32).reshape(-1, 4)


def _pack_instances(mask_list: list[np.ndarray], labels: list[int], height: int, width: int) -> dict:
    masks = np.stack(mask_list).astype(np.uint8) if mask_list else np.zeros((0, height, width), np.uint8)
    label_array = np.asarray(labels, dtype=np.int64)
    return {
        "masks": masks,
        "labels": label_array,
        "boxes": _boxes_from_masks(masks),
        "area": masks.sum(axis=(1, 2), dtype=np.uint64).astype(np.float32),
        "iscrowd": np.zeros(len(masks), dtype=np.int64),
    }


def decode_a2d2_instances(
    rgb_mask: np.ndarray,
    color_to_name: Mapping[tuple[int, int, int], str],
    canonical_classes: Mapping[str, int] = DEFAULT_CANONICAL_CLASSES,
    min_component_area: int = 8,
) -> dict:
    """Split A2D2 participant sub-class colors into connected-component instances.

    Subclass colors are not treated as globally unique object IDs. Connected
    components with the same color become separate masks; tiny fragments are
    discarded by the explicit min_component_area threshold.
    """
    import cv2

    rgb = _rgb_array(rgb_mask)
    h, w = rgb.shape[:2]
    masks, labels = [], []
    for color, source_name in color_to_name.items():
        if not A2D2_INSTANCE_PATTERN.match(source_name.strip()):
            continue
        canonical = normalize_class_name(source_name)
        if canonical not in canonical_classes:
            continue
        binary = np.all(rgb == np.asarray(color, dtype=np.uint8), axis=-1).astype(np.uint8)
        count, component_map, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        for component_id in range(1, count):
            if int(stats[component_id, cv2.CC_STAT_AREA]) < min_component_area:
                continue
            masks.append((component_map == component_id).astype(np.uint8))
            labels.append(int(canonical_classes[canonical]))
    return _pack_instances(masks, labels, h, w)


def decode_urbansyn_semantic(
    semantic_mask: np.ndarray,
    source_to_canonical: Mapping[int, int] | None = None,
    ignore_index: int = IGNORE_INDEX,
) -> np.ndarray:
    """Decode UrbanSyn's RGB-replicated class IDs or single-channel ID mask."""
    arr = np.asarray(semantic_mask)
    if arr.ndim == 3:
        if arr.shape[2] < 3:
            raise ValueError(f"Unexpected semantic mask shape: {arr.shape}")
        if not (np.array_equal(arr[..., 0], arr[..., 1]) and np.array_equal(arr[..., 0], arr[..., 2])):
            raise ValueError("UrbanSyn semantic RGB channels are not identical")
        arr = arr[..., 0]
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D semantic IDs, got {arr.shape}")
    ids = arr.astype(np.int64, copy=False)
    if source_to_canonical is None:
        return ids.astype(np.uint8)
    result = np.full(ids.shape, ignore_index, dtype=np.uint8)
    for source_id, target_id in source_to_canonical.items():
        result[ids == int(source_id)] = int(target_id)
    return result


def decode_urbansyn_panoptic(
    panoptic_rgb: np.ndarray,
    source_to_canonical: Mapping[int, int],
    min_instance_area: int = 1,
) -> dict:
    """Decode UrbanSyn panoptic RGB: instance_id = R*256+G, semantic_id = B."""
    rgb = _rgb_array(panoptic_rgb)
    h, w = rgb.shape[:2]
    instance_ids = rgb[..., 0].astype(np.int64) * 256 + rgb[..., 1].astype(np.int64)
    source_classes = rgb[..., 2].astype(np.int64)
    masks, labels = [], []
    pairs = np.unique(np.stack([instance_ids, source_classes], axis=-1).reshape(-1, 2), axis=0)
    for instance_id, source_class in pairs:
        if instance_id == 0 or int(source_class) not in source_to_canonical:
            continue
        mask = (instance_ids == instance_id) & (source_classes == source_class)
        if int(mask.sum()) < min_instance_area:
            continue
        masks.append(mask.astype(np.uint8))
        labels.append(int(source_to_canonical[int(source_class)]))
    return _pack_instances(masks, labels, h, w)


def to_torchvision_target(decoded: Mapping, image_id: int = 0):
    """Convert decoded instance arrays to Mask R-CNN target tensors."""
    import torch
    masks = torch.as_tensor(decoded["masks"], dtype=torch.uint8)
    return {
        "boxes": torch.as_tensor(decoded["boxes"], dtype=torch.float32).reshape(-1, 4),
        "labels": torch.as_tensor(decoded["labels"], dtype=torch.int64),
        "masks": masks,
        "image_id": torch.tensor([int(image_id)], dtype=torch.int64),
        "area": torch.as_tensor(decoded["area"], dtype=torch.float32),
        "iscrowd": torch.as_tensor(decoded["iscrowd"], dtype=torch.int64),
    }


def _load_rgb_tensor(image_path, size=None, normalize=True):
    from PIL import Image
    import torch
    with Image.open(image_path) as handle:
        image = handle.convert("RGB")
        if size is not None:
            image = image.resize((int(size[1]), int(size[0])), Image.Resampling.BILINEAR)
        array = np.asarray(image, dtype=np.float32) / 255.0
    if normalize:
        mean = np.asarray([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.asarray([0.229, 0.224, 0.225], dtype=np.float32)
        array = (array - mean) / std
    import torch
    return torch.from_numpy(array.transpose(2, 0, 1).copy())


def _load_mask_array(mask_path, size=None):
    from PIL import Image
    with Image.open(mask_path) as handle:
        mask = handle.copy()
        if size is not None:
            mask = mask.resize((int(size[1]), int(size[0])), Image.Resampling.NEAREST)
        return np.asarray(mask)


class _ManifestDataset:
    """Base class for explicit manifests; each record names local image/label paths."""
    def __init__(self, records, size=None):
        self.records = [dict(record) for record in records]
        self.size = size
        if not self.records:
            raise ValueError("Dataset manifest is empty")
        for index, record in enumerate(self.records):
            if "image" not in record or not Path(record["image"]).is_file():
                raise FileNotFoundError(f"Missing image for manifest row {index}: {record.get('image')}")
    def __len__(self):
        return len(self.records)


class A2D2SemanticDataset(_ManifestDataset):
    """A2D2 manifest rows: {'image': RGB path, 'semantic': RGB label path}."""
    def __init__(self, records, color_to_name, canonical_classes=DEFAULT_CANONICAL_CLASSES, size=None):
        super().__init__(records, size)
        self.color_to_name, self.canonical_classes = color_to_name, canonical_classes
        for index, record in enumerate(self.records):
            if "semantic" not in record or not Path(record["semantic"]).is_file():
                raise FileNotFoundError(f"Missing A2D2 semantic label in row {index}")
    def __getitem__(self, index):
        import torch
        record = self.records[index]
        image = _load_rgb_tensor(record["image"], self.size, normalize=True)
        mask = _load_mask_array(record["semantic"], self.size)
        target = decode_a2d2_semantic(mask, self.color_to_name, self.canonical_classes)
        return image, torch.from_numpy(target.astype(np.int64))


class A2D2InstanceDataset(_ManifestDataset):
    """A2D2 manifest rows: {'image': RGB path, 'instance': RGB sub-class mask path}.

    The semantic RGB mask may be supplied as 'instance' because participant
    subclasses are encoded by color in A2D2's semantic labels.
    """
    def __init__(self, records, color_to_name, canonical_classes=DEFAULT_CANONICAL_CLASSES,
                 size=None, min_component_area=8):
        super().__init__(records, size)
        self.color_to_name, self.canonical_classes = color_to_name, canonical_classes
        self.min_component_area = min_component_area
        for index, record in enumerate(self.records):
            if "instance" not in record or not Path(record["instance"]).is_file():
                raise FileNotFoundError(f"Missing A2D2 instance/subclass label in row {index}")
    def __getitem__(self, index):
        record = self.records[index]
        image = _load_rgb_tensor(record["image"], self.size, normalize=False)
        mask = _load_mask_array(record["instance"], self.size)
        decoded = decode_a2d2_instances(mask, self.color_to_name, self.canonical_classes,
                                        self.min_component_area)
        return image, to_torchvision_target(decoded, image_id=int(record.get("image_id", index)))


class UrbanSynSemanticDataset(_ManifestDataset):
    """UrbanSyn manifest rows: {'image': RGB path, 'semantic': class-ID mask path}."""
    def __init__(self, records, source_to_canonical=None, size=None):
        super().__init__(records, size)
        self.source_to_canonical = source_to_canonical
        for index, record in enumerate(self.records):
            if "semantic" not in record or not Path(record["semantic"]).is_file():
                raise FileNotFoundError(f"Missing UrbanSyn semantic label in row {index}")
    def __getitem__(self, index):
        import torch
        record = self.records[index]
        image = _load_rgb_tensor(record["image"], self.size, normalize=True)
        mask = _load_mask_array(record["semantic"], self.size)
        target = decode_urbansyn_semantic(mask, self.source_to_canonical)
        return image, torch.from_numpy(target.astype(np.int64))


class UrbanSynInstanceDataset(_ManifestDataset):
    """UrbanSyn manifest rows: {'image': RGB path, 'panoptic': RGB panoptic path}."""
    def __init__(self, records, source_to_canonical, size=None, min_instance_area=1):
        super().__init__(records, size)
        self.source_to_canonical, self.min_instance_area = source_to_canonical, min_instance_area
        for index, record in enumerate(self.records):
            if "panoptic" not in record or not Path(record["panoptic"]).is_file():
                raise FileNotFoundError(f"Missing UrbanSyn panoptic label in row {index}")
    def __getitem__(self, index):
        record = self.records[index]
        image = _load_rgb_tensor(record["image"], self.size, normalize=False)
        panoptic = _load_mask_array(record["panoptic"], self.size)
        decoded = decode_urbansyn_panoptic(panoptic, self.source_to_canonical,
                                           self.min_instance_area)
        return image, to_torchvision_target(decoded, image_id=int(record.get("image_id", index)))


def detection_collate_fn(batch):
    """Keep variable-length Mask R-CNN targets as lists instead of stacking."""
    images, targets = zip(*batch)
    return list(images), list(targets)
