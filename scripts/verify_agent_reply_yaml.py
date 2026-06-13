#!/usr/bin/env python3
"""Validate Execution Truth YAML footer in agent replies (stdin or file)."""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_KEYS = frozenset(
    {
        "schema_version",
        "repo",
        "agent_tag",
        "task",
        "status",
        "verify_passed",
        "verify_command",
        "verify_output_summary",
        "blocked_reason",
        "next_action",
        "evidence_paths",
        "reported_at",
        "reporter",
    }
)

ISO8601_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def extract_yaml_block(text: str) -> str | None:
    blocks = re.findall(r"```ya?ml\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if not blocks:
        return None
    for block in reversed(blocks):
        if "schema_version:" in block and "repo:" in block:
            return block.strip()
    return blocks[-1].strip()


def parse_flat_yaml(block: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key == "evidence_paths":
            data[key] = "[]" if val in ("", "[]") else val
            continue
        data[key] = val
    return data


def validate_reported_at(value: str) -> bool:
    if not ISO8601_Z.match(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def main() -> int:
    if len(sys.argv) > 1:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    block = extract_yaml_block(text)
    if not block:
        print("FAIL: no ```yaml execution-truth block found", file=sys.stderr)
        return 1

    data = parse_flat_yaml(block)
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        print(f"FAIL: missing keys: {sorted(missing)}", file=sys.stderr)
        return 1

    if data.get("repo") != "noetfield":
        print(f"FAIL: repo must be noetfield, got {data.get('repo')!r}", file=sys.stderr)
        return 1

    if not validate_reported_at(data.get("reported_at", "")):
        print(
            "FAIL: reported_at must be ISO8601 UTC e.g. 2026-06-03T09:09:00Z",
            file=sys.stderr,
        )
        return 1

    if data.get("status") == "done" and data.get("verify_passed") != "true":
        print("FAIL: status done requires verify_passed: true", file=sys.stderr)
        return 1

    print("verify_passed: true")
    print(f"reported_at: {data['reported_at']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
