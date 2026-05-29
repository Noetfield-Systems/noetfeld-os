#!/usr/bin/env python3
"""Audit institutional HTML for GTM lock: shell, viewport, CTAs, forbidden copy."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TIER_PAGES = (
    ROOT / "index.html",
    ROOT / "enterprise" / "index.html",
    ROOT / "trust-brief" / "index.html",
    ROOT / "copilot" / "index.html",
    ROOT / "gate" / "index.html",
)

FORBIDDEN_HOME = (
    "Cross-Border Payments",
    "Payment Intent",
    "Submit Payment",
    "FX Calculator",
)

REQUIRED_TIER = (
    "nfHeader",
    "viewport",
    "Request Governance Brief",
    "noetfield-shell.css",
)


def iter_html() -> list[Path]:
    return sorted(ROOT.rglob("*.html"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for path in TIER_PAGES:
        if not path.is_file():
            errors.append(f"missing tier page: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for req in REQUIRED_TIER:
            if req not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing {req!r}")

    home = ROOT / "index.html"
    if home.is_file():
        ht = home.read_text(encoding="utf-8", errors="replace")
        for phrase in FORBIDDEN_HOME:
            if phrase in ht:
                errors.append(f"index.html contains forbidden: {phrase}")
        if "Governance Execution" not in ht:
            errors.append("index.html missing product truth positioning")

    no_shell = []
    no_viewport = []
    for path in iter_html():
        rel = path.relative_to(ROOT)
        if "node_modules" in rel.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if 'name="viewport"' not in text and "name='viewport'" not in text:
            no_viewport.append(str(rel))
        if "nfHeader" not in text and rel.parts[0] not in ("app", "portal", "ex", "auth", "login", "signup"):
            # allow minimal redirect stubs
            if "http-equiv" in text and "refresh" in text.lower():
                continue
            if len(text) < 800:
                continue
            no_shell.append(str(rel))

    if no_viewport:
        warnings.append(f"{len(no_viewport)} pages without viewport meta (sample: {no_viewport[:5]})")

    if len(no_shell) > 40:
        warnings.append(f"{len(no_shell)} large pages without shell (legacy); tier pages must pass above")

    for w in warnings:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)

    if errors:
        return 1
    print("public site health: OK (tier pages + homepage)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
