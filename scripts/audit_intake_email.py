#!/usr/bin/env python3
"""Ensure public surfaces use operations@noetfield.com as sole intake vector."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = "operations@noetfield.com"

SCAN_DIRS = (
    ROOT / "index.html",
    ROOT / "enterprise",
    ROOT / "trust-brief",
    ROOT / "copilot",
    ROOT / "console",
    ROOT / "gate" / "intake",
    ROOT / "assets" / "partials",
    ROOT / "assets" / "noetfield-intake-email.js",
)

FORBIDDEN_PUBLIC = re.compile(
    r"mailto:(contact|procurement|sales|support|feedback|engagements)@noetfield\.com",
    re.I,
)

LEGACY_INLINE = re.compile(
    r"\b(contact|procurement|sales)@noetfield\.com\b",
    re.I,
)

ALLOWLIST_FILES = {
    "scripts/final_semantic_lock_public.py",
    "scripts/audit_intake_email.py",
    "packages/config/noetfield_config/intake.py",
    "docs/GTM_BANK_GRADE_FINAL.md",
    "STRATEGIC_LOCK.md",
}


def iter_files() -> list[Path]:
    out: list[Path] = []
    for entry in SCAN_DIRS:
        if entry.is_file():
            out.append(entry)
        elif entry.is_dir():
            out.extend(entry.rglob("*.html"))
            out.extend(entry.rglob("*.js"))
    return sorted(set(out))


def main() -> int:
    errors: list[str] = []
    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWLIST_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if FORBIDDEN_PUBLIC.search(text):
            errors.append(f"{rel}: forbidden mailto alias")
        for m in LEGACY_INLINE.finditer(text):
            errors.append(f"{rel}: legacy address {m.group(0)}")
    cfg = ROOT / "packages" / "config" / "noetfield_config" / "intake.py"
    if CANONICAL not in cfg.read_text(encoding="utf-8"):
        errors.append("intake.py missing canonical constant")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print("intake email audit: OK (canonical operations@noetfield.com)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
