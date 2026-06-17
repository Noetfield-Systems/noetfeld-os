#!/usr/bin/env python3
"""Emit nf-live-routing-v1.json — queue head + git + scope pins."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _first_pending(plan: dict) -> dict | None:
    for row in plan.get("next_tasks") or []:
        if str(row.get("status", "")).lower() == "pending":
            return {"id": row.get("id"), "title": row.get("title")}
    return None


def _git_info(root: Path) -> dict:
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
        return {"sha": sha, "branch": branch}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"sha": None, "branch": None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--agent", default=None)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    events = Path(args.events)
    events.mkdir(parents=True, exist_ok=True)
    agent = args.agent or __import__("os").environ.get("NOETFIELD_AGENT_ID", "noetfield_cloud")

    pending = None
    plan_path = root / "os/plan.json"
    if plan_path.is_file():
        pending = _first_pending(json.loads(plan_path.read_text(encoding="utf-8")))

    mirror = (
        root / "ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md"
    ).is_file()

    payload = {
        "schema_version": "nf-live-routing-v1",
        "generated_at": _iso_now(),
        "agent_id": agent,
        "pending_task": pending,
        "git": _git_info(root),
        "sourcea_mirror": mirror,
        "boot": ["make nf-onboard"],
        "pins": {
            "start_here": "entry/START_HERE_LOCKED_v1.md",
            "routing_card": "ROUTING_CARD.md",
            "live_status": "reports/agent-auto/LIVE-STATUS.md",
            "graph": "os/NF_UNIFIED_ROUTING_GRAPH.json",
        },
    }

    out_path = events / "nf-live-routing-v1.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        pid = (pending or {}).get("id") or "none"
        ptitle = (pending or {}).get("title") or ""
        git = payload["git"]
        print("=== Noetfield routing card ===")
        print(f"agent: {agent}")
        print(f"generated: {payload['generated_at']}")
        print(f"pending: {pid} — {ptitle}")
        print(f"git: {git.get('branch') or '?'} @ {git.get('sha') or '?'}")
        print(f"sourceA mirror: {mirror}")
        print("boot: make nf-onboard")
        print("live: reports/agent-auto/LIVE-STATUS.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
