#!/usr/bin/env python3
"""Verify the scheduled Supabase heartbeat."""

from __future__ import annotations

import asyncio
import os
import sys

import asyncpg
import urllib.request


def main() -> int:
    supabase_url = os.environ["NOETFIELD_SUPABASE_URL"].rstrip("/")
    anon_key = os.environ["NOETFIELD_SUPABASE_ANON_KEY"].strip()
    db_url = os.environ["NOETFIELD_SUPABASE_DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")

    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/",
        headers={
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        code = resp.status
    print(f"REST HTTP {code}")
    if code not in (200, 401):
        return 1

    async def ping_sql() -> None:
        conn = await asyncpg.connect(db_url)
        try:
            assert await conn.fetchval("select 1") == 1
            print("SQL heartbeat OK")
        finally:
            await conn.close()

    asyncio.run(ping_sql())
    return 0


if __name__ == "__main__":
    sys.exit(main())
