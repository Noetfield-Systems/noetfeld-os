#!/usr/bin/env python3
"""Living-system governance verify v1 — GHA + Copilot + integrator + parallel registry.

Runs:
  - trigger registry sweep (P1)
  - parallel agent conflict check (L-P1/L-P2)
  - GHA workflow ↔ parallel registry coverage
  - copilot-instructions + integrator protocol presence

Exit 1 on any hard failure. Use --write-receipt for proof snapshots.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_agent_conflict_check_v1 as conflict  # noqa: E402
import sandbox_health_sweep_v1 as sweep  # noqa: E402

PARALLEL_REGISTRY = ROOT / "data/noos-parallel-agent-registry-v1.json"
INTEGRATOR_ROLE = ROOT / "data/noos-integrator-role-v1.json"
COPILOT_INSTRUCTIONS = ROOT / ".github/copilot-instructions.md"
WORKFLOWS_DIR = ROOT / ".github/workflows"

COPILOT_MARKERS = [
    "noos-parallel-agent-registry-v1.json",
    "noos_integrator_sync_v1.py",
    "noos_agent_conflict_check_v1.py",
    "L-P5",
    "L-P7",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def discover_gha_workflows() -> list[str]:
    if not WORKFLOWS_DIR.is_dir():
        return []
    return sorted(p.stem for p in WORKFLOWS_DIR.glob("*.yml"))


def check_gha_coverage(registry: dict[str, Any], workflows: list[str]) -> dict[str, Any]:
    coverage = registry.get("gha_workflow_coverage")
    if not isinstance(coverage, dict):
        return {
            "ok": False,
            "error": "missing_gha_workflow_coverage",
            "unmapped_workflows": workflows,
            "orphan_keys": [],
        }

    mapped: set[str] = set()
    orphan_keys: list[str] = []
    worker_ids = {
        str(w.get("worker_id"))
        for w in (registry.get("workers") or [])
        if isinstance(w, dict) and w.get("worker_id")
    }

    for key, owners in coverage.items():
        if not isinstance(owners, list) or not owners:
            orphan_keys.append(key)
            continue
        for owner in owners:
            if str(owner) not in worker_ids:
                orphan_keys.append(f"{key}→{owner}")
        mapped.add(str(key))

    unmapped = sorted(w for w in workflows if w not in mapped)
    stale_keys = sorted(k for k in coverage if k not in workflows)

    ok = not unmapped and not orphan_keys and not stale_keys
    return {
        "ok": ok,
        "workflow_count": len(workflows),
        "mapped_count": len(mapped),
        "unmapped_workflows": unmapped,
        "stale_coverage_keys": stale_keys,
        "orphan_worker_refs": orphan_keys,
    }


def check_copilot_instructions() -> dict[str, Any]:
    if not COPILOT_INSTRUCTIONS.is_file():
        return {"ok": False, "error": "missing_copilot_instructions"}
    text = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
    missing = [m for m in COPILOT_MARKERS if m not in text]
    return {
        "ok": not missing,
        "path": str(COPILOT_INSTRUCTIONS.relative_to(ROOT)),
        "missing_markers": missing,
    }


def check_integrator_protocol() -> dict[str, Any]:
    role = load_json(INTEGRATOR_ROLE)
    ok = role.get("schema") == "noos-integrator-role-v1"
    return {
        "ok": ok,
        "path": str(INTEGRATOR_ROLE.relative_to(ROOT)),
        "schema": role.get("schema"),
    }


def check_cursor_automation_count(registry: dict[str, Any]) -> dict[str, Any]:
    workers = registry.get("workers") if isinstance(registry.get("workers"), list) else []
    cursor_workers = [
        w for w in workers if isinstance(w, dict) and w.get("surface") == "cursor_automation"
    ]
    expected = 15
    count = len(cursor_workers)
    return {
        "ok": count >= expected,
        "cursor_automation_workers": count,
        "expected_minimum": expected,
        "worker_ids": sorted(str(w.get("worker_id")) for w in cursor_workers),
    }


def check_cursor_local_mac(registry: dict[str, Any]) -> dict[str, Any]:
    workers = registry.get("workers") if isinstance(registry.get("workers"), list) else []
    row = next(
        (w for w in workers if isinstance(w, dict) and w.get("worker_id") == "cursor-local-mac"),
        None,
    )
    ok = isinstance(row, dict) and row.get("tier") == "T2_local" and row.get("requires_integrator_claim") is True
    return {
        "ok": ok,
        "worker_id": "cursor-local-mac",
        "tier": row.get("tier") if isinstance(row, dict) else None,
        "requires_integrator_claim": row.get("requires_integrator_claim") if isinstance(row, dict) else None,
    }


def check_copilot_cli_mac(registry: dict[str, Any]) -> dict[str, Any]:
    workers = registry.get("workers") if isinstance(registry.get("workers"), list) else []
    row = next(
        (w for w in workers if isinstance(w, dict) and w.get("worker_id") == "copilot-cli-mac"),
        None,
    )
    ok = isinstance(row, dict) and row.get("tier") == "T2_local" and row.get("requires_integrator_claim") is True
    return {
        "ok": ok,
        "worker_id": "copilot-cli-mac",
        "tier": row.get("tier") if isinstance(row, dict) else None,
        "requires_integrator_claim": row.get("requires_integrator_claim") if isinstance(row, dict) else None,
    }


def run_verify(*, write_receipt: bool = False) -> dict[str, Any]:
    registry = load_json(PARALLEL_REGISTRY)
    workflows = discover_gha_workflows()

    sweep_row = sweep.run_sweep(repo_root=ROOT)
    conflict_row = conflict.check_conflicts(
        registry=registry,
        integrator=conflict.load_json(conflict.INTEGRATOR_STATE),
    )
    gha_row = check_gha_coverage(registry, workflows)
    copilot_row = check_copilot_instructions()
    integrator_row = check_integrator_protocol()
    cursor_row = check_cursor_automation_count(registry)
    t2_row = check_cursor_local_mac(registry)
    copilot_cli_row = check_copilot_cli_mac(registry)

    checks = {
        "trigger_sweep": sweep_row.get("ok"),
        "parallel_conflict": conflict_row.get("ok"),
        "gha_coverage": gha_row.get("ok"),
        "copilot_instructions": copilot_row.get("ok"),
        "integrator_protocol": integrator_row.get("ok"),
        "cursor_automations": cursor_row.get("ok"),
        "cursor_local_mac": t2_row.get("ok"),
        "copilot_cli_mac": copilot_cli_row.get("ok"),
    }
    ok = all(bool(v) for v in checks.values())

    row: dict[str, Any] = {
        "schema": "noos-living-system-governance-verify-v1",
        "version": "1.0.0",
        "at": utc_now(),
        "ok": ok,
        "checks": checks,
        "trigger_sweep": {
            "ok": checks["trigger_sweep"],
            "report_line": sweep_row.get("report_line") or sweep_row.get("status"),
        },
        "parallel_conflict": {
            "ok": conflict_row.get("ok"),
            "active_claims": conflict_row.get("active_claims"),
            "conflicts": conflict_row.get("conflicts"),
        },
        "gha_coverage": gha_row,
        "copilot_instructions": copilot_row,
        "integrator_protocol": integrator_row,
        "cursor_automations": cursor_row,
        "cursor_local_mac": t2_row,
        "copilot_cli_mac": copilot_cli_row,
        "coordination": registry.get("coordination"),
        "report_line": (
            "living_system_governance_clean · GHA+Copilot+integrator+automations aligned"
            if ok
            else "living_system_governance_drift · see checks"
        ),
    }

    if write_receipt:
        out_dir = ROOT / "receipts/proof"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = out_dir / f"noos-living-system-governance-{ts}.json"
        path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(path.relative_to(ROOT))

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    row = run_verify(write_receipt=args.write_receipt)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
        for name, passed in (row.get("checks") or {}).items():
            if not passed:
                print(f"  FAIL: {name}")

    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
