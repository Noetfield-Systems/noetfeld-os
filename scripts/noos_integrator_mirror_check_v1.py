#!/usr/bin/env python3
"""Check drift between repo-local integrator state and home mirror."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from integrator_runtime_paths_v1 import integrator_home_mirror_path, integrator_state_path  # noqa: E402


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _normalize(state: dict[str, Any]) -> dict[str, Any]:
    tasks = state.get("tasks") if isinstance(state.get("tasks"), list) else []
    agents = state.get("agents") if isinstance(state.get("agents"), list) else []
    norm_tasks = sorted(
        [
            {
                "task_id": t.get("task_id"),
                "status": t.get("status"),
                "claimed_by": t.get("claimed_by"),
                "scope_files": sorted(t.get("scope_files") or []),
            }
            for t in tasks
            if isinstance(t, dict)
        ],
        key=lambda x: str(x.get("task_id")),
    )
    norm_agents = sorted(
        [
            {
                "agent_id": a.get("agent_id"),
                "ide": a.get("ide"),
                "role": a.get("role"),
                "status": a.get("status"),
            }
            for a in agents
            if isinstance(a, dict)
        ],
        key=lambda x: str(x.get("agent_id")),
    )
    return {"tasks": norm_tasks, "agents": norm_agents, "summary": state.get("summary")}


def check_mirror_drift() -> dict[str, Any]:
    repo_path = integrator_state_path()
    home_path = integrator_home_mirror_path()
    repo = load_json(repo_path)
    home = load_json(home_path)

    if not repo:
        return {
            "ok": False,
            "error": "missing_repo_state",
            "repo_path": str(repo_path),
            "home_mirror_path": str(home_path),
        }

    if not home:
        return {
            "ok": True,
            "drift": True,
            "reason": "missing_home_mirror",
            "repo_path": str(repo_path),
            "home_mirror_path": str(home_path),
            "repair": "python3 scripts/noos_integrator_sync_v1.py sync",
        }

    repo_norm = _normalize(repo)
    home_norm = _normalize(home)
    drift = repo_norm != home_norm

    return {
        "ok": not drift,
        "drift": drift,
        "repo_path": str(repo_path),
        "home_mirror_path": str(home_path),
        "repo_tasks": len(repo_norm["tasks"]),
        "home_tasks": len(home_norm["tasks"]),
        "repair": "python3 scripts/noos_integrator_sync_v1.py sync" if drift else None,
        "report_line": (
            "integrator_mirror_clean · repo matches home"
            if not drift
            else "integrator_mirror_drift · run sync"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = check_mirror_drift()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line") or row.get("error") or "integrator_mirror_check")
    strict = __import__("os").environ.get("STRICT_MIRROR", "").strip() == "1"
    if strict and not row.get("ok"):
        return 1
    return 0 if row.get("ok") else 0  # warn-only by default


if __name__ == "__main__":
    raise SystemExit(main())
