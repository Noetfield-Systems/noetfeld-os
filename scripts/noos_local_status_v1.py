#!/usr/bin/env python3
"""Human-readable T2 Mac session status digest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_integrator_mirror_check_v1 as mirror  # noqa: E402
import verify_living_system_governance_v1 as gov  # noqa: E402


def git_line(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def dirty_count() -> int:
    try:
        out = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0
    return sum(1 for line in out.splitlines() if line.strip())


def integrator_summary() -> dict[str, Any]:
    try:
        out = subprocess.check_output(
            [sys.executable, "scripts/noos_integrator_sync_v1.py", "summary", "--json"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return {}


def agent_task_ids(state: dict[str, Any], agent_id: str) -> list[str]:
    for agent in state.get("agents") or []:
        if isinstance(agent, dict) and agent.get("agent_id") == agent_id:
            ids = agent.get("current_task_ids")
            return [str(x) for x in ids] if isinstance(ids, list) else []
    return []


def build_status() -> dict[str, Any]:
    state = integrator_summary()
    summary = state.get("summary") if isinstance(state.get("summary"), dict) else {}
    gov_row = gov.run_verify(write_receipt=False)
    mirror_row = mirror.check_mirror_drift()

    active_claims = int(summary.get("claimed") or 0) + int(summary.get("in_progress") or 0)
    row = {
        "schema": "noos-local-status-v1",
        "branch": git_line(["branch", "--show-current"]),
        "head": git_line(["rev-parse", "--short", "HEAD"]),
        "dirty_count": dirty_count(),
        "active_claims": active_claims,
        "stale_claims": summary.get("stale_claims", 0),
        "active_agents": summary.get("active_agents", 0),
        "governance_ok": gov_row.get("ok"),
        "mirror_ok": mirror_row.get("ok"),
        "cursor_local_mac_tasks": agent_task_ids(state, "cursor-local-mac"),
        "copilot_cli_mac_tasks": agent_task_ids(state, "copilot-cli-mac"),
    }
    row["report_line"] = (
        f"local_status · branch={row['branch']} dirty={row['dirty_count']} "
        f"claims={row['active_claims']} governance={'ok' if row['governance_ok'] else 'drift'}"
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build_status()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
        print(f"  head: {row['head']}")
        print(f"  stale_claims: {row['stale_claims']} active_agents: {row['active_agents']}")
        print(f"  mirror_ok: {row['mirror_ok']} governance_ok: {row['governance_ok']}")
        if row["cursor_local_mac_tasks"]:
            print(f"  cursor-local-mac tasks: {', '.join(row['cursor_local_mac_tasks'])}")
        if row["copilot_cli_mac_tasks"]:
            print(f"  copilot-cli-mac tasks: {', '.join(row['copilot_cli_mac_tasks'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
