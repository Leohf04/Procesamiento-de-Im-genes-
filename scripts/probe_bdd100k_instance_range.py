"""Probe official BDD100K instance-label archive endpoints for byte-range support.

Only headers and the first 4 KiB are requested. Streaming responses are closed
immediately; the archive is never saved to disk.
"""
import json
import requests

URLS = {
    "ETHZ": "https://dl.cv.ethz.ch/bdd100k/data/bdd100k_ins_seg_labels_trainval.zip",
    "Berkeley_S3": "https://bdd-data-storage-release.s3.us-west-2.amazonaws.com/bdd100k/2021/bdd100k_ins_seg_labels_trainval.zip",
}
EXPECTED_MD5 = "651b41f229d7327d8c4af97772de4390"


def probe(name, url):
    result = {"source": name, "url": url}
    try:
        head = requests.head(url, allow_redirects=True, timeout=25)
        result["head_status"] = head.status_code
        result["final_url"] = head.url
        result["content_length"] = head.headers.get("Content-Length")
        result["accept_ranges"] = head.headers.get("Accept-Ranges")
        result["head_content_type"] = head.headers.get("Content-Type")

        response = requests.get(
            url, headers={"Range": "bytes=0-4095"},
            stream=True, allow_redirects=True, timeout=(15, 30),
        )
        result["range_status"] = response.status_code
        result["range_content"] = response.headers.get("Content-Range")
        result["range_length"] = response.headers.get("Content-Length")
        result["range_accept_ranges"] = response.headers.get("Accept-Ranges")
        first = next(response.iter_content(chunk_size=4096), b"")
        result["bytes_received_before_close"] = len(first)
        result["zip_signature"] = first[:4].hex()
        result["range_honored"] = (
            response.status_code == 206
            and response.headers.get("Content-Range", "").startswith("bytes 0-")
            and first.startswith(b"PK\\x03\\x04")
        )
        response.close()
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    outcomes = [probe(name, url) for name, url in URLS.items()]
    usable = [item for item in outcomes if item.get("range_honored")]
    print("RESULT: RANGE_SUPPORTED" if usable else "RESULT: NO_VERIFIED_RANGE_SOURCE")
