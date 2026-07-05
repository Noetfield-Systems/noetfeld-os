#!/usr/bin/env python3
"""Fail closed if www greeting asset, disk SSOT, and platform API diverge."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "chatbot" / "public-chat-greeting.json"
ASSET = ROOT / "assets" / "nf-chat-greeting-ssot.js"


def disk_hash() -> str:
    data = json.loads(SSOT.read_text(encoding="utf-8"))
    canonical = json.dumps(
        {"greeting": data["greeting"], "citations": data["citations"]},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def asset_hash() -> str:
    text = ASSET.read_text(encoding="utf-8")
    match = re.search(r"sha256=([a-f0-9]{64})", text)
    if not match:
        raise RuntimeError(f"missing sha256 marker in {ASSET}")
    return match.group(1)


def fetch_json(url: str) -> dict[str, object]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def live_hashes(platform_base: str, www_base: str) -> tuple[str | None, str | None]:
    platform_hash: str | None = None
    www_hash: str | None = None
    try:
        health = fetch_json(f"{platform_base.rstrip('/')}/api/public/chat/health")
        greeting = health.get("greeting_ssot") or {}
        if isinstance(greeting, dict):
            platform_hash = str(greeting.get("content_hash") or "") or None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        platform_hash = None
    try:
        body = fetch_json(f"{www_base.rstrip('/')}/api/public/chat")
        platform_hash = platform_hash or str(body.get("content_hash") or "") or None
        if not platform_hash and body.get("greeting"):
            canonical = json.dumps(
                {"greeting": body["greeting"], "citations": body.get("citations") or []},
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
            platform_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        pass
    try:
        asset_url = f"{www_base.rstrip('/')}/assets/nf-chat-greeting-ssot.js"
        req = urllib.request.Request(asset_url)
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8")
        match = re.search(r"sha256=([a-f0-9]{64})", text)
        www_hash = match.group(1) if match else None
    except (urllib.error.URLError, TimeoutError):
        www_hash = None
    return platform_hash, www_hash


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--platform-base", default="https://platform.noetfield.com")
    parser.add_argument("--www-base", default="https://www.noetfield.com")
    args = parser.parse_args()

    failures: list[str] = []
    expected = disk_hash()
    if not ASSET.is_file():
        failures.append(f"missing generated asset {ASSET}")
    else:
        got = asset_hash()
        if got != expected:
            failures.append(f"asset hash {got[:12]} != disk ssot {expected[:12]}")

    if args.live:
        platform_hash, www_hash = live_hashes(args.platform_base, args.www_base)
        if platform_hash and platform_hash != expected:
            failures.append(f"platform hash {platform_hash[:12]} != disk ssot {expected[:12]}")
        if www_hash and www_hash != expected:
            failures.append(f"live www asset hash {www_hash[:12]} != disk ssot {expected[:12]}")
        if not www_hash:
            failures.append("live www asset nf-chat-greeting-ssot.js not found or unreadable")

    if failures:
        for item in failures:
            print(f"FAIL {item}", file=sys.stderr)
        return 1
    print(f"verify_chat_greeting_coupling: PASS disk={expected[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
