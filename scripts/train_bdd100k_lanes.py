"""Train a shared-backbone, three-head DeepLabV3 model on BDD100K lane masks."""
import argparse
import json
import os
from pathlib import Path
import sys

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision.models import ResNet50_Weights
from torchvision.models.segmentation import deeplabv3_resnet50

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.utils.bdd100k_dataset import BDD100KLaneDataset

HEADS = {"category": 8, "direction": 2, "style": 2}


def collate_fn(batch):
    images, targets = zip(*batch)
    return torch.stack(images), {key: torch.stack([item[key] for item in targets])
                                 for key in HEADS}


def build_model(pretrained_backbone=True):
    return deeplabv3_resnet50(
        weights=None,
        weights_backbone=ResNet50_Weights.DEFAULT if pretrained_backbone else None,
        num_classes=sum(HEADS.values()),
        aux_loss=False,
    )


def evaluate(model, loader, device):
    model.eval()
    intersections = {key: np.zeros(count, dtype=np.int64) for key, count in HEADS.items()}
    unions = {key: np.zeros(count, dtype=np.int64) for key, count in HEADS.items()}
    offsets = {"category": (0, 8), "direction": (8, 10), "style": (10, 12)}
    with torch.inference_mode():
        for images, targets in loader:
            logits = model(images.to(device))["out"]
            for name, (start, end) in offsets.items():
                prediction = logits[:, start:end].argmax(1).cpu().numpy()
                truth = targets[name].numpy()
                valid = truth != 255
                for class_id in range(end - start):
                    pred_class = (prediction == class_id) & valid
                    true_class = (truth == class_id) & valid
                    intersections[name][class_id] += np.logical_and(pred_class, true_class).sum()
                    unions[name][class_id] += np.logical_or(pred_class, true_class).sum()
    report = {}
    for name, count in HEADS.items():
        ious = [float(intersections[name][i] / unions[name][i])
                for i in range(count) if unions[name][i] > 0]
        report[f"val_{name}_miou"] = float(np.mean(ious)) if ious else None
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-images", required=True)
    parser.add_argument("--train-masks", required=True)
    parser.add_argument("--val-images", required=True)
    parser.add_argument("--val-masks", required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--output", default="data/processed/bdd100k_lanes.pt")
    parser.add_argument("--no-pretrained-backbone", action="store_true")
    parser.add_argument("--resume", nargs="?", const="auto", default=None,
                        help="Resume from --output.last.pt or an explicit checkpoint.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.workers < 0:
        parser.error("--epochs y --batch-size deben ser positivos; --workers no puede ser negativo")
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_data = BDD100KLaneDataset(args.train_images, args.train_masks)
    val_data = BDD100KLaneDataset(args.val_images, args.val_masks)
    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers, collate_fn=collate_fn,
                              pin_memory=device.type == "cuda")
    val_loader = DataLoader(val_data, batch_size=args.batch_size, shuffle=False,
                            num_workers=args.workers, collate_fn=collate_fn,
                            pin_memory=device.type == "cuda")
    output = Path(args.output)
    last_path = Path(str(output) + ".last.pt")
    resume_path = last_path if args.resume == "auto" else Path(args.resume) if args.resume else None
    model = build_model(not args.no_pretrained_backbone and resume_path is None).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=8, gamma=0.5)
    history, start_epoch = [], 0
    if resume_path:
        if not resume_path.is_file():
            raise FileNotFoundError(f"No existe checkpoint para reanudar: {resume_path}")
        checkpoint = torch.load(resume_path, map_location=device, weights_only=False)
        if checkpoint.get("head_classes") != HEADS:
            raise ValueError("El checkpoint no corresponde a las tres subtareas de carriles BDD100K.")
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        start_epoch = int(checkpoint.get("epoch", 0))
        history = checkpoint.get("history", [])
    offsets = {"category": (0, 8), "direction": (8, 10), "style": (10, 12)}
    for epoch in range(start_epoch, args.epochs):
        model.train()
        running = 0.0
        for images, targets in train_loader:
            images = images.to(device)
            targets = {key: value.to(device) for key, value in targets.items()}
            logits = model(images)["out"]
            loss = sum(F.cross_entropy(logits[:, start:end], targets[name],
                                       ignore_index=255)
                       for name, (start, end) in offsets.items())
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            running += float(loss.detach())
        scheduler.step()
        validation = evaluate(model, val_loader, device)
        record = {"epoch": epoch + 1,
                  "train_loss": running / max(1, len(train_loader)),
                  **validation}
        history.append(record)
        print(json.dumps(record), flush=True)
        payload = {"model_state_dict": model.state_dict(),
                   "optimizer_state_dict": optimizer.state_dict(),
                   "scheduler_state_dict": scheduler.state_dict(),
                   "num_classes": 12, "head_classes": HEADS,
                   "epoch": epoch + 1, "seed": args.seed, "history": history}
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        torch.save(payload, temporary)
        os.replace(temporary, output)
        temporary_last = last_path.with_suffix(last_path.suffix + ".tmp")
        torch.save(payload, temporary_last)
        os.replace(temporary_last, last_path)
    print(f"Checkpoint guardado: {output}")
    print(f"Checkpoint reanudable: {last_path}")


if __name__ == "__main__":
    main()
