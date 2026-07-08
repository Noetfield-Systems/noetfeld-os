#!/usr/bin/env python3
"""Fail-closed guard — block edits that embed git conflict markers during merge."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKERS = ("<<<<<<<", ">>>>>>>")


def merge_in_progress() -> bool:
    return (ROOT / ".git/MERGE_HEAD").is_file()


def main() -> int:
    payload = json.load(sys.stdin)
    args = payload.get("tool_input") or payload.get("arguments") or {}
    content = args.get("contents") or args.get("new_string") or args.get("content") or ""
    path = args.get("path") or args.get("file_path") or ""

    if content and any(m in content for m in MARKERS):
        print(
            json.dumps(
                {
                    "permission": "deny",
                    "user_message": "Conflict markers detected. Load pr-conflict-resolver skill and classify before editing.",
                    "agent_message": (
                        f"Blocked write to {path}: content contains git conflict markers. "
                        "Read .cursor/skills/pr-conflict-resolver/SKILL.md (LOCKED). "
                        "Classify file class (registry/receipt/LOCKED/generated/code). "
                        "Do not hand-merge governance-sensitive JSON."
                    ),
                }
            )
        )
        return 0

    if merge_in_progress() and path:
        rel = str(path).lstrip("./")
        proc = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        unmerged = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
        if rel in unmerged:
            print(
                json.dumps(
                    {
                        "permission": "deny",
                        "user_message": "Merge conflict in progress on a governance path. Use pr-conflict-resolver skill first.",
                        "agent_message": (
                            f"Blocked edit to unmerged file {rel} while MERGE_HEAD present. "
                            "Follow pr-conflict-resolver: classify, stop on L1/LOCKED, write resolution receipt."
                        ),
                    }
                )
            )
            return 0

    print(json.dumps({"permission": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
