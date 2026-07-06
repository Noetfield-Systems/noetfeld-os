#!/usr/bin/env python3
"""Seed noos_loop_registry via CF tick?all=1 and Supabase queries."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CF_MOTOR = "https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev"
INTERVALS = ROOT / "cloud/workers/noos-deadman-v1/src/loop-intervals.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env() -> tuple[str, str]:
    env_file = Path.home() / ".sourcea-secrets/noetfield.env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    url = (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or "").rstrip("/")
    key = os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    return url, key


def supabase_rows(url: str, key: str) -> list[dict[str, Any]]:
    req = urllib.request.Request(
        f"{url}/rest/v1/noos_loop_registry?select=loop_id,last_fired_at,interval_minutes",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def tick_all() -> dict[str, Any]:
    req = urllib.request.Request(f"{CF_MOTOR}/tick?all=1", method="POST", headers={"User-Agent": "seed-liveness-v1"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {"ok": resp.status == 200, "status": resp.status, "body": body}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "error": raw[:400]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tick-all", action="store_true", help="POST CF motor tick?all=1")
    ap.add_argument("--wait-sec", type=int, default=90, help="Wait after tick before registry poll")
    ap.add_argument("--assert-min-rows", type=int, default=0)
    ap.add_argument("--assert-table", action="store_true", help="Assert registry table reachable")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    url, key = load_env()
    row: dict[str, Any] = {"schema": "noos-loop-liveness-seed-v1", "at": utc_now(), "ok": True}

    if args.tick_all:
        row["tick_all"] = tick_all()
        row["ok"] = row["ok"] and row["tick_all"].get("ok", False)
        if args.wait_sec > 0:
            time.sleep(args.wait_sec)

    if url and key:
        try:
            rows = supabase_rows(url, key)
            row["registry_rows"] = len(rows)
            row["rows_with_fired"] = sum(1 for r in rows if r.get("last_fired_at"))
            row["registry_sample"] = rows[:5]
        except OSError as exc:
            row["registry_error"] = str(exc)
            row["ok"] = False
    else:
        row["registry_skipped"] = "supabase_not_configured"
        if args.assert_table or args.assert_min_rows:
            row["ok"] = False

    expected = len(json.loads(INTERVALS.read_text(encoding="utf-8"))) if INTERVALS.is_file() else 13
    if args.assert_min_rows:
        row["ok"] = row.get("registry_rows", 0) >= args.assert_min_rows
    if args.assert_table:
        row["ok"] = row.get("registry_rows") is not None and row["ok"]

    row["expected_loops"] = expected
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"seed_liveness · rows={row.get('registry_rows')} ok={row.get('ok')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
