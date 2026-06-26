#!/usr/bin/env python3
"""Noetfield anti-staleness guard — machine wins over static prose + mono nerves."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nf_factory_lib_v1 import (
    cascade_requires_disk_patch,
    latest_founder_cascade,
    load_json,
    load_sina,
    mtime_iso,
    parse_iso,
)


def _iso_now() -> str:
    from nf_factory_lib_v1 import iso_now

    return iso_now()


def _first_pending_task(plan: dict) -> dict | None:
    for row in plan.get("next_tasks") or []:
        if str(row.get("status", "")).lower() == "pending":
            return row
    return None


def run_stale_guard() -> dict:
    root = Path(__file__).resolve().parents[1]
    plan_path = root / "os/plan.json"
    ship_path = root / "os/SHIP_NOW.md"
    live_path = root / "reports/agent-auto/LIVE-STATUS.md"
    inbox_doc = root / "docs/ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md"
    surfaces_path = root / "reports/agent-auto/events/nf-live-surfaces-v1.json"

    issues: list[str] = []
    context_stale = False

    pending = None
    if plan_path.is_file():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        pending = _first_pending_task(plan)
    else:
        issues.append("missing os/plan.json")
        context_stale = True

    if pending and ship_path.is_file():
        ship_text = ship_path.read_text(encoding="utf-8", errors="replace")
        task_id = pending.get("id", "")
        if task_id and task_id not in ship_text:
            issues.append(f"SHIP_NOW.md missing pending id {task_id}")
            context_stale = True

    if live_path.is_file() and plan_path.is_file():
        if live_path.stat().st_mtime < plan_path.stat().st_mtime:
            issues.append("LIVE-STATUS older than plan.json — re-run nf-live-orient")
            context_stale = True
    elif not live_path.is_file():
        issues.append("missing LIVE-STATUS.md — run make nf-live-orient")
        context_stale = True

    mono = load_sina("agent-live-surfaces-v1.json") or {}
    mono_at = mono.get("truth_bundle_at") or mono.get("synced_at")
    live_mtime = mtime_iso(live_path)
    if mono_at and live_mtime:
        m_dt = parse_iso(str(mono_at).split(".")[0].replace("+00:00", "Z") if "." in str(mono_at) else str(mono_at))
        l_dt = parse_iso(live_mtime)
        if m_dt and l_dt and m_dt > l_dt:
            issues.append("mono agent-live-surfaces newer than LIVE-STATUS — re-run make nf-onboard")
            context_stale = True

    mono_nerve = load_json(root / "reports/agent-auto/events/nf-mono-nerve-v1.json") or load_sina("nf-mono-nerve-v1.json") or {}
    nerve_at = mono_nerve.get("generated_at")
    if nerve_at and mono_at:
        n_dt = parse_iso(nerve_at)
        m_dt = parse_iso(str(mono_at).split(".")[0].replace("+00:00", "Z") if "." in str(mono_at) else str(mono_at))
        if n_dt and m_dt and m_dt > n_dt:
            issues.append("mono parent newer than nf-mono-nerve — re-run nf-mono-nerve")
            context_stale = True

    cascade_at, cascade_row = latest_founder_cascade()
    sync = load_sina("nf-founder-disk-sync-receipt-v1.json") or {}
    if cascade_requires_disk_patch(cascade_row):
        if sync.get("cascade_at") != cascade_at or not sync.get("ok"):
            issues.append("founder-input-cascade needs disk sync — run nf-founder-input-sync")
            context_stale = True
        elif cascade_at and ship_path.is_file():
            ship_mtime = mtime_iso(ship_path)
            c_dt = parse_iso(cascade_at)
            s_dt = parse_iso(ship_mtime)
            if c_dt and s_dt and c_dt > s_dt and cascade_at not in ship_path.read_text(encoding="utf-8", errors="replace"):
                issues.append("founder-input-cascade newer than SHIP_NOW.md — run nf-founder-input-sync")
                context_stale = True

    defer = load_sina("commercial-email-send-defer-receipt-v1.json") or {}
    if not defer.get("email_send_defer_line"):
        issues.append("missing commercial-email-send-defer email_send_defer_line — run nf-mono-nerve")
        context_stale = True

    ops = load_sina("noetfield-operations-inbox-active-v1.json") or {}
    if not ops.get("ok"):
        issues.append("operations inbox receipt stale/missing — run nf-mono-nerve")
        context_stale = True

    if inbox_doc.is_file():
        text = inbox_doc.read_text(encoding="utf-8", errors="replace")
        if defer.get("defer_active") and "DEFERRED" not in text:
            issues.append("COMMERCIAL_INBOX doc missing Resend DEFERRED marker while defer ON")
            context_stale = True
        if "operations@noetfield.com" not in text:
            issues.append("COMMERCIAL_INBOX doc missing operations@ routing")
            context_stale = True

    if not mono_nerve.get("ok"):
        issues.append("nf-mono-nerve not PASS — run make nf-mono-nerve")
        context_stale = True

    surfaces = load_json(surfaces_path) or load_sina("nf-live-surfaces-v1.json") or {}
    if not surfaces.get("email_send_defer_line"):
        issues.append("nf-live-surfaces missing email_send_defer_line")
        context_stale = True

    out = {
        "schema_version": "nf-stale-guard-v1",
        "generated_at": _iso_now(),
        "context_stale": context_stale,
        "pending_task": pending,
        "issues": issues,
        "mono_synced_at": mono_at,
        "founder_cascade_at": cascade_at,
        "founder_disk_sync_at": sync.get("cascade_at"),
        "email_send_defer_line": defer.get("email_send_defer_line"),
        "heal": "make nf-onboard" if context_stale else None,
    }

    events = root / "reports/agent-auto/events"
    events.mkdir(parents=True, exist_ok=True)
    (events / "nf-stale-guard-v1.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_stale_guard()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        flag = "STALE" if result["context_stale"] else "FRESH"
        print(f"nf_stale_guard: {flag}")
        for issue in result["issues"]:
            print(f"  - {issue}")
        if result["heal"]:
            print(f"heal: {result['heal']}")
    return 1 if result["context_stale"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
