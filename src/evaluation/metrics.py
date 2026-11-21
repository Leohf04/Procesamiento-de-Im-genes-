import numpy as np


def compute_box_iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    x1 = max(float(box_a[0]), float(box_b[0]))
    y1 = max(float(box_a[1]), float(box_b[1]))
    x2 = min(float(box_a[2]), float(box_b[2]))
    y2 = min(float(box_a[3]), float(box_b[3]))

    inter_w = max(0.0, x2 - x1)
    inter_h = max(0.0, y2 - y1)
    inter_area = inter_w * inter_h

    area_a = max(0.0, float(box_a[2]) - float(box_a[0])) * max(
        0.0, float(box_a[3]) - float(box_a[1])
    )
    area_b = max(0.0, float(box_b[2]) - float(box_b[0])) * max(
        0.0, float(box_b[3]) - float(box_b[1])
    )
    union_area = area_a + area_b - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def match_predictions_to_ground_truth(
    pred_boxes: np.ndarray, gt_boxes: np.ndarray, iou_threshold: float = 0.5
) -> tuple[int, int, int]:
    if len(gt_boxes) == 0:
        return 0, 0, len(pred_boxes)
    if len(pred_boxes) == 0:
        return 0, len(gt_boxes), 0

    iou_matrix = np.zeros((len(pred_boxes), len(gt_boxes)), dtype=np.float32)
    for pred_idx, p_box in enumerate(pred_boxes):
        for gt_idx, g_box in enumerate(gt_boxes):
            iou_matrix[pred_idx, gt_idx] = compute_box_iou(p_box, g_box)

    matched_gt = set()
    true_positives = 0
    for pred_idx in range(len(pred_boxes)):
        best_gt_idx = int(np.argmax(iou_matrix[pred_idx]))
        best_iou = iou_matrix[pred_idx, best_gt_idx]
        if best_iou >= iou_threshold and best_gt_idx not in matched_gt:
            matched_gt.add(best_gt_idx)
            true_positives += 1

    false_positives = len(pred_boxes) - true_positives
    false_negatives = len(gt_boxes) - true_positives
    return true_positives, false_negatives, false_positives


def compute_semantic_miou(
    pred_mask: np.ndarray | None, gt_mask: np.ndarray, num_classes: int = 2
) -> float:
    if pred_mask is None or gt_mask is None:
        return float("nan")

    pred_bin = (pred_mask > 0).astype(np.uint8)
    gt_bin = (gt_mask > 0).astype(np.uint8)
    ious = []

    for cls_id in range(num_classes):
        pred_cls = pred_bin == cls_id
        gt_cls = gt_bin == cls_id
        union = np.logical_or(pred_cls, gt_cls).sum()
        if union == 0:
            continue
        intersection = np.logical_and(pred_cls, gt_cls).sum()
        ious.append(float(intersection) / float(union))

    if not ious:
        return float("nan")
    return float(np.mean(ious))


def compute_average_precision_per_image(
    predictions: list[dict],
    gt_list: list[dict],
    all_classes: list[str],
    iou_threshold: float = 0.5,
) -> dict[str, float]:
    per_class_ap: dict[str, float] = {}

    for cname in all_classes:
        ap_values = []
        for pred, gt in zip(predictions, gt_list):
            p_boxes = np.array(
                [
                    box
                    for box, c in zip(pred["boxes"], pred["class_names"])
                    if c == cname
                ],
                dtype=np.float32,
            )
            g_boxes = np.array(
                [
                    box
                    for box, c in zip(gt["boxes"], gt["class_names"])
                    if c == cname
                ],
                dtype=np.float32,
            )

            if len(g_boxes) == 0 and len(p_boxes) == 0:
                continue
            if len(g_boxes) == 0:
                ap_values.append(0.0)
                continue
            if len(p_boxes) == 0:
                ap_values.append(0.0)
                continue

            tp, _, _ = match_predictions_to_ground_truth(
                p_boxes, g_boxes, iou_threshold=iou_threshold
            )
            ap_values.append(float(tp) / float(len(g_boxes)))

        per_class_ap[cname] = (
            float(np.nanmean(ap_values)) if ap_values else float("nan")
        )

    return per_class_ap
