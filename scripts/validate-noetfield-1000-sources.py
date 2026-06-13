#!/usr/bin/env python3
"""Validate noetfield-1000 LOCKED library completeness and source coverage."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "os" / "plan-library" / "noetfield-1000"
REG = PACK / "REGISTRY.json"

REQUIRED_COMMITTED = [
    "docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md",
    "docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md",
    "docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md",
    "docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md",
    "docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md",
    "docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md",
    "docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md",
    "os/SHIP_NOW.md",
    "os/plan.json",
]

FORBIDDEN_IN_T0_T1 = ("trustfield", "virlux", "runreceipt", "competitor table")


def main() -> int:
    errors: list[str] = []

    if not REG.is_file():
        errors.append(f"missing {REG}")
        _report(errors)
        return 1

    data = json.loads(REG.read_text(encoding="utf-8"))
    plans = data.get("plans", [])
    if len(plans) != 1000:
        errors.append(f"count {len(plans)} != 1000")

    from collections import Counter

    phase_counts = Counter(p.get("phase") for p in plans)
    tier_counts = Counter(p.get("tier") for p in plans)
    if len(phase_counts) != 10:
        errors.append(f"phase count {len(phase_counts)} != 10")
    if any(c != 100 for c in phase_counts.values()):
        errors.append(f"phase grid not 100 each: {dict(phase_counts)}")
    if tier_counts != Counter({"T0": 250, "T1": 250, "T2": 250, "T3": 250}):
        errors.append(f"tier grid mismatch: {dict(tier_counts)}")
    if not data.get("locked"):
        errors.append("REGISTRY not locked")

    for pl in plans:
        if not pl.get("agent_prompt"):
            errors.append(f"{pl['id']}: missing agent_prompt")
        if not pl.get("verify"):
            errors.append(f"{pl['id']}: missing verify")
        if len(pl.get("sources", [])) < 1:
            errors.append(f"{pl['id']}: missing sources")
        if pl["tier"] in ("T0", "T1"):
            blob = (pl.get("title", "") + pl.get("agent_prompt", "")).lower()
            for bad in FORBIDDEN_IN_T0_T1:
                if bad in blob and "grep" not in blob and "reject" not in blob:
                    errors.append(f"{pl['id']}: forbidden phrase {bad}")

    for rel in REQUIRED_COMMITTED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing source: {rel}")

    t0_backlog = [p for p in plans if p.get("tier") == "T0" and p.get("status") == "backlog"]
    if not t0_backlog:
        errors.append("no T0 backlog for pick script")

    pick = ROOT / "scripts" / "pick-noetfield-no-asf-plan.py"
    if pick.is_file():
        r = subprocess.run(
            ["python3", str(pick), "--tier", "T0", "--limit", "1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            errors.append(f"pick script failed: {r.stderr or r.stdout}")

    _report(errors)
    return 1 if errors else 0


def _report(errors: list[str]) -> None:
    if errors:
        print("VALIDATE_FAIL")
        for e in errors[:30]:
            print(f"  - {e}")
        if len(errors) > 30:
            print(f"  ... and {len(errors) - 30} more")
    else:
        print("VALIDATE_PASS noetfield-1000")


if __name__ == "__main__":
    sys.exit(main())
