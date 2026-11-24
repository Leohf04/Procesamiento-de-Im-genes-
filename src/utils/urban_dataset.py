"""Dataset adapters for Cityscapes semantic labels and prepared BDD100K lane masks."""
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset

CITYSCAPES_ID_TO_TRAIN = {
    7: 0, 8: 1, 24: 2, 25: 3, 26: 4, 27: 5, 28: 6, 32: 7, 33: 8, 19: 9, 20: 10
}
CITYSCAPES_CLASSES = ("road", "sidewalk", "person", "rider", "car", "truck",
                      "bus", "motorcycle", "bicycle", "traffic_light", "traffic_sign")


class CityscapesFineDataset(Dataset):
    """Reads *_leftImg8bit.png and matching *_gtFine_labelIds.png files."""
    def __init__(self, root, split="train", size=(512, 1024)):
        self.root, self.size = Path(root), size
        image_root = self.root / "leftImg8bit" / split
        label_root = self.root / "gtFine" / split
        self.images = sorted(image_root.glob("*/*_leftImg8bit.png"))
        if not self.images:
            raise FileNotFoundError(f"No se encontraron imágenes Cityscapes en {image_root}")
        self.label_root = label_root

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        path = self.images[index]
        label = self.label_root / path.parent.name / path.name.replace("_leftImg8bit.png", "_gtFine_labelIds.png")
        if not label.is_file():
            raise FileNotFoundError(f"Falta máscara GT: {label}")
        image = Image.open(path).convert("RGB").resize((self.size[1], self.size[0]), Image.Resampling.BILINEAR)
        ids = np.asarray(Image.open(label).resize((self.size[1], self.size[0]), Image.Resampling.NEAREST))
        target = np.full(ids.shape, 255, dtype=np.uint8)
        for source_id, train_id in CITYSCAPES_ID_TO_TRAIN.items():
            target[ids == source_id] = train_id
        array = np.asarray(image, dtype=np.float32) / 255.0
        array = (array - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
        return torch.from_numpy(array.transpose(2, 0, 1)), torch.from_numpy(target.astype(np.int64))


class LaneMaskDataset(Dataset):
    """Image/mask pairs for BDD100K lane markings after polygon rasterization."""
    def __init__(self, images_dir, masks_dir, size=(512, 1024)):
        self.images_dir, self.masks_dir, self.size = Path(images_dir), Path(masks_dir), size
        self.images = sorted(p for p in self.images_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
        if not self.images:
            raise FileNotFoundError(f"No hay imágenes en {self.images_dir}")
        missing = [p.name for p in self.images if not (self.masks_dir / (p.stem + ".png")).is_file()]
        if missing:
            raise FileNotFoundError(f"Faltan máscaras de carril para {len(missing)} imágenes; primera: {missing[0]}")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        path = self.images[index]
        image = Image.open(path).convert("RGB").resize((self.size[1], self.size[0]), Image.Resampling.BILINEAR)
        mask = Image.open(self.masks_dir / (path.stem + ".png")).convert("L").resize((self.size[1], self.size[0]), Image.Resampling.NEAREST)
        array = np.asarray(image, dtype=np.float32) / 255.0
        array = (array - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
        target = (np.asarray(mask) > 0).astype(np.int64)
        return torch.from_numpy(array.transpose(2, 0, 1)), torch.from_numpy(target)
