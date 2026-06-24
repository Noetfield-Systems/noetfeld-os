#!/usr/bin/env python3
"""NF truth bundle — compose gate + stale + voyage + surfaces + portfolio."""

from __future__ import annotations

import argparse
import json
import sys

from nf_factory_lib_v1 import (
    agent_id,
    iso_now,
    load_event,
    load_sina,
    portfolio_progress,
    repo_root,
    write_event,
    write_sina,
)


def build_truth_bundle() -> dict:
    root = repo_root()
    bundle = {
        "schema_version": "nf-truth-bundle-v1",
        "generated_at": iso_now(),
        "agent_id": agent_id(),
        "plane": "noetfield_cloud",
        "mono_nerve": load_event("nf-mono-nerve-v1.json", root) or load_sina("nf-mono-nerve-v1.json"),
        "session_gate": load_event("nf-session-gate-v1.json", root) or load_sina("nf_session_gate_receipt_v1.json"),
        "stale_guard": load_event("nf-stale-guard-v1.json", root),
        "voyage_integrity": load_event("nf-voyage-integrity-v1.json", root),
        "live_routing": load_event("nf-live-routing-v1.json", root),
        "live_surfaces": load_event("nf-live-surfaces-v1.json", root) or load_sina("nf-live-surfaces-v1.json"),
        "receipt_cascade": load_event("nf-receipt-cascade-v1.json", root),
        "gatekeeper": load_event("nf-gatekeeper-v1.json", root) or load_sina("nf-gatekeeper-receipt-v1.json"),
        "portfolio": portfolio_progress(),
        "live_status": "reports/agent-auto/LIVE-STATUS.md",
        "routing_card": "ROUTING_CARD.md",
    }
    surfaces = bundle.get("live_surfaces") or {}
    mono = bundle.get("mono_nerve") or {}
    bundle["product_now_line"] = surfaces.get("product_now_line")
    bundle["portfolio_now_line"] = surfaces.get("portfolio_now_line")
    bundle["email_send_defer_line"] = surfaces.get("email_send_defer_line") or mono.get("email_send_defer_line")
    bundle["ecosystem_nerve"] = load_sina("ecosystem-live-nerve-v1.json")
    bundle["defer_active"] = surfaces.get("defer_active") if surfaces.get("defer_active") is not None else mono.get("defer_active")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    bundle = build_truth_bundle()
    write_event("nf-truth-bundle-v1.json", bundle)
    write_sina("nf-truth-bundle-v1.json", bundle)

    if args.json:
        print(json.dumps(bundle, indent=2))
    else:
        print(f"product_now_line: {bundle.get('product_now_line')}")
        print(f"portfolio_now_line: {bundle.get('portfolio_now_line')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
