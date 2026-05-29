#!/usr/bin/env python3
"""Verify platform health endpoints (local or production)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

ENDPOINTS = (
    "/health",
    "/api/public/chat/health",
    "/api/intake/health",
    "/api/telegram/health",
    "/api/ecosystem/health",
    "/api/ecosystem/public",
)


def _get(base: str, path: str, timeout: float = 15.0) -> tuple[int, dict | str]:
    url = base.rstrip("/") + path
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, body
    except urllib.error.URLError as exc:
        return 0, str(exc)


def main() -> int:
    base = os.environ.get("PLATFORM_HEALTH_BASE", "http://127.0.0.1:8001").strip()
    print("Platform health verification")
    print("  BASE:", base)
    failed = 0

    for path in ENDPOINTS:
        status, body = _get(base, path)
        ok = 200 <= status < 300
        label = "OK" if ok else "FAIL"
        print(f"\n[{label}] GET {path} -> {status}")
        if isinstance(body, dict):
            print(json.dumps(body, indent=2)[:2000])
            if path == "/api/ecosystem/health" and body.get("ok") is False:
                print("  note: ecosystem ok=false — configure LLM/Telegram keys on this host")
        else:
            print(str(body)[:500])
        if not ok:
            failed += 1

    if failed:
        print(f"\n{failed} endpoint(s) failed.", file=sys.stderr)
        return 1
    print("\nAll health endpoints returned 2xx.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
