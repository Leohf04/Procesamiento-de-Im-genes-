"""Fine-tune COCO-pretrained Mask R-CNN on Cityscapes instance annotations."""
import argparse
import json
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from torchvision.models.detection import maskrcnn_resnet50_fpn_v2, MaskRCNN_ResNet50_FPN_V2_Weights
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from src.utils.cityscapes_instance_dataset import CityscapesInstanceDataset


def collate_fn(batch):
    return tuple(zip(*batch))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--lr", type=float, default=0.002)
    parser.add_argument("--output", default="data/processed/maskrcnn_cityscapes.pt")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_data = CityscapesInstanceDataset(args.data_root, "train")
    val_data = CityscapesInstanceDataset(args.data_root, "val")
    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers, collate_fn=collate_fn,
                              pin_memory=device.type == "cuda")
    model = maskrcnn_resnet50_fpn_v2(weights=MaskRCNN_ResNet50_FPN_V2_Weights.DEFAULT)
    num_classes = 8  # background + person, rider, car, truck, bus, motorcycle, bicycle
    box_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(box_features, num_classes)
    mask_features = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(mask_features, 256, num_classes)
    model.to(device)
    optimizer = torch.optim.SGD([p for p in model.parameters() if p.requires_grad],
                                lr=args.lr, momentum=0.9, weight_decay=0.0005)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
    history = []
    for epoch in range(args.epochs):
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
                  "validation_images": len(val_data), "note": "Validation split is kept separate for scripts/evaluate_cityscapes.py; no val loss computed here."}
        history.append(record)
        print(json.dumps(record))
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"model_state_dict": model.state_dict(), "num_classes": num_classes,
                    "class_names": ["background", "person", "rider", "car", "truck", "bus", "motorcycle", "bicycle"],
                    "epoch": epoch + 1, "seed": args.seed}, output)
    Path(args.output + ".history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(f"Checkpoint guardado: {args.output}")


if __name__ == "__main__":
    main()
