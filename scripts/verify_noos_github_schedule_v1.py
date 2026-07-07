#!/usr/bin/env python3
"""A1 — verify factory schedule proof from Supabase noetfield_truth_log.

Success: >=2 rows with source=noos-factory-autorun, event=schedule,
conclusion=success, ordered by recorded_at desc.

Private-repo GitHub cron lags 10–30+ min; this script is a **native-cron diagnostic only**.
Does NOT gate the VERIFIED window (primary motor = CF repository_dispatch).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_proof_receipt_paths_v1 import proof_receipt  # noqa: E402

from noos_vault_paths_v1 import load_platform_env  # noqa: E402

PROOF_RECEIPT = proof_receipt("noos-github-schedule-a1-v1.json")
SOURCE = "noos-factory-autorun"
TABLE = "noetfield_truth_log"
MIN_SCHEDULE_ROWS = 2


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env() -> dict[str, str]:
    vals = load_platform_env()
    for key in (
        "NOETFIELD_SUPABASE_URL",
        "SUPABASE_URL",
        "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ):
        if os.environ.get(key):
            vals[key] = os.environ[key].strip()
    return vals


def supabase_cfg() -> tuple[str, str] | None:
    vals = load_env()
    url = vals.get("NOETFIELD_SUPABASE_URL") or vals.get("SUPABASE_URL")
    key = vals.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or vals.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return url.rstrip("/"), key
    return None


def fetch_schedule_rows(*, limit: int = 10) -> dict[str, Any]:
    cfg = supabase_cfg()
    if not cfg:
        return {"ok": False, "blocker_reason": "supabase_not_configured", "rows": []}
    base, key = cfg
    params = urllib.parse.urlencode(
        {
            "select": "id,run_id,event,conclusion,recorded_at,workflow,source",
            "source": f"eq.{SOURCE}",
            "event": "eq.schedule",
            "conclusion": "eq.success",
            "order": "recorded_at.desc",
            "limit": str(limit),
        }
    )
    req = urllib.request.Request(
        f"{base}/rest/v1/{TABLE}?{params}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "table": TABLE, "rows": rows}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        if exc.code == 404:
            return {"ok": False, "blocker_reason": "truth_log_table_missing", "error": detail, "rows": []}
        return {"ok": False, "blocker_reason": "supabase_query_failed", "error": detail, "rows": []}


def verify() -> dict[str, Any]:
    fetched = fetch_schedule_rows()
    rows = fetched.get("rows") or []
    ok = fetched.get("ok") and len(rows) >= MIN_SCHEDULE_ROWS
    pair = rows[:2] if len(rows) >= 2 else []
    result: dict[str, Any] = {
        "schema": "noos-github-schedule-a1-v1",
        "verified_at": utc_now(),
        "proof_source": "supabase",
        "table": TABLE,
        "ok": bool(ok),
        "a1_criterion": (
            f">={MIN_SCHEDULE_ROWS} rows in {TABLE} with source={SOURCE}, "
            "event=schedule, conclusion=success (self-registered by workflow)"
        ),
        "schedule_row_count": len(rows),
        "schedule_rows": [
            {
                "run_id": r.get("run_id"),
                "event": r.get("event"),
                "conclusion": r.get("conclusion"),
                "at": r.get("recorded_at"),
            }
            for r in rows[:5]
        ],
        "blocker_reason": None if ok else (fetched.get("blocker_reason") or "insufficient_schedule_rows_in_supabase"),
        "note": "GitHub private-repo cron lags; workflow self-registers every run. No gh polling.",
    }
    if len(pair) == 2:
        result["consecutive_factory_pair"] = {
            "newer_run_id": pair[0].get("run_id"),
            "older_run_id": pair[1].get("run_id"),
            "newer_at": pair[0].get("recorded_at"),
            "older_at": pair[1].get("recorded_at"),
        }
    if not fetched.get("ok"):
        result["supabase_error"] = fetched.get("error")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = verify()
    if args.write_receipt:
        PROOF_RECEIPT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        result["receipt_path"] = str(PROOF_RECEIPT.relative_to(ROOT))
        result["receipt_tier"] = "proof"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        pair = result.get("consecutive_factory_pair") or {}
        print(
            f"a1_ok={result['ok']} schedule_rows={result['schedule_row_count']} "
            f"pair={pair.get('newer_run_id')}/{pair.get('older_run_id')}"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
