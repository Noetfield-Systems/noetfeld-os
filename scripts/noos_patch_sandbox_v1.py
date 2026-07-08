#!/usr/bin/env python3
"""NOOS patch sandbox v1 — bounded patch proposals; no direct main/product mutation."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

sys_path_inserted = False


def _router_config() -> dict[str, Any]:
    global sys_path_inserted  # noqa: PLW0603
    import sys

    if not sys_path_inserted:
        sys.path.insert(0, str(ROOT / "scripts"))
        sys_path_inserted = True
    from noos_model_router_v1 import load_router_config  # noqa: WPS433

    return load_router_config()


def governance_paths(config: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = config or _router_config()
    gov = cfg.get("governance") if isinstance(cfg.get("governance"), dict) else {}
    return {
        "sandbox_root": ROOT / str(gov.get("patch_sandbox_root") or ".noos-runtime/worker-kernel/patches"),
        "allowed_prefixes": [str(p) for p in (gov.get("allowed_patch_prefixes") or [])],
        "forbidden_paths": [str(p) for p in (gov.get("forbidden_patch_paths") or [])],
        "no_direct_main": bool(gov.get("no_direct_main_edits", True)),
        "checks": cfg.get("deterministic_checks") if isinstance(cfg.get("deterministic_checks"), dict) else {},
    }


def normalize_rel(path: str) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def is_allowed_target(rel_path: str, *, config: dict[str, Any] | None = None) -> tuple[bool, str | None]:
    rel = normalize_rel(rel_path)
    paths = governance_paths(config)
    for forbidden in paths["forbidden_paths"]:
        if rel == forbidden or rel.startswith(forbidden.rstrip("/") + "/"):
            return False, f"forbidden_path:{rel}"
    if not any(rel == p.rstrip("/") or rel.startswith(p) for p in paths["allowed_prefixes"]):
        return False, f"outside_allowed_prefix:{rel}"
    return True, None


def rejects_main_mutation(*, target_branch: str | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    paths = governance_paths(config)
    branch = (target_branch or "").strip().lower()
    if paths["no_direct_main"] and branch in ("main", "master"):
        return {"ok": False, "blocker_reason": "direct_main_mutation_forbidden"}
    return {"ok": True, "blocker_reason": None}


def validate_patch_proposal(
    proposal: dict[str, Any],
    *,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic gate for T2 patch proposals."""
    paths = governance_paths(config)
    checks = paths.get("checks") or {}
    patch_req = checks.get("patch_apply_requires") if isinstance(checks.get("patch_apply_requires"), dict) else {}
    max_files = int(patch_req.get("max_files") or 5)
    max_lines = int(patch_req.get("max_lines_changed") or 200)

    files = proposal.get("files") if isinstance(proposal.get("files"), list) else []
    errors: list[str] = []
    if len(files) > max_files:
        errors.append(f"max_files_exceeded:{len(files)}>{max_files}")

    total_lines = 0
    for row in files:
        if not isinstance(row, dict):
            errors.append("invalid_file_row")
            continue
        rel = str(row.get("path") or "")
        ok, reason = is_allowed_target(rel, config=config)
        if not ok:
            errors.append(reason or "path_not_allowed")
        content = str(row.get("content") or "")
        total_lines += content.count("\n") + (1 if content else 0)

    if total_lines > max_lines:
        errors.append(f"max_lines_exceeded:{total_lines}>{max_lines}")

    branch = str(proposal.get("target_branch") or "")
    main_check = rejects_main_mutation(target_branch=branch, config=config)
    if not main_check.get("ok"):
        errors.append(main_check.get("blocker_reason") or "main_forbidden")

    verdict = "PASS" if not errors else "BLOCKED_WITH_REASON"
    return {
        "schema": "noos-patch-sandbox-verdict-v1",
        "verdict": verdict,
        "errors": errors,
        "file_count": len(files),
        "line_count": total_lines,
        "max_files": max_files,
        "max_lines": max_lines,
    }


def write_sandbox_patch(
    proposal: dict[str, Any],
    *,
    op_key: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Materialize proposal under sandbox root only — never touches repo tracked paths."""
    verdict = validate_patch_proposal(proposal, config=config)
    paths = governance_paths(config)
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", op_key)[:80]
    sandbox_dir = paths["sandbox_root"] / safe
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "op_key": op_key,
        "proposal": proposal,
        "verdict": verdict,
    }
    try:
        manifest["sandbox_path"] = str(sandbox_dir.relative_to(ROOT))
    except ValueError:
        manifest["sandbox_path"] = str(sandbox_dir)
    (sandbox_dir / "proposal-v1.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for row in proposal.get("files") or []:
        if not isinstance(row, dict):
            continue
        rel = normalize_rel(str(row.get("path") or "unknown"))
        out = sandbox_dir / "files" / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(str(row.get("content") or ""), encoding="utf-8")
    manifest["written"] = True
    return manifest


def run_deterministic_grep(pattern: str, *, path: str = ".", max_matches: int = 50) -> dict[str, Any]:
    """T0 grep — local ripgrep/grep, no LLM."""
    cmd = ["rg", "-n", "--max-count", str(max_matches), pattern, path]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        cmd = ["grep", "-Rn", pattern, path]
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False, timeout=30)
    lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "match_count": len(lines),
        "matches": lines[:max_matches],
        "ok": proc.returncode in (0, 1),
    }
