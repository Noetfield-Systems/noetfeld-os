#!/usr/bin/env python3
"""ICL-P2-02 — mirror integrator tasks to home + optional Supabase (repo-local SSOT)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts/proof/noos-integrator-tasks-mirror-v1.json"
TASKS_TABLE = "noos_integrator_tasks"

sys.path.insert(0, str(ROOT / "scripts"))
from integrator_runtime_paths_v1 import integrator_state_path  # noqa: E402
from noos_vault_paths_v1 import load_platform_env, supabase_creds  # noqa: E402


def _supabase_post(base: str, key: str, table: str, rows: list[dict[str, Any]], *, on_conflict: str) -> dict:
    req = urllib.request.Request(
        f"{base.rstrip('/')}/rest/v1/{table}?on_conflict={on_conflict}",
        data=json.dumps(rows).encode("utf-8"),
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
            count = len(body) if isinstance(body, list) else 1
            return {"ok": True, "status": resp.status, "upserted": count}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code in (404, 406):
            return {"ok": False, "skipped": True, "reason": "supabase_table_missing", "status": exc.code}
        return {"ok": False, "status": exc.code, "error": detail[:300]}


def _sync_home_mirror(*, mirror_supabase: bool) -> dict:
    cmd = [sys.executable, str(ROOT / "scripts/noos_integrator_sync_v1.py"), "sync"]
    if mirror_supabase:
        cmd.append("--mirror-supabase")
    env = os.environ.copy()
    env.update(load_platform_env())
    if mirror_supabase:
        env["NOOS_INTEGRATOR_SUPABASE_SYNC"] = "1"
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=60, check=False, env=env)
    if not proc.stdout.strip():
        return {"ok": False, "exit_code": proc.returncode, "stderr": proc.stderr[-400:]}
    try:
        doc = json.loads(proc.stdout)
        doc["exit_code"] = proc.returncode
        return doc
    except json.JSONDecodeError:
        return {"ok": False, "exit_code": proc.returncode, "raw": proc.stdout[-500:]}


def _task_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    repo = state.get("repo") or "noetfeld-OS"
    branch = state.get("branch") or "main"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows: list[dict[str, Any]] = []
    for task in state.get("tasks") or []:
        if not isinstance(task, dict) or not task.get("task_id"):
            continue
        rows.append(
            {
                "repo": repo,
                "branch": branch,
                "task_id": task["task_id"],
                "status": task.get("status"),
                "lane": task.get("lane"),
                "priority": task.get("priority"),
                "claimed_by": task.get("claimed_by"),
                "scope_files": task.get("scope_files") or [],
                "updated_at": task.get("updated_at") or now,
                "payload": task,
            }
        )
    return rows


def mirror(*, dry_run: bool = True, mirror_supabase: bool = True) -> dict:
    state_path = integrator_state_path()
    if not state_path.is_file():
        return {"ok": False, "error": "integrator state missing", "path": str(state_path)}
    state = json.loads(state_path.read_text(encoding="utf-8"))
    tasks = state.get("tasks") or []
    task_rows = _task_rows(state)

    row: dict[str, Any] = {
        "schema": "noos-integrator-tasks-mirror-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": True,
        "dry_run": dry_run,
        "state_path": str(state_path),
        "task_count": len(tasks),
        "repo_local_ssot": True,
    }

    if dry_run:
        row["would_sync"] = "python3 scripts/noos_integrator_sync_v1.py sync --mirror-supabase"
        row["would_upsert_tasks"] = len(task_rows)
        url, key = supabase_creds()
        row["supabase_configured"] = bool(url and key)
        return row

    home_sync = _sync_home_mirror(mirror_supabase=mirror_supabase)
    row["home_mirror"] = home_sync
    row_ok = bool(home_sync.get("ok"))

    url, key = supabase_creds()
    if url and key and task_rows:
        batch = _supabase_post(url, key, TASKS_TABLE, task_rows, on_conflict="repo,task_id")
        row["tasks_table"] = batch
        if batch.get("skipped"):
            row["tasks_table_note"] = "optional table; full state still in noos_integrator_agent_state via sync"
        elif not batch.get("ok"):
            row_ok = False
    else:
        row["tasks_table"] = {
            "ok": True,
            "skipped": True,
            "reason": "no_supabase_creds_or_no_tasks",
        }

    row["ok"] = row_ok
    return row


def main() -> int:
    dry = "--apply" not in sys.argv
    row = mirror(dry_run=dry, mirror_supabase="--skip-supabase" not in sys.argv)
    if "--write-receipt" in sys.argv:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
