#!/usr/bin/env python3
"""Noetfield anti-staleness guard — machine wins over static prose."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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

    out = {
        "schema_version": "nf-stale-guard-v1",
        "generated_at": _iso_now(),
        "context_stale": context_stale,
        "pending_task": pending,
        "issues": issues,
        "heal": "make nf-live-orient" if context_stale else None,
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
