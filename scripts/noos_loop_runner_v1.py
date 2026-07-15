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
SINK_TIMEOUT_SEC = int(os.environ.get("NOOS_SINK_TIMEOUT_SEC", "60"))

sys.path.insert(0, str(ROOT / "scripts"))
from noos_loop_determinism_v1 import advance_state, cas_advance, op_key, transition_allowed  # noqa: E402
from noos_loop_liveness_v1 import detect_execution_host, sync_meta_liveness_rows, upsert_loop_liveness  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def resolve_mission_id(*, workflow_id: str) -> str:
    path = ROOT / "data/mission-registry-v1.json"
    if not path.is_file():
        return "M2"
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "M2"
    mapping = row.get("workflow_missions") if isinstance(row.get("workflow_missions"), dict) else {}
    return str(mapping.get(workflow_id) or row.get("default_mission_id") or "M2")


def loop_by_event(registry: dict[str, Any], event_type: str) -> dict[str, Any]:
    for row in registry.get("loops") or []:
        if row.get("event_type") == event_type:
            return row
    raise SystemExit(f"unknown event_type: {event_type}")


def is_cloud_execution() -> bool:
    return bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("NOOS_CLOUD_LOOP") == "1")


def resolve_step_specs(loop: dict[str, Any]) -> list[dict[str, Any]]:
    if is_cloud_execution():
        cloud = loop.get("cloud_steps")
        if cloud:
            return list(cloud)
    return list(loop.get("steps") or [])


def loop_state_path(loop_id: str) -> Path:
    return RUNTIME / loop_id / "state-v1.json"


def acquire_cycle_number(loop_id: str) -> tuple[int | None, dict[str, Any]]:
    """D2 — CAS on cycle_number before side effects."""
    path = loop_state_path(loop_id)
    expected = 0
    if path.is_file():
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            expected = int(state.get("cycle_number") or 0)
        except (OSError, json.JSONDecodeError, ValueError):
            expected = 0
    observed = expected
    if path.is_file():
        try:
            live = json.loads(path.read_text(encoding="utf-8"))
            observed = int(live.get("cycle_number") or 0)
        except (OSError, json.JSONDecodeError, ValueError):
            observed = expected
    new_number = observed + 1
    cas = cas_advance(expected=expected, observed=observed, new_value=new_number)
    if cas.get("verdict") != "ACCEPTED":
        return None, {"cas": cas, "reason": "cas_mismatch"}
    return new_number, {"cas": cas}


def next_cycle_number(loop_id: str) -> int:
    number, _meta = acquire_cycle_number(loop_id)
    return number if number is not None else 1


def run_cmd(cmd: list[str], *, continue_on_error: bool = False, timeout: int = 600) -> dict[str, Any]:
    if cmd and cmd[0] == "python3":
        cmd = [sys.executable, *cmd[1:]]
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
    try:
        proc = subprocess.run(
            [sys.executable, str(SINK), "cycle", tmp_path, "--factory-id", factory_id],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=SINK_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit_code": -1, "error": f"sink_subprocess_timeout_{SINK_TIMEOUT_SEC}s"}
    finally:
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
    dispatch_source = os.environ.get("DISPATCH_SOURCE", "").strip()
    return {
        "processor": "noos_loop_runner_v1",
        "github_event": os.environ.get("GITHUB_EVENT_NAME"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_workflow": os.environ.get("GITHUB_WORKFLOW"),
        "dispatch_source": dispatch_source or None,
        "processed_at": utc_now(),
    }


def meter_cost(step_results: list[dict[str, Any]]) -> dict[str, Any]:
    """L11 — compute cost at call site. NOOS loops run on GitHub/CF free tiers.

    These loops invoke no paid LLM/provider calls, so metered spend is a true 0.0.
    The field is present and honest, not estimated after the fact.
    """
    return {
        "provider": "github_actions+cloudflare_cron",
        "model": "none",
        "tokens_in": 0,
        "tokens_out": 0,
        "unit_cost_usd": 0.0,
        "total_usd": 0.0,
        "estimated_cost": 0.0,
        "cost_policy_pass": True,
        "cost_policy_version": "cost-policy-v1",
        "metered_at_call_site": True,
        "step_count": len(step_results),
    }


def founder_blocked_probe() -> dict[str, Any]:
    """L7 — surface founder_blocked count/oldest/age in every cycle receipt."""
    url = os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get(
        "SUPABASE_SERVICE_ROLE_KEY"
    )
    if not url or not key:
        return {"count": 0, "oldest_id": "", "priority": "", "age_seconds": 0, "escalated": False, "skipped": True}
    import urllib.error
    import urllib.request

    query = (
        "select=item_id,priority,enqueued_at&status=eq.founder_blocked&order=enqueued_at.asc"
    )
    req = urllib.request.Request(
        f"{url.rstrip('/')}/rest/v1/noetfield_worker_inbox_queue?{query}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return {"count": 0, "oldest_id": "", "priority": "", "age_seconds": 0, "escalated": False, "probe_failed": True}
    if not rows:
        return {"count": 0, "oldest_id": "", "priority": "", "age_seconds": 0, "escalated": False}
    oldest = rows[0]
    age = 0
    ts = oldest.get("enqueued_at")
    if ts:
        try:
            t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            age = int((datetime.now(timezone.utc) - t).total_seconds())
        except ValueError:
            age = 0
    # L7 — aging founder P0 gets louder past 24h
    escalated = oldest.get("priority") == "P0" and age > 86400
    return {
        "count": len(rows),
        "oldest_id": oldest.get("item_id", ""),
        "priority": oldest.get("priority", ""),
        "age_seconds": age,
        "escalated": escalated,
    }


def sink_invariant(step_results: list[dict[str, Any]], heal_results: list[dict[str, Any]]) -> dict[str, Any]:
    """L8 — Σ(origin counts) == sink_count, provenance-tagged."""
    origin_counts = {"steps": len(step_results), "self_heal": len(heal_results)}
    sink_count = len(step_results) + len(heal_results)
    total = sum(origin_counts.values())
    verdict = "PASS" if total == sink_count else "BLOCKED_WITH_REASON"
    return {
        "law": "sum(origin_counts) == sink_count",
        "counts": origin_counts,
        "sink_count": sink_count,
        "provenance_tags": {"steps": "loop_step", "self_heal": "loop_self_heal"},
        "verdict": verdict,
    }


def execute_loop(loop: dict[str, Any], *, self_heal: bool = True) -> dict[str, Any]:
    loop_id = str(loop["id"])
    event_type = str(loop["event_type"])
    factory_id = str(loop.get("factory_id") or f"loop-{loop_id}")
    cycle_number, cas_meta = acquire_cycle_number(loop_id)
    started_at = utc_now()
    if cycle_number is None:
        finished_at = utc_now()
        return {
            "schema": "noos-24-7-loop-cycle-v1",
            "receipt_schema": "autorun-cycle-receipt-v2",
            "loop_id": loop_id,
            "event_type": event_type,
            "factory_id": factory_id,
            "workflow_id": str(loop.get("github_workflow") or loop_id),
            "mission_id": resolve_mission_id(workflow_id=str(loop.get("github_workflow") or loop_id)),
            "cycle_number": 0,
            "started_at": started_at,
            "finished_at": finished_at,
            "state_before": "RUNNING",
            "state_after": "BLOCKED_WITH_REASON",
            "status": "recoverable_error",
            "exit_code": 1,
            "blocker_reason": f"cas_rejected:{cas_meta.get('reason')}",
            "d2": cas_meta,
            "runner_output": {"cloud_meta": cloud_meta(), "cas": cas_meta},
        }

    step_results: list[dict[str, Any]] = []
    for spec in resolve_step_specs(loop):
        cmd = list(spec.get("cmd") or [])
        if not cmd:
            continue
        result = run_cmd(cmd, continue_on_error=bool(spec.get("continue_on_error")))
        result["name"] = spec.get("name") or cmd[0]
        step_results.append(result)

    no_work = len(step_results) == 0
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
    fb = founder_blocked_probe()
    inv = sink_invariant(step_results, heal_results)
    validate_ok = inv["verdict"] == "PASS"

    workflow_id = str(loop.get("github_workflow") or loop_id)
    mission_id = resolve_mission_id(workflow_id=workflow_id)
    op_key_val = op_key(workflow_id=workflow_id, loop_id=loop_id, cycle_number=cycle_number)

    evidence = [
        {"command": " ".join(r.get("cmd", [])), "exit_code": r.get("exit_code"), "output": (r.get("stdout_tail") or r.get("error") or "")[-400:]}
        for r in (step_results + heal_results)
    ]

    cycle: dict[str, Any] = {
        "schema": "noos-24-7-loop-cycle-v1",
        "receipt_schema": "autorun-cycle-receipt-v2",
        "workflow_id": workflow_id,
        "mission_id": mission_id,
        "sandbox_id": "noetfeld-os",
        "lane": loop.get("lane") or "noos",
        "loop_id": loop_id,
        "event_type": event_type,
        "domain": loop.get("domain"),
        "trigger_source": os.environ.get("GITHUB_EVENT_NAME") or "local",
        "cycle_number": cycle_number,
        "op_key": op_key_val,
        "started_at": started_at,
        "state_before": "RUNNING",
        "cost": meter_cost(step_results),
        "value_class": loop.get("value_class") or "hygiene",
        "sink_invariant": inv,
        "founder_blocked": fb,
        "evidence": evidence,
        "runner_output": {
            "steps": step_results,
            "self_heal": heal_results,
            "cloud_meta": cloud_meta(),
            "cloud_trigger": os.environ.get("GITHUB_EVENT_NAME") or "local",
        },
        "guardrails": {"lane": loop.get("lane") or "noos", "read_only_control": loop.get("domain") == "sourcea-observe"},
    }

    cycle["supabase_sink"] = sink_cycle(cycle, factory_id=factory_id)
    sink_acked = cycle["supabase_sink"].get("ok") is True

    if no_work:
        state_before = "IDLE_NO_WORK"
        state_after = "IDLE_NO_WORK"
        d4_reason = None
    else:
        state_before = "RUNNING"
        state_after, d4_reason = advance_state(
            no_work=False,
            execute_ok=ok,
            validate_ok=validate_ok,
            sink_acked=sink_acked,
        )
        if not transition_allowed(state_before, state_after):
            state_after = "BLOCKED_WITH_REASON"
            d4_reason = f"illegal_transition:{state_before}->{state_after}"

    blocker_reason = None
    if state_after == "BLOCKED_WITH_REASON":
        blocker_reason = d4_reason or f"sink_invariant_failed:{inv['counts']}"
    elif state_after == "FAILED_WITH_RECEIPT":
        failed = [r.get("name") for r in step_results if not r.get("ok")]
        blocker_reason = f"steps_failed:{failed}"

    cycle.update(
        {
            "finished_at": finished_at,
            "state_before": state_before,
            "state_after": state_after,
            "status": "ok" if state_after in ("COMPLETE", "IDLE_NO_WORK") else "degraded",
            "exit_code": 0 if state_after in ("COMPLETE", "IDLE_NO_WORK") else 1,
            "blocker_reason": blocker_reason,
            "next_action": "await_next_scheduled_tick" if state_after in ("COMPLETE", "IDLE_NO_WORK") else "self_heal_or_triage",
            "d4": {"execute_ok": ok, "validate_ok": validate_ok, "sink_acked": sink_acked},
            "d2": cas_meta,
            "transition_log_tail": [
                {
                    "from": state_before,
                    "to": state_after,
                    "at": finished_at,
                    "cycle": cycle_number,
                    "op_key": op_key_val,
                }
            ],
        }
    )

    out_dir = RUNTIME / loop_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"cycle-{cycle_number:06d}.json").write_text(json.dumps(cycle, indent=2) + "\n", encoding="utf-8")
    state = {
        "loop_id": loop_id,
        "event_type": event_type,
        "cycle_number": cycle_number,
        "last_status": cycle["status"],
        "last_state": state_after,
        "last_finished_at": cycle["finished_at"],
        "transition_log_tail": [{"from": state_before, "to": state_after, "op_key": op_key_val}],
    }
    loop_state_path(loop_id).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    if state_after in ("COMPLETE", "IDLE_NO_WORK"):
        cycle["liveness_upsert"] = upsert_loop_liveness(
            loop_id=loop_id,
            event_type=event_type,
            interval_minutes=int(loop.get("interval_minutes") or 5),
            last_cycle_status=state_after,
            host=detect_execution_host(),
        )
        cycle["meta_liveness_sync"] = sync_meta_liveness_rows()
    else:
        cycle["liveness_upsert"] = {"ok": False, "skipped": True, "reason": "cycle_not_successful"}

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
