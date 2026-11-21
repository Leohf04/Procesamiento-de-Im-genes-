import os
import time

import numpy as np

from src.evaluation.metrics import (
    compute_average_precision_per_image,
    compute_semantic_miou,
    match_predictions_to_ground_truth,
)
from src.preprocessing.atmospheric import (
    apply_motion_blur,
    apply_synthetic_fog,
    apply_synthetic_rain,
)
from src.preprocessing.illumination import (
    adjust_exposure,
    apply_gamma_correction,
    enhance_low_light_clahe,
)


class ScenarioEvaluator:
    def __init__(
        self,
        model,
        config: dict,
        conf_threshold: float = 0.5,
        shared_classes: list[str] | None = None,
    ):
        self.model = model
        self.config = config
        self.conf_threshold = conf_threshold
        self.shared_classes = shared_classes or [
            "person",
            "bicycle",
            "car",
            "motorcycle",
            "bus",
        ]

    def apply_scenario(self, image: np.ndarray, scenario_name: str) -> np.ndarray:
        # No aplicar filtros a la máscara GT, solo a la imagen RGB
        pre_cfg = self.config.get("preprocessing", {})
        if scenario_name == "clear_day":
            return image.copy()
        if scenario_name == "night":
            dark = apply_gamma_correction(image, pre_cfg.get("gamma_night", 0.45))
            return enhance_low_light_clahe(dark)
        if scenario_name == "rain":
            return apply_synthetic_rain(
                image,
                drop_count=pre_cfg.get("rain_drop_count", 600),
                drop_length=pre_cfg.get("rain_drop_length", 18),
                slant=pre_cfg.get("rain_slant", -10),
            )
        if scenario_name == "fog":
            return apply_synthetic_fog(
                image,
                beta=pre_cfg.get("fog_beta", 0.045),
                atmospheric_light=pre_cfg.get("fog_atmospheric_light", 225.0),
            )
        if scenario_name == "motion_blur":
            return apply_motion_blur(
                image,
                kernel_size=pre_cfg.get("motion_blur_kernel", 15),
                angle=pre_cfg.get("motion_blur_angle", 12.0),
            )
        return image.copy()

    def evaluate(self, samples: list[dict], scenarios: list[str]) -> dict:
        iou_threshold = self.config.get("evaluation", {}).get("iou_threshold", 0.5)
        all_class_names = sorted(
            {
                cname
                for sample in samples
                for cname in sample["gt_labels"]
            }
        )
        if not all_class_names:
            all_class_names = list(self.shared_classes)

        report: dict[str, dict] = {}

        for scenario in scenarios:
            preds_for_ap: list[dict] = []
            gts_for_ap: list[dict] = []

            total_images = 0
            total_tp = 0
            total_fp = 0
            total_fn = 0
            miou_values: list[float] = []
            latencies_ms: list[float] = []

            for sample in samples:
                image = self.apply_scenario(sample["image"], scenario)
                start = time.perf_counter()
                prediction = self.model.predict(image)
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                latencies_ms.append(elapsed_ms)

                keep_idx = [
                    i
                    for i, sc in enumerate(prediction["scores"])
                    if float(sc) >= self.conf_threshold
                ]
                gt_boxes = sample["gt_boxes"]
                pred_boxes = (
                    np.asarray(prediction["boxes"])[keep_idx]
                    if prediction.get("boxes") is not None
                    else np.zeros((0, 4), dtype=np.float32)
                )
                tp, fn, fp = match_predictions_to_ground_truth(
                    pred_boxes, gt_boxes, iou_threshold=iou_threshold
                )
                total_tp += tp
                total_fp += fp
                total_fn += fn
                total_images += 1

                if prediction.get("urban_semantic_mask") is not None:
                    miou_values.append(
                        compute_semantic_miou(
                            prediction["urban_semantic_mask"],
                            sample["gt_semantic_mask"],
                            num_classes=2,
                        )
                    )

                preds_for_ap.append(
                    {
                        "boxes": [
                            prediction["boxes"][i] for i in keep_idx
                        ],
                        "class_names": [
                            prediction["class_names"][i] for i in keep_idx
                        ],
                    }
                )
                gts_for_ap.append(
                    {
                        "boxes": [b for b in sample["gt_boxes"]],
                        "class_names": list(sample["gt_labels"]),
                    }
                )

            per_class_ap = compute_average_precision_per_image(
                preds_for_ap, gts_for_ap, all_class_names, iou_threshold=iou_threshold
            )
            valid_aps = [
                v for v in per_class_ap.values() if not np.isnan(v)
            ]

            mean_latency = (
                float(np.mean(latencies_ms)) if latencies_ms else float("nan")
            )
            report[scenario] = {
                "mAP50": float(np.mean(valid_aps)) if valid_aps else 0.0,
                "mIoU": (
                    float(np.nanmean(miou_values)) if miou_values else float("nan")
                ),
                "precision": (
                    total_tp / (total_tp + total_fp)
                    if (total_tp + total_fp) > 0
                    else 0.0
                ),
                "recall": (
                    total_tp / (total_tp + total_fn)
                    if (total_tp + total_fn) > 0
                    else 0.0
                ),
                "mean_latency_ms": mean_latency,
                "fps": (1000.0 / mean_latency if mean_latency > 0 else 0.0),
                "per_class_ap": per_class_ap,
                "evaluated_images": total_images,
            }

        return report

    def export_report(self, report: dict, output_dir: str) -> str:
        import json

        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, "evaluation_report.json")

        def convert_nan(value):
            if isinstance(value, float) and np.isnan(value):
                return None
            return value

        cleaned = {
            scenario: {
                key: (
                    {k: convert_nan(v) for k, v in val.items()}
                    if isinstance(val, dict)
                    else convert_nan(val)
                )
                for key, val in scenario_metrics.items()
            }
            for scenario, scenario_metrics in report.items()
        }

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False)
        return save_path
