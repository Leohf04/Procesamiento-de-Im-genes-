"""Train DeepLabV3+ on Cityscapes or BDD100K lane masks."""
import argparse
import json
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import DataLoader
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.models.deeplabv3plus import DeepLabV3Plus
from src.utils.urban_dataset import CityscapesFineDataset, LaneMaskDataset, CITYSCAPES_CLASSES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["cityscapes", "lanes"], default="cityscapes")
    parser.add_argument("--data-root", help="Cityscapes root for cityscapes task")
    parser.add_argument("--images-dir", help="BDD100K images directory for lanes task")
    parser.add_argument("--masks-dir", help="Rasterized BDD100K masks directory for lanes task")
    parser.add_argument("--val-images-dir", help="Independent BDD100K validation images directory")
    parser.add_argument("--val-masks-dir", help="Independent BDD100K validation masks directory")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--output", default="data/processed/deeplabv3plus_urban.pt")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    size = (args.height, args.width)
    if args.task == "cityscapes":
        if not args.data_root:
            parser.error("--data-root es obligatorio para --task cityscapes")
        dataset = CityscapesFineDataset(args.data_root, "train", size)
        validation_dataset = CityscapesFineDataset(args.data_root, "val", size)
        num_classes, class_names = 11, list(CITYSCAPES_CLASSES)
    else:
        if not all([args.images_dir, args.masks_dir, args.val_images_dir, args.val_masks_dir]):
            parser.error("Para --task lanes indica train y validación: --images-dir, --masks-dir, --val-images-dir y --val-masks-dir")
        dataset = LaneMaskDataset(args.images_dir, args.masks_dir, size)
        validation_dataset = LaneMaskDataset(args.val_images_dir, args.val_masks_dir, size)
        num_classes, class_names = 2, ["background", "lane_marking"]
    if len(dataset) < 1 or len(validation_dataset) < 1:
        raise ValueError("Se requiere al menos una imagen en train y validation.")
    train_set, val_set = dataset, validation_dataset
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers, pin_memory=device.type == "cuda")
    val_loader = DataLoader(val_set, batch_size=args.batch_size, shuffle=False,
                            num_workers=args.workers, pin_memory=device.type == "cuda")
    model = DeepLabV3Plus(num_classes, pretrained_backbone=True).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss(ignore_index=255)
    best_iou = -1.0
    history = []
    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        for images, masks in train_loader:
            images, masks = images.to(device), masks.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(images)["out"], masks)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        model.eval()
        intersections = torch.zeros(num_classes, device=device)
        unions = torch.zeros(num_classes, device=device)
        val_loss = 0.0
        with torch.inference_mode():
            for images, masks in val_loader:
                images, masks = images.to(device), masks.to(device)
                logits = model(images)["out"]
                val_loss += criterion(logits, masks).item()
                pred = logits.argmax(1)
                valid = masks != 255
                for class_id in range(num_classes):
                    p, g = (pred == class_id) & valid, (masks == class_id) & valid
                    intersections[class_id] += (p & g).sum()
                    unions[class_id] += (p | g).sum()
        ious = torch.where(unions > 0, intersections / unions.clamp_min(1), torch.nan)
        miou = torch.nanmean(ious).item()
        record = {"epoch": epoch + 1, "train_loss": train_loss / max(1, len(train_loader)),
                  "val_loss": val_loss / max(1, len(val_loader)), "val_miou": miou}
        history.append(record)
        print(json.dumps(record))
        if miou > best_iou:
            best_iou = miou
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            torch.save({"model_state_dict": model.state_dict(), "num_classes": num_classes,
                        "class_names": class_names, "task": args.task, "input_size": size,
                        "seed": args.seed, "epoch": epoch + 1, "val_miou": miou}, output)
    Path(args.output + ".history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(f"Mejor mIoU de validación: {best_iou:.5f}; checkpoint: {args.output}")


if __name__ == "__main__":
    main()
