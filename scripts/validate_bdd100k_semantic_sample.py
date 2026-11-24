"""Validate BDD100K semantic loader with a tiny sample from a public HF mirror.

The repository stores original images and train-id masks in separate trees.
Pairs are matched by the official image stem; no full archive or dataset
snapshot is downloaded.
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

DEFAULT_REPO = "dronefreak/BDD100K-Semantic-Segmentation"
SPLITS = {"train": "train", "val": "val"}


def paired_repo_files(all_files, source_split):
    """Return sorted (image, mask) repository paths for one split."""
    image_prefix = f"data/images_10k/10k/{source_split}/"
    mask_prefix = f"data/seg_maps/labels/{source_split}/"
    file_set = set(all_files)
    pairs = []
    for image_name in sorted(
        name for name in all_files
        if name.startswith(image_prefix) and name.lower().endswith((".jpg", ".jpeg"))
    ):
        relative = PurePosixPath(image_name).relative_to(image_prefix)
        mask_name = str(PurePosixPath(mask_prefix) / relative.parent /
                        f"{relative.stem}_train_id.png")
        if mask_name in file_set:
            pairs.append((image_name, mask_name))
    return pairs


def fetch_split(api, repo_id, revision, source_split, output, limit):
    all_files = api.list_repo_files(
        repo_id=repo_id, repo_type="dataset", revision=revision
    )
    pairs = paired_repo_files(all_files, source_split)
    if len(pairs) < limit:
        image_candidates = [
            name for name in all_files
            if name.startswith(f"data/images_10k/10k/{source_split}/")
        ]
        mask_candidates = [
            name for name in all_files
            if name.startswith(f"data/seg_maps/labels/{source_split}/")
        ]
        raise RuntimeError(
            f"Solo se encontraron {len(pairs)} pares imagen/máscara para "
            f"{source_split}; se solicitaron {limit}. "
            f"Imágenes detectadas={len(image_candidates)}, "
            f"máscaras detectadas={len(mask_candidates)}. "
            f"Ejemplos imagen={image_candidates[:3]}, máscara={mask_candidates[:3]}"
        )

    image_dir = output / "images" / SPLITS[source_split]
    mask_dir = output / "masks" / SPLITS[source_split]
    image_dir.mkdir(parents=True, exist_ok=True)
    mask_dir.mkdir(parents=True, exist_ok=True)
    records = []

    for image_repo_path, mask_repo_path in pairs[:limit]:
        image_cache = hf_hub_download(
            repo_id=repo_id, repo_type="dataset", revision=revision,
            filename=image_repo_path,
        )
        mask_cache = hf_hub_download(
            repo_id=repo_id, repo_type="dataset", revision=revision,
            filename=mask_repo_path,
        )
        image_name = PurePosixPath(image_repo_path).name
        image_target = image_dir / image_name
        mask_target = mask_dir / f"{PurePosixPath(image_name).stem}.png"
        shutil.copyfile(image_cache, image_target)
        shutil.copyfile(mask_cache, mask_target)

        with Image.open(image_target) as image, Image.open(mask_target) as mask:
            if image.mode != "RGB":
                raise ValueError(f"Imagen no RGB: {image_target} ({image.mode})")
            image_size = image.size
            mask_array = np.asarray(mask)
            if mask_array.ndim != 2:
                raise ValueError(
                    f"Máscara no monocanal: {mask_target}, shape={mask_array.shape}"
                )
            if mask.size != image_size:
                raise ValueError(
                    f"Dimensiones distintas: {image_target}={image_size}, "
                    f"{mask_target}={mask.size}"
                )
            values = np.unique(mask_array)
            invalid = values[~np.isin(values, list(range(19)) + [255])]
            if invalid.size:
                raise ValueError(
                    f"IDs fuera de 0..18/255 en {mask_target}: "
                    f"{invalid[:20].tolist()}"
                )
        records.append({
            "image": image_name,
            "image_repo_path": image_repo_path,
            "mask_repo_path": mask_repo_path,
            "width": image_size[0],
            "height": image_size[1],
            "mask_ids": values.tolist(),
        })
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-id", default=DEFAULT_REPO)
    parser.add_argument("--revision", default="main")
    parser.add_argument("--samples-per-split", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    if not 1 <= args.samples_per_split <= 8:
        parser.error("--samples-per-split debe estar entre 1 y 8")

    temporary = tempfile.TemporaryDirectory(prefix="bdd100k-semantic-probe-") if args.output_dir is None else None
    output = Path(temporary.name) if temporary else args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    api = HfApi()
    report = {
        "source": args.repo_id,
        "revision": args.revision,
        "samples_per_split": args.samples_per_split,
        "splits": {},
    }

    try:
        for source_split, local_split in SPLITS.items():
            records = fetch_split(
                api, args.repo_id, args.revision, source_split,
                output, args.samples_per_split,
            )
            dataset = BDD100KSemanticDataset(
                output / "images" / local_split,
                output / "masks" / local_split,
                size=(256, 512),
            )
            if len(dataset) != args.samples_per_split:
                raise AssertionError(
                    f"Loader {local_split}: esperaba {args.samples_per_split}, "
                    f"obtuvo {len(dataset)}"
                )
            samples = []
            for index in range(len(dataset)):
                image, target = dataset[index]
                if tuple(image.shape) != (3, 256, 512):
                    raise AssertionError(
                        f"Shape imagen inesperado: {tuple(image.shape)}"
                    )
                if tuple(target.shape) != (256, 512) or target.dtype != torch.int64:
                    raise AssertionError(
                        f"Target inesperado: {tuple(target.shape)} {target.dtype}"
                    )
                valid = (target == 255) | ((target >= 0) & (target < 19))
                if not bool(torch.all(valid)):
                    raise AssertionError(
                        "El loader produjo IDs semánticos no permitidos"
                    )
                samples.append({
                    "tensor_shape": list(image.shape),
                    "mask_shape": list(target.shape),
                    "class_ids_after_resize": torch.unique(target).tolist(),
                })
            report["splits"][local_split] = {
                "records": records, "loader_samples": samples
            }

        print(json.dumps(report, indent=2))
        print("RESULT: BDD100K semantic sample validation PASSED")
    finally:
        if temporary:
            temporary.cleanup()


if __name__ == "__main__":
    main()
