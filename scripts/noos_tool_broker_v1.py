#!/usr/bin/env python3
"""NOOS Tool Broker v1 — allowlist-only named wrappers for kernel / Healer L2 / P1 agents.

M1: sole execution path for governed tools; unified receipt stream + L11 cost cap.
M2: no shell strings; egress deny-all except git remote.
M3: open_pr_task_branch, git_push_task_branch with in-wrapper branch pattern.
M4: tainted-commits rejection on git wrappers.
M5: aider_auto_commit pinned to worktree; Aider shell disabled via config.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_model_router_v1 import enforce_budget, estimate_cost, load_router_config  # noqa: E402
from noos_patch_sandbox_v1 import run_deterministic_grep  # noqa: E402
from noos_receipt_writer_v1 import write_receipt  # noqa: E402

CONFIG_PATH = ROOT / "data/noos-tool-broker-config-v1.json"
TAINTED_PATH = ROOT / "data/tainted-commits-v1.json"

FORBIDDEN_PARAM_KEYS = frozenset({"shell", "command", "cmd", "argv", "exec", "bash", "sh"})


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_config() -> dict[str, Any]:
    return load_json(CONFIG_PATH)


def op_key(*, agent_id: str, tool: str, params: dict[str, Any]) -> str:
    material = json.dumps({"agent_id": agent_id, "tool": tool, "params": params}, sort_keys=True)
    return hashlib.sha256(material.encode()).hexdigest()[:24]


def _reject(reason: str, *, detail: str | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "blocked": True,
        "blocker_reason": reason,
        "detail": detail,
    }


def validate_params(params: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(params, dict):
        return _reject("invalid_params", detail="params must be object")
    for key in params:
        if str(key).lower() in FORBIDDEN_PARAM_KEYS:
            return _reject("shell_string_forbidden", detail=f"param key {key!r} not allowed")
        val = params[key]
        if isinstance(val, str) and re.search(r"\b(rm\s+-rf|curl\s+|wget\s+|bash\s+-c|;\s*)\b", val, re.I):
            return _reject("shell_string_forbidden", detail=f"suspicious string in {key}")
    return None


def validate_tool_name(tool: str, config: dict[str, Any]) -> dict[str, Any] | None:
    allowlist = config.get("allowlist") if isinstance(config.get("allowlist"), list) else []
    if tool not in allowlist:
        return _reject("tool_not_in_allowlist", detail=tool)
    return None


def load_tainted_shas() -> list[str]:
    row = load_json(TAINTED_PATH)
    shas = row.get("shas") if isinstance(row.get("shas"), list) else []
    return [str(s).strip() for s in shas if s]


def git_run(args: list[str], *, cwd: Path, timeout: int = 60) -> dict[str, Any]:
    """Fixed-argv git only — egress allow git remote."""
    if not args or args[0] != "git":
        return _reject("egress_denied", detail="only git subprocess allowed")
    try:
        proc = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return _reject("git_execution_failed", detail=str(exc))


def is_descendant_of_tainted(sha: str, *, cwd: Path, tainted: list[str]) -> str | None:
    for bad in tainted:
        if not bad:
            continue
        if sha.startswith(bad) or bad.startswith(sha):
            return bad
        proc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", bad, sha],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return bad
    return None


def assert_not_tainted(*, cwd: Path, config: dict[str, Any]) -> dict[str, Any] | None:
    tainted = load_tainted_shas()
    if not tainted:
        return None
    head = git_run(["git", "rev-parse", "HEAD"], cwd=cwd)
    if not head.get("ok"):
        return _reject("tainted_check_failed", detail=head.get("stderr") or "no HEAD")
    hit = is_descendant_of_tainted(head["stdout"], cwd=cwd, tainted=tainted)
    if hit:
        return _reject("tainted_commit", detail=f"HEAD descends from {hit}")
    return None


def validate_branch_name(name: str, config: dict[str, Any]) -> dict[str, Any] | None:
    protected = {str(b) for b in (config.get("protected_branches") or ["main", "master"])}
    if name in protected:
        return _reject("protected_branch", detail=name)
    pattern = str(config.get("branch_pattern") or "")
    if pattern and not re.fullmatch(pattern, name):
        return _reject("branch_pattern_violation", detail=name)
    return None


def tool_grep(params: dict[str, Any], *, cwd: Path) -> dict[str, Any]:
    return run_deterministic_grep(
        str(params.get("pattern") or ""),
        path=str(params.get("path") or "scripts"),
        max_matches=int(params.get("max_matches") or 20),
    )


def tool_check(params: dict[str, Any], *, cwd: Path) -> dict[str, Any]:
    target = str(params.get("path") or "")
    p = cwd / target if not Path(target).is_absolute() else Path(target)
    exists = p.is_file() or p.is_dir()
    return {"check": "path_exists", "path": target, "ok": exists, "exit_code": 0 if exists else 1}


def tool_pytest_q(params: dict[str, Any], *, cwd: Path) -> dict[str, Any]:
    paths = params.get("paths") if isinstance(params.get("paths"), list) else []
    args = [sys.executable, "-m", "pytest", "-q", *[str(p) for p in paths]]
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=300, check=False)
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-2000:],
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return _reject("pytest_failed", detail=str(exc))


def tool_git_status(params: dict[str, Any], *, cwd: Path) -> dict[str, Any]:
    short = bool(params.get("short", True))
    args = ["git", "status", "--short"] if short else ["git", "status"]
    return git_run(args, cwd=cwd)


def tool_git_rev_parse(params: dict[str, Any], *, cwd: Path) -> dict[str, Any]:
    ref = str(params.get("ref") or "HEAD")
    args = ["git", "rev-parse", ref]
    if params.get("short"):
        args.insert(2, "--short")
    return git_run(args, cwd=cwd)


def tool_git_log_oneline(params: dict[str, Any], *, cwd: Path) -> dict[str, Any]:
    n = int(params.get("n") or 10)
    return git_run(["git", "log", "--oneline", f"-{n}"], cwd=cwd)


def tool_open_pr_task_branch(params: dict[str, Any], *, cwd: Path, config: dict[str, Any]) -> dict[str, Any]:
    branch = str(params.get("branch_name") or params.get("branch") or "")
    if not branch:
        return _reject("missing_branch_name")
    err = validate_branch_name(branch, config)
    if err:
        return err
    taint = assert_not_tainted(cwd=cwd, config=config)
    if taint:
        return taint
    exists = git_run(["git", "rev-parse", "--verify", branch], cwd=cwd)
    if exists.get("ok"):
        checkout = git_run(["git", "checkout", branch], cwd=cwd)
        if not checkout.get("ok"):
            return checkout
        return {"ok": True, "action": "checked_out_existing", "branch": branch}
    base = str(params.get("base_ref") or "HEAD")
    create = git_run(["git", "checkout", "-b", branch, base], cwd=cwd)
    if not create.get("ok"):
        return create
    return {"ok": True, "action": "created_branch", "branch": branch, "base_ref": base}


def tool_git_push_task_branch(params: dict[str, Any], *, cwd: Path, config: dict[str, Any]) -> dict[str, Any]:
    branch = str(params.get("branch_name") or params.get("branch") or "")
    remote = str(params.get("remote") or "origin")
    if not branch:
        return _reject("missing_branch_name")
    err = validate_branch_name(branch, config)
    if err:
        return err
    taint = assert_not_tainted(cwd=cwd, config=config)
    if taint:
        return taint
    current = git_run(["git", "branch", "--show-current"], cwd=cwd)
    if current.get("stdout") != branch:
        return _reject("branch_checkout_required", detail=f"on {current.get('stdout')!r} want {branch!r}")
    return git_run(["git", "push", "-u", remote, branch], cwd=cwd)


def tool_aider_auto_commit(params: dict[str, Any], *, cwd: Path, config: dict[str, Any]) -> dict[str, Any]:
    worktree = str(params.get("worktree_path") or params.get("worktree") or "")
    message = str(params.get("message") or "aider: broker auto-commit")
    if not worktree:
        return _reject("missing_worktree_path")
    wt = Path(worktree)
    if not wt.is_dir():
        return _reject("invalid_worktree", detail=worktree)
    taint = assert_not_tainted(cwd=wt, config=config)
    if taint:
        return taint
    add = git_run(["git", "add", "-A"], cwd=wt)
    if not add.get("ok"):
        return add
    commit = git_run(["git", "commit", "-m", message], cwd=wt)
    if not commit.get("ok") and "nothing to commit" in (commit.get("stdout", "") + commit.get("stderr", "")):
        return {"ok": True, "action": "nothing_to_commit", "worktree": worktree}
    if not commit.get("ok"):
        return commit
    return {"ok": True, "action": "committed", "worktree": worktree, "message": message}


HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "grep": tool_grep,
    "check": tool_check,
    "pytest_q": tool_pytest_q,
    "git_status": tool_git_status,
    "git_rev_parse": tool_git_rev_parse,
    "git_log_oneline": tool_git_log_oneline,
}


def execute_tool(tool: str, params: dict[str, Any], *, cwd: Path, config: dict[str, Any]) -> dict[str, Any]:
    if tool in ("open_pr_task_branch", "git_push_task_branch", "aider_auto_commit"):
        if tool == "open_pr_task_branch":
            return tool_open_pr_task_branch(params, cwd=cwd, config=config)
        if tool == "git_push_task_branch":
            return tool_git_push_task_branch(params, cwd=cwd, config=config)
        return tool_aider_auto_commit(params, cwd=cwd, config=config)
    handler = HANDLERS.get(tool)
    if not handler:
        return _reject("tool_not_in_allowlist", detail=tool)
    return handler(params, cwd=cwd)


def invoke(
    *,
    agent_id: str,
    tool: str,
    params: dict[str, Any] | None = None,
    worktree_root: Path | None = None,
    dry_run: bool = False,
    router_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = load_config()
    body = params if isinstance(params, dict) else {}
    cwd = worktree_root or ROOT

    started_at = utc_now()
    ok_val = op_key(agent_id=agent_id, tool=tool, params=body)

    block = validate_params(body) or validate_tool_name(tool, config)
    result: dict[str, Any]
    if block:
        result = block
    else:
        result = execute_tool(tool, body, cwd=cwd, config=config)

    router_cfg = router_config or load_router_config()
    cost_row = estimate_cost(tier="T0", tokens_in=0, tokens_out=0, config=router_cfg)
    cap = config.get("cost_cap") if isinstance(config.get("cost_cap"), dict) else {}
    max_invoke = float(cap.get("max_usd_per_invoke") or 0.05)
    cost_row["total_usd"] = min(float(cost_row.get("total_usd") or 0), max_invoke)
    budget = enforce_budget(cost_row, config=router_cfg)
    if not budget.get("ok") and result.get("ok"):
        result = _reject("max_cost_exceeded", detail=budget.get("blocker_reason"))

    finished_at = utc_now()
    status = "ok" if result.get("ok") else "blocked"
    receipt_body: dict[str, Any] = {
        "schema": "noos-tool-broker-receipt-v1",
        "version": "1.0.0",
        "op_key": ok_val,
        "agent_id": agent_id,
        "tool": tool,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": status,
        "params": body,
        "worktree_root": str(cwd),
        "cost": {
            "tier": "T0",
            "total_usd": cost_row.get("total_usd", 0),
            "within_budget": budget.get("ok"),
            "value_class": "hygiene",
            "mission_id": "M4",
        },
        "result": result,
        "enforcement": {
            "allowlist_only": True,
            "shell_forbidden": True,
            "egress": "git_remote_only",
        },
        "dry_run": dry_run,
    }
    if not dry_run:
        written = write_receipt(receipt_body, op_key=ok_val)
        receipt_body["receipt_path"] = written.get("receipt_path")
    receipt_body["ok"] = status == "ok"
    return receipt_body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="command", required=True)

    inv = sub.add_parser("invoke", help="Invoke allowlisted tool wrapper")
    inv.add_argument("--agent-id", required=True)
    inv.add_argument("--tool", required=True)
    inv.add_argument("--params", default="{}")
    inv.add_argument("--worktree-root")
    inv.add_argument("--dry-run", action="store_true")

    sub.add_parser("allowlist", help="Print allowlisted tool names")

    args = ap.parse_args()
    if args.command == "allowlist":
        cfg = load_config()
        if args.json:
            print(json.dumps(cfg.get("allowlist") or [], indent=2))
        else:
            for name in cfg.get("allowlist") or []:
                print(name)
        return 0

    params = json.loads(args.params)
    wt = Path(args.worktree_root) if args.worktree_root else None
    row = invoke(agent_id=args.agent_id, tool=args.tool, params=params, worktree_root=wt, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"broker tool={args.tool} status={row.get('status')} ok={row.get('ok')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
