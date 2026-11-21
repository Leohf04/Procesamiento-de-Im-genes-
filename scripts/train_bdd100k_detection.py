"""Train a 10-class Faster R-CNN detector on BDD100K det_20 labels."""
import argparse
import json
import os
from pathlib import Path
import sys

import torch
from torch.utils.data import DataLoader
from torchvision.models.detection import fasterrcnn_resnet50_fpn, FasterRCNN_ResNet50_FPN_Weights
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.utils.bdd100k_dataset import BDD100KDetectionDataset, BDD100K_DETECTION_CLASSES
from src.evaluation.metrics import compute_average_precision_per_image


def collate_fn(batch):
    return tuple(zip(*batch))


def atomic_save(payload, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def build_model(num_classes):
    model = fasterrcnn_resnet50_fpn(
        weights=FasterRCNN_ResNet50_FPN_Weights.DEFAULT,
        weights_backbone=None,
    )
    features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(features, num_classes)
    return model


def evaluate(model, loader, device):
    model.eval()
    predictions, ground_truth = [], []
    names = ["background", *BDD100K_DETECTION_CLASSES]
    with torch.inference_mode():
        for images, targets in loader:
            outputs = model([image.to(device) for image in images])
            for output, target in zip(outputs, targets):
                labels = output["labels"].cpu().numpy().astype(int)
                keep = (labels > 0) & (labels < len(names))
                labels = labels[keep]
                predictions.append({
                    "boxes": output["boxes"].cpu().numpy()[keep],
                    "scores": output["scores"].cpu().numpy()[keep],
                    "class_names": [names[label] for label in labels],
                })
                gt_labels = target["labels"].numpy().astype(int)
                ground_truth.append({
                    "boxes": target["boxes"].numpy(),
                    "class_names": [names[label] for label in gt_labels],
                })
    per_class = compute_average_precision_per_image(
        predictions, ground_truth, BDD100K_DETECTION_CLASSES, 0.5
    )
    valid = [value for value in per_class.values() if value == value]
    return {"val_box_ap50": per_class,
            "val_map50": float(sum(valid) / len(valid)) if valid else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-images", required=True)
    parser.add_argument("--train-labels", required=True)
    parser.add_argument("--val-images", required=True)
    parser.add_argument("--val-labels", required=True)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=0.005)
    parser.add_argument("--output", default="data/processed/bdd100k_fasterrcnn.pt")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.workers < 0:
        parser.error("--epochs y --batch-size deben ser positivos; --workers no puede ser negativo")
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_data = BDD100KDetectionDataset(args.train_images, args.train_labels)
    val_data = BDD100KDetectionDataset(args.val_images, args.val_labels)
    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers, collate_fn=collate_fn,
                              pin_memory=device.type == "cuda")
    val_loader = DataLoader(val_data, batch_size=args.batch_size, shuffle=False,
                            num_workers=args.workers, collate_fn=collate_fn,
                            pin_memory=device.type == "cuda")
    model = build_model(len(BDD100K_DETECTION_CLASSES) + 1).to(device)
    optimizer = torch.optim.SGD([p for p in model.parameters() if p.requires_grad],
                                lr=args.lr, momentum=0.9, weight_decay=0.0005)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
    history = []
    output = Path(args.output)
    last_path = Path(str(output) + ".last.pt")

    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        for images, targets in train_loader:
            images = [image.to(device) for image in images]
            targets = [{key: value.to(device) for key, value in target.items()}
                       for target in targets]
            losses = model(images, targets)
            loss = sum(losses.values())
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            running_loss += float(loss.detach())
        scheduler.step()
        validation = evaluate(model, val_loader, device)
        record = {"epoch": epoch + 1,
                  "train_loss": running_loss / max(1, len(train_loader)),
                  **validation}
        history.append(record)
        print(json.dumps(record), flush=True)
        payload = {"model_state_dict": model.state_dict(),
                   "optimizer_state_dict": optimizer.state_dict(),
                   "scheduler_state_dict": scheduler.state_dict(),
                   "num_classes": len(BDD100K_DETECTION_CLASSES) + 1,
                   "class_names": ["background", *BDD100K_DETECTION_CLASSES],
                   "epoch": epoch + 1, "seed": args.seed, "history": history}
        atomic_save(payload, last_path)
        atomic_save(payload, output)
        Path(str(output) + ".history.json").write_text(
            json.dumps(history, indent=2), encoding="utf-8")
    print(f"Checkpoint guardado: {output}")
    print(f"Checkpoint reanudable: {last_path}")


if __name__ == "__main__":
    main()
