import importlib
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

REQUIRED_MODULES = [
    "numpy",
    "cv2",
    "yaml",
    "matplotlib",
    "sklearn",
    "joblib",
    "tqdm",
]
OPTIONAL_MODULES = ["torch", "torchvision", "pycocotools"]


def check_module(name: str) -> bool:
    try:
        module = importlib.import_module(name)
        version = getattr(module, "__version__", "?")
        print(f"  [OK]   {name} {version}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  [FAIL] {name}: {exc}")
        return False


def main() -> int:
    print("1) Dependencias obligatorias")
    missing = [name for name in REQUIRED_MODULES if not check_module(name)]

    print("\n2) Dependencias opcionales")
    for name in OPTIONAL_MODULES:
        check_module(name)

    print("\n3) Configuración")
    from src.utils.config_utils import HAS_TORCH, load_config, resolve_backend

    try:
        config = load_config("configs/config.yaml")
        print(f"  [OK]   config cargada ({len(config)} secciones)")
    except Exception as exc:  # noqa: BLE001
        print(f"  [FAIL] config: {exc}")
        return 1

    backend = resolve_backend(config.get("system", {}).get("backend", "auto"))
    print(f"  [OK]   Backend activo: {backend} (HAS_TORCH={HAS_TORCH})")

    print("\n4) Dataset")
    dataset_cfg = config.get("dataset", {})
    images_dir = dataset_cfg.get("images_dir", "data/coco/val2017")
    ann_file = dataset_cfg.get(
        "annotations_file", "data/coco/annotations/instances_val2017.json"
    )
    if os.path.isdir(images_dir) and os.path.isfile(ann_file):
        n_images = len(os.listdir(images_dir))
        print(f"  [OK]   {n_images} imágenes en {images_dir}")
    else:
        print("  [PEND] Dataset no descargado (se hace al final).")
        print("         python scripts/download_coco_val2017.py")

    print("\n5) Módulos del proyecto")
    project_modules = [
        "src.utils.config_utils",
        "src.utils.coco_loader",
        "src.utils.visualization",
        "src.preprocessing.illumination",
        "src.preprocessing.atmospheric",
        "src.models.instance_seg",
        "src.models.semantic_hybrid",
        "src.features.descriptors",
        "src.features.fine_classifier",
        "src.evaluation.metrics",
        "src.evaluation.trainer",
        "src.evaluation.error_analysis",
        "src.pipeline",
    ]
    import_failures = [name for name in project_modules if not check_module(name)]

    if missing or import_failures:
        print("\nRESULTADO: fallan dependencias o módulos. Revisa los mensajes.")
        return 1

    print("\nRESULTADO: entorno listo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
