#!/usr/bin/env python3
"""Phase A — trigger host inventory: cloud vs Mac vs founder-manual."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
LOOPS = ROOT / "data/noos-24-7-loops-v1.json"
DISPATCH = ROOT / "data/noos-cf-dispatch-table-v1.json"
AUTORUN = ROOT / "data/autorun-workflows-v1.json"
WORKFLOW_DIR = ROOT / ".github/workflows"
INVENTORY = ROOT / "data/noos-trigger-host-inventory-v1.json"
RECEIPT = ROOT / "receipts/proof/noos-trigger-host-inventory-v1.json"
SCRIPTS = ROOT / "scripts"

SINA_PATH_PATTERNS = (
    r"Path\.home\(\)\s*/\s*[\"']\.sina",
    r"~/.sina/",
    r'"/Users/sinakazemnezhad',
    r"~/Desktop/SourceA",
    r"~/Projects/noetfeld-os",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def workflow_triggers(name: str) -> dict[str, Any]:
    path = WORKFLOW_DIR / name
    if not path.is_file():
        return {"exists": False}
    text = path.read_text(encoding="utf-8")
    return {
        "exists": True,
        "schedule": bool(re.search(r"\n\s*schedule:", text)),
        "workflow_dispatch": bool(re.search(r"\n\s*workflow_dispatch:", text)),
        "repository_dispatch": bool(re.search(r"\n\s*repository_dispatch:", text)),
        "push": bool(re.search(r"\n\s*push:", text)),
    }


def audit_sina_paths() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(SCRIPTS.glob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = [p for p in SINA_PATH_PATTERNS if re.search(p, text)]
        if hits:
            rows.append(
                {
                    "script": str(path.relative_to(ROOT)),
                    "patterns": hits,
                    "loop_critical": path.name
                    in {
                        "noos_loop_runner_v1.py",
                        "cloud_inbox_worker_v1.py",
                        "enqueue_noos_cloud_inbox_v1.py",
                        "observe_sourcea_supabase_v1.py",
                        "run_noetfield_factory_loop_v1.py",
                    },
                }
            )
    return rows


def curl_json(url: str, timeout: int = 15) -> dict[str, Any]:
    try:
        with urlopen(Request(url, headers={"User-Agent": "noos-trigger-host-inventory-v1"}), timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)}


def fly_auth_ok() -> bool:
    fly = Path.home() / ".fly/bin/fly"
    if not fly.is_file():
        return False
    proc = subprocess.run([str(fly), "auth", "whoami"], capture_output=True, text=True, check=False)
    return proc.returncode == 0


def loop_rows() -> list[dict[str, Any]]:
    loops_doc = load_json(LOOPS)
    dispatch_doc = load_json(DISPATCH)
    dispatch_by_event = {t["event_type"]: t for t in dispatch_doc.get("targets") or []}
    rows: list[dict[str, Any]] = []
    for loop in loops_doc.get("loops") or []:
        event_type = str(loop.get("event_type"))
        wf = str(loop.get("github_workflow") or "")
        dispatch = dispatch_by_event.get(event_type, {})
        triggers = workflow_triggers(wf)
        if dispatch:
            trigger_host = "cf"
            execution_host = str(dispatch_doc.get("execution_plane") or "railway:noos-loop-runner").split(":")[0]
            action = "cloud_ok"
            founder_manual = False
        elif triggers.get("schedule"):
            trigger_host = "gha"
            execution_host = "gha"
            action = "migrate_to_cloud"
            founder_manual = False
        elif triggers.get("workflow_dispatch") and not triggers.get("repository_dispatch"):
            trigger_host = "retired_gha_manual"
            execution_host = "railway"
            action = "cloud_ok_via_cf_dispatch_table"
            founder_manual = False
        else:
            trigger_host = "unknown"
            execution_host = "unknown"
            action = "audit"
            founder_manual = False
        rows.append(
            {
                "kind": "loop",
                "loop_id": loop.get("id"),
                "event_type": event_type,
                "github_workflow": wf,
                "interval_minutes": loop.get("interval_minutes"),
                "trigger_host": trigger_host,
                "execution_host": execution_host,
                "cf_dispatch_id": dispatch.get("dispatch_id"),
                "workflow_triggers": triggers,
                "action": action,
                "founder_manual_by_design": founder_manual,
            }
        )
    return rows


def autorun_rows() -> list[dict[str, Any]]:
    doc = load_json(AUTORUN)
    rows: list[dict[str, Any]] = []
    for wf in doc.get("workflows") or []:
        wid = str(wf.get("id"))
        probe = wf.get("probe") or {}
        ptype = str(probe.get("type") or "")
        if ptype in {"url_sweep_readonly"} and "workers.dev" in json.dumps(probe):
            trigger_host = "cf"
            action = "cloud_ok"
            founder_manual = False
        elif ptype == "github_schedule_probe":
            trigger_host = "gha"
            action = "migrate_to_cloud_or_retire"
            founder_manual = False
        elif ptype == "manual_dispatch_only":
            trigger_host = "retired_gha_manual"
            action = "cloud_ok_cf_motor_canary"
            founder_manual = False
        elif ptype.startswith("supabase"):
            trigger_host = "cf"
            execution_host = "railway"
            action = "cloud_ok_when_cf_railway_live"
            founder_manual = False
        elif "verify_command" in wf and "~/Desktop/SourceA" in str(wf.get("verify_command")):
            trigger_host = "script"
            action = "founder_manual_by_design"
            founder_manual = True
        elif "run_command" in wf and str(wf.get("run_command", "")).startswith("make "):
            trigger_host = "script"
            execution_host = "railway"
            action = "cloud_ok_when_cf_railway_live"
            founder_manual = False
        else:
            trigger_host = "observe_only"
            action = "no_trigger"
            founder_manual = False
        rows.append(
            {
                "kind": "autorun_workflow",
                "workflow_id": wid,
                "title": wf.get("title"),
                "probe_type": ptype,
                "trigger_host": trigger_host,
                "action": action,
                "founder_manual_by_design": founder_manual,
                "note": wf.get("verify_command") or wf.get("run_command"),
            }
        )
    return rows


def mac_founder_manual_rows() -> list[dict[str, Any]]:
    return [
        {
            "kind": "integrator",
            "id": "cursor_local_mac",
            "trigger_host": "cursor",
            "action": "founder_manual_by_design",
            "founder_manual_by_design": True,
            "reason": "IDE lane claim/closeout; not a 24/7 loop motor",
        },
        {
            "kind": "integrator",
            "id": "copilot_cli_mac",
            "trigger_host": "cursor",
            "action": "founder_manual_by_design",
            "founder_manual_by_design": True,
            "reason": "Cross-IDE integrator mirror ~/.sina/noos-integrator-state-v1.json",
        },
        {
            "kind": "observation",
            "id": "noos_live_sync_gate",
            "trigger_host": "mac",
            "action": "founder_manual_by_design",
            "founder_manual_by_design": True,
            "reason": "Reads Mac paths for website/SourceA/studio; run on demand not scheduled",
        },
        {
            "kind": "commercial",
            "id": "nw1_outbound_send",
            "trigger_host": "founder",
            "action": "founder_manual_by_design",
            "founder_manual_by_design": True,
            "reason": "L7 founder gate; ~/.sina/nw1-outbound-send-receipt-v1.json",
        },
        {
            "kind": "gha_ci",
            "id": "gel-ci",
            "trigger_host": "gha",
            "action": "cloud_ok",
            "founder_manual_by_design": False,
            "reason": "PR/push CI only; not 24/7 loop motor",
        },
        {
            "kind": "gha_ci",
            "id": "noos_machine_loops_weekly",
            "trigger_host": "retired_gha_manual",
            "action": "cloud_ok_manual_dispatch",
            "founder_manual_by_design": False,
            "reason": "Weekly GHA schedule retired 2026-07-06; push + workflow_dispatch only",
        },
    ]


def cloud_probes() -> dict[str, Any]:
    cf_health = curl_json("https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health")
    railway_health = curl_json("https://noos-loop-runner-production.up.railway.app/health")
    cf_legacy_github = "github_token_ready" in cf_health
    cf_railway_motor = cf_health.get("execution_plane") == "railway:noos-loop-runner" or cf_health.get("schema") == "noos-loop-motor-health-v1"
    railway_ok = railway_health.get("service") == "noos-loop-runner" and railway_health.get("ok") is True
    return {
        "cf_loop_motor": {
            "url": "https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health",
            "ok": cf_health.get("ok") is True,
            "legacy_github_dispatch": cf_legacy_github,
            "railway_motor_deployed": cf_railway_motor and not cf_legacy_github,
            "loop_runner_url_ready": cf_health.get("loop_runner_url_ready"),
            "target_count": cf_health.get("target_count") or len(cf_health.get("loops") or []),
            "step_7_secrets_on_worker": cf_health.get("loop_runner_url_ready") is True,
        },
        "railway_loop_runner": {
            "url": "https://noos-loop-runner-production.up.railway.app/health",
            "ok": railway_ok,
            "wrong_image": railway_health.get("service") not in (None, "noos-loop-runner") and not railway_ok,
            "raw_service": railway_health.get("service"),
            "step_8_deploy_required": not railway_ok,
        },
        "fly_auth": fly_auth_ok(),
        "fly_l4_deferred": not fly_auth_ok(),
        "phase_a_steps_6_10": {
            "cf_paid_plan": "founder_confirm",
            "cf_secrets_wired": cf_health.get("loop_runner_url_ready") is True,
            "railway_loop_runner_live": railway_ok,
            "supabase_on_railway": "founder_confirm_railway_dashboard",
            "fly_l4": "deferred" if not fly_auth_ok() else "ready",
        },
    }


def build_inventory() -> dict[str, Any]:
    loops = loop_rows()
    autorun = autorun_rows()
    mac_rows = mac_founder_manual_rows()
    sina_audit = audit_sina_paths()
    all_rows = loops + autorun + mac_rows
    mac_cursor_unmarked = [
        r
        for r in all_rows
        if r.get("trigger_host") in {"mac", "cursor", "script"}
        and not r.get("founder_manual_by_design")
        and r.get("action") != "cloud_ok_when_cf_railway_live"
    ]
    migrate = [r for r in all_rows if r.get("action", "").startswith("migrate")]
    probes = cloud_probes()
    phase_a_gate = len(mac_cursor_unmarked) == 0
    return {
        "schema": "noos-trigger-host-inventory-v1",
        "inventory_at": utc_now(),
        "authority": "LIVING_SYSTEM_99_PLAN_PHASE_A",
        "founder_sign": {"required": True, "status": "pending"},
        "loops": loops,
        "autorun_workflows": autorun,
        "founder_manual_entries": mac_rows,
        "sina_path_audit": sina_audit,
        "cloud_probes": probes,
        "summary": {
            "loop_count": len(loops),
            "cf_dispatched_loops": sum(1 for r in loops if r.get("trigger_host") == "cf"),
            "migrate_remaining": len(migrate),
            "mac_cursor_unmarked": len(mac_cursor_unmarked),
            "sina_path_scripts": len(sina_audit),
            "phase_a_gate_ok": phase_a_gate,
        },
        "migrate_remaining": migrate,
        "mac_cursor_unmarked": mac_cursor_unmarked,
        "ok": phase_a_gate,
        "report_line": (
            f"trigger_host_inventory · cf_loops={sum(1 for r in loops if r.get('trigger_host') == 'cf')} "
            f"unmarked_mac={len(mac_cursor_unmarked)} gate={phase_a_gate}"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-data", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build_inventory()
    if args.write_data:
        INVENTORY.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["data_path"] = str(INVENTORY.relative_to(ROOT))
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT.relative_to(ROOT))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
