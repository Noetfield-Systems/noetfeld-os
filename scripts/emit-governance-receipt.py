#!/usr/bin/env python3
"""Emit Noetfield governance factory receipt."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    tier = (sys.argv[1] if len(sys.argv) > 1 else "sandbox").lower()
    verdict = "MOCK_ONLY" if tier in ("sandbox", "freemium") else "PASS"
    row = {
        "schema": "noetfield-governance-receipt-v1",
        "receipt_id": f"nf-gov-{int(datetime.now(timezone.utc).timestamp())}",
        "verdict": verdict,
        "board_line": (
            "MOCK_ONLY — sandbox TLE; upgrade for procurement-grade board PDF"
            if verdict == "MOCK_ONLY"
            else "Governance eval PASS — export bundle ready"
        ),
        "emitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    out = Path.home() / ".sina" / "noetfield-governance-receipt-v1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
