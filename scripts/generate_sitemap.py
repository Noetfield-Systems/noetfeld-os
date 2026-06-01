#!/usr/bin/env python3
"""Regenerate sitemap.xml from public index.html routes (NF-WWW-04)."""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.noetfield.com"
SKIP_DIRS = {
    "_archive",
    "apps",
    "packages",
    "services",
    "infrastructure",
    "tests",
    "scripts",
    "docs",
    "Noetfield-All-Documents",
    "L0-law",
    "L1-operational",
    "L2-knowledge",
    "L3-external",
    "governance",
    "node_modules",
    ".git",
    ".github",
    ".pytest_cache",
    "demos",
    "portal",
    "ex",
    "auth",
    "login",
    "signup",
}

NOINDEX_RE = re.compile(
    r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex',
    re.IGNORECASE,
)

PRIORITY = {
    "/": 1.0,
    "/trust-brief/": 0.9,
    "/enterprise/": 0.9,
    "/copilot/": 0.9,
    "/trust-brief/intake/": 0.9,
    "/gate/intake/": 0.85,
    "/bank-pilot/": 0.88,
    "/partners/": 0.88,
    "/trust-ledger/": 0.82,
    "/status/": 0.75,
    "/faq/": 0.8,
    "/for-whom/": 0.8,
    "/trust-ledger/": 0.8,
    "/about/": 0.7,
}

# Top-level marketing paths (index.html at depth 1) included if indexable
MARKETING_TOP = {
    "about",
    "bank-pilot",
    "partners",
    "trust-ledger",
    "copilot",
    "enterprise",
    "status",
    "faq",
    "for-whom",
    "privacy",
    "resources",
    "terms",
    "trust-brief",
    "trust-ledger",
}


def is_public_route(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    if path.name != "index.html":
        return False
    # Only root + one-level marketing dirs (avoid gate/* stubs except gate/intake)
    depth = len(rel.parts) - 1
    if depth == 0:
        pass
    elif depth == 1 and rel.parts[0] in MARKETING_TOP:
        pass
    elif rel.parts[:2] == ("gate", "intake"):
        pass
    elif rel.parts[:2] == ("trust-brief", "intake"):
        pass
    else:
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    if NOINDEX_RE.search(text):
        return False
    if "http-equiv" in text.lower() and "refresh" in text.lower() and len(text) < 1200:
        return False
    return True


def url_path(index_path: Path) -> str:
    rel = index_path.parent.relative_to(ROOT)
    if str(rel) == ".":
        return "/"
    return "/" + "/".join(rel.parts) + "/"


def changefreq(url: str) -> str:
    if url in ("/", "/trust-brief/", "/enterprise/"):
        return "weekly"
    return "monthly"


def priority(url: str) -> str:
    return f"{PRIORITY.get(url, 0.7):.1f}"


def lastmod_for(index_path: Path) -> str:
    """Last commit date for the page (stable in CI); fallback to file mtime locally."""
    rel = index_path.relative_to(ROOT).as_posix()
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()[:10]
    except (OSError, subprocess.TimeoutExpired):
        pass
    mtime = index_path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).date().isoformat()


def main() -> int:
    urls: list[str] = []
    for index in sorted(ROOT.rglob("index.html")):
        if is_public_route(index):
            urls.append(url_path(index))

    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    index_by_url = {}
    for index in sorted(ROOT.rglob("index.html")):
        if is_public_route(index):
            index_by_url[url_path(index)] = index

    for loc_path in sorted(set(urls), key=lambda u: (u != "/", u)):
        url_el = SubElement(urlset, "url")
        SubElement(url_el, "loc").text = BASE + loc_path
        SubElement(url_el, "lastmod").text = lastmod_for(index_by_url[loc_path])
        SubElement(url_el, "changefreq").text = changefreq(loc_path)
        SubElement(url_el, "priority").text = priority(loc_path)

    from xml.dom import minidom

    raw = tostring(urlset, encoding="utf-8")
    pretty = minidom.parseString(raw).toprettyxml(indent="  ", encoding="utf-8")
    xml = pretty
    out = ROOT / "sitemap.xml"
    out.write_bytes(xml)
    print(f"wrote {len(urls)} urls to {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
