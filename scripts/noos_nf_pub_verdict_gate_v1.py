#!/usr/bin/env python3
"""UPG-PLAN-03 — NF public audit verdict gate (machine-safe receipt check)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "receipts/proof"

REQUIRED = [
    "noos-nf-pub-audit-protocol-v1.json",
    "noos-nf-pub-route-inventory-v1.json",
    "noos-nf-pub-claim-evidence-matrix-v1.json",
    "noos-nf-pub-cta-journey-map-v1.json",
    "noos-nf-pub-claim-risk-matrix-v1.json",
    "noos-nf-pub-prioritized-fix-list-v1.json",
]
VERDICT = PROOF / "noos-nf-pub-verdict-v1.json"


def check(*, write_verdict: bool = False) -> dict:
    missing: list[str] = []
    present: list[str] = []
    for name in REQUIRED:
        path = PROOF / name
        if path.is_file():
            present.append(name)
        else:
            missing.append(name)

    verdict_doc = {}
    if VERDICT.is_file():
        try:
            verdict_doc = json.loads(VERDICT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            verdict_doc = {}

    research_complete = not missing
    verdict_status = verdict_doc.get("verdict") or "PENDING"
    p0_ready = research_complete and verdict_status in ("ACCEPT", "PARTIAL_ACCEPT")

    row = {
        "schema": "noos-nf-pub-verdict-gate-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": research_complete,
        "research_artifacts_present": present,
        "research_artifacts_missing": missing,
        "verdict_status": verdict_status,
        "p0_www_edits_allowed": p0_ready,
        "pipeline": "Research → Verdict → matrices → P0 fixes only (founder gate P1+)",
        "forbidden": "bulk audit copy onto noetfield.com without verdict",
    }

    if write_verdict and research_complete and not VERDICT.is_file():
        draft = {
            "schema": "noos-nf-pub-verdict-v1",
            "at": row["at"],
            "verdict": "PENDING",
            "authority": "founder",
            "note": "Set verdict ACCEPT|REJECT|DEFER per finding before P0 www edits",
            "artifacts": present,
        }
        VERDICT.write_text(json.dumps(draft, indent=2) + "\n", encoding="utf-8")
        row["verdict_path"] = str(VERDICT)

    return row


def main() -> int:
    write = "--write-verdict-stub" in sys.argv
    row = check(write_verdict=write)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
