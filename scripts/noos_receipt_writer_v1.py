#!/usr/bin/env python3
"""NOOS receipt writer v1 — every worker-kernel run emits a machine-parseable receipt."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT_DIR = ROOT / "receipts" / "proof"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_receipt(
    row: dict[str, Any],
    *,
    receipt_dir: Path | None = None,
    op_key: str | None = None,
) -> dict[str, Any]:
    """Persist receipt JSON; return row with receipt_path."""
    out_dir = receipt_dir or DEFAULT_RECEIPT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    key = op_key or row.get("op_key") or "run"
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(key))[:80]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    doc = {
        "version": "1.0.0",
        "written_at": utc_now(),
        **row,
    }
    doc.setdefault("schema", "noos-worker-kernel-receipt-v1")
    prefix = "noos-tool-broker" if doc["schema"] == "noos-tool-broker-receipt-v1" else "noos-worker-kernel"
    path = out_dir / f"{prefix}-{safe}-{ts}.json"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    try:
        doc["receipt_path"] = str(path.relative_to(ROOT))
    except ValueError:
        doc["receipt_path"] = str(path)
    return doc


def load_receipt(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
