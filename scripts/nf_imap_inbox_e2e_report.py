#!/usr/bin/env python3
"""Run IMAP sweep + triage on platform and report latest signal row + verdict."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from nf_vault_env import ensure_noetfield_supabase_env  # noqa: E402

READ_VAULT = ROOT / "scripts" / "read_platform_vault.sh"


def read_vault(key: str) -> str:
    out = subprocess.run(
        ["bash", str(READ_VAULT), "get", key],
        capture_output=True,
        text=True,
        check=False,
    )
    return (out.stdout or "").strip() if out.returncode == 0 else ""


def post_json(url: str, *, secret: str) -> dict:
    headers = {
        "Accept": "application/json",
        "User-Agent": "nf-imap-inbox-e2e/1.0",
        "X-Admin-Secret": secret,
    }
    req = urllib.request.Request(url, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        return {"ok": False, "status": "failed", "http": exc.code, "error": detail}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "status": "failed", "error": str(exc)}


async def fetch_latest_signal_report(database_url: str) -> dict:
    import asyncpg

    url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)
    try:
        signal = await conn.fetchrow(
            """
            select id, signal_type, source_event_id, payload, received_at, provenance
            from noetfield.signals
            where signal_type = 'operations_inbox_email'
            order by received_at desc
            limit 1
            """
        )
        verdict = None
        if signal:
            verdict = await conn.fetchrow(
                """
                select verdict, route, label, risk_score, rubric, triaged_at, telegram_message_id
                from noetfield.operations_signal_triage
                where signal_id = $1
                """,
                signal["id"],
            )
        return {
            "signal": dict(signal) if signal else None,
            "verdict": dict(verdict) if verdict else None,
        }
    finally:
        await conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform-base", default=os.environ.get("PLATFORM_API_BASE", "https://platform.noetfield.com"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    secret = read_vault("ADMIN_DASHBOARD_SECRET")
    ensure_noetfield_supabase_env()
    db_url = os.environ.get("NOETFIELD_SUPABASE_DATABASE_URL") or os.environ.get("DATABASE_URL") or ""
    if not secret:
        print("FAIL missing ADMIN_DASHBOARD_SECRET", file=sys.stderr)
        return 1
    if not db_url:
        print("FAIL missing DATABASE_URL", file=sys.stderr)
        return 1

    base = args.platform_base.rstrip("/")
    sweep = post_json(f"{base}/api/operations/gmail/sweep", secret=secret)
    triage = post_json(f"{base}/api/operations/signal-triage/run", secret=secret)
    report = asyncio.run(fetch_latest_signal_report(db_url))

    payload = report.get("signal") or {}
    if isinstance(payload.get("payload"), str):
        try:
            payload["payload"] = json.loads(payload["payload"])
        except json.JSONDecodeError:
            pass

    out = {
        "sweep": sweep,
        "triage": triage,
        "latest_signal": report.get("signal"),
        "latest_verdict": report.get("verdict"),
    }
    if args.json:
        print(json.dumps(out, indent=2, default=str))
    else:
        sig = report.get("signal") or {}
        ver = report.get("verdict") or {}
        pl = sig.get("payload") or {}
        if isinstance(pl, str):
            pl = json.loads(pl)
        print(
            f"sweep: ingested={sweep.get('messages_ingested')} seen={sweep.get('messages_seen')} "
            f"status={sweep.get('status')}"
        )
        print(
            f"signal: id={sig.get('id')} subject={pl.get('subject')} from={pl.get('from')} "
            f"source_event_id={sig.get('source_event_id')}"
        )
        print(
            f"verdict: {ver.get('verdict')} route={ver.get('route')} label={ver.get('label')} "
            f"risk={ver.get('risk_score')}"
        )
    return 0 if sweep.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
