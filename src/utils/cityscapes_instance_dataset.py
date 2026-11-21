"""Cityscapes instance masks for urban Mask R-CNN fine-tuning."""
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset

CITYSCAPES_INSTANCE_IDS = {24: 1, 25: 2, 26: 3, 27: 4, 28: 5, 32: 6, 33: 7}


class CityscapesInstanceDataset(Dataset):
    def __init__(self, root, split="train", size=(512, 1024)):
        self.root, self.split, self.size = Path(root), split, size
        self.images = sorted((self.root / "leftImg8bit" / split).glob("*/*_leftImg8bit.png"))
        if not self.images:
            raise FileNotFoundError(f"No se encontraron imágenes en {self.root}/leftImg8bit/{split}")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        image_path = self.images[index]
        city = image_path.parent.name
        stem = image_path.name.replace("_leftImg8bit.png", "")
        label_path = self.root / "gtFine" / self.split / city / f"{stem}_gtFine_labelIds.png"
        instance_path = self.root / "gtFine" / self.split / city / f"{stem}_gtFine_instanceIds.png"
        if not label_path.is_file() or not instance_path.is_file():
            raise FileNotFoundError(f"Faltan anotaciones GT Fine para {stem}")
        image = Image.open(image_path).convert("RGB").resize((self.size[1], self.size[0]), Image.Resampling.BILINEAR)
        label_ids = np.asarray(Image.open(label_path).resize((self.size[1], self.size[0]), Image.Resampling.NEAREST))
        instance_ids = np.asarray(Image.open(instance_path).resize((self.size[1], self.size[0]), Image.Resampling.NEAREST))
        masks, labels = [], []
        for instance_id in np.unique(instance_ids):
            class_id = int(instance_id // 1000)
            train_id = CITYSCAPES_INSTANCE_IDS.get(class_id)
            if instance_id < 1000 or train_id is None:
                continue
            mask = instance_ids == instance_id
            if mask.sum() == 0:
                continue
            masks.append(mask.astype(np.uint8))
            labels.append(train_id)
        h, w = self.size
        if masks:
            masks_array = np.stack(masks)
            boxes = []
            for mask in masks_array:
                ys, xs = np.where(mask)
                boxes.append([xs.min(), ys.min(), xs.max() + 1, ys.max() + 1])
        else:
            masks_array = np.zeros((0, h, w), np.uint8)
            boxes = []
        image_array = np.asarray(image, dtype=np.float32) / 255.0
        image_tensor = torch.from_numpy(image_array.transpose(2, 0, 1))
        target = {"boxes": torch.as_tensor(boxes, dtype=torch.float32).reshape(-1, 4),
                  "labels": torch.as_tensor(labels, dtype=torch.int64),
                  "masks": torch.as_tensor(masks_array, dtype=torch.uint8),
                  "image_id": torch.tensor([index], dtype=torch.int64),
                  "area": torch.as_tensor([float(mask.sum()) for mask in masks_array], dtype=torch.float32),
                  "iscrowd": torch.zeros((len(labels),), dtype=torch.int64)}
        return image_tensor, target
