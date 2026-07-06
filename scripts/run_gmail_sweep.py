#!/usr/bin/env python3
"""Run one operations@ Gmail sweep (cron / manual)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLATFORM = os.environ.get("PLATFORM_API_BASE", "https://platform.noetfield.com").rstrip("/")
READ_VAULT = ROOT / "scripts" / "read_platform_vault.sh"


def read_vault(key: str) -> str:
    if not READ_VAULT.is_file():
        return ""
    try:
        out = subprocess.run(
            ["bash", str(READ_VAULT), "get", key],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""
    return (out.stdout or "").strip() if out.returncode == 0 else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Trigger platform Gmail sweep for operations@")
    parser.add_argument("--platform-base", default=DEFAULT_PLATFORM)
    parser.add_argument("--admin-secret", default="", help="X-Admin-Secret (default: vault ADMIN_DASHBOARD_SECRET)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    secret = (args.admin_secret or "").strip() or read_vault("ADMIN_DASHBOARD_SECRET")
    headers = {"Accept": "application/json", "User-Agent": "noetfield-gmail-sweep-cli/1.0"}
    if secret:
        headers["X-Admin-Secret"] = secret

    url = f"{args.platform_base.rstrip('/')}/api/operations/gmail/sweep"
    req = urllib.request.Request(url, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"gmail_sweep: FAIL http={exc.code} {detail[:300]}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"gmail_sweep: FAIL {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(body, indent=2))
    else:
        print(
            "gmail_sweep: PASS "
            f"ingested={body.get('messages_ingested')} "
            f"seen={body.get('messages_seen')} "
            f"skipped={body.get('messages_skipped')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
