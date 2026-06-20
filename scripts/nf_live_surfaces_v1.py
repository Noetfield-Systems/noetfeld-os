#!/usr/bin/env python3
"""NF live surfaces — one-line factory truth for panels + orient (L0.5)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from nf_factory_lib_v1 import (
    agent_id,
    first_pending_task,
    iso_now,
    load_event,
    load_sina,
    portfolio_progress,
    repo_root,
    write_event,
    write_ops_live_witness,
    write_sina,
)

try:
    from nf_mono_nerve_v1 import run_mono_nerve
except ImportError:
    run_mono_nerve = None  # type: ignore[misc, assignment]


def _git_short(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _portfolio_commercial_blockers() -> dict:
    """Inherit SourceA nerve / defer / advisory — portfolio agents must not silo."""
    sina = Path.home() / ".sina"
    parent = load_sina("agent-live-surfaces-v1.json") or {}
    defer = load_sina("commercial-email-send-defer-receipt-v1.json") or {}
    tf = load_sina("tf-live-surfaces-v1.json") or {}
    advisory = load_sina("future-loop-prompt-advisory-v1.json") or {}
    nerve = load_sina("agent-nerve-system-receipt-v1.json") or {}
    ship = nerve.get("ship_gates") or {}

    email_line = (
        str(defer.get("email_send_defer_line") or "")
        or str(parent.get("email_send_defer_line") or "")
        or str(tf.get("email_send_defer_line") or "")
        or str(ship.get("email_send_defer_line") or "")
    )
    defer_active = bool(
        defer.get("defer_active")
        if defer.get("defer_active") is not None
        else ship.get("w3_email_send_deferred", True)
    )
    blockers = list(advisory.get("commercial_blockers") or [])
    return {
        "email_send_defer_line": email_line,
        "defer_active": defer_active,
        "w3_send_ready": bool(ship.get("w3_send_ready")),
        "w3_email_send_deferred": bool(ship.get("w3_email_send_deferred", defer_active)),
        "commercial_blockers": blockers,
        "advisory_line": advisory.get("advisory_line"),
        "portfolio_parent_at": parent.get("synced_at") or parent.get("truth_bundle_at"),
    }


def build_live_surfaces(root: Path | None = None) -> dict:
    root = root or repo_root()
    mono_nerve = load_event("nf-mono-nerve-v1.json", root) or load_sina("nf-mono-nerve-v1.json") or {}
    if not mono_nerve.get("ok") and run_mono_nerve is not None:
        mono_nerve = run_mono_nerve(refresh=True)

    plan_path = root / "os/plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else {}
    pending = first_pending_task(plan)

    gate = load_event("nf-session-gate-v1.json", root) or load_sina("nf_session_gate_receipt_v1.json") or {}
    stale = load_event("nf-stale-guard-v1.json", root) or {}
    voyage = load_event("nf-voyage-integrity-v1.json", root) or {}
    routing = load_event("nf-live-routing-v1.json", root) or {}

    pid = (pending or {}).get("id", "")
    title = (pending or {}).get("title", "")
    product_now_line = f"{pid} — {title}" if pid else "no pending next_tasks"

    portfolio = portfolio_progress()
    portfolio_line = None
    if portfolio:
        portfolio_line = f"portfolio {portfolio['done']}/{portfolio['total']} done"

    gate_ok = bool(gate.get("ok"))
    context_stale = bool(stale.get("context_stale"))
    voyage_ok = bool(voyage.get("ok", True))

    portfolio_block = _portfolio_commercial_blockers()
    email_line = portfolio_block.get("email_send_defer_line") or mono_nerve.get("email_send_defer_line") or ""
    defer_active = portfolio_block.get("defer_active")
    if defer_active is None:
        defer_active = mono_nerve.get("defer_active")

    surfaces = {
        "schema_version": "nf-live-surfaces-v1",
        "generated_at": iso_now(),
        "agent_id": agent_id(),
        "plane": "noetfield_cloud",
        "product_now_line": product_now_line,
        "portfolio_now_line": portfolio_line,
        "email_send_defer_line": email_line,
        "defer_active": defer_active,
        "w3_send_ready": portfolio_block.get("w3_send_ready"),
        "w3_email_send_deferred": portfolio_block.get("w3_email_send_deferred"),
        "commercial_blockers": portfolio_block.get("commercial_blockers") or [],
        "advisory_line": portfolio_block.get("advisory_line"),
        "portfolio_parent_at": portfolio_block.get("portfolio_parent_at"),
        "mono_nerve_ok": bool(mono_nerve.get("ok")),
        "operations_inbox": (mono_nerve.get("operations_inbox") or {}).get("gw_status"),
        "gate_ok": gate_ok,
        "context_stale": context_stale,
        "voyage_ok": voyage_ok,
        "pending_task": pending,
        "git_sha": _git_short(root),
        "routing_pending": routing.get("pending_task"),
        "quote_rule": "Quote product_now_line AND email_send_defer_line — not chat memory",
        "heal": "make nf-onboard" if context_stale or not gate_ok or not mono_nerve.get("ok") or not email_line else None,
    }
    if not email_line:
        surfaces["surfaces_ok"] = False
    else:
        surfaces["surfaces_ok"] = True
    return surfaces


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    surfaces = build_live_surfaces()
    write_event("nf-live-surfaces-v1.json", surfaces)
    write_sina("nf-live-surfaces-v1.json", surfaces)
    write_ops_live_witness(surfaces)

    if args.json:
        print(json.dumps(surfaces, indent=2))
    else:
        print(f"product_now_line: {surfaces['product_now_line']}")
        if surfaces.get("portfolio_now_line"):
            print(f"portfolio_now_line: {surfaces['portfolio_now_line']}")
        if surfaces.get("email_send_defer_line"):
            print(f"email_send_defer_line: {surfaces['email_send_defer_line']}")
        print(f"defer_active={surfaces.get('defer_active')} w3_send_ready={surfaces.get('w3_send_ready')}")
        print(f"gate_ok={surfaces['gate_ok']} stale={surfaces['context_stale']} voyage_ok={surfaces['voyage_ok']}")
    ok = bool(surfaces.get("surfaces_ok")) and bool(surfaces.get("email_send_defer_line")) and bool(surfaces.get("mono_nerve_ok"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
