import os
import time

import numpy as np

from src.evaluation.metrics import compute_average_precision_per_image, compute_semantic_miou, match_predictions_to_ground_truth
from src.preprocessing.atmospheric import apply_motion_blur, apply_synthetic_fog, apply_synthetic_rain
from src.preprocessing.illumination import apply_gamma_correction, enhance_low_light_clahe


class ScenarioEvaluator:
    def __init__(self, model, config: dict, conf_threshold: float = 0.5, shared_classes: list[str] | None = None):
        self.model, self.config, self.conf_threshold = model, config, conf_threshold
        self.shared_classes = shared_classes or ["person", "bicycle", "car", "motorcycle", "bus"]

    def apply_scenario(self, image: np.ndarray, scenario_name: str) -> np.ndarray:
        cfg = self.config.get("preprocessing", {})
        if scenario_name == "clear_day": return image.copy()
        if scenario_name == "night": return enhance_low_light_clahe(apply_gamma_correction(image, cfg.get("gamma_night", 0.45)))
        if scenario_name == "rain": return apply_synthetic_rain(image, drop_count=cfg.get("rain_drop_count", 600), drop_length=cfg.get("rain_drop_length", 18), slant=cfg.get("rain_slant", -10))
        if scenario_name == "fog": return apply_synthetic_fog(image, beta=cfg.get("fog_beta", 0.045), atmospheric_light=cfg.get("fog_atmospheric_light", 225.0))
        if scenario_name == "motion_blur": return apply_motion_blur(image, kernel_size=cfg.get("motion_blur_kernel", 15), angle=cfg.get("motion_blur_angle", 12.0))
        raise ValueError(f"Escenario desconocido: {scenario_name}")

    def evaluate(self, samples: list[dict], scenarios: list[str]) -> dict:
        cfg = self.config.get("evaluation", {})
        threshold = float(cfg.get("iou_threshold", 0.5))
        classes = sorted({c for sample in samples for c in sample["gt_labels"]}) or list(self.shared_classes)
        report = {}
        for scenario in scenarios:
            preds, gts, latencies, miou_values = [], [], [], []
            total_tp = total_fp = total_fn = 0
            for sample in samples:
                image = self.apply_scenario(sample["image"], scenario)
                start = time.perf_counter()
                prediction = self.model.predict(image)
                latencies.append((time.perf_counter() - start) * 1000.0)
                scores = np.asarray(prediction.get("scores", []), dtype=float)
                names = list(prediction.get("class_names", []))
                boxes = np.asarray(prediction.get("boxes", []), dtype=np.float32).reshape(-1, 4)
                keep = [i for i, score in enumerate(scores) if score >= self.conf_threshold]
                pboxes = boxes[keep] if len(boxes) else np.zeros((0, 4), dtype=np.float32)
                pnames = [names[i] for i in keep]
                pscores = [float(scores[i]) for i in keep]
                tp, fn, fp = match_predictions_to_ground_truth(pboxes, sample["gt_boxes"], threshold, pnames, sample["gt_labels"])
                total_tp += tp; total_fn += fn; total_fp += fp
                preds.append({"boxes": pboxes, "class_names": pnames, "scores": pscores})
                gts.append({"boxes": sample["gt_boxes"], "class_names": sample["gt_labels"]})
                pred_mask = prediction.get("urban_semantic_mask")
                gt_mask = sample.get("gt_semantic_mask")
                if pred_mask is not None and gt_mask is not None:
                    miou_values.append(compute_semantic_miou(pred_mask, gt_mask))
            per_class_ap = compute_average_precision_per_image(preds, gts, classes, threshold)
            valid = [v for v in per_class_ap.values() if np.isfinite(v)]
            mean_latency = float(np.mean(latencies)) if latencies else float("nan")
            report[scenario] = {
                "mAP50": float(np.mean(valid)) if valid else float("nan"),
                "mIoU": float(np.nanmean(miou_values)) if miou_values else float("nan"),
                "precision": total_tp / (total_tp + total_fp) if total_tp + total_fp else 0.0,
                "recall": total_tp / (total_tp + total_fn) if total_tp + total_fn else 0.0,
                "mean_latency_ms": mean_latency,
                "fps": 1000.0 / mean_latency if mean_latency > 0 else 0.0,
                "per_class_ap": per_class_ap,
                "evaluated_images": len(samples),
                "evaluation_note": "AP@0.5 por clase con ranking global por confianza; condiciones sintéticas si el escenario no es clear_day."
            }
        return report

    def export_report(self, report: dict, output_dir: str) -> str:
        import json
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, "evaluation_report.json")
        def clean(value):
            if isinstance(value, dict): return {k: clean(v) for k, v in value.items()}
            if isinstance(value, list): return [clean(v) for v in value]
            if isinstance(value, (float, np.floating)) and not np.isfinite(value): return None
            if isinstance(value, np.generic): return value.item()
            return value
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(clean(report), stream, indent=2, ensure_ascii=False)
        return path
