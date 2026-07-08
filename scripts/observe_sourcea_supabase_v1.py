#!/usr/bin/env python3
"""Track D — SourceA portfolio-spine observe + CRON_FIRED heartbeat (ICL-P1-03)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_portfolio_spine_heartbeat_v1 import write_observe_heartbeat  # noqa: E402

ENV_PATH = Path.home() / ".sourcea-secrets/portfolio-spine.env"
PLATFORM_ENV = Path.home() / ".noetfield-platform-secrets/portfolio-spine.env"
OUT_DIR = ROOT / ".noos-runtime/observe/sourcea"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env(path: Path) -> dict[str, str]:
    vals: dict[str, str] = {}
    if not path.is_file():
        return vals
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip("'\"")
    return vals


def supabase_cfg() -> tuple[str, str] | None:
    vals: dict[str, str] = {}
    for path in (ENV_PATH, PLATFORM_ENV):
        vals.update(load_env(path))
    url = (
        vals.get("PORTFOLIO_SPINE_SUPABASE_URL")
        or vals.get("SUPABASE_URL")
        or os.environ.get("PORTFOLIO_SPINE_SUPABASE_URL")
        or ""
    ).rstrip("/")
    key = (
        vals.get("PORTFOLIO_SPINE_SERVICE_ROLE_KEY")
        or vals.get("SUPABASE_SERVICE_ROLE_KEY")
        or vals.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("PORTFOLIO_SPINE_SERVICE_ROLE_KEY")
        or ""
    )
    if url and key:
        return url, key
    return None


def fetch_rows(table: str, *, select: str, order: str, limit: int = 5) -> dict:
    cfg = supabase_cfg()
    if not cfg:
        return {"ok": False, "skipped": True, "reason": "portfolio_spine_not_configured"}
    url, key = cfg
    params = urllib.parse.urlencode({"select": select, "order": order, "limit": str(limit)})
    req = urllib.request.Request(
        f"{url}/rest/v1/{table}?{params}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "table": table, "count": len(rows), "rows": rows}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "table": table, "status": exc.code, "error": exc.read().decode()[:300]}


def observe(*, write_heartbeat: bool = True) -> dict:
    truth = fetch_rows("truth_log", select="id,event,recorded_at,queue_head", order="recorded_at.desc")
    cycles = fetch_rows(
        "cycle_receipts",
        select="id,created_at,verdict,trigger_source,queue_head_before,queue_head_after",
        order="created_at.desc",
    )
    telemetry = fetch_rows(
        "telemetry_logs",
        select="id,created_at,memory_type,metadata",
        order="created_at.desc",
        limit=3,
    )
    ok = truth.get("ok") or cycles.get("ok") or telemetry.get("ok")
    row: dict = {
        "schema": "noos-sourcea-supabase-observe-v1",
        "at": utc_now(),
        "read_only": True,
        "one_law": "Observe + heartbeat only — phase_reconciler_v1 remains sole control authority.",
        "ok": ok,
        "truth_log": truth,
        "cycle_receipts": cycles,
        "telemetry_logs": telemetry,
    }
    if write_heartbeat and ok:
        row["spine_heartbeat"] = write_observe_heartbeat()
        row["ok"] = row["ok"] and row["spine_heartbeat"].get("ok", False)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--no-heartbeat", action="store_true", help="observe only, skip CRON_FIRED write")
    args = ap.parse_args()
    row = observe(write_heartbeat=not args.no_heartbeat)
    if args.write_receipt:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / "sourcea-supabase-observe-v1.json"
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(out)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        hb = row.get("spine_heartbeat") or {}
        print(
            f"sourcea_observe ok={row.get('ok')} "
            f"truth={row.get('truth_log', {}).get('count', 0)} "
            f"heartbeat={hb.get('ok')}"
        )

    truth = row.get("truth_log") or {}
    cycles = row.get("cycle_receipts") or {}
    telemetry = row.get("telemetry_logs") or {}

    if row.get("ok"):
        return 0
    if all(bool(s.get("skipped")) for s in (truth, cycles, telemetry) if s):
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
