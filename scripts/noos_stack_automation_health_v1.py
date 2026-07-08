#!/usr/bin/env python3
"""Org-level stack automation health rollup — replaces cross-repo orchestrator stub."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_gha_run_health_v1 import run_gha_health  # noqa: E402

PROOF = ROOT / "receipts/proof/noos-stack-automation-health-v1.json"
CF_FLEET_HEALTH = "https://tf-cf-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
PLAN_WORKER_HEALTH = "https://trustfield-plan-worker-production.up.railway.app/health"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_json(cmd: list[str], *, timeout: int = 180) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if not proc.stdout.strip():
        return {"ok": False, "exit_code": proc.returncode, "stderr": (proc.stderr or "")[-400:]}
    try:
        doc = json.loads(proc.stdout)
        if isinstance(doc, dict):
            doc.setdefault("exit_code", proc.returncode)
        return doc
    except json.JSONDecodeError:
        return {"ok": False, "exit_code": proc.returncode, "raw": proc.stdout[-600:]}


def http_json(url: str, *, timeout: int = 25) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "NOOS-StackHealth/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except (urllib.error.HTTPError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:200]}


def rollup() -> dict[str, Any]:
    integrator = run_json([sys.executable, str(ROOT / "scripts/noos_integrator_status_v1.py")])
    autorun = run_json([sys.executable, str(ROOT / "scripts/autorun_status_v1.py"), "--json"], timeout=180)
    gha = run_gha_health()
    layers = run_json([sys.executable, str(ROOT / "scripts/observe_trustfield_parallel_layers_v1.py"), "--json"])
    registry = run_json([sys.executable, str(ROOT / "scripts/observe_trustfield_loop_registry_v1.py"), "--json"])
    cf = http_json(CF_FLEET_HEALTH)
    pw = http_json(PLAN_WORKER_HEALTH)
    pw_body = pw.get("body") or {}

    critique = autorun.get("critique") or {}
    layer_summary = layers.get("summary") or {}
    reg_summary = registry.get("summary") or {}

    surfaces = integrator.get("surfaces") or {}
    integrator_ok = bool(integrator.get("ok"))
    autorun_ok = bool(critique.get("overall_ok"))
    gha_ok = bool(gha.get("ok"))
    layers_ok = layers.get("overall_status") in ("green", "yellow") and not layer_summary.get("red")
    registry_ok = int(reg_summary.get("red") or 0) == 0

    signals = {
        "integrator_status": integrator_ok,
        "autorun_critique": autorun_ok,
        "gha_health": gha_ok,
        "eleven_layers": layers_ok,
        "trustfield_registry": registry_ok,
        "cf_fleet_tick": bool(cf.get("ok") and (cf.get("body") or {}).get("ok")),
    }
    fails = [k for k, v in signals.items() if not v]
    overall = "green" if not fails else ("yellow" if len(fails) <= 2 else "red")

    return {
        "schema": "noos-stack-automation-health-v1",
        "at": utc_now(),
        "ok": overall == "green",
        "overall_status": overall,
        "closure_token": f"NOOS_STACK_AUTOMATION: {overall}",
        "replaces_workflow": "noos-cross-repo-orchestrator.yml",
        "architecture": {
            "primary": "cloudflare_workers_cron",
            "secondary": "github_actions_enterprise",
            "tertiary": "railway_plan_worker",
        },
        "signals": signals,
        "integrator_status": {
            "ok": integrator_ok,
            "surfaces": surfaces,
            "machine_audit_line": integrator.get("machine_audit_line"),
        },
        "autorun_critique": {
            "overall_ok": critique.get("overall_ok"),
            "findings": len(critique.get("findings") or []),
            "findings_sample": (critique.get("findings") or [])[:5],
        },
        "gha_health": gha,
        "cf_motors": {
            "fleet_tick": "green" if signals["cf_fleet_tick"] else "red",
            "deadman": reg_summary.get("deadman_status"),
            "registry_overall": registry.get("overall_status"),
        },
        "railway_plan_worker": {
            "url": PLAN_WORKER_HEALTH,
            "status": pw_body.get("status"),
            "last_cycle_ok": pw_body.get("last_cycle_ok"),
            "lane_ok": pw_body.get("lane_ok"),
            "lanes_run": pw_body.get("lanes_run"),
        },
        "eleven_layers": layer_summary,
        "trustfield_registry": reg_summary,
        "fix_queue": fails,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    row = rollup()
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["closure_token"])

    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
