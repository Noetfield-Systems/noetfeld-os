#!/usr/bin/env python3
"""07:00 Pacific daily heartbeat — fixed one-line format + JSON receipt."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMAT = ROOT / "data" / "nf-daily-heartbeat-format-v1.json"
PLATFORM_BASE = "https://platform.noetfield.com"
WWW_BASE = "https://www.noetfield.com"


def _probe_url(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "nf-daily-heartbeat/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return "PASS" if 200 <= resp.status < 300 else "FAIL"
    except (urllib.error.URLError, TimeoutError, ValueError):
        return "FAIL"


def _run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    return "PASS" if proc.returncode == 0 else "FAIL"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    supabase_rest = "SKIP"
    supabase_sql = "SKIP"
    if _run(["python3", "scripts/verify_supabase_heartbeat_v1.py"]) == "PASS":
        supabase_rest = "PASS"
        supabase_sql = "PASS"
    else:
        supabase_rest = "FAIL"

    platform = _probe_url(f"{PLATFORM_BASE}/health")
    www = _probe_url(f"{WWW_BASE}/")

    checks = [supabase_rest, supabase_sql, platform, www]
    slo = "PASS" if all(x in ("PASS", "SKIP") for x in checks) and "FAIL" not in checks else "FAIL"

    template = json.loads(FORMAT.read_text(encoding="utf-8"))["line_template"]
    line = template.format(
        ts_utc=ts,
        supabase_rest=supabase_rest,
        supabase_sql=supabase_sql,
        platform=platform,
        www=www,
        slo=slo,
    )

    receipt = {
        "schema": "nf-daily-heartbeat-v1",
        "at": ts,
        "line": line,
        "checks": {
            "supabase_rest": supabase_rest,
            "supabase_sql": supabase_sql,
            "platform": platform,
            "www": www,
            "slo": slo,
        },
    }

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(line)

    return 0 if slo == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
