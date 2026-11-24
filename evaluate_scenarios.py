import argparse
import os

import cv2
import numpy as np

from src.evaluation.error_analysis import (
    plot_per_class_ap_comparison,
    plot_scenario_metrics_evolution,
)
from src.evaluation.trainer import ScenarioEvaluator
from src.models.instance_seg import InstanceSegmentationModel
from src.models.semantic_hybrid import SemanticHybridModel
from src.utils.coco_loader import load_coco_val2017_samples
from src.utils.config_utils import load_config, resolve_backend, set_global_seed

SHARED_VOC_LABELS = ["person", "bicycle", "car", "motorcycle", "bus"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluación multi-escenario sobre COCO val2017"
    )
    parser.add_argument("--approach", choices=["instance", "hybrid"], default="instance")
    parser.add_argument("--backend", choices=["auto", "torch", "onnx_cv2"], default="auto")
    parser.add_argument("--config", type=str, default="configs/config.yaml")
    parser.add_argument("--max-samples", type=int, default=200)
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=["clear_day", "night", "rain", "fog", "motion_blur"],
    )
    return parser.parse_args()


def _build_model(approach: str, backend: str, config: dict):
    device = config.get("system", {}).get("device", "auto")
    target_cfg = config.get("target_classes", {})
    allowed_labels = set(target_cfg.get("urban_labels", []))

    if approach == "instance":
        instance_cfg = config["models"]["instance"]
        return InstanceSegmentationModel(
            backend=backend,
            device=device,
            confidence_threshold=instance_cfg.get("confidence_threshold", 0.50),
            mask_threshold=instance_cfg.get("mask_threshold", 0.50),
            allowed_labels=allowed_labels,
            shared_labels=set(SHARED_VOC_LABELS),
            checkpoint_path=instance_cfg.get("urban_checkpoint"),
        )

    if backend == "onnx_cv2":
        # The lightweight fallback is HOG-only; do not construct the neural hybrid model.
        return InstanceSegmentationModel(
            backend="onnx_cv2", device=device,
            confidence_threshold=config["models"]["instance"].get("confidence_threshold", 0.50),
            allowed_labels=allowed_labels,
            shared_labels=set(SHARED_VOC_LABELS),
        )

    hybrid_cfg = config["models"]["semantic_hybrid"]
    return SemanticHybridModel(
        backend=backend,
        device=device,
        confidence_threshold=hybrid_cfg.get(
            "detector_confidence_threshold", 0.50
        ),
        urban_voc_ids=hybrid_cfg.get("deeplab_urban_voc_ids", [2, 6, 7, 14, 15]),
        allowed_labels=allowed_labels,
        lane_params=hybrid_cfg,
        segmentation_checkpoint=hybrid_cfg.get("checkpoint_path"),
        lane_checkpoint=hybrid_cfg.get("lane_checkpoint"),
        num_semantic_classes=hybrid_cfg.get("num_classes", 11),
        input_size=tuple(hybrid_cfg.get("input_size", [512, 1024])),
    )


def main():
    args = parse_args()
    config = load_config(args.config)
    set_global_seed(config.get("system", {}).get("seed", 42))
    backend = resolve_backend(args.backend)

    if backend != "torch":
        print(
            "ADVERTENCIA: backend sin PyTorch. El modo demo solo detecta peatones "
            "con HOG; mAP y mIoU no serán comparables con el benchmark del plan."
        )

    evaluation_cfg = config.get("evaluation", {})
    dataset_cfg = config.get("dataset", {})
    images_dir = dataset_cfg.get("images_dir", "data/coco/val2017")
    annotations_file = dataset_cfg.get(
        "annotations_file", "data/coco/annotations/instances_val2017.json"
    )

    print(f"Cargando hasta {args.max_samples} muestras de COCO val2017...")
    samples = load_coco_val2017_samples(
        images_dir=images_dir,
        annotations_file=annotations_file,
        max_samples=args.max_samples,
        only_urban_images=True,
        shared_mask_labels=set(SHARED_VOC_LABELS),
    )

    loaded_samples = []
    for sample in samples:
        image = cv2.imread(sample["path"])
        if image is None:
            continue
        sample["image"] = image
        loaded_samples.append(sample)

    if not loaded_samples:
        raise RuntimeError(
            "No se cargó ninguna imagen. Verifica el dataset con "
            "python scripts/download_coco_val2017.py"
        )

    model = _build_model(args.approach, backend, config)
    if args.approach == "instance" and getattr(model, "urban_finetuned", False):
        raise RuntimeError("El modelo Mask R-CNN está ajustado a Cityscapes, pero este evaluador usa GT COCO. Usa scripts/evaluate_cityscapes.py para métricas urbanas.")
    evaluator = ScenarioEvaluator(
        model=model,
        config=config,
        conf_threshold=config.get("models", {})
        .get(args.approach if args.approach == "instance" else "semantic_hybrid", {})
        .get(
            "confidence_threshold" if args.approach == "instance" else "detector_confidence_threshold",
            0.50,
        ),
        shared_classes=SHARED_VOC_LABELS,
    )

    print(
        f"Evaluando {len(loaded_samples)} imágenes en {len(args.scenarios)} escenarios "
        f"(backend={backend}, approach={args.approach})..."
    )
    report = evaluator.evaluate(loaded_samples, args.scenarios)

    output_dir = evaluation_cfg.get("output_dir", "data/outputs")
    report_path = evaluator.export_report(report, output_dir)

    print("\nResultados por escenario")
    print(
        f"{'Escenario':<14}{'mAP@0.5':>10}{'mIoU':>10}"
        f"{'Precision':>12}{'Recall':>10}{'FPS':>10}"
    )
    for scenario, metrics in report.items():
        miou = metrics["mIoU"]
        miou_str = "nan" if np.isnan(miou) else f"{miou:.3f}"
        print(
            f"{scenario:<14}{metrics['mAP50']:>10.3f}{miou_str:>10}"
            f"{metrics['precision']:>12.3f}{metrics['recall']:>10.3f}"
            f"{metrics['fps']:>10.2f}"
        )

    plot_path = plot_scenario_metrics_evolution(report, output_dir)
    ap_plot_path = plot_per_class_ap_comparison(report, output_dir)

    print(f"\nReporte JSON: {report_path}")
    print(f"Gráfico de escenarios: {plot_path}")
    print(f"Gráfico AP por clase: {ap_plot_path}")


if __name__ == "__main__":
    main()
