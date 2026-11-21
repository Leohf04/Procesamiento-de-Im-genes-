"""Validate the BDD100K semantic loader with a tiny sample from a public HF mirror.

The mirror card states that image pixels and train-id masks are redistributed
unmodified from the official BDD100K semantic release. This is a loader smoke
test only; it does not validate instance, detection, or lane annotations.
"""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath

import numpy as np
from PIL import Image
import torch
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.utils.bdd100k_dataset import BDD100KSemanticDataset

DEFAULT_REPO = "liqijia/BDD100K-Semantic-Segmentation"
SPLITS = {"train": "train", "valid": "val"}


def safe_repo_path(parent: str, child: str) -> str:
    path = PurePosixPath(parent) / child
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Ruta inválida en metadata HF: {child}")
    return str(path)


def fetch_split(api: HfApi, repo_id: str, source_split: str, output: Path, limit: int):
    prefix = f"data/images/{source_split}/"
    all_files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
    metadata_files = sorted(
        name for name in all_files
        if name.startswith(prefix) and name.endswith("metadata.jsonl")
    )
    if not metadata_files:
        candidates = [name for name in all_files if "metadata" in name.lower() or source_split in PurePosixPath(name).parts]
        raise RuntimeError(
            f"No se encontraron metadata.jsonl para split {source_split}. "
            f"Primeros archivos del repositorio: {all_files[:30]}; "
            f"candidatos relacionados: {candidates[:50]}"
        )

    image_dir = output / "images" / SPLITS[source_split]
    mask_dir = output / "masks" / SPLITS[source_split]
    image_dir.mkdir(parents=True, exist_ok=True)
    mask_dir.mkdir(parents=True, exist_ok=True)
    records = []

    for metadata_name in metadata_files:
        local_metadata = hf_hub_download(
            repo_id=repo_id, repo_type="dataset", filename=metadata_name
        )
        with open(local_metadata, encoding="utf-8") as stream:
            rows = [json.loads(line) for line in stream if line.strip()]
        for row in rows:
            image_name, mask_name = row.get("file_name"), row.get("mask_file_name")
            if not image_name or not mask_name:
                raise ValueError(f"Metadata incompleta: {row}")
            parent = str(PurePosixPath(metadata_name).parent)
            image_repo_path = safe_repo_path(parent, image_name)
            mask_repo_path = safe_repo_path(parent, mask_name)
            image_cache = hf_hub_download(
                repo_id=repo_id, repo_type="dataset", filename=image_repo_path
            )
            mask_cache = hf_hub_download(
                repo_id=repo_id, repo_type="dataset", filename=mask_repo_path
            )
            image_target = image_dir / Path(image_name).name
            mask_target = mask_dir / (Path(image_name).stem + ".png")
            shutil.copyfile(image_cache, image_target)
            shutil.copyfile(mask_cache, mask_target)

            with Image.open(image_target) as image, Image.open(mask_target) as mask:
                if image.mode not in {"RGB", "RGBA"}:
                    raise ValueError(f"Imagen no RGB: {image_target} ({image.mode})")
                image_size = image.size
                mask_array = np.asarray(mask)
                if mask_array.ndim != 2:
                    raise ValueError(f"Máscara no monocanal: {mask_target}, shape={mask_array.shape}")
                if mask.size != image_size:
                    raise ValueError(
                        f"Dimensiones distintas: {image_target}={image_size}, "
                        f"{mask_target}={mask.size}"
                    )
                values = np.unique(mask_array)
                invalid = values[~np.isin(values, list(range(19)) + [255])]
                if invalid.size:
                    raise ValueError(
                        f"IDs fuera de 0..18/255 en {mask_target}: {invalid[:20].tolist()}"
                    )
            records.append({
                "image": image_target.name,
                "width": image_size[0],
                "height": image_size[1],
                "mask_ids": values.tolist(),
            })
            if len(records) >= limit:
                return records
    raise RuntimeError(
        f"Solo se pudieron obtener {len(records)} muestras de {source_split}; "
        f"se solicitaron {limit}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-id", default=DEFAULT_REPO)
    parser.add_argument("--samples-per-split", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    if not 1 <= args.samples_per_split <= 8:
        parser.error("--samples-per-split debe estar entre 1 y 8")

    temporary = tempfile.TemporaryDirectory(prefix="bdd100k-semantic-probe-") if args.output_dir is None else None
    output = Path(temporary.name) if temporary else args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    api = HfApi()
    report = {"source": args.repo_id, "samples_per_split": args.samples_per_split, "splits": {}}

    for source_split, local_split in SPLITS.items():
        records = fetch_split(api, args.repo_id, source_split, output, args.samples_per_split)
        dataset = BDD100KSemanticDataset(
            output / "images" / local_split,
            output / "masks" / local_split,
            size=(256, 512),
        )
        if len(dataset) != args.samples_per_split:
            raise AssertionError(
                f"Loader {local_split}: esperaba {args.samples_per_split}, obtuvo {len(dataset)}"
            )
        samples = []
        for index in range(len(dataset)):
            image, target = dataset[index]
            if tuple(image.shape) != (3, 256, 512):
                raise AssertionError(f"Shape imagen inesperado: {tuple(image.shape)}")
            if tuple(target.shape) != (256, 512) or target.dtype != torch.int64:
                raise AssertionError(f"Target inesperado: {tuple(target.shape)} {target.dtype}")
            valid = (target == 255) | ((target >= 0) & (target < 19))
            if not bool(torch.all(valid)):
                raise AssertionError("El loader produjo IDs semánticos no permitidos")
            samples.append({
                "tensor_shape": list(image.shape),
                "mask_shape": list(target.shape),
                "class_ids_after_resize": torch.unique(target).tolist(),
            })
        report["splits"][local_split] = {"records": records, "loader_samples": samples}

    print(json.dumps(report, indent=2))
    print("RESULT: BDD100K semantic sample validation PASSED")
    if temporary:
        temporary.cleanup()


if __name__ == "__main__":
    main()
