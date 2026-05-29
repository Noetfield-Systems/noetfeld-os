#!/usr/bin/env python3
"""Redirect non-public routes to / or /enterprise per final simplification."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Full marketing pages (keep content)
ALLOWLIST = {
    ROOT / "index.html",
    ROOT / "enterprise" / "index.html",
    ROOT / "trust-brief" / "index.html",
    ROOT / "trust-brief" / "intake" / "index.html",
    ROOT / "copilot" / "index.html",
    ROOT / "console" / "index.html",
    ROOT / "gate" / "intake" / "index.html",
    ROOT / "privacy" / "index.html",
    ROOT / "terms" / "index.html",
}

# Paths under these prefixes redirect to /enterprise (except allowlisted files)
ENTERPRISE_PREFIXES = (
    "gate",
    "trust-ledger",
    "resources",
    "platform",
    "playbook",
)

HOME_PREFIXES = ("directory",)

REDIRECT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>Noetfield</title>
 <meta http-equiv="refresh" content="0;url={url}" />
 <link rel="canonical" href="https://www.noetfield.com{canonical}" />
</head>
<body>
 <p><a href="{url}">Continue</a></p>
</body>
</html>
"""


def target_for(path: Path) -> tuple[str, str]:
    rel = path.relative_to(ROOT).as_posix()
    first = rel.split("/")[0] if "/" in rel else rel.replace("/index.html", "")
    if first in HOME_PREFIXES or rel.startswith("directory/"):
        return "/", "/"
    if first in ENTERPRISE_PREFIXES or rel.startswith("gate/"):
        return "/enterprise/", "/enterprise/"
    return "/", "/"


def main() -> None:
    count = 0
    for html in ROOT.rglob("index.html"):
        if "node_modules" in html.parts or "services" in html.parts:
            continue
        if html.resolve() in {p.resolve() for p in ALLOWLIST}:
            continue
        url, canonical = target_for(html)
        html.write_text(REDIRECT_TEMPLATE.format(url=url, canonical=canonical), encoding="utf-8")
        count += 1
        print("redirect", html.relative_to(ROOT), "->", url)
    print("total", count)


if __name__ == "__main__":
    main()
