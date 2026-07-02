#!/usr/bin/env python3
"""Dispatch one or all NOOS 24/7 loop ticks via GitHub repository_dispatch."""

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
REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"
REPO = "kazemnezhadsina144-dot/noetfeld-os"


def _token() -> str | None:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0:
        return None
    vals = dict(line.split("=", 1) for line in proc.stdout.splitlines() if "=" in line)
    return vals.get("password")


def dispatch(event_type: str, *, source: str = "trigger_noos_loop_dispatch_v1") -> dict:
    token = _token()
    if not token:
        return {"ok": False, "error": "github_token_not_configured", "event_type": event_type}
    body = {
        "event_type": event_type,
        "client_payload": {"source": source, "event_type": event_type},
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
            return {"ok": True, "status": resp.status, "event_type": event_type}
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "event_type": event_type,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
        }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--event-type", help="Single loop event type")
    ap.add_argument("--all", action="store_true", help="Dispatch every loop in registry")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    events = [args.event_type] if args.event_type else []
    if args.all:
        events = [row["event_type"] for row in registry.get("loops") or []]
    if not events:
        ap.error("provide --event-type or --all")

    results = [dispatch(evt) for evt in events]
    ok = all(r.get("ok") for r in results)
    payload = {"ok": ok, "dispatched": results}
    print(json.dumps(payload, indent=2) if args.json else json.dumps(payload))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
