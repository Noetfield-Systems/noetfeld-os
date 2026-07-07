#!/usr/bin/env python3
"""ICL-P2-03 — publish UPGRADE_MANIFEST deltas for cross-repo sync."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/_NOOS_AGENT/UPGRADE_MANIFEST.json"
OUT = ROOT / "receipts/proof/noos-upgrade-manifest-publish-v1.json"


def publish() -> dict:
    if not MANIFEST.is_file():
        return {"ok": False, "error": "manifest missing"}
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = doc.get("entries") or doc.get("upgrades") or []
    row = {
        "schema": "noos-upgrade-manifest-publish-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": True,
        "manifest_path": str(MANIFEST),
        "entry_count": len(entries) if isinstance(entries, list) else len(doc.keys()),
        "planes": ["NOOS", "Noetfield-contract-surfaces"],
        "note": "Contract-only SourceA deltas; no product repo writes",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    row["receipt_path"] = str(OUT)
    return row


def main() -> int:
    row = publish()
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
