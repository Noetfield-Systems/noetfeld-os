#!/usr/bin/env python3
"""Commissioning harness for deterministic plan-completion (dry-run + live evidence).

Stages:
  1) pytest determinism
  2) drain READY via dry-run dispatch+observe until IDLE or max ticks
  3) emit commissioning receipt (24h window start when LIVE)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_plan_completion_dispatch_v1 as dispatch  # noqa: E402
import noos_role_runway_dispatch_v1 as roles  # noqa: E402
import noos_runway_supervision_adapter_v1 as runway  # noqa: E402
import noos_unified_backlog_compiler_v1 as compiler  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_pytest() -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_noos_plan_completion_v1.py", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[-2000:],
        "stderr": (proc.stderr or "")[-1000:],
    }


def drain_dry_run(*, max_ticks: int = 40) -> dict[str, Any]:
    # Force dry-run drain for commissioning harness (live intake is a separate stage).
    prev = os.environ.get("NOOS_PLAN_COMPLETION_LIVE_INTAKE")
    os.environ["NOOS_PLAN_COMPLETION_LIVE_INTAKE"] = "0"
    try:
        ticks: list[dict[str, Any]] = []
        for i in range(max_ticks):
            row = dispatch.reconcile_and_dispatch(write=True)
            ticks.append(
                {
                    "i": i,
                    "verdict": (row.get("dispatch") or {}).get("verdict"),
                    "observe_completed": (row.get("observe") or {}).get("completed") or [],
                    "counts": (row.get("compile") or {}).get("counts"),
                }
            )
            if (row.get("dispatch") or {}).get("verdict") == "IDLE_NO_WORK":
                return {"ok": True, "ticks": ticks, "final": row, "idle": True}
        return {"ok": False, "ticks": ticks, "idle": False, "reason": "max_ticks"}
    finally:
        if prev is None:
            os.environ.pop("NOOS_PLAN_COMPLETION_LIVE_INTAKE", None)
        else:
            os.environ["NOOS_PLAN_COMPLETION_LIVE_INTAKE"] = prev


def live_smoke_one() -> dict[str, Any]:
    """One live intake when secrets + LIVE flag are present."""
    if os.environ.get("NOOS_PLAN_COMPLETION_LIVE_INTAKE", "").strip() not in ("1", "true", "yes"):
        return {"ok": False, "skipped": True, "reason": "LIVE_INTAKE_OFF"}
    pf = runway.preflight()
    if not pf.get("ok"):
        return {"ok": False, "skipped": True, "reason": pf.get("verdict"), "preflight": pf}
    dispatch.observe_inflight(write=True)
    row = dispatch.dispatch_once(write=True, allow_dry_run=False)
    if row.get("verdict") in {"IDLE_NO_WORK", "THROTTLED_INFLIGHT"}:
        # Backlog may already be drained — prove live path via typed role intake.
        role_row = roles.dispatch_role("research", subject="commission-live-smoke")
        return {
            "ok": bool(role_row.get("ok")) and not bool((role_row.get("ack") or {}).get("dry_run")),
            "verdict": "ROLE_LIVE_INTAKE" if role_row.get("ok") else "ROLE_LIVE_FAILED",
            "job_id": (role_row.get("ack") or {}).get("job_id"),
            "dry_run": (role_row.get("ack") or {}).get("dry_run"),
            "receipt_path": role_row.get("receipt_path"),
            "fallback_from": row.get("verdict"),
        }
    return row


def role_cycle() -> dict[str, Any]:
    out = []
    for role in ("research", "specialist", "self_heal", "orchestrator", "incident_diagnose"):
        out.append(roles.dispatch_role(role, subject="commissioning-cycle"))
    return {
        "ok": all(r.get("ok") and r.get("productive") for r in out),
        "roles": [{k: r.get(k) for k in ("role", "ok", "productive", "value_class", "receipt_path")} for r in out],
    }


def main() -> int:
    live = os.environ.get("NOOS_PLAN_COMPLETION_LIVE_INTAKE", "").strip() in ("1", "true", "yes")
    pin = runway.verify_deepseek_pin()
    pytest_row = run_pytest()
    compiled = compiler.compile_backlog(write=True)
    roles_row = role_cycle()
    live_smoke = live_smoke_one()
    drain = drain_dry_run()
    start = datetime.now(timezone.utc)
    window_end = start + timedelta(hours=24)
    receipt = {
        "schema": "noos-deterministic-plan-completion-commissioning-v1",
        "at": utc_now(),
        "canon_version": "FOUNDER_CANON_v1+MACHINE_LOOPS_v1",
        "live_intake": live,
        "deepseek_pin": pin,
        "pytest": {"ok": pytest_row["ok"], "returncode": pytest_row["returncode"], "tail": pytest_row["stdout"][-400:]},
        "compile_counts": compiled.get("counts"),
        "role_cycle": roles_row,
        "drain": {
            "ok": drain.get("ok"),
            "idle": drain.get("idle"),
            "tick_count": len(drain.get("ticks") or []),
            "final_verdict": ((drain.get("final") or {}).get("dispatch") or {}).get("verdict"),
            "final_counts": ((drain.get("final") or {}).get("compile") or {}).get("counts"),
        },
        "live_smoke": {
            "ok": live_smoke.get("ok"),
            "skipped": live_smoke.get("skipped"),
            "verdict": live_smoke.get("verdict"),
            "job_id": live_smoke.get("job_id"),
            "dry_run": live_smoke.get("dry_run"),
            "receipt_path": live_smoke.get("receipt_path"),
        },
        "window": {
            "started_at": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ends_at": window_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "acceptance": "eligible items COMPLETE|BLOCKED_WITH_REASON|FOUNDER_BLOCKED; next tick IDLE_NO_WORK; no duplicate op_key dispatch",
        },
        "gaps": [],
        "ok": bool(pytest_row["ok"] and pin.get("ok") and roles_row.get("ok") and drain.get("ok")),
    }
    if not live:
        receipt["gaps"].append("LIVE_INTAKE_OFF — Railway/env must set NOOS_PLAN_COMPLETION_LIVE_INTAKE=1 for production drain")
    elif live_smoke.get("skipped") or not live_smoke.get("ok"):
        receipt["gaps"].append(f"LIVE_SMOKE:{live_smoke.get('verdict') or live_smoke.get('reason') or 'failed'}")
    # Telegram token for @NOOS_cycle_bot is org-managed; path is wired, readiness is secret-gated.
    receipt["fleet_observers"] = {
        "telegram_path": "deadman /plan-completion-report + /role-circle-report",
        "telegram_ready_requires": ["DEADMAN_TELEGRAM_BOT_TOKEN", "DEADMAN_TELEGRAM_CHAT_ID"],
        "telegram_lane_forbidden": ["Gateway_A", "NFProbeBot", "NoetfieldOpsBot"],
    }
    if receipt["ok"] and live and live_smoke.get("ok") and not any(g.startswith("LIVE_") for g in receipt["gaps"]):
        receipt["verdict"] = "COMMISSIONED_LIVE_WINDOW_OPEN"
    elif receipt["ok"]:
        receipt["verdict"] = "COMMISSIONED_DRY_RUN_WINDOW_OPEN"
    else:
        receipt["verdict"] = "BLOCKED_WITH_REASON"
    receipt["report_line"] = (
        f"plan_completion_commissioning · {receipt['verdict']} · "
        f"idle={drain.get('idle')} ticks={len(drain.get('ticks') or [])} live={live}"
    )
    out = ROOT / "receipts/proof" / f"noos-plan-completion-commissioning-{start.strftime('%Y%m%dT%H%M%SZ')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**receipt, "receipt_path": str(out.relative_to(ROOT))}, indent=2))
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
