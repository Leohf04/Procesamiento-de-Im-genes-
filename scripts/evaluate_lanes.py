"""Evaluate learned lane-marking segmentation using binary IoU and F1."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.models.deeplabv3plus import DeepLabV3Plus
from src.utils.urban_dataset import LaneMaskDataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", required=True)
    parser.add_argument("--masks-dir", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", default="data/outputs/lane_metrics.json")
    args = parser.parse_args()
    dataset = LaneMaskDataset(args.images_dir, args.masks_dir)
    loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=2)
    checkpoint = torch.load(args.checkpoint, map_location="cpu")
    model = DeepLabV3Plus(2, pretrained_backbone=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()
    tp = fp = fn = 0
    with torch.inference_mode():
        for images, masks in loader:
            pred = model(images.to(device))["out"].argmax(1).cpu().numpy()[0] == 1
            gt = masks.numpy()[0] == 1
            tp += int(np.logical_and(pred, gt).sum())
            fp += int(np.logical_and(pred, ~gt).sum())
            fn += int(np.logical_and(~pred, gt).sum())
    union = tp + fp + fn
    report = {"task": "bdd100k_lane_marking", "images": len(dataset),
              "iou": float(tp / union) if union else None,
              "f1": float(2 * tp / (2 * tp + fp + fn)) if 2 * tp + fp + fn else None,
              "checkpoint": args.checkpoint}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
