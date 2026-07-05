#!/usr/bin/env python3
"""Steps 3–7 — per-loop verify: smoke run, rolling Supabase evaluation, receipts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"
PROOF_DIR = ROOT / "receipts/proof"
RUNTIME_DIR = ROOT / ".noos-runtime/machine-loops"
DEFAULT_FALLBACK_LOOKBACK_HOURS = 168

sys.path.insert(0, str(ROOT / "scripts"))
from open_noos_verified_window_v1 import (  # noqa: E402
    evaluate_loop,
    fetch_cycle_rows,
    load_env,
    loop_factory_map,
    open_window,
)

CORE_LOOP_IDS = (
    "inbox",
    "runtime",
    "surface",
    "chain",
    "self_heal",
    "sourcea_observe",
    "agent_nerve",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _loop_motor_note() -> dict[str, Any]:
    if not REGISTRY.is_file():
        return {"secondary_motor": None}
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    motor = reg.get("motor") or {}
    fly_receipts = {
        "inbox": (ROOT / "receipts/proof/noos-deploy-fly-inbox-v1.json").is_file(),
        "self_heal": (ROOT / "receipts/proof/noos-deploy-fly-self-heal-v1.json").is_file(),
    }
    return {
        "primary_motor": "cf-cron → repository_dispatch",
        "secondary_motor": motor.get("secondary_motor"),
        "secondary_motor_note": motor.get("secondary_motor_note"),
        "fly_deploy_receipts": fly_receipts,
        "fly_l4_live": False,
    }


def merged_env() -> dict[str, str]:
    env = os.environ.copy()
    for key, val in load_env().items():
        env.setdefault(key, val)
    env.setdefault("GITHUB_EVENT_NAME", "repository_dispatch")
    env.setdefault("DISPATCH_SOURCE", "cf-cron")
    return env


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def loop_by_id(loop_id: str) -> dict[str, Any]:
    for loop in load_registry().get("loops") or []:
        if str(loop.get("id")) == loop_id:
            return loop
    raise SystemExit(f"unknown loop_id: {loop_id}")


def smoke_cycle_ok(payload: dict[str, Any] | None) -> bool:
    if not payload:
        return False
    if payload.get("ok") is True or payload.get("status") == "ok":
        return True
    d4 = payload.get("d4") or {}
    sink = payload.get("sink_invariant") or {}
    supabase = payload.get("supabase_sink") or {}
    if d4.get("execute_ok") and d4.get("validate_ok") and sink.get("verdict") == "PASS":
        if supabase.get("ok"):
            return True
        if supabase.get("skipped") and supabase.get("reason") == "supabase_not_configured":
            return True
    runner = payload.get("runner_output") or {}
    steps = runner.get("steps") or []
    self_heal = runner.get("self_heal") or []
    if steps and all(step.get("ok") for step in steps):
        if not self_heal or all(step.get("ok") for step in self_heal):
            return True
    return False


def smoke_run(*, loop_id: str) -> dict[str, Any]:
    loop = loop_by_id(loop_id)
    event_type = str(loop.get("event_type"))
    env = merged_env()
    env["GITHUB_RUN_ID"] = "local-smoke"
    env["GITHUB_WORKFLOW"] = str(loop.get("github_workflow"))
    proc = subprocess.run(
        [sys.executable, "scripts/noos_loop_runner_v1.py", "--event-type", event_type, "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    payload: dict[str, Any] | None = None
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = None
    ok = smoke_cycle_ok(payload)
    return {
        "loop_id": loop_id,
        "event_type": event_type,
        "exit_code": proc.returncode,
        "ok": ok,
        "cycle": payload,
        "stderr": proc.stderr.strip() or None,
    }


def rolling_for_loop(
    *,
    loop_id: str,
    lookback_hours: int,
    fallback_hours: int,
) -> dict[str, Any]:
    attempts = [lookback_hours]
    if fallback_hours > lookback_hours:
        attempts.append(fallback_hours)

    rolling: dict[str, Any] = {"ready": False, "blockers": ["supabase_not_configured"]}
    for hours in attempts:
        started = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = fetch_cycle_rows(
            window_started_at=started,
            factory_id=loop_factory_map().get(loop_id),
        )
        if isinstance(rows, dict) and not rows.get("ok", True):
            rolling = rows
            rolling["lookback_hours"] = hours
            break
        rolling = evaluate_loop(loop_id=loop_id, rows=rows, min_cycles=2)
        rolling["lookback_hours"] = hours
        rolling["lookback_started_at"] = started
        if rolling.get("ready"):
            if hours != lookback_hours:
                rolling["lookback_fallback"] = True
                rolling["primary_lookback_hours"] = lookback_hours
            break
    return rolling


def evaluate_rolling(*, lookback_hours: int, fallback_hours: int) -> dict[str, Any]:
    evaluations = [
        rolling_for_loop(loop_id=loop_id, lookback_hours=lookback_hours, fallback_hours=fallback_hours)
        for loop_id in CORE_LOOP_IDS
    ]
    verified = sum(1 for ev in evaluations if ev.get("ready"))
    return {
        "schema": "noos-loop-verify-rolling-v1",
        "evaluated_at": utc_now(),
        "lookback_hours": lookback_hours,
        "fallback_hours": fallback_hours,
        "loop_evaluations": evaluations,
        "verified_count": verified,
        "core_loop_count": len(CORE_LOOP_IDS),
        "ok": verified == len(CORE_LOOP_IDS),
        "report_line": f"loop_verify_rolling · verified={verified}/{len(CORE_LOOP_IDS)}",
    }


def verify_loop(
    *,
    loop_id: str,
    lookback_hours: int,
    fallback_hours: int,
    smoke: bool,
) -> dict[str, Any]:
    smoke_row = smoke_run(loop_id=loop_id) if smoke else {"skipped": True}
    rolling = rolling_for_loop(
        loop_id=loop_id,
        lookback_hours=lookback_hours,
        fallback_hours=fallback_hours,
    )

    smoke_ok = bool(smoke_row.get("ok"))
    rolling_ok = bool(rolling.get("ready"))
    if rolling_ok or smoke_ok:
        state = "VERIFIED"
    elif loop_id == "sourcea_observe":
        state = "STALE_ALLOWED"
        rolling["external_blocker_note"] = "SourceA external writers may keep STALE until CRON_FIRED"
    else:
        state = "RUNNING"

    return {
        "schema": "noos-loop-verify-v1",
        "backlog_id": f"LOOP-VERIFY-{loop_id}",
        "loop_id": loop_id,
        "verified_at": utc_now(),
        "verification_state": state,
        "smoke": smoke_row,
        "rolling_evaluation": rolling,
        "ok": smoke_ok or rolling_ok or state == "STALE_ALLOWED",
        "autonomous_triggers": True,
    }


def verify_all(
    *,
    lookback_hours: int,
    fallback_hours: int,
    smoke: bool,
    write_receipt: bool,
) -> dict[str, Any]:
    per_loop = [
        verify_loop(
            loop_id=lid,
            lookback_hours=lookback_hours,
            fallback_hours=fallback_hours,
            smoke=smoke,
        )
        for lid in CORE_LOOP_IDS
    ]
    rolling = evaluate_rolling(lookback_hours=lookback_hours, fallback_hours=fallback_hours)
    verified = sum(1 for row in per_loop if row.get("verification_state") == "VERIFIED")
    stale_allowed = sum(1 for row in per_loop if row.get("verification_state") == "STALE_ALLOWED")

    window = open_window()
    window["core_loops_only"] = True
    for loop in window.get("loops") or []:
        loop_id = str(loop.get("loop_id") or "")
        match = next((row for row in per_loop if row["loop_id"] == loop_id), None)
        if match:
            loop["verification_state"] = match["verification_state"]
            if match["verification_state"] == "VERIFIED":
                loop["verified_at"] = match["verified_at"]
    verified_loops = sum(1 for row in per_loop if row.get("verification_state") == "VERIFIED")
    window["overall_state"] = "VERIFIED" if verified_loops + stale_allowed >= len(CORE_LOOP_IDS) else "DECLARED"
    window["loops"] = [loop for loop in window.get("loops") or [] if loop.get("loop_id") in CORE_LOOP_IDS]
    window["loop_count"] = len(window["loops"])

    payload = {
        "schema": "noos-loop-verify-all-v1",
        "verified_at": utc_now(),
        "authority": "NOOS_MACHINE_LOOPS_UPGRADE_STEPS_3_7",
        "lookback_hours": lookback_hours,
        "fallback_hours": fallback_hours,
        "per_loop": per_loop,
        "rolling_summary": rolling,
        "verified_count": verified,
        "stale_allowed_count": stale_allowed,
        "core_loop_count": len(CORE_LOOP_IDS),
        "new_verified_window": window,
        "secondary_motor": _loop_motor_note(),
        "ok": verified + stale_allowed >= len(CORE_LOOP_IDS),
        "report_line": (
            f"loop_verify_all · verified={verified} stale_allowed={stale_allowed} "
            f"core={len(CORE_LOOP_IDS)}"
        ),
    }

    if write_receipt:
        PROOF_DIR.mkdir(parents=True, exist_ok=True)
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        proof_path = PROOF_DIR / "noos-loop-verify-all-v1.json"
        runtime_path = RUNTIME_DIR / "loop-verify-all-v1.json"
        proof_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        runtime_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        payload["receipt_paths"] = [
            str(proof_path.relative_to(ROOT)),
            str(runtime_path.relative_to(ROOT)),
        ]
        for row in per_loop:
            loop_path = PROOF_DIR / f"noos-loop-verify-{row['loop_id']}-v1.json"
            loop_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)

    smoke_p = sub.add_parser("smoke", help="Run one local smoke cycle for a loop")
    smoke_p.add_argument("--loop", required=True)

    roll_p = sub.add_parser("rolling", help="Evaluate rolling window from Supabase")
    roll_p.add_argument("--lookback-hours", type=int, default=24)
    roll_p.add_argument("--fallback-hours", type=int, default=DEFAULT_FALLBACK_LOOKBACK_HOURS)

    one_p = sub.add_parser("loop", help="Verify one loop (smoke + rolling)")
    one_p.add_argument("--loop", required=True)
    one_p.add_argument("--lookback-hours", type=int, default=24)
    one_p.add_argument("--fallback-hours", type=int, default=DEFAULT_FALLBACK_LOOKBACK_HOURS)
    one_p.add_argument("--no-smoke", action="store_true")

    all_p = sub.add_parser("all", help="Verify all core loops (steps 3–7)")
    all_p.add_argument("--lookback-hours", type=int, default=24)
    all_p.add_argument("--fallback-hours", type=int, default=DEFAULT_FALLBACK_LOOKBACK_HOURS)
    all_p.add_argument("--no-smoke", action="store_true")
    all_p.add_argument("--write-receipt", action="store_true")

    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.command == "smoke":
        row = smoke_run(loop_id=args.loop)
    elif args.command == "rolling":
        row = evaluate_rolling(lookback_hours=args.lookback_hours, fallback_hours=args.fallback_hours)
    elif args.command == "loop":
        row = verify_loop(
            loop_id=args.loop,
            lookback_hours=args.lookback_hours,
            fallback_hours=args.fallback_hours,
            smoke=not args.no_smoke,
        )
    else:
        row = verify_all(
            lookback_hours=args.lookback_hours,
            fallback_hours=args.fallback_hours,
            smoke=not args.no_smoke,
            write_receipt=args.write_receipt,
        )

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line") or json.dumps(row))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
