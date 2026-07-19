#!/usr/bin/env python3
"""End-to-end recovery-chain proof for NOOS durable health supervision.

Proves the full mechanism deterministically and offline (NO external model call,
NO live network): fresh RED signal → durable incident id → reconciler
actionable=1 → callable handler accepts and returns a concrete run id →
correction → independent verifier read-back → durable terminal receipt → next
reconciliation actionable=0 for that incident.

This is a MECHANISM proof over the durable-store contract using the file-backed
transport. LIVE activation against the production Supabase control table /
Unified Motor gateway / NOETFIELD-RUNWAY API is reported separately as blocked
when those are unconfigured (see the task's blocker verdicts).
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_health_incident_v1 as inc  # noqa: E402

PROOF_DIR = ROOT / "receipts/proof"
RUNTIME_DIR = ROOT / ".noos-runtime/health-incident-proof"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _callable_handler(incident: dict[str, Any]) -> dict[str, Any]:
    """A real registered NOOS-owned callable that accepts the incident and
    performs a bounded local correction, returning a concrete run id.

    No external model call: this writes a local correction marker so the
    recovery is a genuine side effect the verifier can read back."""
    run_id = f"noos-run-{int(time.time())}-{incident['incident_id'][-6:]}"
    marker = RUNTIME_DIR / f"correction-{incident['incident_id']}.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps({"incident_id": incident["incident_id"], "run_id": run_id, "corrected_at": utc_now()}, indent=2),
        encoding="utf-8",
    )
    return {"ok": True, "run_id": run_id, "receipt": str(marker.relative_to(ROOT))}


def run_proof() -> dict[str, Any]:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    store = RUNTIME_DIR / "incidents.json"
    if store.exists():
        store.unlink()
    transport = inc.FileDurableTransport(store)

    # 1. Fresh RED signal (synthetic, proof-tagged).
    source_sha = f"proofsha{int(time.time())}"
    source_run = "https://github.com/Noetfield-Systems/noetfeld-os/actions/runs/PROOF"
    fix_queue = ["integrator_status"]

    # 2. File durable incident(s).
    filed = inc.file_from_fix_queue(
        fix_queue, source_receipt="receipts/proof/PROOF-red.json",
        source_run_url=source_run, source_sha=source_sha, transport=transport,
    )
    incident_id = filed["created"][0]["incident_id"]

    # 3. Reconciler reads durable → actionable=1.
    before = inc.read_open_incidents(transport=transport)

    # 4. Dispatch to a real callable handler → concrete run id.
    open_row = before["open"][0]
    dispatch = inc.dispatch_incident(
        open_row, transport=transport,
        handlers={open_row["handler_id"]: _callable_handler},
    )

    # 5. Independent verifier: separate read-back of terminal state (author≠subject).
    after = inc.read_open_incidents(transport=transport)
    terminal_rows = [r for r in inc.FileDurableTransport(store)._load().values() if r["incident_id"] == incident_id]
    terminal = terminal_rows[0] if terminal_rows else {}
    verifier_ok = (
        dispatch.get("state") == inc.STATE_RESOLVED
        and terminal.get("state") == inc.STATE_RESOLVED
        and bool(terminal.get("worker_run_id"))
        and after["actionable"] == 0
    )

    # 6. Durable terminal receipt.
    receipt = {
        "schema": "noos-health-incident-recovery-proof-v1",
        "at": utc_now(),
        "proof_kind": "deterministic_offline_mechanism_proof",
        "no_external_model_call": True,
        "chain": {
            "fresh_red_source_sha": source_sha,
            "incident_id": incident_id,
            "reconciler_actionable_before": before["actionable"],
            "handler_id": open_row["handler_id"],
            "worker_run_id": dispatch.get("worker_run_id"),
            "terminal_state": terminal.get("state"),
            "terminal_receipt": terminal.get("terminal_receipt"),
            "reconciler_actionable_after": after["actionable"],
        },
        "independent_verifier_ok": verifier_ok,
        "live_activation": {
            "durable_store": "BLOCKED_DURABLE_STORE_NOT_CONFIGURED (Supabase env absent)",
            "note": "Mechanism proven over the durable-store contract; production authority is the Supabase control table (migration 0020).",
        },
        "ok": verifier_ok,
    }
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    out = PROOF_DIR / f"noos-health-incident-recovery-proof-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(out.relative_to(ROOT))
    return receipt


def main() -> int:
    row = run_proof()
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
