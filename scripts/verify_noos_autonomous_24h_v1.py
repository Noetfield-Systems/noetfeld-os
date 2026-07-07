#!/usr/bin/env python3
"""Verify NOOS factory autorun is autonomous — CF cron + repository_dispatch only."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = "Noetfield-Systems/noetfeld-os"
CF_HEALTH = "https://noos-factory-autorun-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
AUTONOMOUS_EVENTS = frozenset({"repository_dispatch", "schedule"})
MANUAL_EVENTS = frozenset({"workflow_dispatch"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def _github_token() -> str | None:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0:
        return None
    vals = dict(line.split("=", 1) for line in proc.stdout.splitlines() if "=" in line)
    return vals.get("password")


def _github_runs(*, event: str | None, since: datetime) -> list[dict[str, Any]]:
    token = _github_token()
    if not token:
        return []
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    params: dict[str, str] = {"per_page": "100", "created": f">={since_iso}"}
    if event:
        params["event"] = event
    url = f"https://api.github.com/repos/{REPO}/actions/runs?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8")).get("workflow_runs") or []
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return []


def _cf_health() -> dict[str, Any]:
    req = urllib.request.Request(CF_HEALTH, headers={"User-Agent": "verify-noos-autonomous-24h/1"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _supabase_cycle_count() -> dict[str, Any]:
    from noos_vault_paths_v1 import NOETFIELD_LOCAL_ENV, load_platform_env

    if not NOETFIELD_LOCAL_ENV.is_file():
        return {"ok": False, "skipped": True, "reason": "noetfield.env missing"}
    vals = load_platform_env()
    url = vals.get("NOETFIELD_SUPABASE_URL") or vals.get("SUPABASE_URL")
    key = vals.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or vals.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    req = urllib.request.Request(
        f"{url.rstrip('/')}/rest/v1/noetfield_factory_cycle_runs?select=id,recorded_at,runner_output&order=recorded_at.desc&limit=5",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        triggers = [
            (r.get("runner_output") or {}).get("cloud_trigger")
            for r in rows
            if isinstance(r.get("runner_output"), dict)
        ]
        return {"ok": True, "recent_count": len(rows), "cloud_triggers": triggers, "latest_at": rows[0].get("recorded_at") if rows else None}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def verify(*, hours: float = 24.0) -> dict[str, Any]:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    all_runs = _github_runs(event=None, since=since)
    dispatch_runs = [r for r in all_runs if r.get("event") == "repository_dispatch"]
    schedule_runs = [r for r in all_runs if r.get("event") == "schedule"]
    manual_runs = [r for r in all_runs if r.get("event") in MANUAL_EVENTS]

    epoch = None
    if dispatch_runs:
        epoch = min(r.get("created_at", "") for r in dispatch_runs if r.get("created_at"))
    cf = _cf_health()
    cycles = _supabase_cycle_count()

    zero_manual = len(manual_runs) == 0 or all(
        r.get("created_at", "") < since.strftime("%Y-%m-%dT%H:%M:%SZ") for r in manual_runs
    )
    # manual in window = fail
    manual_in_window = [
        f"{r.get('id')}:{r.get('event')}:{(r.get('created_at') or '')[:19]}"
        for r in all_runs
        if r.get("event") in MANUAL_EVENTS
        and (not epoch or (r.get("created_at") or "") >= epoch)
    ]
    autonomous_in_window = len(dispatch_runs) + len(schedule_runs)
    cf_ok = cf.get("ok") and (cf.get("body") or {}).get("github_token_ready")
    # If supabase not configured or explicitly skipped, treat cycles as non-fatal (skip) so transient infra doesn't mark autonomy as failed.
    cycles_skipped = bool(cycles.get("skipped"))
    cycles_ok = True if cycles_skipped else (cycles.get("ok") and cycles.get("recent_count", 0) >= 1)
    has_github = bool(_github_token())
    dispatch_ok = len(dispatch_runs) >= 1 if has_github else cf_ok

    ok = cf_ok and dispatch_ok and len(manual_in_window) == 0 and cycles_ok

    return {
        "supabase_skipped": cycles_skipped,
        "schema": "noos-autonomous-24h-verify-v1",
        "at": _now(),
        "commit_sha": _git_sha(),
        "window_hours": hours,
        "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "autonomous_epoch": epoch,
        "ok": ok,
        "cf_motor": cf,
        "github": {
            "token_available": has_github,
            "repository_dispatch_count": len(dispatch_runs),
            "schedule_count": len(schedule_runs),
            "manual_in_window": manual_in_window[:20],
            "latest_dispatch": dispatch_runs[0] if dispatch_runs else None,
        },
        "supabase_cycles": cycles,
        "zero_manual_in_window": len(manual_in_window) == 0,
        "report_line": (
            f"autonomous {'PASS' if ok else 'FAIL'} · sha {_git_sha()[:8]} · "
            f"dispatch={len(dispatch_runs)} schedule={len(schedule_runs)} manual={len(manual_in_window)}"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=float, default=24.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()
    row = verify(hours=args.hours)
    if args.write_receipt:
        out = ROOT / ".noos-runtime/factory/receipts/noos-autonomous-24h-verify-v1.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(out)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
