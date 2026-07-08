#!/usr/bin/env python3
"""GHA witness — read-only noos_loop_registry stale_count (no /tick, no upsert)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from autorun_status_v1 import WORKFLOWS, probe_supabase_noos_liveness_registry  # noqa: E402

PROOF = ROOT / "receipts/proof/noos-liveness-registry-witness-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def witness(*, write_receipt: bool = False) -> dict[str, Any]:
    wf_doc = json.loads(WORKFLOWS.read_text(encoding="utf-8"))
    wf = next((w for w in wf_doc.get("workflows") or [] if w.get("id") == "noos_loop_liveness_registry"), None)
    if not wf:
        return {"ok": False, "error": "workflow_not_registered"}
    stale_minutes = float(wf_doc.get("stale_threshold_minutes") or 30)
    probe = probe_supabase_noos_liveness_registry(wf, wf_doc, stale_minutes)
    stale_count = int(probe.get("stale_count") or 0)
    status = probe.get("status")
    overall = "green" if stale_count == 0 and status == "RUNNING" else "yellow"
    if probe.get("reason") == "supabase_not_configured":
        overall = "yellow"

    row: dict[str, Any] = {
        "schema": "noos-liveness-registry-witness-v1",
        "at": utc_now(),
        "read_only": True,
        "mutates_registry": False,
        "witness_mode": True,
        "one_law": "Observe Supabase noos_loop_registry only — never call /tick or upsert rows.",
        "stale_count": stale_count,
        "registry_rows": probe.get("registry_rows"),
        "stale_loops": probe.get("stale_loops"),
        "probe_status": status,
        "probe_reason": probe.get("reason"),
        "overall_status": overall,
        "closure_token": f"NOOS_LIVENESS_REGISTRY_WITNESS: {overall}",
        "probe": probe,
        "repair_hint": "make integrator-repair-autorun (local) — witness does not repair",
    }
    row["ok"] = probe.get("reason") != "supabase_query_failed"
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
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
