import cv2
import numpy as np


def extract_hog_features(
    image_bgr: np.ndarray,
    roi_box: tuple[int, int, int, int] | None = None,
    size: tuple[int, int] = (64, 128),
) -> np.ndarray:
    if roi_box is not None:
        x1, y1, x2, y2 = map(int, roi_box)
        h, w = image_bgr.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1:
            return np.zeros((3780,), dtype=np.float32)
        patch = image_bgr[y1:y2, x1:x2]
    else:
        patch = image_bgr

    patch = cv2.resize(patch, size, interpolation=cv2.INTER_AREA)
    patch_gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
    hog = cv2.HOGDescriptor(
        _winSize=(64, 128),
        _blockSize=(16, 16),
        _blockStride=(8, 8),
        _cellSize=(8, 8),
        _nbins=9,
    )
    descriptor = hog.compute(patch_gray)
    if descriptor is None:
        return np.zeros((3780,), dtype=np.float32)
    return descriptor.flatten().astype(np.float32)


def extract_color_histogram(
    image_bgr: np.ndarray, roi_box: tuple[int, int, int, int] | None = None
) -> np.ndarray:
    if roi_box is not None:
        x1, y1, x2, y2 = map(int, roi_box)
        h, w = image_bgr.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1:
            return np.zeros((48,), dtype=np.float32)
        patch = image_bgr[y1:y2, x1:x2]
    else:
        patch = image_bgr

    hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
    histogram = cv2.calcHist(
        [hsv], [0, 1, 2], None, [8, 4, 2], [0, 180, 0, 256, 0, 256]
    )
    return cv2.normalize(histogram, histogram).flatten().astype(np.float32)
