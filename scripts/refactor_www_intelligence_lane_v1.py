#!/usr/bin/env python3
"""Refactor public www pages — Intelligence 613 primary lane (~80%), Copilot governance ~20%."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INTAKE = "/intelligence/intake/"
PILOT = "/trust-brief/intake/?interest=pilot&vector=copilot-governance"

GOVERNANCE_PREFIXES = (
    "governance/",
    "copilot/",
    "trust-brief/",
    "bank-pilot/",
    "enterprise/",
    "federal/",
    "msp/",
    "ai-automation/",
    "trust-ledger/",
    "gate/",
    "console/",
    "docs/api/",
)

PROTECTED = {
    "index.html",
    "governance/index.html",
    "intelligence/intake/index.html",
    "pricing/index.html",
    "contact/index.html",
}

NEUTRAL_PAGES = (
    "start/index.html",
    "next/index.html",
    "faq/index.html",
    "partners/index.html",
    "status/index.html",
    "runtime/index.html",
    "templates/index.html",
    "work-with-us/index.html",
    "trust/index.html",
)


def is_governance(rel: str) -> bool:
    return any(rel.startswith(p) for p in GOVERNANCE_PREFIXES)


def refactor_neutral_hero_cta(text: str) -> str:
    """First primary CTA in hero → Diagnostic on neutral / cross-lane pages."""
    pattern = re.compile(
        r'(<div class="nf-cta-actions">)\s*'
        r'(<a class="btn btn-primary" href=")[^"]*(">)([^<]*Apply for pilot[^<]*)(</a>)',
        re.IGNORECASE,
    )

    def repl(m: re.Match[str]) -> str:
        return f'{m.group(1)}{m.group(2)}{INTAKE}{m.group(3)}Book Diagnostic Sprint{m.group(5)}'

    return pattern.sub(repl, text, count=1)


def demote_lead_wedge_copy(text: str) -> str:
    text = text.replace("Copilot Governance Pack · LEAD", "Copilot Governance Pack · enterprise")
    text = text.replace("Lead wedge", "Enterprise lane")
    text = text.replace("Lead program", "Governance program")
    text = text.replace("pilot-first", "intelligence-primary")
    return text


def refactor_file(path: Path) -> bool:
    rel = str(path.relative_to(ROOT))
    if rel in PROTECTED or "assets/partials" in rel:
        return False
    if "nfHeader" not in path.read_text(encoding="utf-8"):
        return False

    text = path.read_text(encoding="utf-8")
    original = text

    text = demote_lead_wedge_copy(text)

    if rel in NEUTRAL_PAGES or (not is_governance(rel) and rel not in PROTECTED):
        text = refactor_neutral_hero_cta(text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("refactored", rel)
        return True
    return False


def main() -> int:
    changed = 0
    for path in sorted(ROOT.rglob("index.html")):
        rel = path.relative_to(ROOT)
        if "node_modules" in rel.parts or rel.parts[:1] == ("apps",):
            continue
        if refactor_file(path):
            changed += 1
    print(f"refactor complete: {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
