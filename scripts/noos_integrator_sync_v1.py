#!/usr/bin/env python3
"""Local-first task arbitration for Copilot and other IDE agents on the same Mac."""

from __future__ import annotations

import argparse
import copy
import fcntl
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from integrator_runtime_paths_v1 import (
    PROTOCOL_PATH,
    integrator_home_mirror_path,
    integrator_lock_path,
    integrator_state_path,
)

ACTIVE_TASK_STATUSES = {"claimed", "in_progress", "blocked"}
DEFAULT_PROTOCOL = {
    "schema": "noos-integrator-role-v1",
    "version": "1.0.0",
    "claim_ttl_minutes": 90,
    "stale_agent_minutes": 30,
}
SUPABASE_TABLE = "noos_integrator_agent_state"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _age_minutes(value: str | None, *, now: datetime | None = None) -> float | None:
    stamp = parse_iso(value)
    if stamp is None:
        return None
    ref = now or datetime.now(timezone.utc)
    return round((ref - stamp).total_seconds() / 60.0, 2)


def _repo_branch() -> str:
    proc = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    branch = proc.stdout.strip()
    return branch or os.environ.get("GIT_BRANCH", "unknown")


def load_protocol() -> dict[str, Any]:
    if not PROTOCOL_PATH.is_file():
        return copy.deepcopy(DEFAULT_PROTOCOL)
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def _default_state() -> dict[str, Any]:
    protocol = load_protocol()
    return {
        "schema": "noos-integrator-state-v1",
        "version": "1.0.0",
        "updated_at": utc_now(),
        "repo": ROOT.name,
        "repo_root": str(ROOT),
        "branch": _repo_branch(),
        "coordinator": {
            "agent_role": "noos-integrator",
            "protocol_path": str(PROTOCOL_PATH.relative_to(ROOT)),
            "state_path": str(integrator_state_path()),
            "home_mirror_path": str(integrator_home_mirror_path()),
            "one_law": protocol.get("one_law"),
        },
        "tasks": [],
        "agents": [],
        "summary": {
            "open": 0,
            "claimed": 0,
            "in_progress": 0,
            "blocked": 0,
            "done": 0,
            "stale_claims": 0,
            "active_agents": 0,
        },
    }


def _state_path() -> Path:
    return integrator_state_path()


def _lock_path() -> Path:
    return integrator_lock_path()


def read_state() -> dict[str, Any]:
    path = _state_path()
    if not path.is_file():
        return _default_state()
    return json.loads(path.read_text(encoding="utf-8"))


def _write_state(state: dict[str, Any]) -> None:
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


@contextmanager
def locked_state() -> Iterator[dict[str, Any]]:
    lock_path = _lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        state = read_state()
        try:
            yield state
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _task_sort_key(task: dict[str, Any]) -> tuple[str, str]:
    priority = str(task.get("priority") or "P2")
    return priority, str(task.get("task_id") or "")


def _normalize_scope_files(values: list[str] | None) -> list[str]:
    cleaned = sorted({str(v).strip() for v in (values or []) if str(v).strip()})
    return cleaned


def _find_agent(state: dict[str, Any], agent_id: str) -> dict[str, Any] | None:
    for agent in state.get("agents") or []:
        if agent.get("agent_id") == agent_id:
            return agent
    return None


def _find_task(state: dict[str, Any], task_id: str) -> dict[str, Any] | None:
    for task in state.get("tasks") or []:
        if task.get("task_id") == task_id:
            return task
    return None


def _touch_agent(
    state: dict[str, Any],
    *,
    agent_id: str,
    display_name: str | None = None,
    ide: str | None = None,
    role: str | None = None,
    workspace_path: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    now = utc_now()
    agent = _find_agent(state, agent_id)
    if agent is None:
        agent = {
            "agent_id": agent_id,
            "display_name": display_name or agent_id,
            "ide": ide or "unknown",
            "role": role or "executor",
            "status": status or "active",
            "branch": _repo_branch(),
            "workspace_path": workspace_path or str(ROOT),
            "last_seen_at": now,
            "current_task_ids": [],
        }
        state.setdefault("agents", []).append(agent)
    else:
        if display_name:
            agent["display_name"] = display_name
        if ide:
            agent["ide"] = ide
        if role:
            agent["role"] = role
        if workspace_path:
            agent["workspace_path"] = workspace_path
        if status:
            agent["status"] = status
        agent["branch"] = _repo_branch()
        agent["last_seen_at"] = now
    return agent


def _append_history(task: dict[str, Any], *, action: str, agent_id: str, note: str | None = None) -> None:
    task.setdefault("history", []).append(
        {
            "at": utc_now(),
            "action": action,
            "agent_id": agent_id,
            "note": note or "",
        }
    )


def _is_stale_task(task: dict[str, Any], protocol: dict[str, Any], *, now: datetime | None = None) -> bool:
    if task.get("status") not in ACTIVE_TASK_STATUSES:
        return False
    age = _age_minutes(task.get("heartbeat_at") or task.get("claimed_at"), now=now)
    ttl = float(protocol.get("claim_ttl_minutes") or DEFAULT_PROTOCOL["claim_ttl_minutes"])
    return age is not None and age > ttl


def _scope_conflicts(
    state: dict[str, Any],
    protocol: dict[str, Any],
    *,
    scope_files: list[str],
    agent_id: str,
    task_id: str,
) -> list[dict[str, Any]]:
    if not scope_files:
        return []
    requested = set(scope_files)
    conflicts: list[dict[str, Any]] = []
    for task in state.get("tasks") or []:
        if task.get("task_id") == task_id:
            continue
        if task.get("claimed_by") == agent_id:
            continue
        if task.get("status") not in ACTIVE_TASK_STATUSES:
            continue
        if _is_stale_task(task, protocol):
            continue
        overlap = requested.intersection(task.get("scope_files") or [])
        if overlap:
            conflicts.append(
                {
                    "task_id": task.get("task_id"),
                    "claimed_by": task.get("claimed_by"),
                    "scope_overlap": sorted(overlap),
                    "status": task.get("status"),
                }
            )
    return conflicts


def _recompute_summary(state: dict[str, Any]) -> dict[str, Any]:
    protocol = load_protocol()
    now = datetime.now(timezone.utc)
    summary = {
        "open": 0,
        "claimed": 0,
        "in_progress": 0,
        "blocked": 0,
        "done": 0,
        "released": 0,
        "cancelled": 0,
        "stale_claims": 0,
        "active_agents": 0,
        "stale_agents": 0,
    }
    for task in state.get("tasks") or []:
        status = str(task.get("status") or "open")
        summary[status] = summary.get(status, 0) + 1
        if _is_stale_task(task, protocol, now=now):
            summary["stale_claims"] += 1
    stale_agent_minutes = float(protocol.get("stale_agent_minutes") or DEFAULT_PROTOCOL["stale_agent_minutes"])
    for agent in state.get("agents") or []:
        age = _age_minutes(agent.get("last_seen_at"), now=now)
        if age is None or age <= stale_agent_minutes:
            summary["active_agents"] += 1
        else:
            summary["stale_agents"] += 1
    state["summary"] = summary
    state["updated_at"] = utc_now()
    state["branch"] = _repo_branch()
    return summary


def _supabase_config() -> tuple[str, str] | None:
    url = os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""
    key = os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    if not url or not key:
        return None
    return url.rstrip("/"), key


def _supabase_enabled() -> bool:
    return os.environ.get("NOOS_INTEGRATOR_SUPABASE_SYNC", "").strip().lower() in {"1", "true", "yes", "on"}


def _mirror_supabase(state: dict[str, Any]) -> dict[str, Any]:
    cfg = _supabase_config()
    if not cfg:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    base, key = cfg
    row = {
        "repo": state["repo"],
        "branch": state["branch"],
        "updated_at": state["updated_at"],
        "summary": state["summary"],
        "coordinator": state["coordinator"],
        "state": state,
    }
    req = urllib.request.Request(
        f"{base}/rest/v1/{SUPABASE_TABLE}?on_conflict=repo",
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
            item = body[0] if isinstance(body, list) and body else body
            return {"ok": True, "status": resp.status, "id": item.get("id")}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code in (404, 406):
            return {"ok": False, "skipped": True, "reason": "supabase_table_missing", "status": exc.code}
        return {"ok": False, "status": exc.code, "error": detail[:300]}


def _mirror_outputs(state: dict[str, Any], *, force_supabase: bool = False) -> dict[str, Any]:
    summary = _recompute_summary(state)
    _write_state(state)

    home = integrator_home_mirror_path()
    home.parent.mkdir(parents=True, exist_ok=True)
    home.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    result = {
        "ok": True,
        "state_path": str(_state_path()),
        "home_mirror_path": str(home),
        "summary": summary,
    }
    if force_supabase or _supabase_enabled():
        result["supabase"] = _mirror_supabase(state)
    else:
        result["supabase"] = {"ok": False, "skipped": True, "reason": "supabase_sync_disabled"}
    return result


def cmd_init(args: argparse.Namespace) -> int:
    with locked_state() as state:
        if args.force:
            state.clear()
            state.update(_default_state())
        else:
            state.update(read_state())
        result = _mirror_outputs(state, force_supabase=args.mirror_supabase)
    print(json.dumps(result, indent=2))
    return 0


def cmd_register_agent(args: argparse.Namespace) -> int:
    with locked_state() as state:
        _touch_agent(
            state,
            agent_id=args.agent_id,
            display_name=args.display_name,
            ide=args.ide,
            role=args.role,
            workspace_path=args.workspace_path,
            status=args.status,
        )
        result = _mirror_outputs(state, force_supabase=args.mirror_supabase)
    print(json.dumps(result, indent=2))
    return 0


def cmd_open_task(args: argparse.Namespace) -> int:
    with locked_state() as state:
        _touch_agent(
            state,
            agent_id=args.agent_id,
            display_name=args.agent_id,
            ide=args.ide,
            role="integrator",
            workspace_path=str(ROOT),
        )
        task = _find_task(state, args.task_id)
        scope_files = _normalize_scope_files(args.scope_file)
        if task is None:
            task = {
                "task_id": args.task_id,
                "title": args.title,
                "status": "open",
                "priority": args.priority,
                "lane": args.lane,
                "scope_files": scope_files,
                "acceptance": args.acceptance or "",
                "created_at": utc_now(),
                "updated_at": utc_now(),
                "claimed_by": None,
            }
            state.setdefault("tasks", []).append(task)
        else:
            task["title"] = args.title or task.get("title")
            task["priority"] = args.priority or task.get("priority")
            task["lane"] = args.lane or task.get("lane")
            if scope_files:
                task["scope_files"] = scope_files
            if args.acceptance:
                task["acceptance"] = args.acceptance
            task["updated_at"] = utc_now()
        _append_history(task, action="open_task", agent_id=args.agent_id, note=args.note)
        result = _mirror_outputs(state, force_supabase=args.mirror_supabase)
        result["task"] = task
    print(json.dumps(result, indent=2))
    return 0


def cmd_claim(args: argparse.Namespace) -> int:
    protocol = load_protocol()
    with locked_state() as state:
        agent = _touch_agent(
            state,
            agent_id=args.agent_id,
            display_name=args.agent_id,
            ide=args.ide,
            role=args.role,
            workspace_path=str(ROOT),
        )
        task = _find_task(state, args.task_id)
        if task is None:
            task = {
                "task_id": args.task_id,
                "title": args.title,
                "priority": args.priority,
                "lane": args.lane,
                "created_at": utc_now(),
                "history": [],
            }
            state.setdefault("tasks", []).append(task)

        scope_files = _normalize_scope_files(args.scope_file or task.get("scope_files") or [])
        conflicts = _scope_conflicts(
            state,
            protocol,
            scope_files=scope_files,
            agent_id=args.agent_id,
            task_id=args.task_id,
        )
        if conflicts:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "reason": "scope_conflict",
                        "conflicts": conflicts,
                        "state_path": str(_state_path()),
                    },
                    indent=2,
                )
            )
            return 2

        owner = task.get("claimed_by")
        if owner and owner != args.agent_id and task.get("status") in ACTIVE_TASK_STATUSES and not _is_stale_task(task, protocol):
            print(
                json.dumps(
                    {
                        "ok": False,
                        "reason": "task_already_claimed",
                        "task_id": args.task_id,
                        "claimed_by": owner,
                        "state_path": str(_state_path()),
                    },
                    indent=2,
                )
            )
            return 2

        now = utc_now()
        task["title"] = args.title or task.get("title")
        task["priority"] = args.priority or task.get("priority") or "P2"
        task["lane"] = args.lane or task.get("lane") or "NOETFELD-OS"
        task["status"] = args.status
        task["scope_files"] = scope_files
        task["acceptance"] = args.acceptance or task.get("acceptance") or ""
        task["claimed_by"] = args.agent_id
        task["claimed_at"] = now
        task["heartbeat_at"] = now
        task["source_ide"] = args.ide
        task["branch"] = _repo_branch()
        task["updated_at"] = now
        _append_history(task, action="claim", agent_id=args.agent_id, note=args.note)

        current = set(agent.get("current_task_ids") or [])
        current.add(args.task_id)
        agent["current_task_ids"] = sorted(current)

        result = _mirror_outputs(state, force_supabase=args.mirror_supabase)
        result["task"] = task
    print(json.dumps(result, indent=2))
    return 0


def cmd_heartbeat(args: argparse.Namespace) -> int:
    with locked_state() as state:
        agent = _touch_agent(
            state,
            agent_id=args.agent_id,
            display_name=args.agent_id,
            ide=args.ide,
            role=args.role,
            workspace_path=str(ROOT),
        )
        task = None
        if args.task_id:
            task = _find_task(state, args.task_id)
            if task is None:
                print(json.dumps({"ok": False, "reason": "task_not_found", "task_id": args.task_id}, indent=2))
                return 2
            task["heartbeat_at"] = utc_now()
            task["updated_at"] = utc_now()
            _append_history(task, action="heartbeat", agent_id=args.agent_id, note=args.note)
            current = set(agent.get("current_task_ids") or [])
            current.add(args.task_id)
            agent["current_task_ids"] = sorted(current)
        result = _mirror_outputs(state, force_supabase=args.mirror_supabase)
        if task is not None:
            result["task"] = task
    print(json.dumps(result, indent=2))
    return 0


def _finalize_task(
    state: dict[str, Any],
    *,
    agent_id: str,
    task_id: str,
    status: str,
    note: str | None,
    action: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    task = _find_task(state, task_id)
    if task is None:
        return None, None
    owner = task.get("claimed_by")
    protocol = load_protocol()
    if owner and owner != agent_id and task.get("status") in ACTIVE_TASK_STATUSES and not _is_stale_task(task, protocol):
        return task, {"ok": False, "reason": "owned_by_other_agent", "claimed_by": owner, "task_id": task_id}

    task["status"] = status
    task["updated_at"] = utc_now()
    if status == "done":
        task["completed_at"] = utc_now()
    task["released_at"] = utc_now()
    task["released_by"] = agent_id
    task["claimed_by"] = None
    _append_history(task, action=action, agent_id=agent_id, note=note)

    agent = _find_agent(state, agent_id)
    if agent is not None:
        agent["current_task_ids"] = [item for item in agent.get("current_task_ids") or [] if item != task_id]
        agent["last_seen_at"] = utc_now()
    return task, None


def cmd_complete(args: argparse.Namespace) -> int:
    with locked_state() as state:
        _touch_agent(state, agent_id=args.agent_id, display_name=args.agent_id, ide=args.ide, role=args.role)
        task, error = _finalize_task(
            state,
            agent_id=args.agent_id,
            task_id=args.task_id,
            status="done",
            note=args.note,
            action="complete",
        )
        if error:
            print(json.dumps(error, indent=2))
            return 2
        if task is None:
            print(json.dumps({"ok": False, "reason": "task_not_found", "task_id": args.task_id}, indent=2))
            return 2
        result = _mirror_outputs(state, force_supabase=args.mirror_supabase)
        result["task"] = task
    print(json.dumps(result, indent=2))
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    with locked_state() as state:
        _touch_agent(state, agent_id=args.agent_id, display_name=args.agent_id, ide=args.ide, role=args.role)
        task, error = _finalize_task(
            state,
            agent_id=args.agent_id,
            task_id=args.task_id,
            status="open",
            note=args.note,
            action="release",
        )
        if error:
            print(json.dumps(error, indent=2))
            return 2
        if task is None:
            print(json.dumps({"ok": False, "reason": "task_not_found", "task_id": args.task_id}, indent=2))
            return 2
        result = _mirror_outputs(state, force_supabase=args.mirror_supabase)
        result["task"] = task
    print(json.dumps(result, indent=2))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    with locked_state() as state:
        _recompute_summary(state)
        _write_state(state)
        if args.json:
            print(json.dumps(state, indent=2))
        else:
            print(json.dumps({"summary": state["summary"], "tasks": sorted(state.get("tasks") or [], key=_task_sort_key)}, indent=2))
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    with locked_state() as state:
        result = _mirror_outputs(state, force_supabase=args.mirror_supabase)
    print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NOOS integrator coordination layer")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Create or refresh the local integrator state")
    init_p.add_argument("--force", action="store_true")
    init_p.add_argument("--mirror-supabase", action="store_true")
    init_p.set_defaults(func=cmd_init)

    register_p = sub.add_parser("register-agent", help="Register an IDE agent in the integrator state")
    register_p.add_argument("--agent-id", required=True)
    register_p.add_argument("--display-name")
    register_p.add_argument("--ide", required=True)
    register_p.add_argument("--role", default="executor")
    register_p.add_argument("--workspace-path")
    register_p.add_argument("--status", default="active")
    register_p.add_argument("--mirror-supabase", action="store_true")
    register_p.set_defaults(func=cmd_register_agent)

    open_p = sub.add_parser("open-task", help="Create or update an open task for other agents to claim")
    open_p.add_argument("--agent-id", required=True)
    open_p.add_argument("--ide", default="copilot-cli")
    open_p.add_argument("--task-id", required=True)
    open_p.add_argument("--title", required=True)
    open_p.add_argument("--priority", default="P2")
    open_p.add_argument("--lane", default="NOETFELD-OS")
    open_p.add_argument("--scope-file", action="append", default=[])
    open_p.add_argument("--acceptance")
    open_p.add_argument("--note")
    open_p.add_argument("--mirror-supabase", action="store_true")
    open_p.set_defaults(func=cmd_open_task)

    claim_p = sub.add_parser("claim", help="Claim a task and declare file scope")
    claim_p.add_argument("--agent-id", required=True)
    claim_p.add_argument("--ide", required=True)
    claim_p.add_argument("--role", default="executor")
    claim_p.add_argument("--task-id", required=True)
    claim_p.add_argument("--title")
    claim_p.add_argument("--priority", default="P2")
    claim_p.add_argument("--lane", default="NOETFELD-OS")
    claim_p.add_argument("--scope-file", action="append", default=[])
    claim_p.add_argument("--acceptance")
    claim_p.add_argument("--status", choices=["claimed", "in_progress", "blocked"], default="in_progress")
    claim_p.add_argument("--note")
    claim_p.add_argument("--mirror-supabase", action="store_true")
    claim_p.set_defaults(func=cmd_claim)

    heartbeat_p = sub.add_parser("heartbeat", help="Refresh an agent or task heartbeat")
    heartbeat_p.add_argument("--agent-id", required=True)
    heartbeat_p.add_argument("--ide", required=True)
    heartbeat_p.add_argument("--role", default="executor")
    heartbeat_p.add_argument("--task-id")
    heartbeat_p.add_argument("--note")
    heartbeat_p.add_argument("--mirror-supabase", action="store_true")
    heartbeat_p.set_defaults(func=cmd_heartbeat)

    complete_p = sub.add_parser("complete", help="Mark a task done and release the claim")
    complete_p.add_argument("--agent-id", required=True)
    complete_p.add_argument("--ide", required=True)
    complete_p.add_argument("--role", default="executor")
    complete_p.add_argument("--task-id", required=True)
    complete_p.add_argument("--note")
    complete_p.add_argument("--mirror-supabase", action="store_true")
    complete_p.set_defaults(func=cmd_complete)

    release_p = sub.add_parser("release", help="Release a task back to open")
    release_p.add_argument("--agent-id", required=True)
    release_p.add_argument("--ide", required=True)
    release_p.add_argument("--role", default="executor")
    release_p.add_argument("--task-id", required=True)
    release_p.add_argument("--note")
    release_p.add_argument("--mirror-supabase", action="store_true")
    release_p.set_defaults(func=cmd_release)

    summary_p = sub.add_parser("summary", help="Show current coordination summary")
    summary_p.add_argument("--json", action="store_true")
    summary_p.set_defaults(func=cmd_summary)

    sync_p = sub.add_parser("sync", help="Refresh mirrors without mutating tasks")
    sync_p.add_argument("--mirror-supabase", action="store_true")
    sync_p.set_defaults(func=cmd_sync)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
