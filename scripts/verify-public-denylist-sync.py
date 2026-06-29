#!/usr/bin/env python3
"""Verify public-output denylist is wired into Vercel and probes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DENYLIST = ROOT / "governance" / "PUBLIC_OUTPUT_DENYLIST.json"
VERCEL_JSON = ROOT / "vercel.json"
VERCELIGNORE = ROOT / ".vercelignore"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def redirect_sources() -> set[str]:
    config = load_json(VERCEL_JSON)
    return {row.get("source", "") for row in config.get("redirects", [])}


def vercelignore_lines() -> set[str]:
    return {
        line.strip()
        for line in VERCELIGNORE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def prefix_redirects(prefix: str) -> tuple[str, str]:
    base = prefix.rstrip("/")
    return (base, f"{base}/:path*")


def path_is_covered(path: str, exact_paths: list[str], prefix_paths: list[str]) -> bool:
    return path in exact_paths or any(path.startswith(prefix) for prefix in prefix_paths)


def main() -> int:
    denylist = load_json(DENYLIST)
    exact_paths = denylist.get("exact_paths", [])
    prefix_paths = denylist.get("prefix_paths", [])
    ignore_patterns = denylist.get("vercelignore_patterns", [])
    probe_paths = denylist.get("probe_paths", [])
    sources = redirect_sources()
    ignores = vercelignore_lines()

    failures: list[str] = []

    for pattern in ignore_patterns:
        if pattern not in ignores:
            failures.append(f".vercelignore missing pattern: {pattern}")

    for path in exact_paths:
        if path not in sources:
            failures.append(f"vercel.json missing exact redirect: {path}")

    for prefix in prefix_paths:
        base, wildcard = prefix_redirects(prefix)
        if wildcard not in sources:
            failures.append(f"vercel.json missing prefix redirect: {wildcard}")
        if base not in sources:
            failures.append(f"vercel.json missing prefix base redirect: {base}")

    for path in probe_paths:
        if not path_is_covered(path, exact_paths, prefix_paths):
            failures.append(f"probe path not covered by exact/prefix denylist: {path}")

    if failures:
        print("verify-public-denylist-sync: FAIL")
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print("verify-public-denylist-sync: PASS")
    print(f"exact_paths={len(exact_paths)} prefix_paths={len(prefix_paths)} probe_paths={len(probe_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
