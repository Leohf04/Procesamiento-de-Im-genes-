#!/usr/bin/env python3
"""Bounded preflight of the partial public SHIFT Hugging Face mirror.

Reads the small sequence CSV and range-downloads only the first MP4 member from
the RGB and semantic tar archives (maximum 64 MiB per archive). It does not
download the complete archives or the 954 MB instance JSON. The mirror license
metadata is not assumed to override original SHIFT terms.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from pathlib import PurePosixPath

import cv2
import requests
from huggingface_hub import HfApi, hf_hub_download

REPO = "KevinConnorLee/SHIFT"
REVISION = "main"
BASE = f"https://huggingface.co/datasets/{REPO}/resolve/{REVISION}/"
PREFIX = "discrete/videos/val/front/"
MAX_MEMBER_BYTES = 64 * 1024 * 1024


def get_range(path: str, start: int, end: int) -> tuple[bytes, dict]:
    response = requests.get(
        BASE + path, headers={"Range": f"bytes={start}-{end}"},
        stream=True, timeout=90,
    )
    response.raise_for_status()
    expected = end - start + 1
    chunks, total = [], 0
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if not chunk:
            continue
        remaining = expected - total
        chunks.append(chunk[:remaining])
        total += min(len(chunk), remaining)
        if total >= expected:
            break
    meta = {
        "http_status": response.status_code,
        "content_range": response.headers.get("Content-Range"),
        "bytes_read": total,
        "range_supported": response.status_code == 206,
    }
    response.close()
    return b"".join(chunks), meta


def extract_first_video(path: str, target_dir: str, kind: str) -> dict:
    # Tar archives begin with a directory member "./"; scan a bounded prefix
    # until the first MP4 header is found.
    prefix, prefix_meta = get_range(path, 0, 4 * 1024 * 1024 - 1)
    offset = 0
    selected = None
    while offset + 512 <= len(prefix):
        header = prefix[offset:offset + 512]
        if header == b"\\0" * 512:
            break
        name = header[0:100].split(b"\\0", 1)[0].decode("utf-8", "replace")
        size_field = header[124:136].strip(b"\\0 ")
        try:
            member_size = int(size_field or b"0", 8)
        except ValueError:
            break
        member_start = offset + 512
        padded_size = ((member_size + 511) // 512) * 512
        next_offset = member_start + padded_size
        if name.lower().endswith(".mp4"):
            selected = (name, member_size, member_start, next_offset)
            break
        if next_offset <= offset:
            break
        offset = next_offset
    if selected is None:
        return {"status": "NO_MP4_IN_BOUNDED_PREFIX",
                "prefix_bytes": len(prefix), "transfer": prefix_meta}
    name, member_size, member_start, next_offset = selected
    if member_size <= 0 or member_size > MAX_MEMBER_BYTES:
        return {"status": "FIRST_VIDEO_EXCEEDS_SAMPLE_LIMIT",
                "name": name, "member_bytes": member_size,
                "max_member_bytes": MAX_MEMBER_BYTES}
    archive_prefix, transfer = get_range(path, 0, next_offset - 1)
    if len(archive_prefix) < next_offset:
        return {"status": "INCOMPLETE_VIDEO_MEMBER", "name": name,
                "member_bytes": member_size, "bytes_read": len(archive_prefix),
                "transfer": transfer}
    video_path = os.path.join(target_dir, f"{kind}.mp4")
    with open(video_path, "wb") as handle:
        handle.write(archive_prefix[member_start:member_start + member_size])
    capture = cv2.VideoCapture(video_path)
    ok, frame = capture.read()
    fps = capture.get(cv2.CAP_PROP_FPS)
    frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    capture.release()
    if not ok or frame is None:
        return {"status": "VIDEO_DECODE_FAILED", "name": name,
                "member_bytes": member_size, "transfer": transfer}
    sampled = frame[::32, ::32].reshape(-1, 3)
    return {
        "status": "PASS_VIDEO_FRAME",
        "name": name, "member_bytes": member_size,
        "frame_width": int(frame.shape[1]), "frame_height": int(frame.shape[0]),
        "fps": fps, "frame_count": int(frame_count),
        "sampled_unique_colors": len({tuple(int(v) for v in row) for row in sampled}),
        "transfer": transfer,
    }

def main() -> int:
    api = HfApi()
    info = api.dataset_info(REPO, revision=REVISION)
    files = api.list_repo_files(REPO, repo_type="dataset", revision=REVISION)
    file_set = set(files)
    requested = [
        PREFIX + "img.tar", PREFIX + "semseg.tar",
        PREFIX + "det_insseg_2d.json", PREFIX + "det_2d.json",
        PREFIX + "seq.csv",
    ]
    path_info = api.get_paths_info(
        REPO, paths=[p for p in requested if p in file_set],
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
    rows = []
    if seq_path in file_set:
        local = hf_hub_download(
            repo_id=REPO, repo_type="dataset", filename=seq_path,
            revision=REVISION,
        )
        with open(local, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(row)
        report["sequence_metadata"] = {
            "columns": list(rows[0].keys()) if rows else [],
            "row_count": len(rows),
            "first_rows": rows[:5],
        }

    with tempfile.TemporaryDirectory(prefix="shift-mirror-preflight-") as tmp:
        for kind, filename in (("rgb", "img.tar"), ("semantic", "semseg.tar")):
            path = PREFIX + filename
            if path not in file_set:
                report["samples"][kind] = {"status": "FILE_MISSING"}
            else:
                report["samples"][kind] = extract_first_video(path, tmp, kind)

    rgb = report["samples"].get("rgb", {})
    semantic = report["samples"].get("semantic", {})
    report["sample_dimensions_match"] = (
        rgb.get("status") == "PASS_VIDEO_FRAME"
        and semantic.get("status") == "PASS_VIDEO_FRAME"
        and rgb.get("frame_width") == semantic.get("frame_width")
        and rgb.get("frame_height") == semantic.get("frame_height")
    )
    video_id = PurePosixPath(rgb.get("name", "")).stem
    report["sample_sequence_metadata"] = next(
        (row for row in rows if row.get("video") == video_id), None
    )
    report["result"] = (
        "PASS_RGB_SEMANTIC_VIDEO_SAMPLE"
        if report["sample_dimensions_match"] else "PARTIAL_MIRROR_METADATA_ONLY"
    )
    report["note"] = (
        "The mirror contains only discrete/videos data (no continuous paths). "
        "The val/front subset is large; only the first video member of two tar "
        "archives was range-read. No full archive or full instance JSON was downloaded."
    )
    with open("shift_hf_mirror_preflight_report.json", "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["sequence_metadata"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
