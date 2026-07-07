#!/usr/bin/env python3
"""Re-enqueue blocked UPG inbox rows when real handlers exist (Track B B7)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from cloud_inbox_worker_v1 import HANDLERS  # noqa: E402

from noos_vault_paths_v1 import load_platform_env  # noqa: E402


def _load_env() -> dict[str, str]:
    return load_platform_env()


def _supabase_cfg() -> tuple[str, str] | None:
    vals = _load_env()
    url = vals.get("NOETFIELD_SUPABASE_URL") or vals.get("SUPABASE_URL")
    key = vals.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or vals.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return url.rstrip("/"), key
    return None


def _fetch_blocked() -> list[dict]:
    cfg = _supabase_cfg()
    if not cfg:
        return []
    url, key = cfg
    req = urllib.request.Request(
        f"{url}/rest/v1/noetfield_worker_inbox_queue?status=eq.blocked&select=item_id,payload,status",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _patch_pending(item_id: str) -> bool:
    cfg = _supabase_cfg()
    if not cfg:
        return False
    url, key = cfg
    body = json.dumps({"status": "pending"}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/rest/v1/noetfield_worker_inbox_queue?item_id=eq.{urllib.parse.quote(item_id, safe='')}",
        data=body,
        method="PATCH",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError:
        return False


def main() -> int:
    blocked = _fetch_blocked()
    requeued: list[str] = []
    for row in blocked:
        upg = (row.get("payload") or {}).get("upg") or row.get("item_id")
        if upg in HANDLERS and _patch_pending(row["item_id"]):
            requeued.append(row["item_id"])
    print(json.dumps({"requeued": requeued, "blocked_seen": len(blocked)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
