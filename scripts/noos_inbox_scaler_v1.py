#!/usr/bin/env python3
"""UPG-0205 — inbox queue-depth scaler (pending>10 → scale 1→2)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCALING = ROOT / "data/noos-runtime-scaling-v1.json"
PROOF = ROOT / "receipts/proof/noos-inbox-scaler-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def inbox_depth() -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "scripts/reenqueue_blocked_upg_inbox_v1.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    blocked = 0
    if proc.stdout.strip():
        try:
            blocked = int(json.loads(proc.stdout).get("blocked_seen") or 0)
        except json.JSONDecodeError:
            blocked = 0
    return {"pending": blocked, "source": "reenqueue_blocked_probe", "ok": True}


def evaluate(*, simulate: int | None = None) -> dict[str, Any]:
    cfg = json.loads(SCALING.read_text(encoding="utf-8"))
    rule = next((r for r in cfg.get("rules") or [] if r.get("id") == "inbox-queue-depth"), {})
    threshold = int(rule.get("threshold") or 10)
    depth_row = inbox_depth()
    pending = simulate if simulate is not None else int(depth_row.get("pending") or 0)
    should_scale = pending > threshold
    return {
        "schema": "noos-inbox-scaler-v1",
        "evaluated_at": utc_now(),
        "pending": pending,
        "threshold": threshold,
        "should_scale": should_scale,
        "action": rule.get("action"),
        "scale_from": rule.get("from"),
        "scale_to": rule.get("to"),
        "roi_class": rule.get("roi_class"),
        "depth_probe": depth_row,
        "ok": True,
        "report_line": f"inbox_scaler · pending={pending} scale={should_scale}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--simulate-pending", type=int, default=None)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = evaluate(simulate=args.simulate_pending)
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
