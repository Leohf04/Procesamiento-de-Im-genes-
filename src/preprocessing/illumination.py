import cv2
import numpy as np


def apply_gamma_correction(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    if gamma <= 0:
        raise ValueError("El parámetro gamma debe ser estrictamente positivo.")
    inv_gamma = 1.0 / gamma
    lookup_table = np.array(
        [((i / 255.0) ** inv_gamma) * 255.0 for i in range(256)], dtype=np.uint8
    )
    return cv2.LUT(image, lookup_table)


def adjust_exposure(image: np.ndarray, alpha: float = 1.0, beta: int = 0) -> np.ndarray:
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def enhance_low_light_clahe(image: np.ndarray, clip_limit: float = 2.5) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)
    return cv2.cvtColor(
        cv2.merge((l_enhanced, a_channel, b_channel)), cv2.COLOR_LAB2BGR
    )
