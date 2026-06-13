#!/usr/bin/env python3
"""Force every public shell page onto www v7 stack (tokens + shell + www only)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = (
    "node_modules",
    ".next",
    "services/governance",
    "docs/collateral",
    "governance-console/frontend",
)
STRIP_CSS = (
    "noetfield-components.css",
    "noetfield-enterprise.css",
    "noetfield-institutional.css",
    "noetfield-sales.css",
)
WWW = '<link rel="stylesheet" href="/assets/noetfield-www.css?v=10" />'
SHELL_JS = '<script src="/assets/noetfield-shell.js?v=10" defer></script>'


def should_skip(path: Path) -> bool:
    s = str(path)
    return any(p in s for p in SKIP_PARTS)


def migrate(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if 'id="nfHeader"' not in text and "id='nfHeader'" not in text:
        return False
    orig = text
    for name in STRIP_CSS:
        text = re.sub(
            rf'\s*<link rel="stylesheet" href="/assets/{re.escape(name)}[^"]*" />\n?',
            "",
            text,
        )
    if "noetfield-www.css" not in text:
        text = text.replace(
            '<link rel="stylesheet" href="/assets/noetfield-tokens.css" />',
            '<link rel="stylesheet" href="/assets/noetfield-tokens.css" />\n'
            f" {WWW}",
        )
    else:
        text = re.sub(
            r'href="/assets/noetfield-www\.css\?v=[^"]+"',
            'href="/assets/noetfield-www.css?v=10"',
            text,
        )
    text = re.sub(
        r'<script src="/assets/noetfield-shell\.js[^"]*" defer></script>',
        SHELL_JS,
        text,
    )
    text = re.sub(r'<body class="[^"]*">', '<body class="nf-www nf-site-v5">', text, count=1)
    if re.search(r"<body(?![^>]*class=)", text):
        text = re.sub(r"<body>", '<body class="nf-www">', text, count=1)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    n = 0
    for path in ROOT.rglob("*.html"):
        if should_skip(path):
            continue
        if migrate(path):
            print("migrated", path.relative_to(ROOT))
            n += 1
    print(f"done — {n} files migrated")


if __name__ == "__main__":
    main()
