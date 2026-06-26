#!/usr/bin/env python3
"""NF orient cascade — lost-state recovery (manual trigger only)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from nf_factory_lib_v1 import load_json, load_sina


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], root: Path) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, cwd=root, text=True, stderr=subprocess.STDOUT)
        return 0, out.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, (e.output or "").strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=None)
    args = parser.parse_args()
    root = Path(args.root or Path(__file__).resolve().parents[1])

    steps: list[dict] = []
    for label, cmd in [
        ("mono_nerve", ["python3", "scripts/nf_mono_nerve_v1.py", "--json"]),
        ("founder_input_sync", ["python3", "scripts/nf_founder_input_sync_v1.py", "--json"]),
        ("session_gate", ["python3", "scripts/nf_session_gate_run_v1.py", "--json"]),
        ("live_orient", ["bash", "scripts/nf-live-orient-v1.sh"]),
        ("stale_guard", ["python3", "scripts/nf_stale_guard_v1.py", "--json"]),
        ("voyage_integrity", ["python3", "scripts/nf_voyage_integrity_v1.py", "--json"]),
        ("live_surfaces", ["python3", "scripts/nf_live_surfaces_v1.py", "--json"]),
        ("receipt_cascade", ["python3", "scripts/nf_receipt_cascade_v1.py", "--json"]),
        ("orient_read_chain", ["python3", "scripts/nf_orient_read_chain_v1.py", "--json"]),
        ("anti_staleness_max", ["python3", "scripts/nf_anti_staleness_max_v1.py", "--json"]),
        ("gatekeeper", ["python3", "scripts/nf_gatekeeper_v1.py", "--json"]),
    ]:
        rc, out = _run(cmd, root)
        steps.append({"step": label, "ok": rc == 0, "exit_code": rc})

    ssot = load_json(root / "data/nf_orient_routing_v1.json") or {}
    read_chain = ssot.get("orient_read_chain") or []

    graph_path = root / "os/NF_UNIFIED_ROUTING_GRAPH.json"
    ladder = []
    if graph_path.is_file():
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        ladder = graph.get("routing_ladder") or []

    events = root / "reports/agent-auto/events"
    stale = {}
    routing = {}
    cascade = {}
    surfaces = {}
    mono = load_sina("nf-mono-nerve-v1.json") or {}
    eco = load_sina("ecosystem-live-nerve-v1.json") or {}
    if (events / "nf-stale-guard-v1.json").is_file():
        stale = json.loads((events / "nf-stale-guard-v1.json").read_text())
    if (events / "nf-live-routing-v1.json").is_file():
        routing = json.loads((events / "nf-live-routing-v1.json").read_text())
    if (events / "nf-receipt-cascade-v1.json").is_file():
        cascade = json.loads((events / "nf-receipt-cascade-v1.json").read_text())
    if (events / "nf-live-surfaces-v1.json").is_file():
        surfaces = json.loads((events / "nf-live-surfaces-v1.json").read_text())

    pending = surfaces.get("pending_task") or routing.get("pending_task") or stale.get("pending_task")
    next_action = "ASK founder for implement order"
    if pending and pending.get("id"):
        next_action = f"Propose task {pending['id']} — wait for founder implement"

    report = {
        "schema_version": "nf-orient-routing-v1",
        "generated_at": _iso_now(),
        "ok": all(s["ok"] for s in steps),
        "steps": steps,
        "routing_ladder": ladder,
        "pending_task": pending,
        "product_now_line": surfaces.get("product_now_line"),
        "email_send_defer_line": surfaces.get("email_send_defer_line") or mono.get("email_send_defer_line"),
        "ecosystem_nerve_ok": eco.get("ok"),
        "receipt_cascade": cascade,
        "next_action": next_action,
        "read_chain": read_chain,
        "quote_rule": "Quote product_now_line AND email_send_defer_line — not chat memory",
    }

    events.mkdir(parents=True, exist_ok=True)
    (events / "nf-orient-routing-v1.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    sina = Path.home() / ".sina"
    try:
        sina.mkdir(parents=True, exist_ok=True)
        (sina / "nf-orient-routing-report-v1.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"nf_orient: {'PASS' if report['ok'] else 'FAIL'}")
        print(f"defer: {report.get('email_send_defer_line')}")
        print(f"next: {next_action}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
