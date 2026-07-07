#!/usr/bin/env python3
"""Apply a numbered Supabase migration from infrastructure/supabase/migrations/.

Verifies post-state (e.g. founder_blocked in inbox status check) and writes a receipt.
Uses ~/.noetfield-platform-secrets/noetfield-db.env + noetfield.env — never prints secret values.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_proof_receipt_paths_v1 import proof_receipt  # noqa: E402
MIGRATIONS = ROOT / "infrastructure/supabase/migrations"
from noos_vault_paths_v1 import NOETFIELD_DB_ENV, NOETFIELD_LOCAL_ENV

NOETFIELD_ENV = NOETFIELD_LOCAL_ENV
DEFAULT_REF = "tkgpapowwplupyekpivy"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    vals: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        vals[k.strip()] = v.strip().strip("'\"")
    return vals


def merged_env() -> dict[str, str]:
    vals = load_env_file(NOETFIELD_ENV)
    vals.update(load_env_file(NOETFIELD_DB_ENV))
    for k, v in os.environ.items():
        if k.startswith(("NOETFIELD_", "SUPABASE_")) and v.strip():
            vals[k] = v.strip()
    return vals


def postgres_url(vals: dict[str, str]) -> str | None:
    url = vals.get("NOETFIELD_SUPABASE_DATABASE_URL") or vals.get("DATABASE_URL")
    if url:
        return url.replace("postgresql+asyncpg://", "postgresql://")
    ref = vals.get("NOETFIELD_SUPABASE_REF") or vals.get("SUPABASE_PROJECT_ID") or DEFAULT_REF
    password = vals.get("SUPABASE_DB_PASSWORD") or vals.get("NOETFIELD_SUPABASE_DB_PASSWORD")
    if not password:
        return None
    return f"postgresql://postgres:{quote_plus(password)}@db.{ref}.supabase.co:5432/postgres"


def migration_path(number: str) -> Path:
    matches = sorted(MIGRATIONS.glob(f"{number}_*.sql"))
    if not matches:
        raise FileNotFoundError(f"no migration matching {number}_*.sql under {MIGRATIONS}")
    return matches[0]


async def _run_sql(url: str, sql: str) -> None:
    import asyncpg

    conn = await asyncpg.connect(url)
    try:
        await conn.execute(sql)
    finally:
        await conn.close()


async def _verify_table_exists(url: str, table: str) -> dict[str, Any]:
    import asyncpg

    conn = await asyncpg.connect(url)
    try:
        row = await conn.fetchrow(
            "select to_regclass($1) as reg",
            f"public.{table}",
        )
        ok = row["reg"] is not None
        return {"ok": ok, "table": table, "exists": ok}
    finally:
        await conn.close()


async def _verify_factory_cycle_degraded(url: str) -> dict[str, Any]:
    import asyncpg

    conn = await asyncpg.connect(url)
    try:
        row = await conn.fetchrow(
            """
            select pg_get_constraintdef(c.oid) as def
            from pg_constraint c
            join pg_class t on t.oid = c.conrelid
            where t.relname = 'noetfield_factory_cycle_runs'
              and c.conname = 'noetfield_factory_cycle_runs_status_check'
            """
        )
        defn = (row["def"] if row else "") or ""
        ok = "degraded" in defn
        aliased = await conn.fetchval(
            """
            select count(*) from noetfield_factory_cycle_runs
            where status = 'recoverable_error' and exit_code = 1 and factory_id like 'loop-%'
            """
        )
        return {
            "ok": ok,
            "constraint_def": defn[:500],
            "remaining_aliased_loop_rows": int(aliased or 0),
        }
    finally:
        await conn.close()


async def _verify_rls_machine_tables(url: str) -> dict[str, Any]:
    import asyncpg

    tables = [
        "noetfield_truth_log",
        "probe_cron_receipts",
        "improvement_queue",
        "noos_loop_registry",
        "noos_deadman_runs",
        "workflow_census_v1",
        "workflow_census_runs_v1",
        "trustfield_loop_registry",
        "trustfield_loop_receipts",
        "trustfield_verify_recipe_runs",
    ]
    conn = await asyncpg.connect(url)
    try:
        rows = await conn.fetch(
            """
            select c.relname as table_name, c.relrowsecurity as rls, c.relforcerowsecurity as force_rls
            from pg_class c
            join pg_namespace n on n.oid = c.relnamespace
            where n.nspname = 'public' and c.relname = any($1::text[])
            """,
            tables,
        )
        by_name = {r["table_name"]: bool(r["rls"] and r["force_rls"]) for r in rows}
        missing = [t for t in tables if t not in by_name]
        not_enabled = [t for t, v in by_name.items() if not v]
        ok = not missing and not not_enabled
        return {
            "ok": ok,
            "rls_enabled": by_name,
            "missing_tables": missing,
            "rls_not_enabled": not_enabled,
        }
    finally:
        await conn.close()


async def _verify_founder_blocked(url: str) -> dict[str, Any]:
    import asyncpg

    conn = await asyncpg.connect(url)
    try:
        row = await conn.fetchrow(
            """
            select pg_get_constraintdef(c.oid) as def
            from pg_constraint c
            join pg_class t on t.oid = c.conrelid
            where t.relname = 'noetfield_worker_inbox_queue'
              and c.conname = 'noetfield_worker_inbox_queue_status_check'
            """
        )
        defn = (row["def"] if row else "") or ""
        ok = "founder_blocked" in defn
        return {"ok": ok, "constraint_def": defn[:500]}
    finally:
        await conn.close()


def verify_migration(number: str, *, url: str) -> dict[str, Any]:
    if number == "0012":
        return asyncio.run(_verify_founder_blocked(url))
    if number == "0013":
        return asyncio.run(_verify_table_exists(url, "noetfield_truth_log"))
    if number == "0014":
        return asyncio.run(_verify_factory_cycle_degraded(url))
    if number == "0016":
        return asyncio.run(_verify_table_exists(url, "noos_loop_registry"))
    if number == "0017":
        return asyncio.run(_verify_rls_machine_tables(url))
    return {"ok": True, "note": "no specific verifier for migration"}


def apply_migration(number: str, *, dry_run: bool = False) -> dict[str, Any]:
    vals = merged_env()
    url = postgres_url(vals)
    path = migration_path(number)
    sql = path.read_text(encoding="utf-8")
    receipt: dict[str, Any] = {
        "schema": "supabase-migration-receipt-v1",
        "migration": number,
        "migration_file": str(path.relative_to(ROOT)),
        "applied_at": utc_now(),
        "dry_run": dry_run,
        "postgres_configured": bool(url),
    }
    if not url:
        receipt.update({"ok": False, "blocker_reason": "postgres_not_configured"})
        return receipt

    pre = verify_migration(number, url=url)
    receipt["pre_verify"] = pre
    if pre.get("ok") and not dry_run:
        receipt.update({
            "ok": True,
            "skipped": True,
            "reason": "already_applied",
            "post_verify": pre,
        })
        return receipt

    if dry_run:
        receipt.update({"ok": True, "would_apply": True, "sql_bytes": len(sql.encode("utf-8"))})
        return receipt

    try:
        asyncio.run(_run_sql(url, sql))
        post = verify_migration(number, url=url)
        receipt["post_verify"] = post
        receipt["ok"] = bool(post.get("ok"))
        if not receipt["ok"]:
            receipt["blocker_reason"] = "post_verify_failed"
    except Exception as exc:
        receipt.update({"ok": False, "blocker_reason": "apply_failed", "error": str(exc)[:500]})

    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--migration", required=True, help="Migration number e.g. 0012")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    number = re.sub(r"\D", "", args.migration).zfill(4) if args.migration.isdigit() else args.migration
    result = apply_migration(number, dry_run=args.dry_run)

    if args.write_receipt:
        out = proof_receipt(f"supabase-migration-{number}-v1.json")
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        result["receipt_path"] = str(out.relative_to(ROOT))
        result["receipt_tier"] = "proof"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"migration={number} ok={result.get('ok')} "
            f"skipped={result.get('skipped')} reason={result.get('reason') or result.get('blocker_reason')}"
        )

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
