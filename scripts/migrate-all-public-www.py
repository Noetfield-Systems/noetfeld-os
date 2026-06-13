#!/usr/bin/env python3
"""Force every public shell page onto www v14 stack (tokens + shell + www only)."""
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
    "noetfield-ops.css",
)
WWW_VER = "16"
FONT_LINKS = (
    ' <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    ' <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    ' <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700&amp;family=IBM+Plex+Serif:ital,wght@0,500;0,600;0,700&amp;display=swap" />'
)
WWW = f'<link rel="stylesheet" href="/assets/noetfield-www.css?v={WWW_VER}" />'
SHELL_JS = f'<script src="/assets/noetfield-shell.js?v={WWW_VER}" defer></script>'


def should_skip(path: Path) -> bool:
    s = str(path)
    return any(p in s for p in SKIP_PARTS)


def body_class_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    base = "nf-www nf-site-v14"
    if rel == "trust/index.html":
        return f"{base} nf-trust-diligence"
    return base


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
    if "fonts.googleapis.com" not in text:
        text = text.replace(
            '<link rel="stylesheet" href="/assets/noetfield-tokens.css" />',
            FONT_LINKS + '\n <link rel="stylesheet" href="/assets/noetfield-tokens.css" />',
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
            f'href="/assets/noetfield-www.css?v={WWW_VER}"',
            text,
        )
    text = re.sub(
        r'<script src="/assets/noetfield-shell\.js[^"]*" defer></script>',
        SHELL_JS,
        text,
    )
    body_class = body_class_for(path)
    text = re.sub(r'<body class="[^"]*">', f'<body class="{body_class}">', text, count=1)
    if re.search(r"<body(?![^>]*class=)", text):
        text = re.sub(r"<body>", f'<body class="{body_class}">', text, count=1)
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
