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

COCO_URBAN_ID_TO_NAME = {
    1: "person",
    2: "bicycle",
    3: "car",
    4: "motorcycle",
    6: "bus",
    8: "truck",
    10: "traffic light",
    13: "stop sign",
}

SHARED_VOC_COCO_LABELS = {"person", "bicycle", "car", "motorcycle", "bus"}


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
        else:
            return mask
        decoded = mask_utils.decode(rle)
        if decoded.ndim == 3:
            decoded = np.max(decoded, axis=2)
        return (decoded > 0).astype(np.uint8)

    if isinstance(segmentation, list):
        for poly in segmentation:
            if len(poly) >= 6:
                pts = np.array(poly, dtype=np.int32).reshape((-1, 2))
                cv2.fillPoly(mask, [pts], 1)
    return mask


def load_coco_val2017_samples(
    images_dir: str,
    annotations_file: str,
    max_samples: int | None = 200,
    only_urban_images: bool = True,
    shared_mask_labels: set[str] | None = None,
) -> list[dict]:
    if not os.path.isfile(annotations_file) or not os.path.isdir(images_dir):
        raise FileNotFoundError(
            f"Dataset no encontrado en '{images_dir}' o '{annotations_file}'. "
            "Ejecuta: python scripts/download_coco_val2017.py"
        )

    shared_set = (
        shared_mask_labels
        if shared_mask_labels is not None
        else SHARED_VOC_COCO_LABELS
    )

    with open(annotations_file, "r", encoding="utf-8") as f:
        coco_data = json.load(f)

    images_by_id = {img["id"]: img for img in coco_data.get("images", [])}
    anns_by_img_id: dict[int, list[dict]] = {}
    for ann in coco_data.get("annotations", []):
        cat_id = ann.get("category_id")
        if cat_id in COCO_URBAN_ID_TO_NAME:
            anns_by_img_id.setdefault(ann["image_id"], []).append(ann)

    selected_ids = (
        sorted(anns_by_img_id.keys())
        if only_urban_images
        else sorted(images_by_id.keys())
    )
    if max_samples is not None:
        selected_ids = selected_ids[:max_samples]

    samples = []
    for img_id in selected_ids:
        img_info = images_by_id.get(img_id)
        if img_info is None:
            continue
        img_path = os.path.join(images_dir, img_info["file_name"])
        if not os.path.isfile(img_path):
            continue

        h, w = img_info["height"], img_info["width"]
        gt_boxes = []
        gt_labels = []
        mask_all8 = np.zeros((h, w), dtype=np.uint8)
        mask_shared5 = np.zeros((h, w), dtype=np.uint8)

        for ann in anns_by_img_id.get(img_id, []):
            x, y, bw, bh = ann["bbox"]
            if bw <= 0 or bh <= 0:
                continue
            cname = COCO_URBAN_ID_TO_NAME[ann["category_id"]]
            gt_boxes.append([x, y, x + bw, y + bh])
            gt_labels.append(cname)
            inst_mask = decode_segmentation_mask(ann.get("segmentation"), h, w)
            mask_all8 = np.maximum(mask_all8, inst_mask)
            if cname in shared_set:
                mask_shared5 = np.maximum(mask_shared5, inst_mask)

        samples.append(
            {
                "image_id": int(img_id),
                "path": img_path,
                "gt_boxes": (
                    np.array(gt_boxes, dtype=np.float32)
                    if gt_boxes
                    else np.zeros((0, 4), dtype=np.float32)
                ),
                "gt_labels": gt_labels,
                "gt_semantic_mask": mask_shared5,
                "gt_semantic_mask_all8": mask_all8,
            }
        )

    return samples
