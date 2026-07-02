#!/usr/bin/env python3
"""Execute one NOOS 24/7 domain loop — steps, receipt, Supabase sink, optional self-heal."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"
SINK = ROOT / "scripts/factory_supabase_sink_v1.py"
RUNTIME = ROOT / ".noos-runtime/loops"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def loop_by_event(registry: dict[str, Any], event_type: str) -> dict[str, Any]:
    for row in registry.get("loops") or []:
        if row.get("event_type") == event_type:
            return row
    raise SystemExit(f"unknown event_type: {event_type}")


def loop_state_path(loop_id: str) -> Path:
    return RUNTIME / loop_id / "state-v1.json"


def next_cycle_number(loop_id: str) -> int:
    path = loop_state_path(loop_id)
    if path.is_file():
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            return int(state.get("cycle_number") or 0) + 1
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    return 1


def run_cmd(cmd: list[str], *, continue_on_error: bool = False, timeout: int = 600) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        ok = proc.returncode == 0 or continue_on_error
        return {
            "cmd": cmd,
            "ok": ok,
            "exit_code": proc.returncode,
            "stdout_tail": (proc.stdout or "").strip()[-1200:],
            "stderr_tail": (proc.stderr or "").strip()[-800:],
            "continued_on_error": continue_on_error and proc.returncode != 0,
        }
    except subprocess.TimeoutExpired:
        return {"cmd": cmd, "ok": False, "exit_code": -1, "error": f"timeout_{timeout}s"}
    except OSError as exc:
        return {"cmd": cmd, "ok": False, "exit_code": -1, "error": str(exc)}


def sink_cycle(cycle: dict[str, Any], *, factory_id: str) -> dict[str, Any]:
    if not SINK.is_file():
        return {"ok": False, "skipped": True, "reason": "sink_missing"}
    import tempfile

    if not (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL")):
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(cycle, tmp)
        tmp_path = tmp.name
    proc = subprocess.run(
        [sys.executable, str(SINK), "cycle", tmp_path, "--factory-id", factory_id],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        Path(tmp_path).unlink(missing_ok=True)
    except OSError:
        pass
    sink_out: dict[str, Any] = {"ok": proc.returncode == 0, "exit_code": proc.returncode}
    if proc.stdout.strip():
        try:
            sink_out["detail"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            sink_out["stdout"] = proc.stdout[-500:]
    if proc.stderr.strip():
        sink_out["stderr"] = proc.stderr[-500:]
    return sink_out


def cloud_meta() -> dict[str, Any]:
    return {
        "processor": "noos_loop_runner_v1",
        "github_event": os.environ.get("GITHUB_EVENT_NAME"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_workflow": os.environ.get("GITHUB_WORKFLOW"),
        "processed_at": utc_now(),
    }


def execute_loop(loop: dict[str, Any], *, self_heal: bool = True) -> dict[str, Any]:
    loop_id = str(loop["id"])
    event_type = str(loop["event_type"])
    factory_id = str(loop.get("factory_id") or f"loop-{loop_id}")
    cycle_number = next_cycle_number(loop_id)
    started_at = utc_now()

    step_results: list[dict[str, Any]] = []
    for spec in loop.get("steps") or []:
        cmd = list(spec.get("cmd") or [])
        if not cmd:
            continue
        result = run_cmd(cmd, continue_on_error=bool(spec.get("continue_on_error")))
        result["name"] = spec.get("name") or cmd[0]
        step_results.append(result)

    ok = all(r.get("ok") for r in step_results)
    heal_results: list[dict[str, Any]] = []
    if not ok and self_heal:
        for spec in loop.get("self_heal") or []:
            cmd = list(spec.get("cmd") or [])
            if not cmd:
                continue
            heal = run_cmd(cmd, continue_on_error=True)
            heal["name"] = spec.get("name") or "self_heal"
            heal_results.append(heal)

    finished_at = utc_now()
    cycle = {
        "schema": "noos-24-7-loop-cycle-v1",
        "loop_id": loop_id,
        "event_type": event_type,
        "domain": loop.get("domain"),
        "cycle_number": cycle_number,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": "ok" if ok else "degraded",
        "exit_code": 0 if ok else 1,
        "runner_output": {
            "steps": step_results,
            "self_heal": heal_results,
            "cloud_meta": cloud_meta(),
            "cloud_trigger": os.environ.get("GITHUB_EVENT_NAME") or "local",
        },
        "guardrails": {"lane": "NOETFELD-OS", "read_only_control": False},
    }

    out_dir = RUNTIME / loop_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"cycle-{cycle_number:06d}.json").write_text(json.dumps(cycle, indent=2) + "\n", encoding="utf-8")
    state = {
        "loop_id": loop_id,
        "event_type": event_type,
        "cycle_number": cycle_number,
        "last_status": cycle["status"],
        "last_finished_at": finished_at,
    }
    loop_state_path(loop_id).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    cycle["supabase_sink"] = sink_cycle(cycle, factory_id=factory_id)
    return cycle


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--event-type", required=True, help="repository_dispatch event type")
    ap.add_argument("--no-self-heal", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    registry = load_registry()
    loop = loop_by_event(registry, args.event_type)
    cycle = execute_loop(loop, self_heal=not args.no_self_heal)
    if args.json:
        print(json.dumps(cycle, indent=2))
    else:
        print(
            f"loop={cycle['loop_id']} cycle={cycle['cycle_number']} "
            f"status={cycle['status']} sink={cycle.get('supabase_sink', {}).get('ok')}"
        )
    return 0 if cycle.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
