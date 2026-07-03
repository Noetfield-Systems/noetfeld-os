#!/usr/bin/env python3
"""Verify T8 pg_cron stale-lane detector registration (read-only)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _env(name: str) -> str:
    return (os.environ.get(name) or os.environ.get(f"NOETFIELD_{name}") or "").strip()


def probe_t8(*, limit: int = 5) -> dict[str, Any]:
    url = _env("SUPABASE_URL") or _env("NOETFIELD_SUPABASE_URL")
    key = _env("SUPABASE_SERVICE_ROLE_KEY") or _env("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
    errors: list[str] = []
    stale_events: list[dict[str, Any]] = []
    table_ok = False
    if not url or not key:
        errors.append("supabase_not_configured")
    else:
        target = (
            f"{url.rstrip('/')}/rest/v1/noetfield_stale_lane_events"
            f"?select=id,recorded_at,lane_id,event&order=recorded_at.desc&limit={limit}"
        )
        req = urllib.request.Request(
            target,
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                stale_events = body if isinstance(body, list) else []
                table_ok = True
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                errors.append("stale_lane_table_missing")
            else:
                errors.append(f"rest_error:{exc.code}")
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            errors.append(str(exc)[:80])

    ok = table_ok and not errors
    return {
        "schema": "noetfield-t8-stale-lane-probe-v1",
        "at": utc_now(),
        "registry_trigger_id": "NOOS-T8-stale-lane-pgcron",
        "table_ok": table_ok,
        "recent_events": stale_events,
        "ok": ok,
        "errors": errors,
        "report_line": (
            "t8_stale_lane_probe_ok · table reachable"
            if ok
            else f"t8_stale_lane_probe_fail · {','.join(errors) or 'unknown'}"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = probe_t8()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
