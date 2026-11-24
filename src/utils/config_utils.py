import importlib.util
import random
import numpy as np
import yaml

HAS_TORCH = importlib.util.find_spec("torch") is not None and importlib.util.find_spec("torchvision") is not None


def load_config(config_path: str = "configs/config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_backend(requested_backend: str = "auto") -> str:
    if requested_backend == "torch":
        if not HAS_TORCH:
            raise RuntimeError("Se solicitó backend='torch' pero PyTorch no está disponible.")
        return "torch"
    if requested_backend == "onnx":
        if importlib.util.find_spec("onnxruntime") is None:
            raise RuntimeError("Se solicitó backend='onnx' pero falta onnxruntime.")
        return "onnx"
    if requested_backend == "onnx_cv2":
        return "onnx_cv2"
    return "torch" if HAS_TORCH else "onnx_cv2"


def set_global_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    if HAS_TORCH:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
