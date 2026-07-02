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
WORKER = ROOT / "scripts/cloud_inbox_worker_v1.py"
SINK_SCRIPT = ROOT / "scripts/factory_supabase_sink_v1.py"

import sys

sys.path.insert(0, str(ROOT / "scripts"))
from factory_runtime_paths_v1 import MANIFEST_PATH, execution_dir, receipt_commit_enabled


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


def update_manifest(factory_state: dict[str, Any], *, paths: dict[str, Path]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["factory_runtime"] = {
        "status": factory_state["status"],
        "factory_id": factory_state["factory_id"],
        "started_at": factory_state["started_at"],
        "last_heartbeat_at": factory_state["last_heartbeat_at"],
        "cycle_count": factory_state["cycle_count"],
        "last_cycle_result": factory_state["last_cycle_result"],
        "state_path": str(paths["state"].relative_to(ROOT)),
        "heartbeat_path": str(paths["heartbeat"].relative_to(ROOT)),
        "cycle_log_path": str(paths["log"].relative_to(ROOT)),
        "guardrails": factory_state["guardrails"],
    }
    write_json(MANIFEST_PATH, manifest)


def run_cycle(cycle_number: int, *, exec_dir: Path, receipt_commit: bool) -> dict[str, Any]:
    import os as _os

    started_at = utc_now()
    use_patch_pack = _os.environ.get("NOOS_FACTORY_PATCH_PACK", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if use_patch_pack:
        command = ["python3", str(RUNNER), "--runtime-dir", str(exec_dir)]
        if not receipt_commit:
            command.append("--no-manifest-update")
        timeout = 120
    else:
        command = ["python3", str(WORKER)]
        timeout = 180
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout,
    )
    finished_at = utc_now()
    parsed = parse_runner_output(completed.stdout)
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if lines:
        try:
            parsed["worker_result"] = json.loads(lines[-1])
        except json.JSONDecodeError:
            pass
    if isinstance(parsed.get("worker_result"), dict):
        wr = parsed["worker_result"]
        for key in ("status", "idle_reason", "action", "founder_blocked", "founder_blocked_this_cycle"):
            if key in wr and wr[key] is not None:
                parsed[key] = wr[key]
        if wr.get("status") == "IDLE_NO_WORK":
            parsed["cycle_status"] = "IDLE_NO_WORK"
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
    parser.add_argument(
        "--receipt-commit",
        action="store_true",
        help="Write factory receipts into tracked docs/run_patches paths and update manifest.",
    )
    args = parser.parse_args()

    receipt_commit = receipt_commit_enabled(args.receipt_commit)
    exec_dir = execution_dir(receipt_commit=receipt_commit)
    exec_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "state": exec_dir / "noetfield_factory_state_v1.json",
        "heartbeat": exec_dir / "noetfield_factory_heartbeat_v1.json",
        "log": exec_dir / "noetfield_factory_cycles_v1.jsonl",
    }

    max_cycles = 1 if args.once else args.max_cycles
    factory_id = f"noetfield-factory-v1-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    started_at = utc_now()
    cycle_count = 0
    last_cycle: dict[str, Any] = {"status": "not_started"}

    while True:
        cycle_count += 1
        try:
            last_cycle = run_cycle(cycle_count, exec_dir=exec_dir, receipt_commit=receipt_commit)
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

        append_jsonl(paths["log"], last_cycle)
        import os as _os

        trigger = _os.environ.get("GITHUB_EVENT_NAME")
        if trigger:
            runner = last_cycle.get("runner_output")
            if not isinstance(runner, dict):
                runner = {}
            runner["cloud_trigger"] = trigger
            runner["cloud_meta"] = {
                "github_event": trigger,
                "github_run_id": _os.environ.get("GITHUB_RUN_ID"),
                "github_workflow": _os.environ.get("GITHUB_WORKFLOW"),
            }
            if _os.environ.get("GITHUB_RUN_ID"):
                runner["github_run_id"] = _os.environ.get("GITHUB_RUN_ID")
            last_cycle["runner_output"] = runner
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
            "runtime_dir": str(exec_dir.relative_to(ROOT)),
            "receipt_commit": receipt_commit,
            "guardrails": {
                "repo_env_read": False,
                "secret_values_printed": False,
                "production_mutation": False,
                "portfolio_spine_used": False,
                "restart_on_recoverable_error": True,
            },
        }
        write_json(paths["state"], state)
        write_json(paths["heartbeat"], state)
        if receipt_commit:
            update_manifest(state, paths=paths)
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
