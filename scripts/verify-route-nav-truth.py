#!/usr/bin/env python3
"""Verify public route labels do not imply missing hubs."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "assets" / "partials" / "header.html"
FOOTER = ROOT / "assets" / "partials" / "footer.html"
ABOUT = ROOT / "about" / "index.html"
INTELLIGENCE_HUB = ROOT / "intelligence" / "index.html"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL route-nav-truth: {message}")


def main() -> int:
    failures: list[str] = []
    header = HEADER.read_text(encoding="utf-8")

    primary_match = re.search(r'<div class="menuPrimary">(.*?)</div>', header, flags=re.S)
    primary_html = primary_match.group(1) if primary_match else ""

    if not INTELLIGENCE_HUB.is_file():
        if re.search(r'href="/"\s*>\s*Intelligence\s*</a>', primary_html):
            fail('primary nav labels "/" as Intelligence while /intelligence/ has no hub', failures)
        if 'href="/intelligence/"' in primary_html:
            fail("primary nav links to missing /intelligence/ hub", failures)

    if 'href="/">Home</a>' not in primary_html:
        fail('primary nav must label "/" as Home until /intelligence/ exists', failures)

    if ABOUT.is_file():
        about = ABOUT.read_text(encoding="utf-8")
        for term in ("SourceA", "TrustField Technologies Inc.", "Intelligence home"):
            if term in about:
                fail(f"public /about/ contains internal or stale term: {term}", failures)

    if FOOTER.is_file():
        footer = FOOTER.read_text(encoding="utf-8")
        for term in ("SourceA", "TrustField Technologies Inc."):
            if term in footer:
                fail(f"public footer contains internal portfolio term: {term}", failures)

    if failures:
        return 1

    print("verify-route-nav-truth: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
