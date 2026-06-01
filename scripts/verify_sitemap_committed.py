#!/usr/bin/env python3
"""Ensure sitemap.xml structure matches generator (ignores lastmod volatility)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def _find(el: ET.Element, tag: str) -> ET.Element | None:
    node = el.find(f"sm:{tag}", NS)
    if node is None:
        node = el.find(tag)
    return node


def canonical_entries(path: Path) -> list[tuple[str, str, str]]:
    root = ET.parse(path).getroot()
    rows: list[tuple[str, str, str]] = []
    for url_el in root.findall("sm:url", NS) or root.findall("url"):
        loc = _find(url_el, "loc")
        freq = _find(url_el, "changefreq")
        prio = _find(url_el, "priority")
        if loc is None or loc.text is None:
            continue
        rows.append(
            (
                loc.text.strip(),
                (freq.text.strip() if freq is not None and freq.text else ""),
                (prio.text.strip() if prio is not None and prio.text else ""),
            )
        )
    return sorted(rows)


def main() -> int:
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        print("missing sitemap.xml", file=sys.stderr)
        return 1

    before = canonical_entries(sitemap)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_sitemap.py")],
        cwd=ROOT,
        check=True,
    )
    after = canonical_entries(sitemap)

    if before != after:
        print(
            "sitemap.xml structure is out of date "
            "(loc/changefreq/priority) — run: python3 scripts/generate_sitemap.py",
            file=sys.stderr,
        )
        only_before = set(before) - set(after)
        only_after = set(after) - set(before)
        if only_before:
            print("  only in committed:", *only_before, sep="\n    ", file=sys.stderr)
        if only_after:
            print("  only after regen:", *only_after, sep="\n    ", file=sys.stderr)
        return 1

    print(f"sitemap structure ok ({len(before)} urls)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
