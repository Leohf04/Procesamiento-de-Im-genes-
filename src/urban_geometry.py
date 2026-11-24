"""Aspect-preserving letterbox transforms shared by urban image and mask adapters."""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
from PIL import Image


@dataclass(frozen=True)
class LetterboxGeometry:
    source_height: int
    source_width: int
    target_height: int
    target_width: int
    resized_height: int
    resized_width: int
    top: int
    left: int

    @property
    def scale_x(self) -> float:
        return self.resized_width / self.source_width

    @property
    def scale_y(self) -> float:
        return self.resized_height / self.source_height

    def boxes_xyxy(self, boxes):
        """Map Nx4 xyxy boxes into the letterboxed target coordinate frame."""
        import torch
        if torch.is_tensor(boxes):
            out = boxes.clone().to(dtype=torch.float32)
            out[:, [0, 2]] = out[:, [0, 2]] * self.scale_x + self.left
            out[:, [1, 3]] = out[:, [1, 3]] * self.scale_y + self.top
            out[:, [0, 2]].clamp_(0, self.target_width)
            out[:, [1, 3]].clamp_(0, self.target_height)
            return out
        out = np.asarray(boxes, dtype=np.float32).copy().reshape(-1, 4)
        out[:, [0, 2]] = np.clip(out[:, [0, 2]] * self.scale_x + self.left, 0, self.target_width)
        out[:, [1, 3]] = np.clip(out[:, [1, 3]] * self.scale_y + self.top, 0, self.target_height)
        return out


def letterbox_geometry(source_hw, target_hw) -> LetterboxGeometry:
    h, w = map(int, source_hw)
    th, tw = map(int, target_hw)
    if min(h, w, th, tw) <= 0:
        raise ValueError("Source and target dimensions must be positive")
    scale = min(th / h, tw / w)
    nh = max(1, min(th, int(round(h * scale))))
    nw = max(1, min(tw, int(round(w * scale))))
    return LetterboxGeometry(h, w, th, tw, nh, nw, (th - nh) // 2, (tw - nw) // 2)


def letterbox_image(image: Image.Image, target_hw):
    """Resize RGB image with bilinear interpolation and centered RGB padding."""
    image = image.convert("RGB")
    g = letterbox_geometry((image.height, image.width), target_hw)
    resized = image.resize((g.resized_width, g.resized_height), Image.Resampling.BILINEAR)
    canvas = Image.new("RGB", (g.target_width, g.target_height), (0, 0, 0))
    canvas.paste(resized, (g.left, g.top))
    return canvas, g


def letterbox_mask(mask, target_hw, fill_value=255):
    """Resize a label mask with nearest-neighbor and centered ignore/background padding."""
    array = np.asarray(mask)
    if array.ndim not in (2, 3):
        raise ValueError(f"Expected HxW or HxWxC mask, got {array.shape}")
    h, w = array.shape[:2]
    g = letterbox_geometry((h, w), target_hw)
    if array.ndim == 2:
        resized = np.asarray(Image.fromarray(array).resize(
            (g.resized_width, g.resized_height), Image.Resampling.NEAREST))
        canvas = np.full((g.target_height, g.target_width), fill_value, dtype=array.dtype)
        canvas[g.top:g.top+g.resized_height, g.left:g.left+g.resized_width] = resized
    else:
        resized = np.asarray(Image.fromarray(array).resize(
            (g.resized_width, g.resized_height), Image.Resampling.NEAREST))
        fill = np.asarray(fill_value, dtype=array.dtype)
        if fill.ndim == 0:
            fill = np.repeat(fill, array.shape[2])
        canvas = np.empty((g.target_height, g.target_width, array.shape[2]), dtype=array.dtype)
        canvas[...] = fill
        canvas[g.top:g.top+g.resized_height, g.left:g.left+g.resized_width] = resized
    return canvas, g
