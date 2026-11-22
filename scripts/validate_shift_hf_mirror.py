#!/usr/bin/env python3
"""Bounded preflight of the partial public SHIFT Hugging Face mirror.

Downloads seq.csv and at most 16 MiB from each of the RGB/semantic tar archives
using HTTP Range. It never downloads the full archives or the 954 MB instance
JSON. The mirror's license metadata is not assumed to override original SHIFT
terms.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import tarfile
from pathlib import PurePosixPath

import requests
from huggingface_hub import HfApi, hf_hub_download
from PIL import Image

REPO = "KevinConnorLee/SHIFT"
REVISION = "main"
BASE = f"https://huggingface.co/datasets/{REPO}/resolve/{REVISION}/"
PREFIX = "discrete/videos/val/front/"
MAX_RANGE_BYTES = 16 * 1024 * 1024


def range_prefix(path: str) -> tuple[bytes, dict]:
    url = BASE + path
    response = requests.get(
        url, headers={"Range": f"bytes=0-{MAX_RANGE_BYTES - 1}"},
        stream=True, timeout=90,
    )
    response.raise_for_status()
    chunks, total = [], 0
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if not chunk:
            continue
        remaining = MAX_RANGE_BYTES - total
        chunks.append(chunk[:remaining])
        total += min(len(chunk), remaining)
        if total >= MAX_RANGE_BYTES:
            break
    meta = {
        "http_status": response.status_code,
        "content_range": response.headers.get("Content-Range"),
        "content_length_header": response.headers.get("Content-Length"),
        "bytes_read": total,
        "range_supported": response.status_code == 206,
    }
    response.close()
    return b"".join(chunks), meta


def inspect_tar_prefix(data: bytes) -> dict:
    files = []
    sample = None
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r|") as archive:
            for member in archive:
                if not member.isfile():
                    continue
                files.append(member.name)
                suffix = PurePosixPath(member.name).suffix.lower()
                if suffix in {".png", ".jpg", ".jpeg"} and sample is None:
                    extracted = archive.extractfile(member)
                    if extracted:
                        payload = extracted.read()
                        try:
                            with Image.open(io.BytesIO(payload)) as image:
                                image.load()
                                sample = {
                                    "name": member.name, "bytes": len(payload),
                                    "format": image.format, "mode": image.mode,
                                    "width": image.width, "height": image.height,
                                }
                        except Exception as exc:
                            sample = {"name": member.name, "decode_error": repr(exc)}
                if len(files) >= 30 and sample:
                    break
    except Exception as exc:
        return {"members_seen": len(files), "first_members": files[:20],
                "sample": sample, "tar_parse_note": repr(exc)}
    return {"members_seen": len(files), "first_members": files[:20], "sample": sample}


def main() -> int:
    api = HfApi()
    info = api.dataset_info(REPO, revision=REVISION)
    files = api.list_repo_files(REPO, repo_type="dataset", revision=REVISION)
    paths = {path for path in files}
    requested = [
        PREFIX + "img.tar", PREFIX + "semseg.tar",
        PREFIX + "det_insseg_2d.json", PREFIX + "det_2d.json",
        PREFIX + "seq.csv",
    ]
    path_info = api.get_paths_info(
        REPO, paths=[p for p in requested if p in paths],
        repo_type="dataset", revision=REVISION,
    )
    sizes = {item.path: getattr(item, "size", None) for item in path_info}

    card_data = getattr(info, "card_data", None)
    mirror_license = getattr(card_data, "license", None) if card_data else None
    report = {
        "dataset": REPO, "revision": REVISION, "commit": getattr(info, "sha", None),
        "file_count": len(files),
        "continuous_paths_present": any(path.startswith("continuous/") for path in files),
        "mirror_license_metadata": mirror_license,
        "official_license_note": "Original SHIFT DevKit declares CC BY-NC-SA 4.0; mirror MIT metadata is not treated as permission to relicense source data.",
        "files": sizes, "sequence_metadata": None, "samples": {},
    }

    seq_path = PREFIX + "seq.csv"
    if seq_path in paths:
        local = hf_hub_download(
            repo_id=REPO, repo_type="dataset", filename=seq_path,
            revision=REVISION,
        )
        with open(local, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = []
            for _, row in zip(range(5), reader):
                rows.append(row)
            report["sequence_metadata"] = {
                "columns": reader.fieldnames, "first_rows": rows,
            }

    for kind, filename in (("rgb", "img.tar"), ("semantic", "semseg.tar")):
        path = PREFIX + filename
        if path not in paths:
            report["samples"][kind] = {"available": False}
            continue
        data, transfer = range_prefix(path)
        report["samples"][kind] = {
            "available": True, "transfer": transfer,
            "archive_prefix": inspect_tar_prefix(data),
            "prefix_sha256": hashlib.sha256(data).hexdigest(),
        }

    rgb_sample = report["samples"].get("rgb", {}).get("archive_prefix", {}).get("sample")
    sem_sample = report["samples"].get("semantic", {}).get("archive_prefix", {}).get("sample")
    report["result"] = (
        "PASS_RGB_SEMANTIC_SAMPLE" if rgb_sample and sem_sample
        else "PARTIAL_MIRROR_METADATA_ONLY"
    )
    report["note"] = (
        "This mirror contains only discrete/videos data; it is not a replacement "
        "for SHIFT continuous splits. No full archive or full instance JSON was downloaded."
    )
    with open("shift_hf_mirror_preflight_report.json", "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["sequence_metadata"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
