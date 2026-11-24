#!/usr/bin/env python3
"""Check SHIFT's official public endpoints without downloading dataset files.

The URLs follow the official SysCV/shift-dev downloader. This is a bounded
HEAD-only access check, not a dataset or annotation validation.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

BASE = "https://dl.cv.ethz.ch/shift/discrete/images/minival/front/"
FILES = {
    "rgb": BASE + "img.zip",
    "semantic": BASE + "semseg.zip",
    "instance_2d": BASE + "det_insseg_2d.json",
}


def main() -> int:
    report = {
        "dataset": "SHIFT (SysCV, CVPR 2022)",
        "method": "HTTP HEAD only; no dataset bytes intentionally downloaded",
        "license": "CC BY-NC-SA 4.0 (non-commercial; verify current terms)",
        "urls": {},
    }
    for name, url in FILES.items():
        request = urllib.request.Request(
            url, method="HEAD",
            headers={"User-Agent": "urban-dataset-preflight/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                report["urls"][name] = {
                    "status": response.status,
                    "content_length": response.headers.get("Content-Length"),
                    "final_url": response.geturl(),
                }
        except urllib.error.HTTPError as exc:
            report["urls"][name] = {
                "status": exc.code, "reason": str(exc.reason), "url": url,
            }
        except Exception as exc:
            report["urls"][name] = {"status": None, "error": repr(exc), "url": url}

    passed = all(
        item.get("status") is not None and 200 <= item["status"] < 300
        for item in report["urls"].values()
    )
    report["result"] = "PASS_ENDPOINTS" if passed else "ACCESS_INCOMPLETE"
    report["note"] = (
        "Even PASS_ENDPOINTS confirms only endpoint reachability. A bounded file "
        "sample and annotation/condition metadata still require validation."
    )
    with open("shift_access_preflight_report.json", "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
