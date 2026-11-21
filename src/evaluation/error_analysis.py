import os

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from src.evaluation.metrics import compute_box_iou  # noqa: E402


def save_confusion_matrix(
    confusion_matrix: np.ndarray, class_names: list[str], output_dir: str
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "confusion_matrix.png")

    plt.figure(figsize=(9, 7))
    plt.imshow(confusion_matrix, interpolation="nearest", cmap="Blues")
    plt.title("Matriz de confusión: clasificador fino SVM")
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45, ha="right")
    plt.yticks(tick_marks, class_names)

    threshold = confusion_matrix.max() / 2.0 if confusion_matrix.size else 0
    for i in range(confusion_matrix.shape[0]):
        for j in range(confusion_matrix.shape[1]):
            plt.text(
                j,
                i,
                str(int(confusion_matrix[i, j])),
                horizontalalignment="center",
                color="white" if confusion_matrix[i, j] > threshold else "black",
            )

    plt.ylabel("Clase real")
    plt.xlabel("Clase predicha")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_scenario_metrics_evolution(report: dict, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "scenario_metrics_evolution.png")

    scenarios = list(report.keys())
    map_values = [report[s]["mAP50"] for s in scenarios]
    miou_values = [report[s]["mIoU"] for s in scenarios]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    x_positions = np.arange(len(scenarios))
    width = 0.36

    bars_map = ax1.bar(
        x_positions - width / 2, map_values, width, label="mAP@0.5", color="#2E86C1"
    )
    bars_miou = ax1.bar(
        x_positions + width / 2, miou_values, width, label="mIoU", color="#28B463"
    )

    for bar in bars_map:
        bar_h = float(bar.get_height())
        if not np.isnan(bar_h):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar_h,
                f"{bar_h:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
    for bar in bars_miou:
        bar_h = float(bar.get_height())
        if not np.isnan(bar_h):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar_h,
                f"{bar_h:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax1.set_title("Degradación de métricas por escenario adverso")
    ax1.set_xlabel("Escenario")
    ax1.set_ylabel("Métrica")
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(scenarios, rotation=15)
    ax1.set_ylim(0.0, 1.0)
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_per_class_ap_comparison(report: dict, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "per_class_ap_comparison.png")

    class_names = sorted(
        {cname for metrics in report.values() for cname in metrics["per_class_ap"]}
    )
    scenarios = list(report.keys())
    x_positions = np.arange(len(class_names))
    bar_width = 0.8 / max(1, len(scenarios))

    plt.figure(figsize=(11, 5.5))
    for idx, scenario in enumerate(scenarios):
        ap_values = [
            report[scenario]["per_class_ap"].get(cname, float("nan"))
            for cname in class_names
        ]
        plt.bar(
            x_positions + idx * bar_width,
            ap_values,
            bar_width,
            label=scenario,
        )

    plt.title("AP@0.5 por clase en cada escenario")
    plt.xlabel("Clase")
    plt.ylabel("AP@0.5")
    plt.xticks(x_positions + bar_width * (len(scenarios) - 1) / 2, class_names)
    plt.ylim(0.0, 1.0)
    plt.legend(fontsize=8)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def save_failure_case(
    image_bgr: np.ndarray,
    gt_boxes: np.ndarray,
    pred_boxes: np.ndarray,
    pred_scores: np.ndarray,
    output_path: str,
    iou_threshold: float = 0.5,
) -> str:
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    canvas = image_bgr.copy()
    for x1, y1, x2, y2 in gt_boxes:
        cv2.rectangle(
            canvas,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            (0, 255, 0),
            2,
        )

    for pred_box, pred_score in zip(pred_boxes, pred_scores):
        best_iou = 0.0
        for gt_box in gt_boxes:
            best_iou = max(best_iou, compute_box_iou(pred_box, gt_box))
        color = (0, 165, 255) if best_iou >= iou_threshold else (0, 0, 255)
        x1, y1, x2, y2 = map(int, pred_box)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            canvas,
            f"{float(pred_score):.2f} IoU {best_iou:.2f}",
            (x1, max(y1 - 6, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
        )

    cv2.imwrite(output_path, canvas)
    return output_path
