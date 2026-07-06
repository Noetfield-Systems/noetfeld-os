#!/usr/bin/env python3
"""Phase C — execute motor restart recipes (machine_safe only unless --force-founder-gated)."""

from __future__ import annotations

import argparse
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
RECIPES = ROOT / "data/noos-motor-restart-recipes-v1.json"
PROOF_DIR = ROOT / "receipts/proof"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_recipes() -> dict[str, Any]:
    return json.loads(RECIPES.read_text(encoding="utf-8"))


def find_recipe(doc: dict[str, Any], recipe_id: str) -> dict[str, Any] | None:
    for row in doc.get("recipes") or []:
        if row.get("id") == recipe_id:
            return row
    return None


def probe_health(url: str, *, timeout: float = 15.0) -> dict[str, Any]:
    if not url:
        return {"ok": False, "error": "health_url_missing"}
    req = urllib.request.Request(url, headers={"User-Agent": "noos-motor-restart-v1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = {"raw": raw[:300]}
            return {"ok": resp.status == 200 and body.get("ok", True), "status": resp.status, "body": body}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": str(exc)}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def executor_env_for_recipe(recipe: dict[str, Any], *, dry_run: bool = False) -> dict[str, str]:
    env = os.environ.copy()
    if recipe.get("id") != "cf-loop-motor":
        return env
    env.setdefault("FLY_LOOP_EXECUTOR_URL", "https://noos-loop-executor.fly.dev")
    if not env.get("NOOS_LOOP_SECRET"):
        if dry_run:
            env["NOOS_LOOP_SECRET"] = "dry-run-placeholder"
        else:
            env_file = Path.home() / ".sourcea-secrets/noetfield.env"
            if env_file.is_file():
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    if line.startswith("NOOS_LOOP_SECRET="):
                        env["NOOS_LOOP_SECRET"] = line.split("=", 1)[1].strip()
                        break
    return env


def run_shell_step(step: dict[str, Any], *, dry_run: bool, extra_env: dict[str, str]) -> dict[str, Any]:
    cmd = str(step.get("command") or "").strip()
    cwd = ROOT / str(step.get("cwd") or ".")
    requires = [str(x) for x in step.get("requires_env") or []]
    missing = [k for k in requires if not extra_env.get(k)]
    if missing and not dry_run:
        return {"ok": False, "command": cmd, "error": f"missing_env:{','.join(missing)}"}
    if dry_run:
        return {"ok": True, "command": cmd, "dry_run": True}
    proc = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        env=extra_env,
        capture_output=True,
        text=True,
        check=False,
        timeout=1800,
    )
    return {
        "ok": proc.returncode == 0,
        "command": cmd,
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-500:],
        "stderr_tail": (proc.stderr or "")[-500:],
    }


def run_verify(command: str | None, *, dry_run: bool) -> dict[str, Any]:
    if not command:
        return {"ok": True, "skipped": True}
    if dry_run:
        return {"ok": True, "command": command, "dry_run": True}
    proc = subprocess.run(command, shell=True, cwd=ROOT, capture_output=True, text=True, check=False, timeout=1800)
    return {
        "ok": proc.returncode == 0,
        "command": command,
        "exit_code": proc.returncode,
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def execute_recipe(
    recipe_id: str,
    *,
    dry_run: bool = False,
    force_founder_gated: bool = False,
    write_receipt: bool = False,
) -> dict[str, Any]:
    doc = load_recipes()
    recipe = find_recipe(doc, recipe_id)
    if not recipe:
        return {"ok": False, "error": "recipe_not_found", "recipe_id": recipe_id}

    gate = str(recipe.get("gate") or "founder_gated")
    if gate == "founder_gated" and not force_founder_gated:
        return {
            "ok": False,
            "recipe_id": recipe_id,
            "gate": gate,
            "error": "founder_gated",
            "fail_closed": True,
        }

    health_before = probe_health(str(recipe.get("health_url") or ""))
    extra_env = executor_env_for_recipe(recipe, dry_run=dry_run)
    step_results: list[dict[str, Any]] = []
    for step in recipe.get("steps") or []:
        if step.get("kind") != "shell":
            continue
        step_results.append(run_shell_step(step, dry_run=dry_run, extra_env=extra_env))

    verify = run_verify(recipe.get("external_verify_command"), dry_run=dry_run)
    health_after = probe_health(str(recipe.get("health_url") or "")) if not dry_run else {"ok": True, "skipped": True}

    ok = all(s.get("ok", False) for s in step_results) and verify.get("ok", False)
    row: dict[str, Any] = {
        "schema": "noos-motor-restart-v1",
        "recipe_id": recipe_id,
        "motor": recipe.get("motor"),
        "gate": gate,
        "dry_run": dry_run,
        "executed_at": utc_now(),
        "health_before": health_before,
        "health_after": health_after,
        "steps": step_results,
        "external_verify": verify,
        "ok": ok if step_results or dry_run else False,
    }
    if write_receipt and not dry_run:
        PROOF_DIR.mkdir(parents=True, exist_ok=True)
        ts = utc_now().replace(":", "").replace("-", "")
        path = PROOF_DIR / f"noos-motor-restart-{recipe_id}-{ts}.json"
        path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(path.relative_to(ROOT))
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--recipe", required=True, help="Recipe id (cf-loop-motor, cf-deadman, fly-loop-executor)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force-founder-gated", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = execute_recipe(
        args.recipe,
        dry_run=args.dry_run,
        force_founder_gated=args.force_founder_gated,
        write_receipt=args.write_receipt,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"motor_restart · recipe={args.recipe} ok={row.get('ok')} dry_run={args.dry_run}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
