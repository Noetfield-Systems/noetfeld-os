#!/usr/bin/env python3
"""Machine owner for NOOS route ``receipt_writer_completion_evidence_repair``.

Executes the machine-safe portion of recipe NF-MOTOR-RECEIPT-WRITER-REPAIR-001
(v1.1.0) when a loop is classified DISPATCHING_COMPLETION_UNPROVEN:

    diagnose (BEFORE)  ->  repair (keyed evidence-sink retries ONLY)
                       ->  verify (AFTER, via the OBSERVER's read path)
                       ->  receipt (SUBMITTED for independent verification)

Hard walls, enforced in code and tested:
  * NEVER restarts or redeploys anything — the runner's restart endpoint is
    founder-only and this module contains no reference to it (test-enforced).
  * NEVER dispatches loop execution as a "repair" — re-running a loop is not
    retrying a receipt write. With no retryable outbox, it ESCALATES.
  * Writes only the evidence sink (noetfield_factory_cycle_runs), keyed by
    run_id with a read-before-write idempotency guard (L13).
  * recovery is PROVEN only by the before/after external check pair; a missing
    AFTER means UNPROVEN, never assumed (correlation != causality).

LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_observability_semantics_v1 import (  # noqa: E402
    DISPATCHING_COMPLETION_UNPROVEN,
    ROUTE_RECEIPT_WRITER_REPAIR,
    classify_loop_state,
)

RECIPE_ID = "NF-MOTOR-RECEIPT-WRITER-REPAIR-001"
RECIPE_VERSION = "1.1.0"
CANON_VERSION = "FOUNDER_CANON_v1+MACHINE_LOOPS_v1"
SINK_TABLE = "noetfield_factory_cycle_runs"
REGISTRY_TABLE = "noos_loop_registry"
RECEIPT_DIR = ROOT / "receipts"

# Actions this owner is structurally forbidden from taking (recipe
# founder_required + mutation_policy). Tests assert the module never gains the
# vocabulary to perform them.
FORBIDDEN_ACTIONS = ("restart_production_runtime", "redeploy_any_service", "modify_loop_execution_logic")

ESCALATE = "ESCALATE_FOUNDER_DECISION"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dedupe_key(loop_id: str, diagnosis_id: str) -> str:
    """Recipe trigger dedupe_key: receipt-repair:{loop_id}:{diagnosis_id}."""
    return f"receipt-repair:{loop_id}:{diagnosis_id}"


def _supabase_creds() -> tuple[str, str] | None:
    url = (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or "").strip()
    key = (
        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    if not url or not key:
        return None
    return url.rstrip("/"), key


def _rest(creds: tuple[str, str], table: str, *, query: str = "", payload: dict | None = None) -> dict[str, Any]:
    url, key = creds
    endpoint = f"{url}/rest/v1/{table}" + (f"?{query}" if query else "")
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if payload is not None:
        headers["Prefer"] = "return=minimal"
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read()
            return {"ok": True, "status": resp.getcode(), "rows": json.loads(body) if body and payload is None else []}
    except Exception as exc:  # noqa: BLE001 — probe surfaces the failure, never crashes the loop
        return {"ok": False, "status": None, "error": str(exc)[:300]}


# --- observer read path (BEFORE / AFTER captures) ---------------------------
def observe_loop(creds: tuple[str, str] | None, loop_id: str, factory_id: str, *, stale_minutes: float = 240.0) -> dict[str, Any]:
    """Classify one loop via the same dual-signal observer path the cockpit
    uses (dispatch heartbeat + completion receipt). This is deliberately NOT
    the writer's path — the recipe requires the independent observer read."""
    if creds is None:
        return {"ok": False, "reason": "supabase_not_configured", "execution_state": None}
    hb = _rest(
        creds, REGISTRY_TABLE,
        query=urllib.parse.urlencode({"select": "loop_id,last_fired_at,interval_minutes", "loop_id": f"eq.{loop_id}", "limit": "1"}),
    )
    cr = _rest(
        creds, SINK_TABLE,
        query=urllib.parse.urlencode({"select": "cycle_number,status,recorded_at,factory_id", "factory_id": f"eq.{factory_id}", "order": "recorded_at.desc", "limit": "1"}),
    )
    hb_row = (hb.get("rows") or [{}])[0] if hb.get("rows") else {}
    cr_row = (cr.get("rows") or [{}])[0] if cr.get("rows") else {}
    dispatch_at, completion_at = hb_row.get("last_fired_at"), cr_row.get("recorded_at")
    interval = hb_row.get("interval_minutes")

    def _age(ts: str | None) -> float | None:
        if not ts:
            return None
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            return (datetime.now(timezone.utc) - dt).total_seconds() / 60.0
        except ValueError:
            return None

    return classify_and_wrap(
        dispatch_age=_age(dispatch_at), completion_age=_age(completion_at),
        dispatch_threshold=(float(interval) * 2.0) if interval else stale_minutes,
        completion_threshold=stale_minutes,
        dispatch_ok=bool(hb.get("ok")), completion_ok=bool(cr.get("ok")),
        dispatch_at=dispatch_at, completion_at=completion_at,
    )


def classify_and_wrap(*, dispatch_age, completion_age, dispatch_threshold, completion_threshold,
                      dispatch_ok, completion_ok, dispatch_at, completion_at) -> dict[str, Any]:
    """Pure classification wrapper — injectable for hermetic tests."""
    c = classify_loop_state(
        dispatch_age_minutes=dispatch_age,
        dispatch_stale_threshold_minutes=dispatch_threshold,
        completion_age_minutes=completion_age,
        completion_stale_threshold_minutes=completion_threshold,
        dispatch_query_ok=dispatch_ok,
        completion_query_ok=completion_ok,
        dispatch_last_fired_at=dispatch_at,
        completion_last_recorded_at=completion_at,
        observed_at=utc_now(),
        status_source=f"{REGISTRY_TABLE}+{SINK_TABLE}",
        success_rate_sample_window_minutes=completion_threshold,
    )
    return {"ok": True, "execution_state": c["execution_state"], "route": c.get("route"),
            "dispatch_last_fired_at": dispatch_at, "completion_last_recorded_at": completion_at,
            "observed_at": utc_now(), "classification": c}


def build_repair_intent(loop_id: str, factory_id: str, before: dict[str, Any]) -> dict[str, Any] | None:
    """Consume a diagnosis; emit a repair intent ONLY for the bound route."""
    if before.get("execution_state") != DISPATCHING_COMPLETION_UNPROVEN:
        return None
    diagnosis_id = f"diag-{uuid.uuid4().hex[:12]}"
    return {
        "recipe_id": RECIPE_ID,
        "recipe_version": RECIPE_VERSION,
        "noos_route": ROUTE_RECEIPT_WRITER_REPAIR,
        "loop_id": loop_id,
        "factory_id": factory_id,
        "diagnosis_id": diagnosis_id,
        "dedupe_key": dedupe_key(loop_id, diagnosis_id),
        "before": before,
        "created_at": utc_now(),
    }


# --- machine-safe repair -----------------------------------------------------
def retry_outbox(creds: tuple[str, str] | None, outbox_rows: list[dict[str, Any]], *,
                 existing_run_ids: set[str] | None = None) -> dict[str, Any]:
    """Retry keyed failed evidence-sink writes. Idempotency: read-before-write
    on run_id; a row whose run_id already exists in the sink is skipped, never
    duplicated (L13). Only SINK_TABLE writes ever happen here."""
    retried, skipped, failed = [], [], []
    for row in outbox_rows:
        run_id = str(row.get("run_id") or "")
        if not run_id:
            failed.append({"row": row, "error": "missing run_id idempotency key"})
            continue
        if existing_run_ids is not None:
            exists = run_id in existing_run_ids
        else:
            if creds is None:
                failed.append({"run_id": run_id, "error": "sink not configured"})
                continue
            hit = _rest(creds, SINK_TABLE, query=urllib.parse.urlencode({"select": "run_id", "run_id": f"eq.{run_id}", "limit": "1"}))
            if not hit.get("ok"):
                failed.append({"run_id": run_id, "error": f"idempotency read failed: {hit.get('error')}"})
                continue
            exists = bool(hit.get("rows"))
        if exists:
            skipped.append(run_id)
            continue
        if existing_run_ids is not None:
            retried.append(run_id)  # hermetic mode: caller owns the actual write
            continue
        wr = _rest(creds, SINK_TABLE, payload=row)
        (retried if wr.get("ok") else failed).append(run_id if wr.get("ok") else {"run_id": run_id, "error": wr.get("error")})
    return {"retried": retried, "skipped_existing": skipped, "failed": failed}


def repair(intent: dict[str, Any], *, creds: tuple[str, str] | None, outbox_rows: list[dict[str, Any]] | None,
           existing_run_ids: set[str] | None = None) -> dict[str, Any]:
    """The ONLY machine-safe repair is retrying keyed failed writes. With no
    retryable outbox there is nothing this owner may do alone: it escalates
    with the diagnosis attached. It never re-dispatches loop execution and
    never touches runtime (recipe failure_policy: escalate, never improvise)."""
    if not outbox_rows:
        return {
            "action": ESCALATE,
            "reason": "no retryable failed-write outbox available; writer-component fix or runner-side re-emit needs founder-gated work",
            "dedupe_key": intent["dedupe_key"],
            "diagnosis": intent["before"],
            "escalation_route": "founder-decision issue with the diagnosis attached (recipe escalation_route)",
        }
    result = retry_outbox(creds, outbox_rows, existing_run_ids=existing_run_ids)
    result["action"] = "retried_keyed_failed_receipt_writes"
    result["dedupe_key"] = intent["dedupe_key"]
    return result


# --- before/after causality pair ---------------------------------------------
def before_after_pair(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Recovery is PROVEN only when the AFTER observation (observer read path)
    shows fresh completion evidence. Anything else is UNPROVEN — including a
    missing/unqueryable AFTER."""
    after_state = after.get("execution_state")
    proven = bool(after.get("ok")) and after_state == "RUNNING_CONFIRMED"
    return {
        "check": "before_after_pair",
        "decision": "PASS" if proven else "FAIL",
        "recovery_state": "PROVEN" if proven else "UNPROVEN",
        "reason": (
            "AFTER observation shows fresh completion evidence via the independent observer path"
            if proven else
            f"AFTER observation is {after_state or 'unavailable'} — recovery not claimed (correlation != causality)"
        ),
        "external": True,
        "before": {"execution_state": before.get("execution_state"), "completion_last_recorded_at": before.get("completion_last_recorded_at"), "observed_at": before.get("observed_at")},
        "after": {"execution_state": after_state, "completion_last_recorded_at": after.get("completion_last_recorded_at"), "observed_at": after.get("observed_at")},
        "checked_at": utc_now(),
    }


def write_receipt(payload: dict[str, Any], *, kind: str) -> Path:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = utc_now().replace(":", "").replace("-", "")
    path = RECEIPT_DIR / f"noos-receipt-writer-repair-{kind}-{stamp}.json"
    payload.setdefault("status", "SUBMITTED for independent verification")
    payload.setdefault("canon_version", CANON_VERSION)
    payload.setdefault("laws", "FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.")
    payload.setdefault("forbidden_actions_not_taken", list(FORBIDDEN_ACTIONS))
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


# --- CLI ----------------------------------------------------------------------
def cmd_run(args: argparse.Namespace) -> int:
    creds = _supabase_creds()
    before = observe_loop(creds, args.loop_id, args.factory_id or f"loop-{args.loop_id}")
    if not before.get("ok"):
        print(json.dumps({"status": "BLOCKED_WITH_REASON", "reason": before.get("reason", "observer unavailable")}, indent=2))
        return 2
    intent = build_repair_intent(args.loop_id, args.factory_id or f"loop-{args.loop_id}", before)
    if intent is None:
        print(json.dumps({"status": "NO_ACTION", "reason": f"loop is {before.get('execution_state')}, route not {ROUTE_RECEIPT_WRITER_REPAIR}"}, indent=2))
        return 0
    outbox_rows = json.loads(Path(args.outbox).read_text()) if args.outbox else None
    repair_result = repair(intent, creds=creds, outbox_rows=outbox_rows)
    after = observe_loop(creds, args.loop_id, intent["factory_id"]) if args.verify_after else {"ok": False, "execution_state": None, "note": "AFTER capture deferred — rerun with --verify-after after one full loop cycle"}
    pair = before_after_pair(before, after)
    receipt = {
        "schema": "noos-receipt-writer-repair-run-v1",
        "recipe_id": RECIPE_ID, "recipe_version": RECIPE_VERSION,
        "intent": intent, "repair": repair_result, "verification_results": [pair],
        "states": {"recovery": {"state": pair["recovery_state"], **({"evidence_ref": pair["reason"]} if pair["recovery_state"] == "PROVEN" else {"reason": pair["reason"]})}},
        "generated_at": utc_now(),
    }
    path = write_receipt(receipt, kind=args.loop_id)
    print(json.dumps({"status": repair_result.get("action"), "recovery": pair["recovery_state"], "receipt": str(path.relative_to(ROOT))}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="diagnose -> machine-safe repair -> before/after pair -> receipt")
    run.add_argument("--loop-id", required=True)
    run.add_argument("--factory-id", default="")
    run.add_argument("--outbox", default="", help="JSON file of keyed failed sink writes to retry (run_id required per row)")
    run.add_argument("--verify-after", action="store_true", help="capture the AFTER observation now (run one full loop cycle after repair first)")
    run.set_defaults(fn=cmd_run)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
