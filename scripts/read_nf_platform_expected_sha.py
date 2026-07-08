#!/usr/bin/env python3
"""Resolve expected platform git SHA for drift/deploy checks (pin file, not repo HEAD)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN_FILE = ROOT / "data" / "nf-platform-deploy-pin-v1.json"
DEFAULT_PLATFORM_BASE = "https://platform.noetfield.com"
USER_AGENT = "noetfield-platform-expected-sha/1.0"


def read_pin() -> str:
    if not PIN_FILE.is_file():
        return ""
    try:
        doc = json.loads(PIN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    return str(doc.get("git_sha") or "").strip()


def fetch_live(platform_base: str = DEFAULT_PLATFORM_BASE) -> str:
    url = f"{platform_base.rstrip('/')}/api/public/chat/health"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return ""
    return str(body.get("git_sha") or "").strip()


def resolve(*, prefer_live: bool = False, platform_base: str = DEFAULT_PLATFORM_BASE) -> str:
    pin = read_pin()
    live = fetch_live(platform_base) if prefer_live else ""
    if prefer_live and live:
        return live
    if pin:
        return pin
    return live


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--prefer-live", action="store_true", help="Use live platform health over pin file")
    parser.add_argument("--platform-base", default=DEFAULT_PLATFORM_BASE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    sha = resolve(prefer_live=args.prefer_live, platform_base=args.platform_base)
    if not sha:
        print("FAIL: no platform expected SHA (pin missing and live health unreachable)", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"git_sha": sha, "pin_file": str(PIN_FILE.relative_to(ROOT))}))
    else:
        print(sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
