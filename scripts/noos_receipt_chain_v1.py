#!/usr/bin/env python3
"""Receipt chain integrity — content-hash chain with optional HMAC seal."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# Meta-audit receipts self-seal per audit run; exclude from operational chain walks.
CHAIN_EXCLUDED_SCHEMAS = frozenset({"noos-outside-audit-receipt-v1"})


def _canonical_json(row: dict[str, Any]) -> bytes:
    body = {k: v for k, v in row.items() if k not in {"chain_hash", "prev_chain_hash", "hmac_seal"}}
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def content_hash(row: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(row)).hexdigest()


def chain_hash(row: dict[str, Any], *, prev_hash: str | None) -> str:
    material = f"{prev_hash or 'GENESIS'}:{content_hash(row)}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def hmac_seal(chain: str, *, key: str | None = None) -> str | None:
    secret = key or os.environ.get("NOOS_RECEIPT_CHAIN_KEY", "").strip()
    if not secret:
        return None
    return hmac.new(secret.encode("utf-8"), chain.encode("utf-8"), hashlib.sha256).hexdigest()


def seal_receipt(row: dict[str, Any], *, prev_hash: str | None = None, key: str | None = None) -> dict[str, Any]:
    out = dict(row)
    out["prev_chain_hash"] = prev_hash
    out["chain_hash"] = chain_hash(out, prev_hash=prev_hash)
    seal = hmac_seal(out["chain_hash"], key=key)
    if seal:
        out["hmac_seal"] = seal
    return out


def chain_eligible(row: dict[str, Any]) -> bool:
    return str(row.get("schema") or "") not in CHAIN_EXCLUDED_SCHEMAS


def verify_chain_operational(receipts: list[dict[str, Any]], *, key: str | None = None) -> dict[str, Any]:
    eligible = [r for r in receipts if chain_eligible(r)]
    row = verify_chain(eligible, key=key)
    row["excluded_schemas"] = sorted(CHAIN_EXCLUDED_SCHEMAS)
    row["excluded_count"] = len(receipts) - len(eligible)
    return row


def verify_chain(receipts: list[dict[str, Any]], *, key: str | None = None) -> dict[str, Any]:
    hashed = [r for r in receipts if r.get("chain_hash")]
    if not hashed:
        return {
            "ok": True,
            "count": len(receipts),
            "broken_links": [],
            "tail_hash": None,
            "note": "unchained_receipts",
        }
    prev: str | None = None
    broken: list[dict[str, Any]] = []
    for idx, row in enumerate(hashed):
        expected = chain_hash(row, prev_hash=prev)
        actual = row.get("chain_hash")
        if actual != expected:
            broken.append({"index": idx, "reason": "chain_hash_mismatch", "schema": row.get("schema")})
        seal = row.get("hmac_seal")
        if seal:
            secret = key or os.environ.get("NOOS_RECEIPT_CHAIN_KEY", "").strip()
            if not secret or hmac_seal(actual or "", key=secret) != seal:
                broken.append({"index": idx, "reason": "hmac_seal_invalid", "schema": row.get("schema")})
        prev = actual or expected
    return {
        "ok": len(broken) == 0,
        "count": len(receipts),
        "chained_count": len(hashed),
        "broken_links": broken,
        "tail_hash": prev,
    }


def load_receipt_dir(path: Path, *, limit: int = 200) -> list[dict[str, Any]]:
    if not path.is_dir():
        return []
    files = sorted(path.glob("*.json"), key=lambda p: p.stat().st_mtime)[-limit:]
    rows: list[dict[str, Any]] = []
    for fp in files:
        try:
            rows.append(json.loads(fp.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return rows
