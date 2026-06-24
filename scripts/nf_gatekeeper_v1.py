#!/usr/bin/env python3
"""NF execution gatekeeper — invariant before implement (no LLM).

Invariant:
  session_gate.ok ∧ mono_nerve.ok ∧ ¬context_stale ∧ voyage.ok ∧ receipt_cascade.ok
  ∧ email_send_defer_line present ∧ ¬(defer_active ∧ email_lane_task)
  ∧ (founder implement OR dry-run advisory)

Law: docs/ops/NF_GAOS_W3_FACTORY_SPINE_LOCKED_v1.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from nf_factory_lib_v1 import (
    agent_id,
    iso_now,
    load_event,
    load_lock,
    load_sina,
    repo_root,
    write_event,
    write_sina,
)
from nf_mono_nerve_v1 import task_touches_email_lane


def run_gatekeeper(require_implement: bool = False) -> dict:
    root = repo_root()
    reasons: list[str] = []

    gate = load_event("nf-session-gate-v1.json", root) or load_sina("nf_session_gate_receipt_v1.json") or {}
    if not gate.get("ok"):
        reasons.append("SESSION_GATE_FAIL")

    mono = load_event("nf-mono-nerve-v1.json", root) or load_sina("nf-mono-nerve-v1.json") or {}
    if not mono.get("ok"):
        reasons.append("MONO_NERVE_FAIL")

    stale = load_event("nf-stale-guard-v1.json", root) or {}
    if stale.get("context_stale"):
        reasons.append("CONTEXT_STALE")

    voyage = load_event("nf-voyage-integrity-v1.json", root) or {}
    if voyage and not voyage.get("ok", True):
        reasons.append("VOYAGE_INTEGRITY_FAIL")

    cascade = load_event("nf-receipt-cascade-v1.json", root) or load_sina("nf-receipt-cascade-v1.json") or {}
    if cascade and not cascade.get("ok", True):
        nodes = cascade.get("nodes") or []
        reasons.append(f"RECEIPT_CASCADE_FAIL:{','.join(nodes)}")

    surfaces = load_event("nf-live-surfaces-v1.json", root) or load_sina("nf-live-surfaces-v1.json") or {}
    pending = surfaces.get("pending_task") or stale.get("pending_task") or voyage.get("pending_task")
    task_id = (pending or {}).get("id", "")
    task_override = os.environ.get("NF_TASK_ID", "").strip()
    check_task = pending or ({"id": task_override, "title": task_override} if task_override else None)

    email_line = surfaces.get("email_send_defer_line") or mono.get("email_send_defer_line") or ""
    if not email_line:
        reasons.append("MISSING_EMAIL_SEND_DEFER_LINE")

    defer_active = surfaces.get("defer_active")
    if defer_active is None:
        defer_active = mono.get("defer_active")
    if defer_active and task_touches_email_lane(check_task):
        reasons.append("EMAIL_SEND_DEFERRED")

    founder_implement = os.environ.get("NF_FOUNDER_IMPLEMENT", "").strip().lower() in ("1", "true", "yes")
    if require_implement and not founder_implement:
        reasons.append("FOUNDER_IMPLEMENT_REQUIRED")

    lock = load_lock() or {}
    if lock.get("locked") and lock.get("agent_id") != agent_id():
        reasons.append(f"EXECUTOR_LOCK_HELD:{lock.get('agent_id')}")

    ok = len(reasons) == 0
    receipt = {
        "schema_version": "nf-gatekeeper-v1",
        "generated_at": iso_now(),
        "status": "PASS" if ok else "FAIL",
        "ok": ok,
        "safe_to_implement": ok,
        "reasons": reasons,
        "agent_id": agent_id(),
        "pending_task_id": task_id,
        "founder_implement": founder_implement,
        "product_now_line": surfaces.get("product_now_line"),
        "email_send_defer_line": email_line,
        "defer_active": defer_active,
        "next": "SAFE TO IMPLEMENT" if ok else "EXECUTION DENIED — fix reasons then re-run nf-gatekeeper",
    }

    write_event("nf-gatekeeper-v1.json", receipt)
    write_sina("nf-gatekeeper-receipt-v1.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-implement", action="store_true", help="Fail unless NF_FOUNDER_IMPLEMENT=1")
    args = parser.parse_args()

    receipt = run_gatekeeper(require_implement=args.require_implement)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"STATUS: {receipt['status']}")
        if receipt["ok"]:
            print(f"Task: {receipt.get('pending_task_id')}")
            print(f"Line: {receipt.get('product_now_line')}")
            print(f"Defer: {receipt.get('email_send_defer_line')}")
            print("SAFE TO IMPLEMENT")
        else:
            print("EXECUTION DENIED")
            for r in receipt["reasons"]:
                print(f"  - {r}")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
