#!/usr/bin/env python3
"""Ensure GTM tier sales pages include shell injection anchors."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "enterprise" / "index.html",
    ROOT / "gate" / "index.html",
    ROOT / "copilot" / "index.html",
    ROOT / "trust-brief" / "index.html",
]

SHELL_HEAD_EXTRA = """
 <meta name="theme-color" content="#07070b" />
 <link rel="preconnect" href="https://fonts.googleapis.com" />
 <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
 <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
"""

BODY_PREFIX = """
 <div class="bg" aria-hidden="true"></div>
 <a class="skip" href="#main">Skip to content</a>
 <header id="nfHeader"></header>
"""

BODY_SUFFIX = """
 <footer id="nfFooter"></footer>
"""


def wrap(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "nfHeader" in text and 'id="main"' in text:
        return False
    if "<body>" not in text or "</body>" not in text:
        return False
    if 'name="theme-color"' not in text:
        text = text.replace("</head>", SHELL_HEAD_EXTRA + "</head>", 1)
    inner = text.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    inner = inner.replace('<main class="nf-sales">', '<main id="main" class="wrap nf-sales">', 1)
    if 'class="wrap nf-sales"' not in inner and 'id="main"' not in inner:
        inner = inner.replace("<main", '<main id="main" class="wrap"', 1)
    new_body = BODY_PREFIX + inner.strip() + "\n" + BODY_SUFFIX
    text = text.split("<body>", 1)[0] + "<body>\n" + new_body + "\n</body>" + text.rsplit("</body>", 1)[1]
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    for p in PAGES:
        if p.is_file() and wrap(p):
            print("wrapped", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
