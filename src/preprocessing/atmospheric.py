import cv2
import numpy as np


def apply_motion_blur(image: np.ndarray, kernel_size: int = 15, angle: float = 0.0) -> np.ndarray:
    if kernel_size < 3:
        return image.copy()
    if kernel_size % 2 == 0:
        kernel_size += 1

    kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
    center = kernel_size // 2
    rad = np.deg2rad(angle)
    dx = np.cos(rad) * center
    dy = np.sin(rad) * center
    pt1 = (int(round(center - dx)), int(round(center - dy)))
    pt2 = (int(round(center + dx)), int(round(center + dy)))
    cv2.line(kernel, pt1, pt2, 1.0, thickness=1)
    kernel_sum = np.sum(kernel)
    if kernel_sum > 0:
        kernel /= kernel_sum
    return cv2.filter2D(image, -1, kernel)


def apply_synthetic_fog(
    image: np.ndarray, beta: float = 0.045, atmospheric_light: float = 225.0
) -> np.ndarray:
    h, w = image.shape[:2]
    vertical_profile = np.linspace(1.0, 0.15, h, dtype=np.float32)
    depth_map = np.tile(vertical_profile[:, np.newaxis], (1, w)) * 40.0
    transmission = np.exp(-beta * depth_map)
    transmission_3c = np.repeat(transmission[:, :, np.newaxis], 3, axis=2)
    img_float = image.astype(np.float32)
    foggy = img_float * transmission_3c + atmospheric_light * (1.0 - transmission_3c)
    return np.clip(foggy, 0, 255).astype(np.uint8)


def apply_synthetic_rain(
    image: np.ndarray,
    drop_count: int = 600,
    drop_length: int = 18,
    slant: int = -10,
    seed: int = 42,
) -> np.ndarray:
    h, w = image.shape[:2]
    rain_layer = np.zeros((h, w), dtype=np.uint8)
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, w, size=drop_count)
    ys = rng.integers(0, h, size=drop_count)
    for x, y in zip(xs, ys):
        x_end = int(np.clip(x + slant, 0, w - 1))
        y_end = int(np.clip(y + drop_length, 0, h - 1))
        cv2.line(rain_layer, (int(x), int(y)), (x_end, y_end), 200, thickness=1)
    rain_layer = cv2.blur(rain_layer, (3, 3))
    rain_bgr = cv2.cvtColor(rain_layer, cv2.COLOR_GRAY2BGR)
    darkened = cv2.convertScaleAbs(image, alpha=0.85, beta=-5)
    return cv2.addWeighted(darkened, 1.0, rain_bgr, 0.35, 0)
