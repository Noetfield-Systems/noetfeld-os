#!/usr/bin/env python3
"""Classify git-conflicted or specified paths per nf-pr-conflict-resolver-v1."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "nf-pr-conflict-resolver-v1.json"


def load_ssot() -> dict:
    return json.loads(SSOT.read_text(encoding="utf-8"))


def git_conflicted() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        return []
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def classify(path: str, classes: list[dict]) -> str:
    for item in classes:
        for pattern in item.get("patterns", []):
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, f"**/{pattern}"):
                return item["id"]
    return "ordinary_code"


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify conflicted files for PR resolution")
    parser.add_argument("--git", action="store_true", help="Use git unmerged paths")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("paths", nargs="*", help="Explicit paths to classify")
    args = parser.parse_args()

    ssot = load_ssot()
    classes = ssot.get("file_classes", [])
    paths = args.paths or (git_conflicted() if args.git else [])
    if not paths:
        if args.json:
            print(json.dumps({"paths": [], "classifications": {}}))
        else:
            print("No conflicted paths (git clean or pass paths explicitly)")
        return 0

    result = {p: classify(p, classes) for p in paths}
    if args.json:
        print(json.dumps({"paths": paths, "classifications": result}, indent=2))
    else:
        for p, cls in result.items():
            print(f"{cls}\t{p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
