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


def dry_run_ack(intake: dict[str, Any]) -> dict[str, Any]:
    """Offline deterministic ack when Runway API is not live (commissioning / CI)."""
    job_id = "rj_" + intake["idempotency_key"][:32]
    return {
        "ok": True,
        "status": 202,
        "dry_run": True,
        "op_key": intake["idempotency_key"],
        "body": {"job_id": job_id, "status": "queued", "created": True},
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
            },
            "artifact_refs": [],
        },
    }

    live = os.environ.get("NOOS_PLAN_COMPLETION_LIVE_INTAKE", "").strip() in ("1", "true", "yes")
    if pf.get("ok") and live:
        ack = runway.submit_intake(intake)
    elif allow_dry_run:
        ack = dry_run_ack(intake)
    else:
        return {
            "ok": False,
            "verdict": runway.BLOCKED_RUNWAY_API_NOT_LIVE,
            "preflight": pf,
            "selected": selected,
            "report_line": "plan_dispatch · runway not live",
        }

    acknowledged = bool(ack.get("ok")) and str(ack.get("op_key") or "") == selected["op_key"]
    job_id = None
    if isinstance(ack.get("body"), dict):
        job_id = ack["body"].get("job_id")

    event = {
        "schema": "noos-plan-completion-dispatch-event-v1",
        "event": "intake_submitted" if acknowledged else "intake_rejected",
        "at": utc_now(),
        "op_key": selected["op_key"],
        "item_id": selected["item_id"],
        "plan_id": selected["plan_id"],
        "job_id": job_id,
        "ack": {"ok": ack.get("ok"), "status": ack.get("status"), "dry_run": ack.get("dry_run"), "error": ack.get("error")},
        "recipe": recipe,
    }

    if acknowledged:
        for item in items:
            if item["op_key"] == selected["op_key"]:
                item["status"] = "DISPATCHED"
                item["job_id"] = job_id
                item["concurrency_key"] = concurrency_key
                item["dispatched_at"] = utc_now()
                break
        backlog["items"] = items
        backlog["counts"] = {
            s: sum(1 for i in items if i.get("status") == s)
            for s in ("READY", "DISPATCHED", "COMPLETE", "BLOCKED_WITH_REASON", "FOUNDER_BLOCKED")
        }
        backlog["updated_at"] = utc_now()
        if write:
            save_json(backlog_path, backlog)
            append_event(events_path, event)

    row = {
        "schema": "noos-plan-completion-dispatch-v1",
        "at": utc_now(),
        "verdict": "DISPATCHED" if acknowledged else "BLOCKED_WITH_REASON",
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
        "dry_run": bool(ack.get("dry_run")),
        "report_line": (
            f"plan_dispatch · {'DISPATCHED' if acknowledged else 'REJECTED'} "
            f"item={selected['item_id']} job={job_id} dry_run={bool(ack.get('dry_run'))}"
        ),
    }
    if write:
        proof = ROOT / "receipts/proof" / f"noos-plan-completion-dispatch-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        proof.parent.mkdir(parents=True, exist_ok=True)
        proof.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(proof.relative_to(ROOT))
    return row


def mark_complete(*, op_key: str, write: bool = True) -> dict[str, Any]:
    """External verifier / Runway terminal observation marks COMPLETE (D4)."""
    config = load_json(CONFIG)
    backlog_path = ROOT / str(config.get("runtime_queue_path") or ".noos-runtime/plan-completion/backlog-v1.json")
    events_path = ROOT / str(config.get("dispatch_events_path") or ".noos-runtime/plan-completion/dispatch-events-v1.jsonl")
    backlog = load_json(backlog_path)
    found = False
    for item in backlog.get("items") or []:
        if item.get("op_key") == op_key:
            item["status"] = "COMPLETE"
            item["completed_at"] = utc_now()
            found = True
            break
    if not found:
        return {"ok": False, "verdict": "BLOCKED_UNKNOWN_OP_KEY", "op_key": op_key}
    items = backlog["items"]
    backlog["counts"] = {
        s: sum(1 for i in items if i.get("status") == s)
        for s in ("READY", "DISPATCHED", "COMPLETE", "BLOCKED_WITH_REASON", "FOUNDER_BLOCKED")
    }
    backlog["updated_at"] = utc_now()
    if write:
        save_json(backlog_path, backlog)
        append_event(events_path, {"event": "complete", "op_key": op_key, "at": utc_now()})
    return {"ok": True, "verdict": "COMPLETE", "op_key": op_key, "counts": backlog["counts"]}


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
    dispatched = dispatch_once(write=write, allow_dry_run=True)
    row = {
        "schema": "noos-plan-completion-reconcile-v1",
        "at": utc_now(),
        "compile": {"ok": compiled.get("ok"), "counts": compiled.get("counts"), "idle_no_work": compiled.get("idle_no_work")},
        "dispatch": dispatched,
        "ok": bool(compiled.get("ok")) and bool(dispatched.get("ok")),
        "report_line": f"plan_reconcile · {compiled.get('report_line')} · {dispatched.get('report_line')}",
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
    c = sub.add_parser("complete")
    c.add_argument("--op-key", required=True)
    c.set_defaults(func=lambda a: mark_complete(op_key=a.op_key))
    args = p.parse_args(argv)
    row = args.func(args)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
