#!/usr/bin/env python3
"""Verify RLS enabled on machine-only Supabase tables; anon key must not read rows."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts/proof/supabase-rls-machine-tables-v1.json"

TABLES = [
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

sys.path.insert(0, str(ROOT / "scripts"))
from noos_vault_paths_v1 import load_platform_env  # noqa: E402


def _pg_rls_status(url: str) -> dict[str, bool]:
    import asyncio
    import asyncpg

    async def _run() -> dict[str, bool]:
        conn = await asyncpg.connect(url)
        try:
            rows = await conn.fetch(
                """
                select c.relname as table_name, c.relrowsecurity as rls, c.relforcerowsecurity as force_rls
                from pg_class c
                join pg_namespace n on n.oid = c.relnamespace
                where n.nspname = 'public'
                  and c.relname = any($1::text[])
                """,
                TABLES,
            )
            return {r["table_name"]: bool(r["rls"] and r["force_rls"]) for r in rows}
        finally:
            await conn.close()

    return asyncio.run(_run())


def _anon_probe(base: str, anon_key: str, table: str) -> dict:
    req = urllib.request.Request(
        f"{base.rstrip('/')}/rest/v1/{table}?select=*&limit=1",
        headers={"apikey": anon_key, "Authorization": f"Bearer {anon_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            rows = json.loads(body) if body.strip().startswith("[") else []
            return {"ok": False, "status": resp.status, "rows": len(rows), "leak": True}
    except urllib.error.HTTPError as exc:
        # 401/403/406 = blocked as expected
        return {"ok": True, "status": exc.code, "blocked": True}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def verify(*, write_receipt: bool = False) -> dict:
    env = load_platform_env()
    base = env.get("NOETFIELD_SUPABASE_URL") or env.get("SUPABASE_URL") or ""
    anon = env.get("NOETFIELD_SUPABASE_ANON_KEY") or env.get("SUPABASE_ANON_KEY") or ""
    service = env.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or env.get("SUPABASE_SERVICE_ROLE_KEY") or ""

    sys.path.insert(0, str(ROOT / "scripts"))
    from apply_supabase_migration_v1 import merged_env, postgres_url  # noqa: E402

    pg_url = postgres_url(merged_env())
    pg_rls: dict[str, bool] = {}
    if pg_url:
        try:
            pg_rls = _pg_rls_status(pg_url)
        except Exception as exc:
            pg_rls = {"_error": str(exc)[:200]}  # type: ignore[assignment]

    rls_ok = all(pg_rls.get(t) for t in TABLES if t in pg_rls) if pg_rls and "_error" not in pg_rls else False

    anon_probes: dict[str, dict] = {}
    if base and anon:
        for table in TABLES:
            anon_probes[table] = _anon_probe(base, anon, table)
    anon_blocked = all(p.get("blocked") or p.get("ok") for p in anon_probes.values()) if anon_probes else None

    service_ok = False
    if base and service:
        probe = _anon_probe(base, service, "noos_loop_registry")
        # service_role should read (not blocked with 401 on empty is ok - check not leak from anon pattern)
        req = urllib.request.Request(
            f"{base.rstrip('/')}/rest/v1/noos_loop_registry?select=loop_id&limit=1",
            headers={"apikey": service, "Authorization": f"Bearer {service}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                service_ok = resp.status == 200
        except urllib.error.HTTPError:
            service_ok = False

    ok = bool(rls_ok and anon_blocked is not False and service_ok)
    row = {
        "schema": "supabase-rls-machine-tables-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": ok,
        "tables": TABLES,
        "pg_rls_enabled": pg_rls,
        "anon_probes": anon_probes,
        "anon_blocked": anon_blocked,
        "service_role_read_ok": service_ok,
        "project_ref": "tkgpapowwplupyekpivy",
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
