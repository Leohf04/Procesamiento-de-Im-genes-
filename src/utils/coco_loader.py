import json
import os

import cv2
import numpy as np

try:
    from pycocotools import mask as mask_utils
    HAS_PYCOCOTOOLS = True
except ImportError:
    mask_utils = None
    HAS_PYCOCOTOOLS = False

COCO_URBAN_ID_TO_NAME = {1: "person", 2: "bicycle", 3: "car", 4: "motorcycle", 6: "bus", 8: "truck", 10: "traffic light", 13: "stop sign"}
SHARED_VOC_COCO_LABELS = {"person", "bicycle", "car", "motorcycle", "bus"}
SEMANTIC_CLASS_IDS = {name: idx for idx, name in enumerate(["person", "bicycle", "car", "motorcycle", "bus"], start=1)}


def decode_segmentation_mask(segmentation, height: int, width: int) -> np.ndarray:
    mask = np.zeros((height, width), dtype=np.uint8)
    if not segmentation:
        return mask
    if HAS_PYCOCOTOOLS:
        if isinstance(segmentation, list):
            rles = mask_utils.frPyObjects(segmentation, height, width)
            rle = mask_utils.merge(rles)
        elif isinstance(segmentation, dict) and "counts" in segmentation:
            rle = segmentation
            if isinstance(rle["counts"], list):
                rle = mask_utils.frPyObjects(rle, height, width)
        else:
            return mask
        decoded = mask_utils.decode(rle)
        if decoded.ndim == 3:
            decoded = np.max(decoded, axis=2)
        return (decoded > 0).astype(np.uint8)
    if isinstance(segmentation, list):
        for poly in segmentation:
            if len(poly) >= 6:
                pts = np.array(poly, dtype=np.float32).reshape((-1, 2))
                cv2.fillPoly(mask, [np.round(pts).astype(np.int32)], 1)
    return mask


def load_coco_val2017_samples(images_dir: str, annotations_file: str, max_samples: int | None = 200,
                              only_urban_images: bool = True, shared_mask_labels: set[str] | None = None) -> list[dict]:
    if not os.path.isfile(annotations_file) or not os.path.isdir(images_dir):
        raise FileNotFoundError(f"Dataset no encontrado en '{images_dir}' o '{annotations_file}'. Ejecuta: python scripts/download_coco_val2017.py")
    shared_set = shared_mask_labels if shared_mask_labels is not None else SHARED_VOC_COCO_LABELS
    with open(annotations_file, "r", encoding="utf-8") as stream:
        data = json.load(stream)
    images = {img["id"]: img for img in data.get("images", [])}
    by_image = {}
    for ann in data.get("annotations", []):
        if ann.get("category_id") in COCO_URBAN_ID_TO_NAME:
            by_image.setdefault(ann["image_id"], []).append(ann)
    selected = sorted(by_image if only_urban_images else images)
    if max_samples is not None:
        selected = selected[:max_samples]
    samples = []
    for image_id in selected:
        info = images.get(image_id)
        if info is None:
            continue
        path = os.path.join(images_dir, info["file_name"])
        if not os.path.isfile(path):
            continue
        h, w = int(info["height"]), int(info["width"])
        boxes, labels = [], []
        semantic_shared = np.zeros((h, w), dtype=np.uint8)
        semantic_all = np.zeros((h, w), dtype=np.uint8)
        for ann in by_image.get(image_id, []):
            x, y, bw, bh = ann["bbox"]
            if bw <= 0 or bh <= 0:
                continue
            name = COCO_URBAN_ID_TO_NAME[ann["category_id"]]
            boxes.append([x, y, x + bw, y + bh])
            labels.append(name)
            mask = decode_segmentation_mask(ann.get("segmentation"), h, w)
            semantic_all[mask > 0] = ann["category_id"]
            if name in shared_set and name in SEMANTIC_CLASS_IDS:
                semantic_shared[mask > 0] = SEMANTIC_CLASS_IDS[name]
        samples.append({
            "image_id": int(image_id), "path": path,
            "gt_boxes": np.asarray(boxes, dtype=np.float32).reshape(-1, 4),
            "gt_labels": labels,
            "gt_semantic_mask": semantic_shared,
            "gt_semantic_mask_all8": semantic_all,
        })
    return samples
