#!/usr/bin/env python3
"""UPG-PLAN-01 / ICL-P2 — unified integrator status (vault + autorun + machine + mirror)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_vault_paths_v1 import (  # noqa: E402
    NOETFIELD_LOCAL_ENV,
    NOOS_LOCAL_ENV,
    parse_env_file,
    workers_api_token,
)


def _run_json(cmd: list[str], *, timeout: int = 120) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if not proc.stdout.strip():
        return {"ok": False, "exit_code": proc.returncode, "stderr": proc.stderr[-500:]}
    try:
        doc = json.loads(proc.stdout)
        if isinstance(doc, dict):
            doc.setdefault("exit_code", proc.returncode)
        return doc
    except json.JSONDecodeError:
        return {"ok": False, "exit_code": proc.returncode, "raw": proc.stdout[-800:]}


def vault_row() -> dict:
    from noos_vault_paths_v1 import load_platform_env

    merged = load_platform_env()
    noos = parse_env_file(NOOS_LOCAL_ENV)
    product = parse_env_file(NOETFIELD_LOCAL_ENV)
    token = workers_api_token(merged)
    dupes = "CLOUDFLARE_API_TOKEN" in merged and "CF_NOETFIELD_API_TOKEN" in merged and merged.get(
        "CLOUDFLARE_API_TOKEN"
    ) != merged.get("CF_NOETFIELD_API_TOKEN")
    return {
        "ok": bool(token) and not dupes,
        "noos_local_env": str(NOOS_LOCAL_ENV),
        "cf_token_set": bool(token),
        "duplicate_cloudflare_keys": dupes,
        "noos_keys": len(noos) or len([k for k in merged if k.startswith("NOOS_") or k.startswith("CF_")]),
        "product_keys": len(product) or len([k for k in merged if k.startswith("NOETFIELD_") or k == "SUPABASE_URL"]),
        "gha_env": bool(__import__("os").environ.get("GITHUB_ACTIONS") == "true"),
    }


def _receipt_summary(path: Path) -> dict:
    if not path.is_file():
        return {"ok": False, "missing": True, "path": str(path)}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return {"ok": bool(doc.get("ok", True)), "at": doc.get("at"), "schema": doc.get("schema")}
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "path": str(path)}


def status() -> dict:
    vault = vault_row()
    cf_verify = _run_json([sys.executable, str(ROOT / "scripts/verify_noos_cf_deploy_token_v1.py")])
    mirror = _run_json([sys.executable, str(ROOT / "scripts/noos_integrator_mirror_check_v1.py"), "--json"])
    motor = _run_json([sys.executable, str(ROOT / "scripts/verify_noos_motor_sustain_v1.py")])
    autorun = _run_json([sys.executable, str(ROOT / "scripts/autorun_status_v1.py"), "--json"], timeout=180)
    machine = subprocess.run(
        [sys.executable, str(ROOT / "scripts/noos_machine_loops_v1.py"), "audit"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    machine_ok = "chain_ok=True" in machine.stdout or machine.returncode == 0
    conflict = _run_json(
        [sys.executable, str(ROOT / "scripts/noos_agent_conflict_check_v1.py"), "--json"],
        timeout=30,
    )

    surfaces = {
        "vault": vault.get("ok"),
        "cf_deploy_token": cf_verify.get("ok"),
        "integrator_mirror": mirror.get("ok") and not mirror.get("drift"),
        "motor_sustain": motor.get("ok"),
        "autorun": (autorun.get("critique") or {}).get("overall_ok"),
        "machine_audit": machine_ok,
        "agent_conflicts": conflict.get("ok", True) if conflict else True,
        "tasks_mirror": _receipt_summary(ROOT / "receipts/proof/noos-integrator-tasks-mirror-v1.json").get("ok"),
        "upgrade_manifest": _receipt_summary(ROOT / "receipts/proof/noos-upgrade-manifest-publish-v1.json").get("ok"),
    }
    ok = all(surfaces.values())
    return {
        "schema": "noos-integrator-status-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": ok,
        "surfaces": surfaces,
        "vault": vault,
        "cf_deploy_token": cf_verify,
        "integrator_mirror": mirror,
        "motor_sustain": motor,
        "autorun_critique": autorun.get("critique"),
        "machine_audit_line": machine.stdout.strip().splitlines()[-1] if machine.stdout else "",
        "agent_conflicts": conflict,
        "icl_p2": {
            "tasks_mirror": _receipt_summary(ROOT / "receipts/proof/noos-integrator-tasks-mirror-v1.json"),
            "upgrade_manifest": _receipt_summary(ROOT / "receipts/proof/noos-upgrade-manifest-publish-v1.json"),
        },
    }


def main() -> int:
    row = status()
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
