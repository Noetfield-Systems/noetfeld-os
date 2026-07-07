#!/usr/bin/env python3
"""Self-register a noos-factory-autorun GHA run into noetfield_truth_log (Supabase).

Writes {run_id, event, conclusion, at} every workflow completion (L13/D1 idempotent upsert).
Called from .github/workflows/noos-factory-autorun.yml final step (if: always).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_vault_paths_v1 import load_platform_env  # noqa: E402

SOURCE = "noos-factory-autorun"
TABLE = "noetfield_truth_log"


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


def supabase_cfg(vals: dict[str, str]) -> tuple[str, str] | None:
    url = vals.get("NOETFIELD_SUPABASE_URL") or vals.get("SUPABASE_URL")
    key = vals.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or vals.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return url.rstrip("/"), key
    return None


def register_row(
    *,
    run_id: str,
    event: str,
    conclusion: str,
    workflow: str | None = None,
    recorded_at: str | None = None,
) -> dict:
    vals = load_env()
    cfg = supabase_cfg(vals)
    if not cfg:
        return {"ok": False, "blocker_reason": "supabase_not_configured"}
    base, key = cfg
    at = recorded_at or utc_now()
    row = {
        "source": SOURCE,
        "run_id": str(run_id),
        "event": event,
        "conclusion": conclusion,
        "workflow": workflow or "noos-factory-autorun.yml",
        "recorded_at": at,
        "metadata": {"registered_by": "register_noos_factory_run_truth_v1.py"},
    }
    req = urllib.request.Request(
        f"{base}/rest/v1/{TABLE}?on_conflict=run_id,source",
        data=json.dumps(row).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "return=representation,resolution=merge-duplicates",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            inserted = body[0] if isinstance(body, list) and body else body
            return {
                "ok": True,
                "table": TABLE,
                "id": inserted.get("id"),
                "run_id": run_id,
                "event": event,
                "conclusion": conclusion,
                "at": at,
            }
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        return {"ok": False, "status": exc.code, "error": detail}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", ""))
    ap.add_argument("--event", default=os.environ.get("GITHUB_EVENT_NAME", ""))
    ap.add_argument("--conclusion", default=os.environ.get("JOB_CONCLUSION", "success"))
    ap.add_argument("--workflow", default=os.environ.get("GITHUB_WORKFLOW", ""))
    ap.add_argument("--at", default=utc_now())
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.run_id or not args.event:
        result = {"ok": False, "blocker_reason": "missing_run_id_or_event"}
    else:
        result = register_row(
            run_id=args.run_id,
            event=args.event,
            conclusion=args.conclusion,
            workflow=args.workflow or None,
            recorded_at=args.at,
        )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"truth_register ok={result.get('ok')} run_id={result.get('run_id')} "
            f"event={result.get('event')} conclusion={result.get('conclusion')}"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
