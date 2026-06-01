#!/usr/bin/env python3
"""Lightweight HTML smoke for bank-grade P0 pages and platform console (no browser)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

P0_PAGES = (
    ROOT / "bank-pilot" / "index.html",
    ROOT / "enterprise" / "index.html",
    ROOT / "trust-brief" / "intake" / "index.html",
)

CONSOLE_HTML = (
    ROOT / "services" / "governance" / "noetfield_governance" / "static" / "governance-console-v1.html"
)

P0_MARKERS = ('name="viewport"', "nfHeader", "noetfield-tokens.css")
CONSOLE_MARKERS = (
    "noetfield-tokens.css",
    "noetfield-console.css",
    "pilotKeyInput",
    "noetfield_governance_pilot_api_key",
    "audit-export",
)


def main() -> int:
    errors: list[str] = []
    for path in P0_PAGES:
        if not path.is_file():
            errors.append(f"missing P0 page: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in P0_MARKERS:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing {marker!r}")

    if not CONSOLE_HTML.is_file():
        errors.append("governance-console-v1.html missing")
    else:
        text = CONSOLE_HTML.read_text(encoding="utf-8")
        for marker in CONSOLE_MARKERS:
            if marker not in text:
                errors.append(f"console: missing {marker!r}")

    for e in errors:
        print("ERROR:", e)
    if errors:
        return 1
    print("bank-grade HTML smoke: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
