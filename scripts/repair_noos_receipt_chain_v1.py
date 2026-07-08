#!/usr/bin/env python3
"""Append corrective receipt-chain repair proof — no historical rewrite."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_receipt_chain_v1 as chain  # noqa: E402

PROOF_DIR = ROOT / "receipts" / "proof"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_recent(limit: int = 300) -> list[dict[str, Any]]:
    files = sorted(PROOF_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)[-limit:]
    rows: list[dict[str, Any]] = []
    for fp in files:
        try:
            rows.append(json.loads(fp.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    scanned = load_recent()
    full = chain.verify_chain([r for r in scanned if r.get("chain_hash")])
    operational = chain.verify_chain_operational(scanned)
    repair = {
        "schema": "noos-receipt-chain-repair-v1",
        "version": "1.0.0",
        "at": utc_now(),
        "action": "append_corrective_receipt",
        "historical_rewrite": False,
        "broken_full_chain": full.get("broken_links", [])[:10],
        "full_chain_ok": full.get("ok"),
        "operational_chain_ok": operational.get("ok"),
        "operational_chain": {
            "chained_count": operational.get("chained_count"),
            "excluded_count": operational.get("excluded_count"),
            "excluded_schemas": operational.get("excluded_schemas"),
        },
        "law": "Outside-audit receipts excluded from operational chain; forward seals unchanged.",
        "ok": operational.get("ok", False),
    }

    if args.write_receipt:
        tail = operational.get("tail_hash")
        sealed = chain.seal_receipt(repair, prev_hash=tail)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = PROOF_DIR / f"noos-receipt-chain-repair-{ts}.json"
        out.write_text(json.dumps(sealed, indent=2) + "\n", encoding="utf-8")
        repair["receipt_path"] = str(out.relative_to(ROOT))

    if args.json:
        print(json.dumps(repair, indent=2))
    else:
        print(
            f"receipt_chain_repair · operational_ok={repair['operational_chain_ok']} "
            f"full_ok={repair['full_chain_ok']}"
        )
    return 0 if repair.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
