#!/usr/bin/env python3
"""Write factory cycle + inbox rows to Noetfield Supabase (REST · service role env only)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cloud_inbox_constants_v1 import PRESERVED_INBOX_STATUSES


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def _supabase_config() -> tuple[str, str] | None:
    url = _env("NOETFIELD_SUPABASE_URL") or _env("SUPABASE_URL")
    key = _env("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or _env("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return url.rstrip("/"), key


def _postgres_url() -> str | None:
    url = _env("NOETFIELD_SUPABASE_DATABASE_URL") or _env("DATABASE_URL")
    if url:
        return url.replace("postgresql+asyncpg://", "postgresql://")
    ref = _env("NOETFIELD_SUPABASE_REF") or "tkgpapowwplupyekpivy"
    password = _env("SUPABASE_DB_PASSWORD") or _env("NOETFIELD_SUPABASE_DB_PASSWORD")
    if not password:
        return None
    return f"postgresql://postgres:{quote_plus(password)}@db.{ref}.supabase.co:5432/postgres"


def _insert_pg(table: str, row: dict[str, Any], *, merge: bool = False) -> dict[str, Any]:
    url = _postgres_url()
    if not url:
        return {"ok": False, "skipped": True, "reason": "postgres_not_configured"}
    try:
        import asyncio
        import asyncpg
    except ImportError:
        return {"ok": False, "skipped": True, "reason": "asyncpg_not_installed"}

    cols = list(row.keys())
    vals = [row[c] for c in cols]
    placeholders = ", ".join(f"${i + 1}" for i in range(len(cols)))
    col_sql = ", ".join(cols)

    if merge and "item_id" in row:
        updates = ", ".join(f"{c} = excluded.{c}" for c in cols if c != "item_id")
        sql = (
            f"insert into {table} ({col_sql}) values ({placeholders}) "
            f"on conflict (item_id) do update set {updates} returning id"
        )
    else:
        sql = f"insert into {table} ({col_sql}) values ({placeholders}) returning id"

    async def _run() -> str | None:
        conn = await asyncpg.connect(url)
        try:
            row_id = await conn.fetchval(sql, *vals)
            return str(row_id) if row_id else None
        finally:
            await conn.close()

    try:
        row_id = asyncio.run(_run())
        return {"ok": True, "id": row_id, "via": "postgres"}
    except Exception as exc:
        return {"ok": False, "via": "postgres", "error": str(exc)[:500]}


def _post_row(table: str, row: dict[str, Any], *, merge: bool = False) -> dict[str, Any]:
    cfg = _supabase_config()
    if not cfg:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    base, key = cfg
    prefer = "return=representation"
    if merge:
        prefer += ",resolution=merge-duplicates"
    url = f"{base}/rest/v1/{table}"
    if merge and "item_id" in row:
        url = f"{url}?on_conflict=item_id"
    req = urllib.request.Request(
        url,
        data=json.dumps(row).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": prefer,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            inserted = body[0] if isinstance(body, list) and body else body
            return {"ok": True, "id": inserted.get("id"), "status": resp.status}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == 409 and merge:
            return {"ok": True, "status": 409, "merged": True}
        if exc.code in (404, 406):
            pg = _insert_pg(table, row, merge=merge)
            if pg.get("ok") or pg.get("skipped"):
                return pg
        return {"ok": False, "status": exc.code, "error": detail[:500]}


def _sink_status(cycle: dict[str, Any]) -> str:
    """Map loop/factory cycle status to Supabase check constraint values."""
    raw = str(cycle.get("status") or "ok")
    state = str(cycle.get("state_after") or "")
    if raw == "ok" or state in ("COMPLETE", "IDLE_NO_WORK"):
        return "ok"
    if state in ("FAILED_WITH_RECEIPT", "BLOCKED_WITH_REASON", "TRIAGE_REQUIRED"):
        return "recoverable_error"
    if raw == "degraded":
        return "recoverable_error"
    return raw if raw in ("recoverable_error", "recoverable_exception") else "recoverable_error"


def insert_factory_cycle(cycle: dict[str, Any], *, factory_id: str) -> dict[str, Any]:
    runner = cycle.get("runner_output") or {}
    row = {
        "factory_id": factory_id,
        "cycle_number": int(cycle.get("cycle_number") or 0),
        "started_at": cycle.get("started_at"),
        "finished_at": cycle.get("finished_at"),
        "exit_code": cycle.get("exit_code"),
        "status": _sink_status(cycle),
        "runner_output": runner if isinstance(runner, dict) else {"raw": runner},
        "guardrails": cycle.get("guardrails") or {},
    }
    return _post_row("noetfield_factory_cycle_runs", row)


def _get_inbox_item(item_id: str) -> dict[str, Any] | None:
    cfg = _supabase_config()
    if not cfg:
        return None
    base, key = cfg
    req = urllib.request.Request(
        f"{base}/rest/v1/noetfield_worker_inbox_queue?item_id=eq.{item_id}&select=*",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
            return rows[0] if rows else None
    except urllib.error.HTTPError:
        return None


def upsert_inbox_item(item: dict[str, Any]) -> dict[str, Any]:
    existing = _get_inbox_item(item["item_id"])
    if existing and existing.get("status") in PRESERVED_INBOX_STATUSES:
        return {
            "ok": True,
            "skipped": True,
            "reason": "status_preserved",
            "item_id": item["item_id"],
            "status": existing.get("status"),
        }
    row = {
        "item_id": item["item_id"],
        "lane": item.get("lane") or "NOETFELD-OS",
        "title": item["title"],
        "priority": item.get("priority") or "P1",
        "status": item.get("status") or "pending",
        "source_trace": item.get("source_trace"),
        "payload": item.get("payload") or {},
    }
    return _post_row("noetfield_worker_inbox_queue", row, merge=True)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Supabase sink for factory/inbox rows")
    sub = parser.add_subparsers(dest="command", required=True)

    cycle_p = sub.add_parser("cycle", help="Insert one factory cycle row from JSON file")
    cycle_p.add_argument("path", help="Cycle JSON file")
    cycle_p.add_argument("--factory-id", required=True)

    inbox_p = sub.add_parser("inbox", help="Upsert inbox items from JSON file")
    inbox_p.add_argument("path", help="Inbox bundle JSON with items[]")

    args = parser.parse_args(argv)
    if args.command == "cycle":
        cycle = json.loads(open(args.path, encoding="utf-8").read())
        result = insert_factory_cycle(cycle, factory_id=args.factory_id)
    else:
        bundle = json.loads(open(args.path, encoding="utf-8").read())
        results = []
        for item in bundle.get("items") or []:
            results.append(upsert_inbox_item(item))
        ok = all(r.get("ok") or r.get("skipped") for r in results)
        print(json.dumps({"ok": ok, "count": len(results), "results": results}, indent=2))
        return 0 if ok else 1

    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") or result.get("skipped") else 1


if __name__ == "__main__":
    raise SystemExit(main())
