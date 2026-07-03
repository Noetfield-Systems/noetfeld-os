#!/usr/bin/env python3
"""Track D — read-only SourceA portfolio-spine observe (truth_log + cycle receipts)."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = Path.home() / ".sourcea-secrets/portfolio-spine.env"
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
    vals = load_env(ENV_PATH)
    url = vals.get("SUPABASE_URL", "").rstrip("/")
    key = vals.get("SUPABASE_SERVICE_ROLE_KEY") or vals.get("SUPABASE_SERVICE_KEY")
    if url and key:
        return url, key
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
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


def observe() -> dict:
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
    return {
        "schema": "noos-sourcea-supabase-observe-v1",
        "at": utc_now(),
        "read_only": True,
        "one_law": "Observe only — phase_reconciler_v1 remains sole control authority.",
        "ok": ok,
        "truth_log": truth,
        "cycle_receipts": cycles,
        "telemetry_logs": telemetry,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()
    row = observe()
    if args.write_receipt:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / "sourcea-supabase-observe-v1.json"
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(out)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"sourcea_observe ok={row.get('ok')} "
            f"truth={row.get('truth_log', {}).get('count', 0)} "
            f"cycles={row.get('cycle_receipts', {}).get('count', 0)}"
        )

    # If the Supabase profile is simply not configured (observations skipped), treat
    # this as non-fatal in CI runs: write the receipt and exit 0 so read-only probes
    # do not cause workflow failure in environments without Supabase.
    def all_skipped(*sections):
        return all(bool(s.get("skipped")) for s in sections)

    if row.get("ok"):
        return 0
    if all_skipped(truth, cycles, telemetry):
        # not configured — non-fatal
        return 0
    # Otherwise, a real failure (HTTP errors, partial data) should return non-zero
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
