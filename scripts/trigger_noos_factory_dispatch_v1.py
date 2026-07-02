#!/usr/bin/env python3
"""Fire noos factory autorun via repository_dispatch (external cron bridge).

Usage (Cloudflare cron / headless automation only — not Cursor manual):
  GITHUB_TOKEN=... python3 scripts/trigger_noos_factory_dispatch_v1.py

Requires token with `repo` scope on kazemnezhadsina144-dot/noetfeld-os.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPO = "kazemnezhadsina144-dot/noetfeld-os"
EVENT_TYPE = "noos_factory_autorun_tick"


def _token() -> str | None:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    vals = dict(line.split("=", 1) for line in proc.stdout.splitlines() if "=" in line)
    return vals.get("password")


def dispatch(*, client_payload: dict | None = None) -> dict:
    token = _token()
    if not token:
        return {"ok": False, "error": "github_token_not_configured"}
    body = {
        "event_type": EVENT_TYPE,
        "client_payload": client_payload or {"source": "trigger_noos_factory_dispatch_v1"},
    }
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/dispatches",
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"ok": True, "status": resp.status, "event_type": EVENT_TYPE}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": exc.read().decode("utf-8", errors="replace")[:300]}


def main() -> int:
    result = dispatch()
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
