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
import io
import json
import os
import re
import tarfile
import tempfile
import subprocess
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
    # Parse only tar headers from a 16 MiB prefix, then range-fetch one MP4.
    prefix, prefix_meta = get_range(path, 0, 16 * 1024 * 1024 - 1)
    selected = None
    header_diagnostics = []
    try:
        with tarfile.open(fileobj=io.BytesIO(prefix), mode="r:") as archive:
            while True:
                member = archive.next()
                if member is None:
                    break
                header_diagnostics.append({
                    "name": member.name, "size": member.size,
                    "type": member.type.decode("ascii", "replace") if isinstance(member.type, bytes) else str(member.type),
                    "offset_data": member.offset_data,
                })
                if member.isfile() and member.name.lower().endswith(".mp4"):
                    selected = (member.name, member.size, member.offset_data)
                    break
    except (tarfile.ReadError, EOFError, OSError) as exc:
        if selected is None:
            return {"status": "TAR_HEADER_SCAN_INCOMPLETE",
                    "prefix_bytes": len(prefix),
                    "first_members": header_diagnostics[:10],
                    "parse_error": repr(exc), "transfer": prefix_meta}
    if selected is None:
        return {"status": "NO_MP4_IN_BOUNDED_PREFIX",
                "prefix_bytes": len(prefix),
                "first_members": header_diagnostics[:10],
                "transfer": prefix_meta}
    name, member_size, offset_data = selected
    if member_size <= 0 or member_size > MAX_MEMBER_BYTES:
        return {"status": "FIRST_VIDEO_EXCEEDS_SAMPLE_LIMIT",
                "name": name, "member_bytes": member_size,
                "max_member_bytes": MAX_MEMBER_BYTES}
    video_bytes, transfer = get_range(
        path, offset_data, offset_data + member_size - 1
    )
    if len(video_bytes) < member_size:
        return {"status": "INCOMPLETE_VIDEO_MEMBER", "name": name,
                "member_bytes": member_size, "bytes_read": len(video_bytes),
                "transfer": transfer}
    video_path = os.path.join(target_dir, f"{kind}.mp4")
    with open(video_path, "wb") as handle:
        handle.write(video_bytes)
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
        "transfer": transfer, "tar_prefix_transfer": prefix_meta,
        "first_members": header_diagnostics[:10],
    }


def probe_video_timestamps(path: str) -> dict:
    """Read decoded presentation timestamps, not nominal OpenCV FPS metadata."""
    command = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=avg_frame_rate,r_frame_rate,duration,nb_frames,time_base",
        "-show_entries", "frame=best_effort_timestamp_time",
        "-of", "json", path,
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    stream = (payload.get("streams") or [{}])[0]
    timestamps = [
        float(frame["best_effort_timestamp_time"])
        for frame in payload.get("frames", [])
        if frame.get("best_effort_timestamp_time") is not None
    ]
    if not timestamps:
        raise RuntimeError(f"No frame PTS found in {path}")
    return {
        "frame_pts_count": len(timestamps),
        "first_pts_seconds": timestamps[0],
        "last_pts_seconds": timestamps[-1],
        "duration_from_pts_seconds": timestamps[-1] - timestamps[0],
        "avg_frame_rate": stream.get("avg_frame_rate"),
        "r_frame_rate": stream.get("r_frame_rate"),
        "container_duration_seconds": stream.get("duration"),
        "nb_frames_metadata": stream.get("nb_frames"),
        "_timestamps": timestamps,
    }


def compare_video_pts(rgb_path: str, semantic_path: str) -> dict:
    rgb = probe_video_timestamps(rgb_path)
    sem = probe_video_timestamps(semantic_path)
    rt, st = rgb.pop("_timestamps"), sem.pop("_timestamps")
    overlap_start, overlap_end = max(rt[0], st[0]), min(rt[-1], st[-1])
    overlap = max(0.0, overlap_end - overlap_start)
    shorter_duration = max(1e-9, min(rt[-1] - rt[0], st[-1] - st[0]))
    overlap_ratio = overlap / shorter_duration
    same_index = None
    if len(rt) == len(st):
        errors = [abs(a - b) for a, b in zip(rt, st)]
        same_index = {
            "median_abs_delta_seconds": float(__import__("numpy").median(errors)),
            "p95_abs_delta_seconds": float(__import__("numpy").percentile(errors, 95)),
            "max_abs_delta_seconds": max(errors),
        }
    # Nearest semantic timestamp for each RGB frame within shared timeline.
    import bisect
    nearest = []
    for value in rt:
        if overlap_start <= value <= overlap_end:
            pos = bisect.bisect_left(st, value)
            candidates = st[max(0, pos - 1):min(len(st), pos + 1)]
            if candidates:
                nearest.append(min(abs(value - candidate) for candidate in candidates))
    nearest_stats = None
    if nearest:
        np = __import__("numpy")
        nearest_stats = {
            "matched_rgb_frames": len(nearest),
            "median_abs_delta_seconds": float(np.median(nearest)),
            "p95_abs_delta_seconds": float(np.percentile(nearest, 95)),
            "max_abs_delta_seconds": max(nearest),
        }
    return {
        "rgb": rgb, "semantic": sem,
        "shared_timeline_overlap_seconds": overlap,
        "overlap_fraction_of_shorter_stream": overlap_ratio,
        "same_index_pts_delta": same_index,
        "nearest_timestamp_delta": nearest_stats,
        "status": "PTS_ALIGNMENT_CANDIDATE_REQUIRES_VISUAL_SPOTCHECK"
            if overlap_ratio >= 0.95 and nearest_stats is not None
            else "NOT_TEMPORALLY_ALIGNED_BY_PTS",
        "caveat": "Matching PTS is necessary but not sufficient; semantic/RGB content still requires visual frame-pair verification.",
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
        if all(report["samples"].get(k, {}).get("status") == "PASS_VIDEO_FRAME" for k in ("rgb", "semantic")):
            report["pts_alignment"] = compare_video_pts(
                os.path.join(tmp, "rgb.mp4"), os.path.join(tmp, "semantic.mp4")
            )

    rgb = report["samples"].get("rgb", {})
    semantic = report["samples"].get("semantic", {})
    report["sample_dimensions_match"] = (
        rgb.get("status") == "PASS_VIDEO_FRAME"
        and semantic.get("status") == "PASS_VIDEO_FRAME"
        and rgb.get("frame_width") == semantic.get("frame_width")
        and rgb.get("frame_height") == semantic.get("frame_height")
    )
    report["sample_frame_count_match"] = (
        rgb.get("status") == "PASS_VIDEO_FRAME"
        and semantic.get("status") == "PASS_VIDEO_FRAME"
        and rgb.get("frame_count") == semantic.get("frame_count")
    )
    report["sample_fps_match"] = (
        rgb.get("status") == "PASS_VIDEO_FRAME"
        and semantic.get("status") == "PASS_VIDEO_FRAME"
        and abs(float(rgb.get("fps", 0)) - float(semantic.get("fps", 0))) < 0.01
    )
    report["temporal_alignment_status"] = (
        "PENDING_FPS_MISMATCH"
        if report["sample_dimensions_match"] and report["sample_frame_count_match"]
        and not report["sample_fps_match"]
        else "PENDING_FRAME_PAIR_VERIFICATION"
    )
    video_id = PurePosixPath(rgb.get("name", "")).stem
    report["sample_sequence_metadata"] = next(
        (row for row in rows if row.get("video") == video_id), None
    )
    report["result"] = (
        "PASS_DECODED_SAMPLE_ALIGNMENT_PENDING"
        if report["sample_dimensions_match"] and report["sample_frame_count_match"]
        else "PARTIAL_MIRROR_METADATA_ONLY"
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
