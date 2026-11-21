"""Fine-tune COCO-pretrained Mask R-CNN on Cityscapes or BDD100K instances."""
import argparse
import json
import os
from pathlib import Path
import sys

import torch
from torch.utils.data import DataLoader
from torchvision.models.detection import maskrcnn_resnet50_fpn_v2, MaskRCNN_ResNet50_FPN_V2_Weights
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.utils.cityscapes_instance_dataset import CityscapesInstanceDataset
from src.utils.bdd100k_dataset import BDD100KInstanceDataset, BDD100K_INSTANCE_CLASSES


CLASS_NAMES = ["background", "person", "rider", "car", "truck", "bus", "motorcycle", "bicycle"]


def collate_fn(batch):
    return tuple(zip(*batch))


def atomic_save(payload, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, destination)


def build_model(pretrained, num_classes=None):
    model = maskrcnn_resnet50_fpn_v2(
        weights=MaskRCNN_ResNet50_FPN_V2_Weights.DEFAULT if pretrained else None,
        weights_backbone=None if not pretrained else None,
    )
    num_classes = num_classes or len(CLASS_NAMES)
    box_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(box_features, num_classes)
    mask_features = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(mask_features, 256, num_classes)
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["cityscapes", "bdd100k"], default="bdd100k")
    parser.add_argument("--data-root", help="Cityscapes root")
    parser.add_argument("--images-dir", help="BDD100K 10K images split")
    parser.add_argument("--bitmasks-dir", help="BDD100K RGBA instance bitmasks split")
    parser.add_argument("--val-images-dir", help="BDD100K validation images")
    parser.add_argument("--val-bitmasks-dir", help="BDD100K validation RGBA bitmasks")
    parser.add_argument("--epochs", type=int, default=20, help="Total target epochs, not additional epochs")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=0.002)
    parser.add_argument("--output", default="data/processed/maskrcnn_bdd100k.pt")
    parser.add_argument("--resume", nargs="?", const="auto", default=None,
                        help="Resume from --output.last.pt, or provide a checkpoint path")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if args.dataset == "cityscapes":
        if not args.data_root:
            parser.error("--data-root es obligatorio para Cityscapes")
        train_data = CityscapesInstanceDataset(args.data_root, "train")
        val_data = CityscapesInstanceDataset(args.data_root, "val")
        class_names = CLASS_NAMES
    else:
        if not all([args.images_dir, args.bitmasks_dir, args.val_images_dir, args.val_bitmasks_dir]):
            parser.error("BDD100K requiere --images-dir, --bitmasks-dir, --val-images-dir y --val-bitmasks-dir")
        train_data = BDD100KInstanceDataset(args.images_dir, args.bitmasks_dir)
        val_data = BDD100KInstanceDataset(args.val_images_dir, args.val_bitmasks_dir)
        class_names = ["background", *BDD100K_INSTANCE_CLASSES]
    num_classes = len(class_names)
    if len(train_data) == 0 or len(val_data) == 0:
        raise ValueError("El dataset seleccionado debe contener imágenes y bitmasks/etiquetas en train y val.")

    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers, collate_fn=collate_fn,
                              pin_memory=device.type == "cuda")
    output = Path(args.output)
    last_path = Path(str(output) + ".last.pt")
    resume_path = last_path if args.resume == "auto" else Path(args.resume) if args.resume else None

    model = build_model(pretrained=resume_path is None, num_classes=num_classes).to(device)
    optimizer = torch.optim.SGD([p for p in model.parameters() if p.requires_grad],
                                lr=args.lr, momentum=0.9, weight_decay=0.0005)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
    start_epoch, history = 0, []

    if resume_path:
        if not resume_path.is_file():
            raise FileNotFoundError(f"No existe checkpoint para reanudar: {resume_path}")
        checkpoint = torch.load(resume_path, map_location=device, weights_only=False)
        if checkpoint.get("num_classes") != num_classes:
            raise ValueError("El checkpoint no tiene las 8 clases de Mask R-CNN esperadas.")
        if "optimizer_state_dict" not in checkpoint or "scheduler_state_dict" not in checkpoint:
            raise ValueError("Checkpoint antiguo sin estado del optimizador/scheduler; no permite reanudación exacta.")
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        start_epoch = int(checkpoint.get("epoch", 0))
        history = checkpoint.get("history", [])
        print(f"Reanudando desde época {start_epoch}")

    for epoch in range(start_epoch, args.epochs):
        model.train()
        running = 0.0
        for images, targets in train_loader:
            images = [image.to(device) for image in images]
            targets = [{k: v.to(device) for k, v in target.items()} for target in targets]
            losses = model(images, targets)
            loss = sum(losses.values())
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            running += float(loss.detach())
        scheduler.step()
        record = {"epoch": epoch + 1, "train_loss": running / max(1, len(train_loader)),
                  "validation_images": len(val_data),
                  "note": "Validation split remains separate for scripts/evaluate_cityscapes.py; this trainer does not calculate validation loss."}
        history.append(record)
        print(json.dumps(record), flush=True)

        atomic_save({"model_state_dict": model.state_dict(),
                     "optimizer_state_dict": optimizer.state_dict(),
                     "scheduler_state_dict": scheduler.state_dict(),
                     "num_classes": num_classes, "class_names": class_names,
                     "epoch": epoch + 1, "seed": args.seed, "history": history}, last_path)
        # Keep the public checkpoint path usable by the existing evaluation/inference scripts.
        atomic_save({"model_state_dict": model.state_dict(),
                     "num_classes": num_classes, "class_names": class_names,
                     "epoch": epoch + 1, "seed": args.seed}, output)
        Path(str(output) + ".history.json").write_text(
            json.dumps(history, indent=2), encoding="utf-8")

    print(f"Checkpoint guardado: {output}")
    print(f"Checkpoint reanudable: {last_path}")


if __name__ == "__main__":
    main()
