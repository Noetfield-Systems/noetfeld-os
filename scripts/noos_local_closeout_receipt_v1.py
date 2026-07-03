#!/usr/bin/env python3
"""Write T2 local-closeout receipt (noos-local-closeout-v1)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_integrator_mirror_check_v1 as mirror  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def git_line(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def run_step(cmd: list[str]) -> bool:
    try:
        subprocess.run(cmd, cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def build_receipt(
    *,
    task_id: str,
    agent_id: str,
    ide: str,
    pytest_ok: bool | None = None,
    clean_tree_ok: bool | None = None,
    complete_ok: bool | None = None,
    write_file: bool = True,
) -> dict[str, Any]:
    if pytest_ok is None:
        pytest_ok = run_step([sys.executable, "-m", "pytest", "-q"])
    if clean_tree_ok is None:
        clean_tree_ok = run_step(["bash", "scripts/check_noos_clean_tree.sh"])

    if complete_ok is None:
        complete_ok = run_step(
            [
                sys.executable,
                "scripts/noos_integrator_sync_v1.py",
                "complete",
                "--agent-id",
                agent_id,
                "--ide",
                ide,
                "--task-id",
                task_id,
                "--note",
                "lane closed",
            ]
        )

    mirror_row = mirror.check_mirror_drift()
    ok = bool(pytest_ok and clean_tree_ok and complete_ok)

    row: dict[str, Any] = {
        "schema": "noos-local-closeout-v1",
        "version": "1.0.0",
        "at": utc_now(),
        "task_id": task_id,
        "agent_id": agent_id,
        "ide": ide,
        "branch": git_line(["branch", "--show-current"]),
        "head": git_line(["rev-parse", "--short", "HEAD"]),
        "pytest_ok": pytest_ok,
        "clean_tree_ok": clean_tree_ok,
        "integrator_complete_ok": complete_ok,
        "mirror_drift": mirror_row,
        "ok": ok,
        "report_line": (
            f"local_closeout_clean · task={task_id}"
            if ok
            else f"local_closeout_incomplete · task={task_id}"
        ),
    }

    if write_file:
        out_dir = ROOT / "receipts/proof"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = out_dir / f"noos-local-closeout-{ts}.json"
        path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(path.relative_to(ROOT))

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--agent-id", default="cursor-local-mac")
    ap.add_argument("--ide", default="cursor")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--pytest-ok", choices=["true", "false"])
    ap.add_argument("--clean-tree-ok", choices=["true", "false"])
    ap.add_argument("--complete-ok", choices=["true", "false"])
    args = ap.parse_args()

    def tri(val: str | None) -> bool | None:
        if val is None:
            return None
        return val == "true"

    row = build_receipt(
        task_id=args.task_id,
        agent_id=args.agent_id,
        ide=args.ide,
        pytest_ok=tri(args.pytest_ok),
        clean_tree_ok=tri(args.clean_tree_ok),
        complete_ok=tri(args.complete_ok),
        write_file=not args.no_write,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
