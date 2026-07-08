#!/usr/bin/env python3
"""UPG-PLAN-08 / UPG-0209 — gel-api multi-region canary verify (yyz + ord)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts/proof/noos-gel-api-multi-region-v1.json"

# Canonical public gel-api surfaces per deploy scopes
REGIONS = {
    "yyz": "https://api.noetfield.com/health",
    "ord": "https://gel-api-ord.noetfield.com/health",
}


def _probe(url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "noos-gel-multi-region-v1"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": resp.status == 200, "status": resp.status, "url": url}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "url": url}
    except OSError as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def verify(*, write_receipt: bool = False) -> dict:
    regions = {name: _probe(url) for name, url in REGIONS.items()}
    ok = all(r.get("ok") for r in regions.values())
    row = {
        "schema": "noos-gel-api-multi-region-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": ok,
        "regions": regions,
        "backlog_id": "UPG-0209",
        "note": "ord URL is canary target; configure DNS when region live",
    }
    if write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)
    return row


def main() -> int:
    write = "--write-receipt" in sys.argv
    row = verify(write_receipt=write)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
