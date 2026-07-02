#!/usr/bin/env python3
"""Supabase spine Realtime feed v1 — pg_notify push + optional REST snapshot.

Replaces on-demand REST-only dashboard pulls for stale-lane awareness (T8).
Enable Supabase Realtime on noetfield_stale_lane_events for browser clients;
this CLI feed uses postgres LISTEN on channel noetfield_spine_feed (asyncpg).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".noos-runtime/spine-feed"
DEFAULT_CACHE = RUNTIME / "spine-realtime-feed-v1.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _env(name: str) -> str:
    return (os.environ.get(name) or os.environ.get(f"NOETFIELD_{name}") or "").strip()


def supabase_rest(path: str, *, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
    url = _env("SUPABASE_URL") or _env("NOETFIELD_SUPABASE_URL")
    key = _env("SUPABASE_SERVICE_ROLE_KEY") or _env("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return []
    query = urllib.parse.urlencode(params or {})
    target = f"{url.rstrip('/')}/rest/v1/{path}"
    if query:
        target = f"{target}?{query}"
    req = urllib.request.Request(
        target,
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body if isinstance(body, list) else []
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return []


def fetch_stale_events(*, limit: int = 20) -> list[dict[str, Any]]:
    return supabase_rest(
        "noetfield_stale_lane_events",
        params={
            "select": "id,recorded_at,lane_id,factory_id,last_seen_at,stale_threshold_minutes,event,metadata",
            "order": "recorded_at.desc",
            "limit": str(limit),
        },
    )


def append_cache(row: dict[str, Any], *, cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, separators=(",", ":")) + "\n")


async def listen_pg_notify(*, dsn: str, cache_path: Path, once: bool) -> dict[str, Any]:
    import asyncpg  # noqa: WPS433

    received: list[dict[str, Any]] = []

    async def _handler(_conn, _pid, channel, payload) -> None:
        try:
            row = json.loads(payload)
        except json.JSONDecodeError:
            row = {"raw": payload, "at": utc_now()}
        row["transport"] = "pg_notify"
        row["channel"] = channel
        row["received_at"] = utc_now()
        received.append(row)
        append_cache(row, cache_path=cache_path)

    conn = await asyncpg.connect(dsn)
    await conn.add_listener("noetfield_spine_feed", _handler)
    if once:
        await asyncio.sleep(0.5)
    else:
        await asyncio.sleep(30)
    await conn.remove_listener("noetfield_spine_feed", _handler)
    await conn.close()
    return {"ok": True, "received": len(received), "events": received[-5:]}


def run_snapshot(*, cache_path: Path) -> dict[str, Any]:
    rows = fetch_stale_events()
    for row in rows:
        row["transport"] = "rest_snapshot"
        row["received_at"] = utc_now()
        append_cache(row, cache_path=cache_path)
    return {
        "schema": "spine-realtime-feed-v1",
        "mode": "rest_snapshot",
        "at": utc_now(),
        "stale_events": rows,
        "cache_path": str(cache_path.relative_to(ROOT)),
    }


async def run_listen(*, once: bool, cache_path: Path) -> dict[str, Any]:
    dsn = _env("SUPABASE_DB_URL") or _env("NOETFIELD_SUPABASE_DB_URL")
    if not dsn:
        return {**run_snapshot(cache_path=cache_path), "listen_skipped": "supabase_db_url_missing"}
    listen_row = await listen_pg_notify(dsn=dsn, cache_path=cache_path, once=once)
    snapshot = fetch_stale_events(limit=5)
    return {
        "schema": "spine-realtime-feed-v1",
        "mode": "pg_notify_listen",
        "at": utc_now(),
        "listen": listen_row,
        "latest_stale_events": snapshot,
        "cache_path": str(cache_path.relative_to(ROOT)),
        "realtime_note": "Enable Supabase Realtime on noetfield_stale_lane_events for browser push clients",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--listen", action="store_true", help="Listen on pg_notify channel (asyncpg)")
    ap.add_argument("--once", action="store_true", help="Listen briefly then exit")
    ap.add_argument("--snapshot", action="store_true", help="REST snapshot only")
    ap.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.listen:
        row = asyncio.run(run_listen(once=args.once, cache_path=args.cache))
    else:
        row = run_snapshot(cache_path=args.cache)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        stale = row.get("stale_events") or row.get("latest_stale_events") or []
        print(f"spine_feed mode={row.get('mode')} stale_events={len(stale)} cache={row.get('cache_path')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
