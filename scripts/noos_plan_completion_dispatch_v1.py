#!/usr/bin/env python3
"""Single reconciler bridge: READY backlog items → HMAC Runway /v1/intake.

Advance only after Runway acknowledges the same op_key (D1/D4).
LLM never transitions state here — intake is deterministic envelope only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_runway_supervision_adapter_v1 as runway  # noqa: E402
from noos_founder_execution_contract_v1 import FOUNDER_EXECUTION_CONTRACT  # noqa: E402
import noos_unified_backlog_compiler_v1 as compiler  # noqa: E402

CONFIG = ROOT / "data/noos-unified-plan-completion-v1.json"
CONTRACT = ROOT / "data/noetfield-runway-contract-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")


def resolve_recipe(item: dict[str, Any], contract: dict[str, Any]) -> dict[str, str]:
    """Contract role_recipe_map is supervision SSOT; item fields are fallback only."""
    role_map = contract.get("role_recipe_map") or {}
    role = str(item.get("role") or "research")
    mapped = role_map.get(role) or role_map.get("research") or {}
    return {
        "runway_id": str(mapped.get("runway_id") or item.get("runway_id") or "research"),
        "recipe_id": str(mapped.get("recipe_id") or item.get("recipe_id") or "vendor-decision-brief"),
        "recipe_version": str(mapped.get("recipe_version") or item.get("recipe_version") or "0.1.0"),
    }


def pick_ready(items: list[dict[str, Any]], *, concurrency_key: str, max_inflight: int) -> dict[str, Any] | None:
    inflight = [i for i in items if i.get("status") == "DISPATCHED" and i.get("concurrency_key") == concurrency_key]
    if len(inflight) >= max_inflight:
        return None
    ready = [i for i in items if i.get("status") == "READY"]
    ready.sort(key=lambda x: (str(x.get("authority_class") or ""), x.get("item_id") or ""))
    return ready[0] if ready else None


def dry_run_preview(intake: dict[str, Any]) -> dict[str, Any]:
    """Return a side-effect-free preview; never fabricate a job id or acknowledgement."""
    return {
        "dry_run": True,
        "expected_op_key": intake.get("idempotency_key"),
        "intake": intake,
    }

def dispatch_once(*, write: bool = True, allow_dry_run: bool = True) -> dict[str, Any]:
    config = load_json(CONFIG)
    contract = load_json(CONTRACT)
    backlog_path = ROOT / str(config.get("runtime_queue_path") or ".noos-runtime/plan-completion/backlog-v1.json")
    events_path = ROOT / str(config.get("dispatch_events_path") or ".noos-runtime/plan-completion/dispatch-events-v1.jsonl")

    if backlog_path.is_file():
        backlog = load_json(backlog_path)
    else:
        backlog = compiler.compile_backlog(write=write)

    items = list(backlog.get("items") or [])
    conc = config.get("concurrency") or {}
    concurrency_key = str(conc.get("default_key") or "plan-completion")
    max_inflight = int(conc.get("max_inflight_per_key") or 1)

    pf = runway.preflight()
    pin = runway.verify_deepseek_pin()
    if not pin.get("ok"):
        return {
            "ok": False,
            "verdict": "BLOCKED_DEEPSEEK_PIN_DRIFT",
            "pin": pin,
            "report_line": "plan_dispatch · deepseek pin drift",
        }

    selected = pick_ready(items, concurrency_key=concurrency_key, max_inflight=max_inflight)
    if selected is None:
        idle = not any(i.get("status") == "DISPATCHED" for i in items)
        row = {
            "schema": "noos-plan-completion-dispatch-v1",
            "at": utc_now(),
            "verdict": "IDLE_NO_WORK" if idle else "THROTTLED_INFLIGHT",
            "ok": True,
            "selected": None,
            "preflight": pf,
            "counts": backlog.get("counts"),
            "report_line": f"plan_dispatch · {'IDLE_NO_WORK' if idle else 'THROTTLED_INFLIGHT'}",
        }
        if write:
            append_event(events_path, {**row, "event": "idle_or_throttle"})
        return row

    recipe = resolve_recipe(selected, contract)
    intake = {
        "runway_id": recipe["runway_id"],
        "recipe_id": recipe["recipe_id"],
        "recipe_version": recipe["recipe_version"],
        "idempotency_key": selected["op_key"],
        "requested_at": utc_now(),
        "budget_usd": selected.get("budget_usd") or 0.25,
        "input": {
            "goal": {
                "plan_id": selected["plan_id"],
                "item_id": selected["item_id"],
                "title": selected["title"],
                "role": selected["role"],
                "value_class": selected["value_class"],
                "acceptance_checks": selected.get("acceptance_checks") or [],
                "repository": selected.get("repository"),
                "founder_execution_contract": FOUNDER_EXECUTION_CONTRACT,
            },
            "artifact_refs": [],
        },
    }

    live = os.environ.get("NOOS_PLAN_COMPLETION_LIVE_INTAKE", "").strip().lower() in ("1", "true", "yes")
    # Read-only calls and disabled/unhealthy intake may preview, but never
    # create a synthetic job id, event, receipt or state transition.
    if not write or not (pf.get("ok") and live):
        if allow_dry_run:
            preview = dry_run_preview(intake)
            return {
                "schema": "noos-plan-completion-dispatch-v1",
                "at": utc_now(),
                "verdict": "DRY_RUN_ONLY",
                "ok": True,
                "selected": {
                    "item_id": selected["item_id"],
                    "plan_id": selected["plan_id"],
                    "op_key": selected["op_key"],
                    "role": selected["role"],
                    "title": selected["title"],
                },
                "job_id": None,
                "ack": None,
                "preflight": {"ok": pf.get("ok"), "verdict": pf.get("verdict")},
                "dry_run": True,
                "would_submit": preview["intake"],
                "report_line": f"plan_dispatch · DRY_RUN_ONLY item={selected['item_id']} no_state_change=true",
            }
        return {
            "ok": False,
            "verdict": pf.get("verdict") or runway.BLOCKED_RUNWAY_API_NOT_LIVE,
            "preflight": pf,
            "selected": selected,
            "report_line": "plan_dispatch · runway not live",
        }

    ack = runway.submit_intake(intake)
    ack_body = ack.get("body") if isinstance(ack.get("body"), dict) else {}
    job_id = ack_body.get("job_id")
    valid_job_id = (
        isinstance(job_id, str)
        and len(job_id) == 35
        and job_id.startswith("rj_")
        and all(char in "0123456789abcdef" for char in job_id[3:])
    )
    http_accepted = ack.get("ok") is True and ack.get("status") in (200, 202) and ack.get("dry_run") is not True
    readback = runway.get_job(job_id) if http_accepted and valid_job_id else {"ok": False, "error": "invalid_or_missing_job_id"}
    readback_body = readback.get("body") if isinstance(readback.get("body"), dict) else {}
    readback_request = readback_body.get("request") if isinstance(readback_body.get("request"), dict) else {}
    readback_key = readback_request.get("idempotency_key")
    readback_matches = (
        readback.get("ok") is True
        and readback_body.get("job_id") == job_id
        and readback_key == selected["op_key"]
        and readback_body.get("status") in (
            "QUEUED", "LEASED", "EXECUTION_SUBMITTED", "VERIFYING", "SUCCEEDED", "FAILED", "BLOCKED"
        )
    )
    acknowledged = bool(http_accepted and valid_job_id and readback_matches)
    ack_note = {
        "ok": ack.get("ok"),
        "status": ack.get("status"),
        "dry_run": False,
        "error": ack.get("error"),
        "job_id_valid": valid_job_id,
        "readback_ok": readback.get("ok"),
        "readback_key_matches": readback_key == selected["op_key"],
        "readback_status": readback_body.get("status"),
        "readback_error": readback.get("error"),
    }
    event = {
        "schema": "noos-plan-completion-dispatch-event-v1",
        "event": "intake_submitted" if acknowledged else "intake_rejected",
        "at": utc_now(),
        "op_key": selected["op_key"],
        "item_id": selected["item_id"],
        "plan_id": selected["plan_id"],
        "job_id": job_id,
        "ack": ack_note,
        "recipe": recipe,
    }
    if acknowledged:
        updated_item: dict[str, Any] | None = None
        for item in items:
            if item["op_key"] == selected["op_key"]:
                item["status"] = "DISPATCHED"
                item["job_id"] = job_id
                item["concurrency_key"] = concurrency_key
                item["dispatched_at"] = utc_now()
                item["dry_run"] = False
                item["fencing_token"] = int(item.get("fencing_token") or 1) + 1
                updated_item = item
                break
        backlog["items"] = items
        backlog["counts"] = {
            s: sum(1 for i in items if i.get("status") == s)
            for s in ("READY", "DISPATCHED", "COMPLETE", "BLOCKED_WITH_REASON", "FOUNDER_BLOCKED")
        }
        backlog["updated_at"] = utc_now()

        sink_row: dict[str, Any] = {"ok": False, "skipped": True, "reason": "not_attempted"}
        try:
            import noos_plan_completion_supabase_sink_v1 as sink  # noqa: PLC0415

            if updated_item is not None:
                sink_row = sink.record_dispatch(item=updated_item, job_id=job_id, dry_run=False)
        except Exception as exc:  # noqa: BLE001
            sink_row = {"ok": False, "error": str(exc)[:240]}

        require_sink = (
            os.environ.get("NOOS_REQUIRE_SUPABASE_SINK", "").strip().lower() in ("1", "true", "yes")
            or os.environ.get("RAILWAY_ENVIRONMENT", "").strip().lower() == "production"
        )
        sink_durable = sink_row.get("ok") is True and not (require_sink and sink_row.get("skipped") is True)
        event["supabase_sink"] = sink_row
        if sink_durable:
            save_json(backlog_path, backlog)
            append_event(events_path, event)
        else:
            # Runway has an idempotent job already. Leave the item READY so the
            # same op_key can safely replay and reconcile after persistence recovers.
            acknowledged = False
            event["event"] = "intake_ack_persistence_failed"
            event["recovery"] = "retry_same_op_key; Runway idempotency prevents duplicate job creation"
            append_event(events_path, event)
    else:
        if write:
            append_event(events_path, event)

    row = {
        "schema": "noos-plan-completion-dispatch-v1",
        "at": utc_now(),
        "verdict": "DISPATCHED" if acknowledged else ("BLOCKED_SUPABASE_PERSISTENCE" if event.get("event") == "intake_ack_persistence_failed" else "BLOCKED_WITH_REASON"),
        "ok": acknowledged,
        "selected": {
            "item_id": selected["item_id"],
            "plan_id": selected["plan_id"],
            "op_key": selected["op_key"],
            "role": selected["role"],
            "title": selected["title"],
        },
        "job_id": job_id,
        "ack": event["ack"],
        "recipe": recipe,
        "preflight": {"ok": pf.get("ok"), "verdict": pf.get("verdict")},
        "dry_run": False,
        "report_line": (
            f"plan_dispatch · {'DISPATCHED' if acknowledged else 'BLOCKED'} "
            f"item={selected['item_id']} job={job_id} readback_verified=true"
        ),
    }
    if write:
        proof = ROOT / "receipts/proof" / f"noos-plan-completion-dispatch-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        proof.parent.mkdir(parents=True, exist_ok=True)
        proof.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(proof.relative_to(ROOT))
    return row


def mark_complete(*, op_key: str, write: bool = True, observation: dict[str, Any] | None = None) -> dict[str, Any]:
    """Mark COMPLETE only from a matching, independently verified Runway terminal receipt."""
    config = load_json(CONFIG)
    backlog_path = ROOT / str(config.get("runtime_queue_path") or ".noos-runtime/plan-completion/backlog-v1.json")
    events_path = ROOT / str(config.get("dispatch_events_path") or ".noos-runtime/plan-completion/dispatch-events-v1.jsonl")
    backlog = load_json(backlog_path)
    matched: dict[str, Any] | None = None
    for item in backlog.get("items") or []:
        if item.get("op_key") == op_key:
            matched = item
            break
    if matched is None:
        return {"ok": False, "verdict": "BLOCKED_UNKNOWN_OP_KEY", "op_key": op_key}
    if matched.get("status") == "COMPLETE":
        return {"ok": True, "verdict": "ALREADY_COMPLETE", "op_key": op_key}
    if matched.get("status") != "DISPATCHED":
        return {"ok": False, "verdict": "BLOCKED_ITEM_NOT_DISPATCHED", "op_key": op_key, "status": matched.get("status")}
    if matched.get("dry_run") is True:
        return {"ok": False, "verdict": "BLOCKED_DRY_RUN_HAS_NO_EXECUTION", "op_key": op_key}

    proof = observation if isinstance(observation, dict) else {}
    expected_job_id = matched.get("job_id")
    state = str(proof.get("state") or "").upper()
    evidence_ok = (
        bool(expected_job_id)
        and proof.get("job_id") == expected_job_id
        and proof.get("op_key") == op_key
        and state in _TERMINAL_OK
        and str(proof.get("verification_verdict") or "").upper() == "SUCCEEDED"
        and bool(proof.get("verified_at"))
        and bool(proof.get("terminal_receipt"))
        and proof.get("dry_run") is not True
    )
    if not evidence_ok:
        return {
            "ok": False,
            "verdict": "BLOCKED_TERMINAL_EVIDENCE_REQUIRED",
            "op_key": op_key,
            "expected_job_id": expected_job_id,
            "observed_job_id": proof.get("job_id"),
            "state": state or None,
            "verification_verdict": proof.get("verification_verdict"),
            "receipt_present": bool(proof.get("terminal_receipt")),
        }

    matched["status"] = "COMPLETE"
    matched["completed_at"] = utc_now()
    matched["fencing_token"] = int(matched.get("fencing_token") or 1) + 1
    matched["terminal_observation"] = proof
    items = backlog["items"]
    backlog["counts"] = {
        s: sum(1 for i in items if i.get("status") == s)
        for s in ("READY", "DISPATCHED", "COMPLETE", "BLOCKED_WITH_REASON", "FOUNDER_BLOCKED")
    }
    backlog["updated_at"] = utc_now()

    sink_row: dict[str, Any] | None = None
    if write:
        try:
            import noos_plan_completion_supabase_sink_v1 as sink  # noqa: PLC0415

            sink_row = sink.record_complete(item=matched, observation=proof)
        except Exception as exc:  # noqa: BLE001
            sink_row = {"ok": False, "error": str(exc)[:240]}
        require_sink = (
            os.environ.get("NOOS_REQUIRE_SUPABASE_SINK", "").strip().lower() in ("1", "true", "yes")
            or os.environ.get("RAILWAY_ENVIRONMENT", "").strip().lower() == "production"
        )
        sink_durable = sink_row.get("ok") is True and not (require_sink and sink_row.get("skipped") is True)
        if not sink_durable:
            return {
                "ok": False,
                "verdict": "BLOCKED_SUPABASE_PERSISTENCE",
                "op_key": op_key,
                "supabase_sink": sink_row,
            }
        save_json(backlog_path, backlog)
        append_event(events_path, {"event": "complete", "op_key": op_key, "at": utc_now(), "observation": proof})
    out = {"ok": True, "verdict": "COMPLETE" if write else "WOULD_COMPLETE", "op_key": op_key, "counts": backlog["counts"]}
    if sink_row is not None:
        out["supabase_sink"] = sink_row
    return out

_TERMINAL_OK = {"SUCCEEDED", "SUCCESS", "COMPLETE", "DONE", "COMPLETED"}
_TERMINAL_FAIL = {"FAILED", "FAILED_WITH_RECEIPT", "CANCELLED", "CANCELED", "DEAD_LETTER"}


def observe_inflight(*, write: bool = True) -> dict[str, Any]:
    """Poll Runway for DISPATCHED jobs; advance COMPLETE only on terminal success."""
    config = load_json(CONFIG)
    backlog_path = ROOT / str(config.get("runtime_queue_path") or ".noos-runtime/plan-completion/backlog-v1.json")
    events_path = ROOT / str(config.get("dispatch_events_path") or ".noos-runtime/plan-completion/dispatch-events-v1.jsonl")
    if not backlog_path.is_file():
        return {"ok": True, "verdict": "NO_BACKLOG", "observed": [], "completed": []}
    backlog = load_json(backlog_path)
    observed: list[dict[str, Any]] = []
    completed: list[str] = []
    blocked: list[dict[str, Any]] = []
    live = os.environ.get("NOOS_PLAN_COMPLETION_LIVE_INTAKE", "").strip() in ("1", "true", "yes")
    for item in list(backlog.get("items") or []):
        if item.get("status") != "DISPATCHED":
            continue
        job_id = item.get("job_id")
        if not job_id:
            item["status"] = "BLOCKED_WITH_REASON"
            item["blocker_reason"] = "dispatched_missing_job_id"
            item["fencing_token"] = int(item.get("fencing_token") or 1) + 1
            blocked.append({"op_key": item.get("op_key"), "state": "MISSING_JOB_ID"})
            if write:
                backlog["counts"] = {
                    s: sum(1 for i in backlog.get("items") or [] if i.get("status") == s)
                    for s in ("READY", "DISPATCHED", "COMPLETE", "BLOCKED_WITH_REASON", "FOUNDER_BLOCKED")
                }
                backlog["updated_at"] = utc_now()
                save_json(backlog_path, backlog)
                append_event(events_path, {"event": "dispatched_missing_job_id", "op_key": item.get("op_key"), "at": utc_now()})
            continue
        # Historical synthetic dispatches from the old dry-run path were never
        # real jobs. Return them to READY; never manufacture terminal success.
        if item.get("dry_run") is True:
            old_job_id = job_id
            item["status"] = "READY"
            item["simulation_job_id"] = old_job_id
            item["job_id"] = None
            item["dry_run_reset_at"] = utc_now()
            item["fencing_token"] = int(item.get("fencing_token") or 1) + 1
            obs = {"state": "DRY_RUN_RESET_TO_READY", "job_id": old_job_id, "dry_run": True, "op_key": item.get("op_key")}
            observed.append(obs)
            if write:
                backlog["counts"] = {
                    s: sum(1 for i in backlog.get("items") or [] if i.get("status") == s)
                    for s in ("READY", "DISPATCHED", "COMPLETE", "BLOCKED_WITH_REASON", "FOUNDER_BLOCKED")
                }
                backlog["updated_at"] = utc_now()
                save_json(backlog_path, backlog)
                append_event(events_path, {"event": "dry_run_reset_to_ready", "op_key": item["op_key"], "at": utc_now(), "simulation_job_id": old_job_id})
            continue
        if not live:
            continue
        job = runway.get_job(str(job_id))
        body = job.get("body") if isinstance(job.get("body"), dict) else {}
        state = str(body.get("status") or body.get("state") or "").upper()
        if not job.get("ok"):
            obs = {
                "state": "LOOKUP_FAILED",
                "job_id": job_id,
                "op_key": item.get("op_key"),
                "error": job.get("error") or job.get("status"),
            }
            observed.append(obs)
            if write:
                append_event(events_path, {"event": "job_lookup_failed", "op_key": item["op_key"], "job_id": job_id, "at": utc_now(), "error": obs["error"]})
            continue
        obs = runway.observe_job(
            {
                "job_id": job_id,
                "status": state,
                "op_key": item.get("op_key"),
                "updated_at": body.get("updated_at"),
                "started_at": body.get("started_at"),
                "budget": body.get("budget"),
                "provider": body.get("provider"),
                "terminal_receipt": (
                    body.get("receipt_ref")
                    or (body.get("result") or {}).get("receipt_ref")
                    or ((body.get("candidate") or {}).get("receipt_ref") if isinstance(body.get("candidate"), dict) else None)
                    or body.get("terminal_receipt")
                    or body.get("receipt")
                ),
                "verification_verdict": (body.get("verification") or {}).get("verdict") if isinstance(body.get("verification"), dict) else None,
                "verified_at": (body.get("verification") or {}).get("verified_at") if isinstance(body.get("verification"), dict) else None,
            }
        )
        observed.append(obs)
        if write:
            append_event(
                events_path,
                {"event": "observe", "op_key": item["op_key"], "job_id": job_id, "state": state, "at": utc_now()},
            )
        if state in _TERMINAL_OK:
            mark = mark_complete(op_key=item["op_key"], write=write, observation=obs)
            if mark.get("ok") and mark.get("verdict") == "COMPLETE":
                completed.append(item["op_key"])
                # Keep the current in-memory snapshot consistent if a later
                # item in this same batch causes the backlog file to be saved.
                item["status"] = "COMPLETE"
                item["completed_at"] = utc_now()
                item["terminal_observation"] = obs
            elif mark.get("verdict") == "BLOCKED_TERMINAL_EVIDENCE_REQUIRED":
                item["status"] = "BLOCKED_WITH_REASON"
                item["blocker_reason"] = "runway_success_missing_independent_verification_receipt"
                item["fencing_token"] = int(item.get("fencing_token") or 1) + 1
                blocked.append({"op_key": item["op_key"], "state": state, "reason": item["blocker_reason"]})
                if write:
                    backlog["counts"] = {
                        s: sum(1 for i in backlog.get("items") or [] if i.get("status") == s)
                        for s in ("READY", "DISPATCHED", "COMPLETE", "BLOCKED_WITH_REASON", "FOUNDER_BLOCKED")
                    }
                    backlog["updated_at"] = utc_now()
                    save_json(backlog_path, backlog)
                    append_event(events_path, {"event": "terminal_success_missing_proof", "op_key": item["op_key"], "job_id": job_id, "at": utc_now()})
        elif state in _TERMINAL_FAIL:
            item["status"] = "BLOCKED_WITH_REASON"
            item["blocker_reason"] = f"runway_terminal:{state}"
            item["fencing_token"] = int(item.get("fencing_token") or 1) + 1
            blocked.append({"op_key": item["op_key"], "state": state})
            if write:
                items = backlog["items"]
                backlog["counts"] = {
                    s: sum(1 for i in items if i.get("status") == s)
                    for s in ("READY", "DISPATCHED", "COMPLETE", "BLOCKED_WITH_REASON", "FOUNDER_BLOCKED")
                }
                backlog["updated_at"] = utc_now()
                save_json(backlog_path, backlog)
    return {
        "ok": True,
        "verdict": "OBSERVED",
        "observed": len(observed),
        "completed": completed,
        "blocked": blocked,
        "report_line": f"plan_observe · observed={len(observed)} completed={len(completed)} blocked={len(blocked)}",
    }


def post_telegram_summary(row: dict[str, Any]) -> dict[str, Any]:
    """Best-effort notify via deadman /plan-completion-report (secret from env)."""
    import urllib.error
    import urllib.request

    deadman = (os.environ.get("NOOS_DEADMAN_URL") or "https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev").rstrip("/")
    secret = (os.environ.get("NOOS_LOOP_SECRET") or os.environ.get("LOOP_RUNNER_SECRET") or "").strip()
    if not secret:
        return {"ok": False, "skipped": True, "reason": "loop_secret_missing"}
    counts = (row.get("compile") or {}).get("counts") or {}
    dispatch = row.get("dispatch") or {}
    payload = {
        "verdict": dispatch.get("verdict"),
        "ready": counts.get("READY"),
        "complete": counts.get("COMPLETE"),
        "founder_blocked": counts.get("FOUNDER_BLOCKED"),
        "item_id": (dispatch.get("selected") or {}).get("item_id"),
        "job_id": dispatch.get("job_id"),
        "receipt_path": dispatch.get("receipt_path"),
    }
    req = urllib.request.Request(
        deadman + "/plan-completion-report",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-NOOS-Loop-Secret": secret,
            "User-Agent": "noos-plan-completion-v1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {"ok": resp.status < 300, "status": resp.status, "body": body}
    except (OSError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:240]}


def reconcile_and_dispatch(*, write: bool = True) -> dict[str, Any]:
    compiled = compiler.compile_backlog(write=write)
    observed = observe_inflight(write=write)
    dispatched = dispatch_once(write=write, allow_dry_run=True)
    row = {
        "schema": "noos-plan-completion-reconcile-v1",
        "at": utc_now(),
        "compile": {
            "ok": compiled.get("ok"),
            "counts": compiled.get("counts"),
            "idle_no_work": compiled.get("idle_no_work"),
            "supabase_sink": compiled.get("supabase_sink"),
        },
        "observe": observed,
        "dispatch": dispatched,
        "ok": bool(compiled.get("ok")) and bool(dispatched.get("ok")) and bool(observed.get("ok")),
        "report_line": (
            f"plan_reconcile · {compiled.get('report_line')} · "
            f"{observed.get('report_line')} · {dispatched.get('report_line')}"
        ),
    }
    if os.environ.get("NOOS_PLAN_COMPLETION_TELEGRAM", "").strip() in ("1", "true", "yes"):
        row["telegram"] = post_telegram_summary(row)
    return row


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("reconcile").set_defaults(func=lambda _a: reconcile_and_dispatch())
    sub.add_parser("dispatch").set_defaults(func=lambda _a: dispatch_once())
    sub.add_parser("observe").set_defaults(func=lambda _a: observe_inflight())
    c = sub.add_parser("complete")
    c.add_argument("--op-key", required=True)
    c.add_argument("--observation-json", help="JSON read-back from the canonical Runway job and independent verifier")
    c.set_defaults(
        func=lambda a: mark_complete(
            op_key=a.op_key,
            observation=json.loads(a.observation_json) if a.observation_json else None,
        )
    )
    args = p.parse_args(argv)
    row = args.func(args)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
