#!/usr/bin/env python3
"""Phase B — dead-man switch: staleness math, restart cap, receipt builder."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data/noos-deadman-config-v1.json"
LOOPS = ROOT / "data/noos-24-7-loops-v1.json"
DISPATCH = ROOT / "data/noos-cf-dispatch-table-v1.json"
PROOF = ROOT / "receipts/proof"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def stale_minutes(last_fired_at: str | None, interval_minutes: int, *, multiplier: float = 2.0) -> float | None:
    ts = parse_ts(last_fired_at)
    if ts is None:
        return None
    age = (datetime.now(timezone.utc) - ts).total_seconds() / 60.0
    return age - (interval_minutes * multiplier)


def is_stale(last_fired_at: str | None, interval_minutes: int, *, multiplier: float = 2.0) -> bool:
    delta = stale_minutes(last_fired_at, interval_minutes, multiplier=multiplier)
    if delta is None:
        return True
    return delta > 0


def loop_intervals() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    loops_doc = load_json(LOOPS)
    for loop in loops_doc.get("loops") or []:
        lid = str(loop.get("id"))
        rows[lid] = {
            "loop_id": lid,
            "event_type": loop.get("event_type"),
            "interval_minutes": int(loop.get("interval_minutes") or 5),
        }
    dispatch_doc = load_json(DISPATCH)
    for target in dispatch_doc.get("targets") or []:
        if target.get("handler") == "factory":
            rows["factory_autorun"] = {
                "loop_id": "factory_autorun",
                "event_type": target.get("event_type"),
                "interval_minutes": int(target.get("interval_minutes") or 10),
            }
    return rows


def evaluate_stale(
    registry_rows: list[dict[str, Any]],
    *,
    intervals: dict[str, dict[str, Any]] | None = None,
    multiplier: float = 2.0,
) -> list[dict[str, Any]]:
    intervals = intervals or loop_intervals()
    stale: list[dict[str, Any]] = []
    seen = set()
    for row in registry_rows:
        lid = str(row.get("loop_id"))
        seen.add(lid)
        spec = intervals.get(lid, {})
        interval = int(row.get("interval_minutes") or spec.get("interval_minutes") or 5)
        last = row.get("last_fired_at")
        if is_stale(last, interval, multiplier=multiplier):
            stale.append(
                {
                    "loop_id": lid,
                    "event_type": row.get("event_type") or spec.get("event_type"),
                    "interval_minutes": interval,
                    "last_fired_at": last,
                    "stale_by_minutes": stale_minutes(last, interval, multiplier=multiplier),
                }
            )
    for lid, spec in intervals.items():
        if lid in seen:
            continue
        stale.append(
            {
                "loop_id": lid,
                "event_type": spec.get("event_type"),
                "interval_minutes": spec.get("interval_minutes"),
                "last_fired_at": None,
                "stale_by_minutes": None,
                "reason": "never_fired",
            }
        )
    return stale


def cap_restart_attempts(
    stale_loops: list[dict[str, Any]], *, max_attempts: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for row in stale_loops:
        if len(attempts) >= max_attempts:
            skipped.append({**row, "restart_skipped": True, "reason": "restart_attempts_max"})
            continue
        attempts.append({**row, "restart_attempt": True})
    return attempts, skipped


def _supabase_creds() -> tuple[str, str] | None:
    url = (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or "").strip()
    key = (
        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    if url and key:
        return url.rstrip("/"), key
    return None


def fetch_registry_rows() -> list[dict[str, Any]]:
    creds = _supabase_creds()
    if not creds:
        return []
    base, key = creds
    req = urllib.request.Request(
        f"{base}/rest/v1/noos_loop_registry?select=*",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def sink_deadman_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    creds = _supabase_creds()
    run_id = receipt.get("run_id") or str(uuid.uuid4())
    receipt["run_id"] = run_id
    if not creds:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured", "run_id": run_id}
    base, key = creds
    req = urllib.request.Request(
        f"{base}/rest/v1/noos_deadman_runs",
        data=json.dumps({"run_id": run_id, "receipt": receipt}).encode("utf-8"),
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": 200 <= resp.status < 300, "run_id": run_id}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "run_id": run_id, "error": f"http_{exc.code}"}


def write_local_receipt(receipt: dict[str, Any]) -> Path:
    PROOF.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = PROOF / f"noos-deadman-{stamp}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return path


def build_receipt(
    *,
    stale_loops: list[dict[str, Any]],
    restart_attempts: list[dict[str, Any]],
    alert_sent: bool,
    source: str = "local",
) -> dict[str, Any]:
    return {
        "schema": "noos-deadman-run-v1",
        "run_at": utc_now(),
        "source": source,
        "stale_count": len(stale_loops),
        "stale_loops": stale_loops,
        "restart_attempts": restart_attempts,
        "restart_attempt_count": len(restart_attempts),
        "alert_sent": alert_sent,
        "ok": True,
    }


# Probe authority modes. OBSERVE_ONLY performs NO INSERT/UPDATE/DELETE/RPC or
# diagnostic sink write; DIAGNOSTIC_CANARY_WRITE is explicitly authorized to
# INSERT into the approved terminal diagnostic sink only. Neither mode can
# alter execution, dispatch, reconcile or recovery state — the sink table
# (noos_deadman_runs) is a terminal append-only audit log read by none of
# those decision paths.
MODE_OBSERVE_ONLY = "OBSERVE_ONLY"
MODE_DIAGNOSTIC_CANARY_WRITE = "DIAGNOSTIC_CANARY_WRITE"

CANARY_SINK_DISCLOSURE = {
    "sink_table": "noos_deadman_runs",
    "write_kind": "INSERT (append-only; POST, Prefer: return=minimal; new run_id per call)",
    "persistence": "indefinite — no TTL/expiry in the write path",
    "automatic_cleanup": "none (retention/dead-letter proposal tracked separately)",
    "affects_operational_state": False,
    "operational_state_note": "terminal audit sink; not read by liveness eval, dispatch, reconcile, or recovery",
}


def run_check(*, source: str = "local", mode: str = MODE_OBSERVE_ONLY) -> dict[str, Any]:
    cfg = load_json(CONFIG)
    multiplier = float((cfg.get("interval_multipliers") or {}).get("default") or 2)
    max_attempts = int(cfg.get("restart_attempts_max") or 1)
    registry = fetch_registry_rows()
    stale = evaluate_stale(registry, multiplier=multiplier)
    attempts, skipped = cap_restart_attempts(stale, max_attempts=max_attempts)
    receipt = build_receipt(
        stale_loops=stale,
        restart_attempts=attempts,
        alert_sent=False,
        source=source,
    )
    if skipped:
        receipt["restart_skipped"] = skipped
    receipt["probe_mode"] = mode
    if mode == MODE_DIAGNOSTIC_CANARY_WRITE:
        sink = sink_deadman_receipt(receipt)
        sink["disclosure"] = CANARY_SINK_DISCLOSURE
        receipt["supabase_sink"] = sink
    else:
        # OBSERVE_ONLY: no mutation of any kind, including the diagnostic sink.
        receipt["supabase_sink"] = {
            "ok": True,
            "skipped": True,
            "reason": "observe_only_mode",
            "write_performed": False,
            "run_id": receipt.get("run_id"),
        }
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--mode",
        choices=[MODE_OBSERVE_ONLY, MODE_DIAGNOSTIC_CANARY_WRITE],
        default=MODE_OBSERVE_ONLY,
        help="OBSERVE_ONLY performs no writes (default). DIAGNOSTIC_CANARY_WRITE "
        "inserts one disclosed row into the terminal diagnostic sink.",
    )
    ap.add_argument(
        "--canary",
        dest="mode",
        action="store_const",
        const=MODE_DIAGNOSTIC_CANARY_WRITE,
        help="Alias for --mode DIAGNOSTIC_CANARY_WRITE (an authorized write).",
    )
    args = ap.parse_args()
    receipt = run_check(source="cli", mode=args.mode)
    if args.write_receipt:
        path = write_local_receipt(receipt)
        receipt["receipt_path"] = str(path.relative_to(ROOT))
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        wrote = receipt.get("supabase_sink", {}).get("write_performed", True)
        print(
            f"deadman mode={receipt.get('probe_mode')} stale={receipt['stale_count']} "
            f"restarts={receipt['restart_attempt_count']} sink_write={wrote}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
