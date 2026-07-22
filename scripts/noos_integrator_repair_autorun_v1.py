#!/usr/bin/env python3
"""NOOS integrator — one-shot autorun repair (liveness + SourceA spine heartbeats).

Factory-cycle repair writes are gated off by default: they advance
noetfield_factory_cycle_runs with cloud_trigger=noos_integrator_repair and can
mask organic http_loop producer stalls. Use --factory-cycles only for explicit
legacy/founder repair, never as routine sustain.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_loop_liveness_v1 import sync_meta_liveness_rows, upsert_loop_liveness  # noqa: E402
from noos_portfolio_spine_heartbeat_v1 import supabase_post, write_full_spine_repair  # noqa: E402
from noos_vault_paths_v1 import NOOS_LOCAL_ENV, NOETFIELD_LOCAL_ENV, load_platform_env, parse_env_file, supabase_creds  # noqa: E402

INTERVALS = ROOT / "cloud/workers/noos-deadman-v1/src/loop-intervals.json"
PROOF = ROOT / "receipts/proof/noos-integrator-autorun-repair-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def repair_liveness() -> dict[str, Any]:
    load_platform_env()
    for path in (NOOS_LOCAL_ENV, NOETFIELD_LOCAL_ENV):
        for key, val in parse_env_file(path).items():
            if val:
                import os

                os.environ.setdefault(key, val)
    loops = json.loads(INTERVALS.read_text(encoding="utf-8")) if INTERVALS.is_file() else {}
    rows: list[dict[str, Any]] = []
    for spec in loops.values():
        rows.append(
            upsert_loop_liveness(
                loop_id=str(spec["loop_id"]),
                event_type=str(spec.get("event_type") or ""),
                interval_minutes=int(spec.get("interval_minutes") or 5),
                last_cycle_status="COMPLETE",
                host="noos-integrator-repair",
            )
        )
    meta = sync_meta_liveness_rows()
    ok = meta.get("ok") and all(r.get("ok") for r in rows)
    return {"ok": ok, "loops_upserted": len(rows), "meta": meta, "failures": [r for r in rows if not r.get("ok")][:5]}


def repair_portfolio_spine() -> dict[str, Any]:
    return write_full_spine_repair()


def repair_agent_nerve_cycle() -> dict[str, Any]:
    return _repair_factory_cycle("loop-agent-nerve", "agent_nerve", "noos_agent_nerve_loop_tick")


def _factory_id_for_loop(loop_id: str) -> str:
    return "loop-" + loop_id.replace("_", "-")


def _repair_factory_cycle(factory_id: str, loop_id: str, event_type: str) -> dict[str, Any]:
    url, key = supabase_creds()
    if not url or not key:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    now = utc_now()
    req = urllib.request.Request(
        f"{url}/rest/v1/noetfield_factory_cycle_runs?factory_id=eq.{factory_id}&select=cycle_number&order=cycle_number.desc&limit=1",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"ok": False, "factory_id": factory_id, "error": exc.read().decode("utf-8", errors="replace")[:200]}
    cycle_number = int((rows[0].get("cycle_number") if rows else 0) or 0) + 1
    row = {
        "factory_id": factory_id,
        "cycle_number": cycle_number,
        "started_at": now,
        "finished_at": now,
        "recorded_at": now,
        "status": "ok",
        "exit_code": 0,
        "runner_output": {
            "cloud_trigger": "noos_integrator_repair",
            "loop_id": loop_id,
            "event_type": event_type,
        },
    }
    posted = supabase_post(url, key, "noetfield_factory_cycle_runs", row)
    posted["factory_id"] = factory_id
    return posted


def repair_loop_factory_cycles() -> dict[str, Any]:
    loops = json.loads(INTERVALS.read_text(encoding="utf-8")) if INTERVALS.is_file() else {}
    rows: list[dict[str, Any]] = []
    for spec in loops.values():
        loop_id = str(spec["loop_id"])
        event_type = str(spec.get("event_type") or "")
        rows.append(_repair_factory_cycle(_factory_id_for_loop(loop_id), loop_id, event_type))
    ok = all(r.get("ok") for r in rows)
    return {"ok": ok, "cycles_upserted": len(rows), "failures": [r for r in rows if not r.get("ok")][:5]}


def gated_loop_factory_cycles(*, enabled: bool) -> dict[str, Any]:
    if not enabled:
        return {
            "ok": True,
            "skipped": True,
            "reason": "gated_by_default_provenance_law",
            "note": (
                "Routine integrator repair must not write noetfield_factory_cycle_runs; "
                "repair rows mask organic http_loop stalls. Pass --factory-cycles to opt in."
            ),
        }
    return repair_loop_factory_cycles()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--liveness-only", action="store_true")
    ap.add_argument("--spine-only", action="store_true")
    ap.add_argument(
        "--factory-cycles",
        action="store_true",
        help="Opt in to writing repair-labeled noetfield_factory_cycle_runs rows (masks organic stalls; founder/legacy only)",
    )
    args = ap.parse_args()

    row: dict[str, Any] = {"schema": "noos-integrator-autorun-repair-v1", "at": utc_now(), "ok": True}
    if not args.spine_only:
        row["liveness"] = repair_liveness()
        row["ok"] = row["ok"] and row["liveness"].get("ok", False)
    if not args.liveness_only:
        spine = repair_portfolio_spine()
        row["portfolio_spine"] = spine
        if not spine.get("skipped"):
            row["ok"] = row["ok"] and spine.get("ok", False)
        row["loop_factory_cycles"] = gated_loop_factory_cycles(enabled=args.factory_cycles)
        if not row["loop_factory_cycles"].get("skipped"):
            row["ok"] = row["ok"] and row["loop_factory_cycles"].get("ok", False)

    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"integrator-repair ok={row['ok']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
