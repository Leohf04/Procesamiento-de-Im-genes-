import argparse
import os
import sys
import zipfile

import urllib.request

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

IMAGES_URL = "http://images.cocodataset.org/zips/val2017.zip"
ANNOTATIONS_URL = (
    "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
)


def _progress_hook(block_num: int, block_size: int, total_size: int) -> None:
    if tqdm is None or total_size <= 0:
        return
    downloaded = block_num * block_size
    if not hasattr(_progress_hook, "bar"):
        _progress_hook.bar = tqdm(
            total=total_size, unit="B", unit_scale=True, desc="Descargando"
        )
    bar = _progress_hook.bar
    bar.n = min(downloaded, total_size)
    bar.refresh()


def download_file(url: str, destination: str) -> None:
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    if os.path.isfile(destination):
        with zipfile.ZipFile(destination) as zf:
            if zf.testzip() is None:
                print(f"[OK] {destination} ya existe y es válido.")
                return
        print(f"[WARN] {destination} corrupto. Se descarga de nuevo.")
        os.remove(destination)

    partial = destination + ".part"
    resume_from = os.path.getsize(partial) if os.path.isfile(partial) else 0

    request = urllib.request.Request(url)
    if resume_from:
        request.add_header("Range", f"bytes={resume_from}-")
        print(f"[INFO] Reanudando desde {resume_from} bytes.")

    with urllib.request.urlopen(request) as response:
        mode = "ab" if resume_from else "wb"
        total = response.headers.get("Content-Length")
        total_size = int(total) + resume_from if total else 0
        if tqdm is not None:
            bar = tqdm(total=total_size, unit="B", unit_scale=True, desc="Descargando")
        else:
            bar = None

        with open(partial, mode) as f:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                if bar is not None:
                    bar.update(len(chunk))
        if bar is not None:
            bar.close()

    os.replace(partial, destination)
    print(f"[OK] Descargado {destination}")


def extract_zip(zip_path: str, destination: str, marker: str) -> None:
    if os.path.exists(marker):
        print(f"[OK] {marker} ya existe. Se omite extracción.")
        return

    print(f"[INFO] Extrayendo {zip_path}...")
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise RuntimeError(f"Zip corrupto en {zip_path}: {bad}")
        zf.extractall(destination)
    print(f"[OK] Extraído en {destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Descarga COCO val2017")
    parser.add_argument("--base-dir", default="data/coco")
    args = parser.parse_args()

    base_dir = args.base_dir
    os.makedirs(base_dir, exist_ok=True)

    images_zip = os.path.join(base_dir, "val2017.zip")
    annotations_zip = os.path.join(base_dir, "annotations_trainval2017.zip")

    download_file(IMAGES_URL, images_zip)
    download_file(ANNOTATIONS_URL, annotations_zip)

    extract_zip(
        images_zip,
        base_dir,
        os.path.join(base_dir, "val2017"),
    )
    extract_zip(
        annotations_zip,
        base_dir,
        os.path.join(base_dir, "annotations", "instances_val2017.json"),
    )

    n_images = (
        len(os.listdir(os.path.join(base_dir, "val2017")))
        if os.path.isdir(os.path.join(base_dir, "val2017"))
        else 0
    )
    print(f"\nDataset listo: {n_images} imágenes en {base_dir}/val2017")
    print("Siguiente paso: python evaluate_scenarios.py --max-samples 30")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
