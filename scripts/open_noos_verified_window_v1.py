#!/usr/bin/env python3
"""Open DECLARED→VERIFIED 24h window for all NOOS loops from a merge SHA.

Proof receipt: receipts/proof/noos-loop-verified-window-v1.json
Closes green only after 24h schedule-only cycles per loop (governed-autorun L4).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"
sys.path.insert(0, str(ROOT / "scripts"))
from noos_proof_receipt_paths_v1 import proof_receipt  # noqa: E402

PROOF_RECEIPT = proof_receipt("noos-loop-verified-window-v1.json")
WINDOW_HOURS = 24


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def git_sha() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def open_window(*, merge_sha: str | None = None) -> dict[str, Any]:
    sha = merge_sha or git_sha()
    started = utc_now()
    closes = started + timedelta(hours=WINDOW_HOURS)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    loops = [
        {
            "loop_id": str(loop["id"]),
            "github_workflow": loop.get("github_workflow"),
            "interval_minutes": loop.get("interval_minutes"),
            "verification_state": "DECLARED",
            "verified_at": None,
        }
        for loop in registry.get("loops") or []
    ]
    return {
        "schema": "noos-loop-verified-window-v1",
        "merge_sha": sha,
        "window_hours": WINDOW_HOURS,
        "window_started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_closes_at": closes.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "overall_state": "DECLARED",
        "law": "Manual dispatch green ≠ cron green (L4). Each loop VERIFIED after 24h schedule-only.",
        "founder_blocked_note": "NOOS-C-01 remains founder_blocked; does not block window.",
        "loops": loops,
        "loop_count": len(loops),
        "close_criteria": {
            "per_loop": "2+ consecutive schedule runs + sink invariant PASS",
            "zero_manual": True,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--merge-sha", help="Merge commit SHA (default: HEAD)")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = open_window(merge_sha=args.merge_sha)
    if args.write_receipt:
        PROOF_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF_RECEIPT.relative_to(ROOT))
        row["receipt_tier"] = "proof"

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"verified_window state={row['overall_state']} sha={row['merge_sha'][:8]} "
            f"closes={row['window_closes_at']} loops={row['loop_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
