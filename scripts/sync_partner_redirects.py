#!/usr/bin/env python3
"""Emit partner subsite redirects to unified /gate/partners/ hub."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTNERS = ROOT / "gate" / "partners"

REDIRECTS: dict[str, str] = {
    "apply": "integrator",
    "apply-integration": "integrator",
    "integration": "integrator",
    "channel": "integrator",
    "delivery": "integrator",
    "structure": "integrator",
    "deal": "integrator",
    "hub": "integrator",
    "programs": "integrator",
    "programs/portfolio-offer": "integrator",
    "notes": "integrator",
    "investors": "allocator",
    "case-bank-1": "allocator",
}

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>Noetfield — Partner Gateway</title>
 <meta http-equiv="refresh" content="0;url={url}" />
 <link rel="canonical" href="https://www.noetfield.com/gate/partners/" />
 <link rel="stylesheet" href="/assets/noetfield-shell.css" />
 <script src="/assets/noetfield-shell.js" defer></script>
</head>
<body>
 <div class="bg" aria-hidden="true"></div>
 <header id="nfHeader"></header>
 <main class="wrap" style="padding:48px 24px;">
 <p>Redirecting to the unified partner gateway…</p>
 <p><a class="btn primary" href="{url}">Continue</a></p>
 </main>
 <footer id="nfFooter"></footer>
</body>
</html>
"""


def main() -> None:
    for rel, vector in REDIRECTS.items():
        dest = f"/gate/partners/?vector={vector}"
        path = PARTNERS / rel / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TEMPLATE.format(url=dest), encoding="utf-8")
        print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
