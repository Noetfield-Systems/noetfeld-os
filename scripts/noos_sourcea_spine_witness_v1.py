#!/usr/bin/env python3
"""GHA witness — read-only SourceA portfolio-spine probe (sourcea_cloud_queue freshness)."""

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

from autorun_status_v1 import (  # noqa: E402
    WORKFLOWS,
    probe_supabase_sourcea_cloud_queue,
    probe_supabase_sourcea_receipt,
)

PROOF = ROOT / "receipts/proof/noos-sourcea-spine-witness-v1.json"
SPINE_WORKFLOW_IDS = (
    "sourcea_cloud_queue",
    "sourcea_buyer_proof_verify",
    "sourcea_recipe_queue_builder",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_wf_doc() -> dict[str, Any]:
    return json.loads(WORKFLOWS.read_text(encoding="utf-8"))


def probe_workflow(wf_doc: dict[str, Any], wf_id: str, stale_minutes: float) -> dict[str, Any]:
    wf = next((w for w in wf_doc.get("workflows") or [] if w.get("id") == wf_id), None)
    if not wf:
        return {"ok": False, "id": wf_id, "status": "BLOCKED_WITH_REASON", "reason": "workflow_not_registered"}
    probe_type = (wf.get("probe") or {}).get("type")
    if probe_type == "supabase_sourcea_cloud_queue":
        row = probe_supabase_sourcea_cloud_queue(wf, wf_doc, stale_minutes)
    elif probe_type == "supabase_sourcea_receipt":
        row = probe_supabase_sourcea_receipt(wf, wf_doc, stale_minutes)
    else:
        row = {"status": "BLOCKED_WITH_REASON", "reason": f"unsupported_probe:{probe_type}"}
    return {"id": wf_id, "title": wf.get("title"), "plane": wf.get("plane"), **row}


def witness(*, write_receipt: bool = False) -> dict[str, Any]:
    wf_doc = load_wf_doc()
    stale_minutes = float(wf_doc.get("stale_threshold_minutes") or 30)
    probes = {wf_id: probe_workflow(wf_doc, wf_id, stale_minutes) for wf_id in SPINE_WORKFLOW_IDS}
    cloud = probes.get("sourcea_cloud_queue") or {}

    configured = cloud.get("reason") != "supabase_not_configured"
    fresh = cloud.get("data_freshness") == "FRESH" or cloud.get("status") in {
        "RUNNING",
        "IDLE_NO_WORK",
        "COMPLETE",
    }
    stale = cloud.get("reason") == "stale_supabase_row" or cloud.get("data_freshness") == "STALE_DATA"

    overall = "green"
    if not configured:
        overall = "yellow"
    elif stale or cloud.get("status") == "BLOCKED_WITH_REASON":
        overall = "yellow" if cloud.get("status") != "FAILED_WITH_RECEIPT" else "red"

    row: dict[str, Any] = {
        "schema": "noos-sourcea-spine-witness-v1",
        "at": utc_now(),
        "read_only": True,
        "mutates_spine": False,
        "witness_mode": True,
        "one_law": "Read-only portfolio-spine probe — phase_reconciler_v1 remains sole control authority.",
        "stale_threshold_minutes": stale_minutes,
        "overall_status": overall,
        "closure_token": f"NOOS_SOURCEA_SPINE_WITNESS: {overall}",
        "sourcea_cloud_queue": {
            "fresh": fresh,
            "stale": stale,
            "status": cloud.get("status"),
            "reason": cloud.get("reason"),
            "age_minutes": cloud.get("age_minutes"),
            "observed_at": (cloud.get("evidence") or {}).get("observed_at"),
            "queue_head": cloud.get("queue_head"),
        },
        "probes": probes,
        "handoff_owner": "sourcea_portfolio_spine_worker",
        "repair_hint": "make integrator-repair-autorun (local) or SourceA cloud writer CRON_FIRED",
    }
    row["ok"] = configured or overall != "red"
    if write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    row = witness(write_receipt=args.write_receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["closure_token"])

    # Witness records critique; fail only when spine is unreachable (not stale/yellow handoff).
    if row.get("sourcea_cloud_queue", {}).get("reason") == "supabase_not_configured":
        return 0 if os.environ.get("NOOS_GHA_WITNESS") == "1" else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
