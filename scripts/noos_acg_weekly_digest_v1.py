#!/usr/bin/env python3
"""UPG-PLAN-07 — ACG outbound weekly digest receipt."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/noos-acg-outbound-queue-v1.json"
RECEIPT_DIR = ROOT / "receipts/proof"


def digest(*, write_receipt: bool = False) -> dict:
    queue_doc = json.loads(QUEUE.read_text(encoding="utf-8"))
    items = queue_doc.get("queue") or []
    ready = sum(1 for x in items if x.get("status") == "ready")
    queued = sum(1 for x in items if x.get("status") == "queued")
    row = {
        "schema": "noos-acg-weekly-digest-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": True,
        "slots_total": len(items),
        "slots_ready": ready,
        "slots_queued": queued,
        "founder_gated": True,
        "send_receipt_path": str(Path.home() / ".sina/nw1-outbound-send-receipt-v1.json"),
        "note": "NW1 sends require founder; machine prepares queue only",
    }
    if write_receipt:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        out = RECEIPT_DIR / f"noos-acg-weekly-digest-{stamp}.json"
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(out)
    return row


def main() -> int:
    write = "--write-receipt" in sys.argv
    row = digest(write_receipt=write)
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
