"""Validate BDD100K instance masks from an authorized remote archive URL.

The archive URL must be supplied as BDD100K_INSTANCE_LABELS_URL (for example
as a GitHub Actions secret). The 111 MB archive is downloaded only on the
ephemeral runner, checksum-verified, and only a few matching PNG/JPEG pairs
are retained in a temporary directory. Nothing is uploaded to the repository.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
import zipfile
from pathlib import PurePosixPath
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download
from PIL import Image
import torch

from src.utils.bdd100k_dataset import BDD100KInstanceDataset

EXPECTED_MD5 = "651b41f229d7327d8c4af97772de4390"
DEFAULT_IMAGE_REPO = "dronefreak/BDD100K-Semantic-Segmentation"
MAX_PER_SPLIT = 2
ARCHIVE_ENV = "BDD100K_INSTANCE_LABELS_URL"


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_mask_members(archive: zipfile.ZipFile, split: str) -> dict[str, str]:
    suffix = f"/labels/ins_seg/bitmasks/{split}/"
    matches = {}
    for name in archive.namelist():
        normalized = name.replace("\\", "/")
        path = PurePosixPath(normalized)
        if suffix in f"/{normalized}" and path.suffix.lower() == ".png":
            matches.setdefault(path.stem, normalized)
    return matches


def find_image_files(repo_id: str, split: str) -> dict[str, str]:
    api = HfApi()
    files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
    prefix = f"data/images_10k/10k/{split}/"
    return {
        PurePosixPath(name).stem: name
        for name in files
        if name.startswith(prefix) and name.lower().endswith(".jpg")
    }


def main() -> None:
    archive_url = os.environ.get(ARCHIVE_ENV)
    if not archive_url:
        raise SystemExit(
            f"Falta el secreto {ARCHIVE_ENV}. Añade la URL de descarga autorizada "
            "del portal BDD100K en GitHub Actions > Settings > Secrets and variables > Actions."
        )

    with tempfile.TemporaryDirectory(prefix="bdd100k-insseg-") as temp:
        root = Path(temp)
        archive_path = root / "instance_labels.zip"
        import requests

        digest = hashlib.md5()
        with requests.get(archive_url, stream=True, timeout=(30, 180)) as response:
            response.raise_for_status()
            total = 0
            with archive_path.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    output.write(chunk)
                    digest.update(chunk)
                    total += len(chunk)
        actual_md5 = digest.hexdigest()
        print(f"Archive bytes downloaded remotely: {total}")
        print(f"Archive MD5: {actual_md5}")
        if actual_md5 != EXPECTED_MD5:
            raise RuntimeError(
                f"MD5 incorrecto: esperado {EXPECTED_MD5}, recibido {actual_md5}. "
                "Se rechaza el archivo y no se extraen máscaras."
            )

        sample_images = root / "images"
        sample_masks = root / "masks"
        sample_images.mkdir()
        sample_masks.mkdir()

        with zipfile.ZipFile(archive_path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise RuntimeError(f"ZIP corrupto: {bad_member}")
            selected = []
            for split in ("train", "val"):
                mask_members = find_mask_members(archive, split)
                image_members = find_image_files(DEFAULT_IMAGE_REPO, split)
                common = sorted(set(mask_members) & set(image_members))
                if not common:
                    raise RuntimeError(
                        f"No hay stems coincidentes entre bitmasks oficiales y "
                        f"las imágenes del mirror para split={split}. "
                        "No se sustituirán etiquetas ni se inventarán parejas."
                    )
                selected.extend((split, stem, mask_members[stem], image_members[stem])
                                for stem in common[:MAX_PER_SPLIT])

            if len(selected) < 2:
                raise RuntimeError("No se encontraron suficientes pares reales.")

            for split, stem, mask_member, image_member in selected:
                target_mask = sample_masks / f"{stem}.png"
                with archive.open(mask_member) as source, target_mask.open("wb") as dest:
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        dest.write(chunk)
                image_path = hf_hub_download(
                    repo_id=DEFAULT_IMAGE_REPO,
                    repo_type="dataset",
                    filename=image_member,
                )
                target_image = sample_images / f"{stem}.jpg"
                target_image.write_bytes(Path(image_path).read_bytes())

                with Image.open(target_mask) as mask:
                    if mask.mode != "RGBA":
                        raise RuntimeError(f"{stem}: máscara {mask.mode}, se esperaba RGBA")
                    mask_size = mask.size
                with Image.open(target_image) as image:
                    if image.mode != "RGB" or image.size != mask_size:
                        raise RuntimeError(
                            f"{stem}: imagen {image.mode}/{image.size} y máscara "
                            f"RGBA/{mask_size} no coinciden"
                        )
                print(f"PAIR {split}: {stem} {mask_size} mask=RGBA image=RGB")

        dataset = BDD100KInstanceDataset(
            sample_images, sample_masks, size=(256, 512)
        )
        if len(dataset) != len(selected):
            raise RuntimeError(f"El loader encontró {len(dataset)} pares, esperados {len(selected)}")
        for index in range(len(dataset)):
            image, target = dataset[index]
            assert tuple(image.shape) == (3, 256, 512)
            assert image.dtype == torch.float32
            assert target["boxes"].ndim == 2 and target["boxes"].shape[1] == 4
            assert target["labels"].dtype == torch.int64
            assert target["masks"].ndim == 3
            assert target["masks"].shape[1:] == (256, 512)
            assert len(target["labels"]) == len(target["boxes"]) == len(target["masks"])
            assert all(1 <= int(label) <= 8 for label in target["labels"])
            print(
                f"LOADER sample={index} image={tuple(image.shape)} "
                f"instances={len(target['labels'])} boxes={tuple(target['boxes'].shape)} "
                f"masks={tuple(target['masks'].shape)}"
            )

        archive_path.unlink(missing_ok=True)
        print("RESULT: BDD100K INSTANCE SAMPLE VALIDATION PASSED")


if __name__ == "__main__":
    main()
