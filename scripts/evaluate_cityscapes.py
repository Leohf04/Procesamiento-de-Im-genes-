"""Evaluate Cityscapes validation: semantic mIoU or Mask R-CNN box AP@0.5."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
import torch
from torch.utils.data import DataLoader
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.models.deeplabv3plus import DeepLabV3Plus
from src.models.instance_seg import InstanceSegmentationModel
from src.utils.urban_dataset import CityscapesFineDataset, CITYSCAPES_CLASSES
from src.utils.bdd100k_dataset import BDD100KSemanticDataset, BDD100K_SEMANTIC_CLASSES
from src.utils.cityscapes_instance_dataset import CityscapesInstanceDataset
from src.evaluation.metrics import compute_average_precision_per_image


INSTANCE_NAMES = ["background", "person", "rider", "car", "truck", "bus", "motorcycle", "bicycle"]


def evaluate_semantic(root, checkpoint_path, output_path):
    dataset = CityscapesFineDataset(root, "val")
    loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=2)
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    model = DeepLabV3Plus(11, pretrained_backbone=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()
    intersections = np.zeros(11, np.int64)
    unions = np.zeros(11, np.int64)
    with torch.inference_mode():
        for images, masks in loader:
            pred = model(images.to(device))["out"].argmax(1).cpu().numpy()[0]
            gt = masks.numpy()[0]
            valid = gt != 255
            for class_id in range(11):
                p, g = (pred == class_id) & valid, (gt == class_id) & valid
                intersections[class_id] += np.logical_and(p, g).sum()
                unions[class_id] += np.logical_or(p, g).sum()
    per_class = {name: (float(intersections[i] / unions[i]) if unions[i] else None)
                 for i, name in enumerate(CITYSCAPES_CLASSES)}
    valid_ious = [v for v in per_class.values() if v is not None]
    report = {"task": "cityscapes_semantic", "images": len(dataset),
              "per_class_iou": per_class, "miou": float(np.mean(valid_ious)) if valid_ious else None,
              "checkpoint": str(checkpoint_path), "split": "val"}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


def evaluate_bdd100k_semantic(images_dir, masks_dir, checkpoint_path, output_path):
    dataset = BDD100KSemanticDataset(images_dir, masks_dir)
    loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=2)
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    if checkpoint.get("num_classes") != 19:
        raise ValueError("El checkpoint no contiene las 19 clases semánticas BDD100K.")
    model = DeepLabV3Plus(19, pretrained_backbone=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()
    intersections = np.zeros(19, np.int64)
    unions = np.zeros(19, np.int64)
    with torch.inference_mode():
        for images, masks in loader:
            pred = model(images.to(device))["out"].argmax(1).cpu().numpy()[0]
            gt = masks.numpy()[0]
            valid = gt != 255
            for class_id in range(19):
                p, g = (pred == class_id) & valid, (gt == class_id) & valid
                intersections[class_id] += np.logical_and(p, g).sum()
                unions[class_id] += np.logical_or(p, g).sum()
    per_class = {name: (float(intersections[i] / unions[i]) if unions[i] else None)
                 for i, name in enumerate(BDD100K_SEMANTIC_CLASSES)}
    valid_ious = [v for v in per_class.values() if v is not None]
    report = {"task": "bdd100k_semantic", "images": len(dataset),
              "per_class_iou": per_class, "miou": float(np.mean(valid_ious)) if valid_ious else None,
              "checkpoint": str(checkpoint_path), "split": "val"}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


def evaluate_instances(root, checkpoint_path, output_path):
    if not Path(checkpoint_path).is_file():
        raise FileNotFoundError(f"No existe el checkpoint urbano Mask R-CNN: {checkpoint_path}")
    dataset = CityscapesInstanceDataset(root, "val")
    model = InstanceSegmentationModel(backend="torch", device="auto",
                                      confidence_threshold=0.0, checkpoint_path=checkpoint_path)
    if not model.urban_finetuned:
        raise RuntimeError("Se requiere un checkpoint Mask R-CNN fine-tuned en Cityscapes; no se evaluarán pesos COCO contra GT Cityscapes.")
    predictions, ground_truth = [], []
    for index in range(len(dataset)):
        image_tensor, target = dataset[index]
        rgb = (image_tensor.permute(1, 2, 0).numpy() * 255).clip(0, 255).astype(np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        pred = model.predict(bgr)
        predictions.append({"boxes": pred["boxes"], "class_names": pred["class_names"], "scores": pred["scores"]})
        labels = [INSTANCE_NAMES[int(i)] for i in target["labels"].tolist()]
        ground_truth.append({"boxes": target["boxes"].numpy(), "class_names": labels})
    classes = INSTANCE_NAMES[1:]
    per_class = compute_average_precision_per_image(predictions, ground_truth, classes, 0.5)
    valid = [v for v in per_class.values() if np.isfinite(v)]
    report = {"task": "cityscapes_instance_box_ap", "images": len(dataset),
              "iou_threshold": 0.5, "per_class_ap50": per_class,
              "map50": float(np.mean(valid)) if valid else None,
              "metric_note": "AP de cajas estilo VOC; no es AP de máscaras de instancias.",
              "checkpoint": str(checkpoint_path), "split": "val"}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["semantic", "bdd100k-semantic", "instance"], required=True)
    parser.add_argument("--data-root")
    parser.add_argument("--images-dir", help="BDD100K validation images")
    parser.add_argument("--masks-dir", help="BDD100K validation semantic masks")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", default="data/outputs/cityscapes_metrics.json")
    args = parser.parse_args()
    if args.task == "semantic":
        if not args.data_root:
            parser.error("--data-root es obligatorio para Cityscapes semantic")
        evaluate_semantic(args.data_root, args.checkpoint, args.output)
    elif args.task == "bdd100k-semantic":
        if not args.images_dir or not args.masks_dir:
            parser.error("BDD100K semantic requiere --images-dir y --masks-dir")
        evaluate_bdd100k_semantic(args.images_dir, args.masks_dir, args.checkpoint, args.output)
    else:
        if not args.data_root:
            parser.error("--data-root es obligatorio para Cityscapes instance")
        evaluate_instances(args.data_root, args.checkpoint, args.output)


if __name__ == "__main__":
    main()
