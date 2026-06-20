#!/usr/bin/env python3
"""Noetfield session gate — mono nerve receipts required (read-only SourceA/data)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "entry/START_HERE_LOCKED_v1.md",
    "ROUTING_CARD.md",
    "docs/ops/NF_GAOS_W0_LOCKED_v1.md",
    "docs/ops/NF_GAOS_W1_LOCKED_v1.md",
    "docs/ops/NF_GAOS_W3_FACTORY_SPINE_LOCKED_v1.md",
    "docs/ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md",
    "docs/ops/NF_ANTI_STALENESS_MAXIMUM_FIX_SET_LOCKED_v1.md",
    "data/nf_anti_staleness_max_v1.json",
    "data/nf_orient_routing_v1.json",
    "data/nf_mono_nerve_wiring_v1.json",
    "os/NF_REPO_CAPABILITY_MAP.json",
    "os/NF_UNIFIED_ROUTING_GRAPH.json",
    "os/NF_SSOT_INVENTORY.json",
    "os/NF_BAVT_STRATEGY.json",
    "os/plan.json",
    "os/SHIP_NOW.md",
    "PROJECT_BOUNDARIES_LOCKED.md",
    ".cursor/agent-memory/MEMORY_LOCKED.yaml",
    ".cursor/incidents/REGISTRY.md",
]

ROLE_AGENTS = {
    "cloud": "noetfield_cloud",
    "local": "noetfield_local",
    "default": "noetfield_cloud",
}


def run_gate(role: str, agent_override: str | None) -> dict:
    root = _repo_root()
    agent_id = agent_override or os.environ.get("NOETFIELD_AGENT_ID") or ROLE_AGENTS.get(role, ROLE_AGENTS["default"])
    gates: list[dict] = []
    ok = True

    for rel in REQUIRED_FILES:
        path = root / rel
        passed = path.is_file()
        gates.append({"gate": rel, "ok": passed, "path": str(path)})
        if not passed:
            ok = False

    memory = root / ".cursor/agent-memory/MEMORY_LOCKED.yaml"
    if memory.is_file():
        text = memory.read_text(encoding="utf-8", errors="replace")
        for token in ("R-007", "R-011", "version:"):
            passed = token in text
            gates.append({"gate": f"memory_{token.strip(':')}", "ok": passed})
            if not passed:
                ok = False

    sina = Path.home() / ".sina"
    mono_paths = [
        ("mono_defer_ssot", Path.home() / "Desktop/SourceA/data/commercial-email-send-defer-v1.json"),
        ("mono_defer_receipt", sina / "commercial-email-send-defer-receipt-v1.json"),
        ("mono_agent_live_surfaces", sina / "agent-live-surfaces-v1.json"),
        ("mono_nf_inbox", sina / "agent-workspaces/noetfield_cloud/INBOX.md"),
    ]
    for gate_name, path in mono_paths:
        passed = path.is_file()
        gates.append({"gate": gate_name, "ok": passed, "path": str(path)})
        if not passed:
            ok = False

    defer_receipt = {}
    dr_path = sina / "commercial-email-send-defer-receipt-v1.json"
    if dr_path.is_file():
        try:
            defer_receipt = json.loads(dr_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            defer_receipt = {}
    has_defer_line = bool(defer_receipt.get("email_send_defer_line"))
    gates.append({"gate": "mono_email_send_defer_line", "ok": has_defer_line})
    if not has_defer_line:
        ok = False

    incidents = root / ".cursor/incidents/REGISTRY.md"
    open_incidents = 0
    if incidents.is_file():
        for line in incidents.read_text(encoding="utf-8", errors="replace").splitlines():
            if "| **P0** | **open**" in line or "| P0 | open" in line:
                open_incidents += 1
        gates.append({"gate": "open_p0_incidents", "ok": open_incidents == 0, "count": open_incidents})
        if open_incidents > 0:
            ok = False

    receipt = {
        "schema_version": "nf-session-gate-v1",
        "ok": ok,
        "agent_id": agent_id,
        "role": role,
        "generated_at": _iso_now(),
        "repo_root": str(root),
        "gates": gates,
        "next": "make nf-live-orient" if ok else "fix missing gates before edits",
    }

    events = root / "reports/agent-auto/events"
    events.mkdir(parents=True, exist_ok=True)
    (events / "nf-session-gate-v1.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    sina = Path.home() / ".sina"
    try:
        sina.mkdir(parents=True, exist_ok=True)
        (sina / "nf_session_gate_receipt_v1.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
    except OSError:
        pass

    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Noetfield session gate")
    parser.add_argument("--role", default="cloud", choices=["cloud", "local", "default"])
    parser.add_argument("--agent", default=None, help="Override NOETFIELD_AGENT_ID")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    receipt = run_gate(args.role, args.agent)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        status = "PASS" if receipt["ok"] else "FAIL"
        print(f"nf_session_gate: {status} agent={receipt['agent_id']}")
        for g in receipt["gates"]:
            if g["gate"].startswith("memory_") or g["gate"] == "open_p0_incidents":
                mark = "OK" if g["ok"] else "FAIL"
                extra = f" count={g['count']}" if "count" in g else ""
                print(f"  {mark} {g['gate']}{extra}")
            elif not g["ok"]:
                print(f"  FAIL missing {g['gate']}")
        print(f"next: {receipt['next']}")

    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
