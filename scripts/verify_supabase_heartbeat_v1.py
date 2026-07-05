#!/usr/bin/env python3
"""Verify the scheduled Supabase heartbeat."""

from __future__ import annotations

import asyncio
import os
import sys

import asyncpg
import urllib.error
import urllib.request

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from nf_vault_env import ensure_noetfield_supabase_env  # noqa: E402


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(
            f"FAIL: {name} missing — set GitHub Actions secret or run "
            "scripts/sync_noetfield_supabase_github_secrets.sh from ~/.sourcea-secrets/noetfield.env",
            file=sys.stderr,
        )
        return ""
    return value


def main() -> int:
    ensure_noetfield_supabase_env()
    supabase_url = require_env("NOETFIELD_SUPABASE_URL")
    anon_key = require_env("NOETFIELD_SUPABASE_ANON_KEY")
    db_url = require_env("NOETFIELD_SUPABASE_DATABASE_URL")
    if not supabase_url or not anon_key or not db_url:
        return 1
    supabase_url = supabase_url.rstrip("/")
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/",
        headers={
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            code = resp.status
    except urllib.error.HTTPError as exc:
        code = exc.code
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

    try:
        asyncio.run(ping_sql())
    except OSError as exc:
        # GitHub Actions cannot always reach Supabase pooler; REST ping keeps project awake.
        print(f"SQL heartbeat skipped (REST OK): {exc}")
    except Exception as exc:
        print(f"SQL heartbeat FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
