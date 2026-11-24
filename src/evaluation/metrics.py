import numpy as np


def compute_box_iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    x1, y1 = max(float(box_a[0]), float(box_b[0])), max(float(box_a[1]), float(box_b[1]))
    x2, y2 = min(float(box_a[2]), float(box_b[2])), min(float(box_a[3]), float(box_b[3]))
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area_a = max(0.0, float(box_a[2]) - float(box_a[0])) * max(0.0, float(box_a[3]) - float(box_a[1]))
    area_b = max(0.0, float(box_b[2]) - float(box_b[0])) * max(0.0, float(box_b[3]) - float(box_b[1]))
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def match_predictions_to_ground_truth(pred_boxes, gt_boxes, iou_threshold=0.5,
                                      pred_labels=None, gt_labels=None):
    pred_boxes = np.asarray(pred_boxes, dtype=np.float32).reshape(-1, 4)
    gt_boxes = np.asarray(gt_boxes, dtype=np.float32).reshape(-1, 4)
    if pred_labels is not None and gt_labels is not None:
        pred_labels, gt_labels = list(pred_labels), list(gt_labels)
    matched = set()
    tp = 0
    # Global greedy matching: highest-IoU pair first, one-to-one.
    pairs = []
    for pi, pb in enumerate(pred_boxes):
        for gi, gb in enumerate(gt_boxes):
            if pred_labels is not None and pred_labels[pi] != gt_labels[gi]:
                continue
            iou = compute_box_iou(pb, gb)
            if iou >= iou_threshold:
                pairs.append((iou, pi, gi))
    used_pred = set()
    for _, pi, gi in sorted(pairs, reverse=True):
        if pi not in used_pred and gi not in matched:
            used_pred.add(pi)
            matched.add(gi)
            tp += 1
    return tp, len(gt_boxes) - tp, len(pred_boxes) - tp


def compute_semantic_miou(pred_mask, gt_mask, num_classes=None, ignore_index=None):
    if pred_mask is None or gt_mask is None:
        return float("nan")
    pred = np.asarray(pred_mask)
    gt = np.asarray(gt_mask)
    if pred.shape != gt.shape:
        raise ValueError(f"Las máscaras deben tener la misma forma: {pred.shape} != {gt.shape}")
    if pred.ndim != 2:
        raise ValueError("Las máscaras semánticas deben ser mapas 2D de IDs de clase.")
    classes = range(num_classes) if num_classes is not None else sorted(set(np.unique(pred)) | set(np.unique(gt)))
    ious = []
    valid = np.ones(gt.shape, dtype=bool)
    if ignore_index is not None:
        valid &= gt != ignore_index
    for cls_id in classes:
        pred_cls, gt_cls = (pred == cls_id) & valid, (gt == cls_id) & valid
        union = np.logical_or(pred_cls, gt_cls).sum()
        if union:
            ious.append(float(np.logical_and(pred_cls, gt_cls).sum() / union))
    return float(np.mean(ious)) if ious else float("nan")


def compute_average_precision_per_image(predictions, gt_list, all_classes,
                                        iou_threshold=0.5):
    """VOC-style AP@IoU: rank all detections by confidence and integrate the PR envelope."""
    result = {}
    for cname in all_classes:
        gt_by_image = {}
        n_gt = 0
        for image_idx, gt in enumerate(gt_list):
            boxes = [np.asarray(b, dtype=np.float32) for b, c in zip(gt["boxes"], gt["class_names"]) if c == cname]
            gt_by_image[image_idx] = {"boxes": boxes, "matched": np.zeros(len(boxes), dtype=bool)}
            n_gt += len(boxes)
        detections = []
        for image_idx, pred in enumerate(predictions):
            scores = pred.get("scores", [1.0] * len(pred["boxes"]))
            for box, cls, score in zip(pred["boxes"], pred["class_names"], scores):
                if cls == cname:
                    detections.append((float(score), image_idx, np.asarray(box, dtype=np.float32)))
        if n_gt == 0:
            result[cname] = float("nan")
            continue
        detections.sort(key=lambda item: item[0], reverse=True)
        tp = np.zeros(len(detections), dtype=np.float64)
        fp = np.zeros(len(detections), dtype=np.float64)
        for idx, (_, image_idx, box) in enumerate(detections):
            entry = gt_by_image[image_idx]
            if not entry["boxes"]:
                fp[idx] = 1
                continue
            ious = np.array([compute_box_iou(box, gt_box) for gt_box in entry["boxes"]])
            best = int(np.argmax(ious))
            if ious[best] >= iou_threshold and not entry["matched"][best]:
                tp[idx] = 1
                entry["matched"][best] = True
            else:
                fp[idx] = 1
        if not len(detections):
            result[cname] = 0.0
            continue
        recall = np.cumsum(tp) / n_gt
        precision = np.cumsum(tp) / np.maximum(np.cumsum(tp + fp), np.finfo(float).eps)
        mrec = np.concatenate(([0.0], recall, [1.0]))
        mpre = np.concatenate(([0.0], precision, [0.0]))
        for i in range(len(mpre) - 2, -1, -1):
            mpre[i] = max(mpre[i], mpre[i + 1])
        changes = np.where(mrec[1:] != mrec[:-1])[0]
        result[cname] = float(np.sum((mrec[changes + 1] - mrec[changes]) * mpre[changes + 1]))
    return result


def _to_bool_mask(mask):
    """Decode a bool mask or the compact (np.packbits(mask), original_shape) form."""
    if isinstance(mask, tuple) and len(mask) == 2:
        packed, shape = mask
        count = int(np.prod(shape))
        return np.unpackbits(np.asarray(packed, dtype=np.uint8), count=count).reshape(shape).astype(bool)
    return np.asarray(mask, dtype=bool)


def compute_mask_average_precision_per_image(predictions, gt_list, all_classes,
                                              iou_threshold=0.5):
    """VOC-style AP for binary instance masks, matched one-to-one per image.

    Masks may be compacted with np.packbits(mask.reshape(-1)), paired with
    their original shape, to reduce memory during evaluation.
    """
    result = {}
    for cname in all_classes:
        gt_by_image = {}
        n_gt = 0
        for image_idx, gt in enumerate(gt_list):
            masks = [_to_bool_mask(mask)
                     for mask, cls in zip(gt["masks"], gt["class_names"]) if cls == cname]
            gt_by_image[image_idx] = {"masks": masks,
                                      "matched": np.zeros(len(masks), dtype=bool)}
            n_gt += len(masks)
        detections = []
        for image_idx, pred in enumerate(predictions):
            scores = pred.get("scores", [1.0] * len(pred["masks"]))
            for mask, cls, score in zip(pred["masks"], pred["class_names"], scores):
                if cls == cname:
                    detections.append((float(score), image_idx, _to_bool_mask(mask)))
        if n_gt == 0:
            result[cname] = float("nan")
            continue
        detections.sort(key=lambda item: item[0], reverse=True)
        tp = np.zeros(len(detections), dtype=np.float64)
        fp = np.zeros(len(detections), dtype=np.float64)
        for idx, (_, image_idx, mask) in enumerate(detections):
            entry = gt_by_image[image_idx]
            if not entry["masks"]:
                fp[idx] = 1
                continue
            ious = []
            for gt_mask in entry["masks"]:
                if mask.shape != gt_mask.shape:
                    raise ValueError(f"Máscaras de predicción/GT incompatibles: {mask.shape} != {gt_mask.shape}")
                intersection = np.logical_and(mask, gt_mask).sum()
                union = np.logical_or(mask, gt_mask).sum()
                ious.append(float(intersection / union) if union else 0.0)
            best = int(np.argmax(ious))
            if ious[best] >= iou_threshold and not entry["matched"][best]:
                tp[idx] = 1
                entry["matched"][best] = True
            else:
                fp[idx] = 1
        if not len(detections):
            result[cname] = 0.0
            continue
        recall = np.cumsum(tp) / n_gt
        precision = np.cumsum(tp) / np.maximum(np.cumsum(tp + fp), np.finfo(float).eps)
        mrec = np.concatenate(([0.0], recall, [1.0]))
        mpre = np.concatenate(([0.0], precision, [0.0]))
        for i in range(len(mpre) - 2, -1, -1):
            mpre[i] = max(mpre[i], mpre[i + 1])
        changes = np.where(mrec[1:] != mrec[:-1])[0]
        result[cname] = float(np.sum((mrec[changes + 1] - mrec[changes]) * mpre[changes + 1]))
    return result
