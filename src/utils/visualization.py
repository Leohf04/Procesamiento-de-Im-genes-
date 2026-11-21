import cv2
import numpy as np


def render_predictions(image_bgr: np.ndarray, predictions: dict, fps: float) -> np.ndarray:
    canvas = image_bgr.copy()
    rng = np.random.default_rng(123)

    if predictions.get("urban_semantic_mask") is not None:
        sem_mask = predictions["urban_semantic_mask"]
        overlay = np.zeros_like(canvas)
        overlay[sem_mask > 0] = (255, 140, 0)
        canvas = cv2.addWeighted(canvas, 0.78, overlay, 0.22, 0)

    if predictions.get("lane_mask") is not None:
        lane_mask = predictions["lane_mask"]
        canvas[lane_mask > 0] = (0, 255, 255)

    if predictions.get("instance_masks") is not None:
        for mask in predictions["instance_masks"]:
            color = rng.integers(60, 255, size=3).tolist()
            colored = np.zeros_like(canvas)
            colored[mask > 0] = color
            canvas = cv2.addWeighted(canvas, 1.0, colored, 0.42, 0)

    boxes = predictions.get("boxes", [])
    names = predictions.get("fine_labels", predictions.get("class_names", []))
    scores = predictions.get("scores", [])

    for box, name, score in zip(boxes, names, scores):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 220, 0), 2)
        caption = f"{name} ({score:.2f})"
        cv2.putText(
            canvas,
            caption,
            (x1, max(y1 - 8, 15)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2,
        )

    cv2.putText(
        canvas,
        f"FPS: {fps:.2f}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 255),
        2,
    )
    return canvas
