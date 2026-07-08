#!/usr/bin/env python3
"""Verify Supabase Security Advisor warnings cleared (0018)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts/proof/supabase-security-advisor-warnings-v1.json"

FUNCTIONS = [
    ("noetfield", "prevent_update_delete"),
    ("noetfield", "tle_entries_immutable_guard"),
    ("noetfield", "current_tenant_id"),
]


def verify(*, write_receipt: bool = False) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from apply_supabase_migration_v1 import merged_env, postgres_url  # noqa: E402

    import asyncio
    import asyncpg

    url = postgres_url(merged_env())
    if not url:
        return {"ok": False, "error": "postgres_not_configured"}

    async def _run() -> dict:
        conn = await asyncpg.connect(url)
        try:
            func_check: dict[str, bool] = {}
            for schema, name in FUNCTIONS:
                row = await conn.fetchrow(
                    """
                    select p.proconfig
                    from pg_proc p
                    join pg_namespace n on n.oid = p.pronamespace
                    where n.nspname = $1 and p.proname = $2
                    """,
                    schema,
                    name,
                )
                cfg = row["proconfig"] if row else None
                has_path = bool(cfg) and any(str(c).startswith("search_path=") for c in (cfg or []))
                func_check[f"{schema}.{name}"] = has_path

            ext = await conn.fetchrow(
                """
                select n.nspname
                from pg_extension e
                join pg_namespace n on n.oid = e.extnamespace
                where e.extname = 'vector'
                """
            )
            vector_schema = ext["nspname"] if ext else None

            pol = await conn.fetchrow(
                """
                select policyname, qual, with_check
                from pg_policies
                where schemaname = 'public' and tablename = 'gateway_leads'
                order by policyname
                limit 1
                """
            )
            with_check = (pol["with_check"] or "").strip().lower() if pol else ""
            gateway_ok = bool(pol) and with_check not in ("true", "")

            ok = all(func_check.values()) and vector_schema == "extensions" and gateway_ok
            return {
                "functions_search_path": func_check,
                "vector_extension_schema": vector_schema,
                "gateway_leads_policy": {
                    "name": pol["policyname"] if pol else None,
                    "with_check": pol["with_check"] if pol else None,
                },
                "ok": ok,
            }
        finally:
            await conn.close()

    checks = asyncio.run(_run())
    row = {
        "schema": "supabase-security-advisor-warnings-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_ref": "tkgpapowwplupyekpivy",
        **checks,
    }
    if write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)
    return row


def main() -> int:
    write = "--write-receipt" in sys.argv
    row = verify(write_receipt=write)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
