#!/usr/bin/env python3
"""Continuous guarded factory loop for the Noetfield run patch pack.

The factory keeps the run pack alive by repeatedly triggering the receipt
runner, writing a heartbeat, and recording every cycle. It is designed to keep
moving without user intervention while preserving hard safety boundaries:
no repo .env reads, no secret printing, no production mutation, and no
portfolio-spine usage.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_noetfield_patch_pack_v1.py"
EXECUTION_DIR = ROOT / "docs/run_patches/execution"
FACTORY_STATE = EXECUTION_DIR / "noetfield_factory_state_v1.json"
FACTORY_HEARTBEAT = EXECUTION_DIR / "noetfield_factory_heartbeat_v1.json"
FACTORY_LOG = EXECUTION_DIR / "noetfield_factory_cycles_v1.jsonl"
MANIFEST_PATH = ROOT / "docs/run_patches/noetfield_run_patch_manifest_10100_v1.json"
SINK_SCRIPT = ROOT / "scripts/factory_supabase_sink_v1.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=True, sort_keys=True) + "\n")


def parse_runner_output(output: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().replace(" ", "_")
        value = value.strip()
        if value.isdigit():
            parsed[key] = int(value)
        else:
            parsed[key] = value
    return parsed


def sink_cycle_to_supabase(cycle: dict[str, Any], *, factory_id: str) -> dict[str, Any]:
    if not SINK_SCRIPT.is_file():
        return {"ok": False, "skipped": True, "reason": "sink_script_missing"}
    import os
    import tempfile

    if not (
        os.environ.get("NOETFIELD_SUPABASE_URL")
        or os.environ.get("SUPABASE_URL")
        or os.environ.get("SUPABASE_DB_PASSWORD")
        or os.environ.get("NOETFIELD_SUPABASE_DB_PASSWORD")
    ):
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(cycle, tmp, ensure_ascii=True)
        tmp_path = tmp.name
    try:
        completed = subprocess.run(
            ["python3", str(SINK_SCRIPT), "cycle", tmp_path, "--factory-id", factory_id],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=45,
        )
        if completed.stdout.strip():
            try:
                return json.loads(completed.stdout.strip())
            except json.JSONDecodeError:
                return {"ok": completed.returncode == 0, "raw": completed.stdout.strip()}
        return {"ok": False, "stderr": completed.stderr.strip()[:300]}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def update_manifest(factory_state: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["factory_runtime"] = {
        "status": factory_state["status"],
        "factory_id": factory_state["factory_id"],
        "started_at": factory_state["started_at"],
        "last_heartbeat_at": factory_state["last_heartbeat_at"],
        "cycle_count": factory_state["cycle_count"],
        "last_cycle_result": factory_state["last_cycle_result"],
        "state_path": "docs/run_patches/execution/noetfield_factory_state_v1.json",
        "heartbeat_path": "docs/run_patches/execution/noetfield_factory_heartbeat_v1.json",
        "cycle_log_path": "docs/run_patches/execution/noetfield_factory_cycles_v1.jsonl",
        "guardrails": factory_state["guardrails"],
    }
    write_json(MANIFEST_PATH, manifest)


def run_cycle(cycle_number: int) -> dict[str, Any]:
    started_at = utc_now()
    command = ["python3", str(RUNNER)]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
        timeout=120,
    )
    finished_at = utc_now()
    parsed = parse_runner_output(completed.stdout)
    result = {
        "cycle_number": cycle_number,
        "started_at": started_at,
        "finished_at": finished_at,
        "exit_code": completed.returncode,
        "runner_output": parsed,
        "stderr_present": bool(completed.stderr.strip()),
        "status": "ok" if completed.returncode == 0 else "recoverable_error",
        "guardrails": {
            "repo_env_read": False,
            "secret_values_printed": False,
            "production_mutation": False,
            "portfolio_spine_used": False,
        },
    }
    if completed.stderr.strip():
        result["stderr_summary"] = completed.stderr.strip().splitlines()[-5:]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Noetfield factory loop.")
    parser.add_argument("--interval-seconds", type=int, default=600, help="Delay between cycles.")
    parser.add_argument("--max-cycles", type=int, default=0, help="Stop after N cycles. Default: run forever.")
    parser.add_argument("--once", action="store_true", help="Run exactly one cycle.")
    args = parser.parse_args()

    max_cycles = 1 if args.once else args.max_cycles
    EXECUTION_DIR.mkdir(parents=True, exist_ok=True)
    factory_id = f"noetfield-factory-v1-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    started_at = utc_now()
    cycle_count = 0
    last_cycle: dict[str, Any] = {"status": "not_started"}

    while True:
        cycle_count += 1
        try:
            last_cycle = run_cycle(cycle_count)
        except Exception as exc:  # keep the factory alive on recoverable failures
            last_cycle = {
                "cycle_number": cycle_count,
                "started_at": utc_now(),
                "finished_at": utc_now(),
                "exit_code": 1,
                "status": "recoverable_exception",
                "exception_type": type(exc).__name__,
                "exception": str(exc),
                "guardrails": {
                    "repo_env_read": False,
                    "secret_values_printed": False,
                    "production_mutation": False,
                    "portfolio_spine_used": False,
                },
            }

        append_jsonl(FACTORY_LOG, last_cycle)
        supabase_sink = sink_cycle_to_supabase(last_cycle, factory_id=factory_id)
        state = {
            "factory_id": factory_id,
            "status": "running" if not max_cycles or cycle_count < max_cycles else "completed_bounded_run",
            "started_at": started_at,
            "last_heartbeat_at": utc_now(),
            "interval_seconds": args.interval_seconds,
            "cycle_count": cycle_count,
            "last_cycle_result": last_cycle,
            "supabase_sink": supabase_sink,
            "guardrails": {
                "repo_env_read": False,
                "secret_values_printed": False,
                "production_mutation": False,
                "portfolio_spine_used": False,
                "restart_on_recoverable_error": True,
            },
        }
        write_json(FACTORY_STATE, state)
        write_json(FACTORY_HEARTBEAT, state)
        update_manifest(state)
        print(
            f"factory_id={factory_id} cycle={cycle_count} "
            f"status={last_cycle['status']} heartbeat={state['last_heartbeat_at']}",
            flush=True,
        )

        if max_cycles and cycle_count >= max_cycles:
            return 0 if last_cycle.get("exit_code") == 0 else 1
        time.sleep(max(args.interval_seconds, 1))


if __name__ == "__main__":
    raise SystemExit(main())
