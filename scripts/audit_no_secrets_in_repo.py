#!/usr/bin/env python3
"""Fail if known secret patterns appear in tracked source (not .env)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAN_EXT = {".html", ".js", ".css", ".py", ".md", ".json", ".yml", ".yaml", ".sh"}
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "Noetfield-All-Documents"}

PATTERNS = [
    ("OpenRouter key", re.compile(r"sk-or-v1-[A-Za-z0-9]{20,}")),
    ("Telegram bot token", re.compile(r"\d{8,12}:AAG[A-Za-z0-9_-]{30,}")),
    ("Google API key style", re.compile(r"AIza[A-Za-z0-9_-]{30,}")),
]

ALLOWLIST_SUBSTRINGS = (
    "audit_no_secrets_in_repo.py",
    "TELEGRAM_BOT_SETUP.md",
    "CHATBOT_SETUP.md",
    ".env.example",
)


def main() -> int:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in SCAN_EXT:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == ".env":
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("docs/SOURCE_OF_TRUTH/"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in PATTERNS:
            for match in pattern.finditer(text):
                snippet = match.group(0)
                if any(a in rel for a in ALLOWLIST_SUBSTRINGS):
                    continue
                errors.append(f"{rel}: possible {label} ({snippet[:12]}…)")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print("secret pattern audit: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
