#!/usr/bin/env python3
"""NOOS control layer — read-only observe of TrustField trustfield_loop_registry (W3/W5/W10)."""

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
from noos_vault_paths_v1 import (  # noqa: E402
    LEGACY_SOURCEA_NOETFIELD_ENV,
    NOETFIELD_LOCAL_ENV,
    load_platform_env,
    parse_env_file,
)

TABLE = "trustfield_loop_registry"
EXPECTED_REF = "tkgpapowwplupyekpivy"
PROBE_LOOP_ID = "tf_w3_supabase_sink_probe_v1"
DEADMAN_LOOP_ID = "tf_cf_deadman_v1"
GATE_48H_LOOP_ID = "tf_cf_48h_gate_v1"

# Mirrors tf-cf-deadman-v1 WATCH_LOOP_IDS (W2 cron motors).
DEADMAN_WATCH_IDS = frozenset(
    {
        "tf_cf_fleet_tick_v1",
        "tf_cf_lane_self_heal_v1",
        "tf_cf_lane_critic_circle_v1",
        "tf_cf_lane_deep_research_v1",
        "tf_cf_lane_plan_matrix_v1",
        "tf_cf_lane_www_upgrade_queue_v1",
        "tf_cf_lane_autorun_stack_v1",
    }
)

# Loop-specific stale overrides (minutes). Default uses deadman 2x interval_seconds.
LOOP_STALE_MINUTES: dict[str, float] = {
    PROBE_LOOP_ID: 60 * 24 * 7,  # on_verify — weekly warn threshold
    GATE_48H_LOOP_ID: 60 * 72,  # W10 laptop-closed gate — 72h warn, not 2h
}

PROOF = ROOT / "receipts/proof/noos-trustfield-loop-registry-observe-v1.json"
RUNTIME = ROOT / ".noos-runtime/observe/trustfield"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def noetfield_supabase_cfg() -> tuple[str, str] | None:
    merged: dict[str, str] = {}
    for path in (NOETFIELD_LOCAL_ENV, LEGACY_SOURCEA_NOETFIELD_ENV):
        merged.update(parse_env_file(path))
    merged.update(load_platform_env())
    for key in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_PROJECT_ID"):
        env_key = f"NOETFIELD_{key}"
        if os.environ.get(env_key):
            merged[key] = os.environ[env_key]
    url = str(merged.get("SUPABASE_URL") or "").rstrip("/")
    key = str(merged.get("SUPABASE_SERVICE_ROLE_KEY") or "")
    ref = str(merged.get("SUPABASE_PROJECT_ID") or "")
    if not url or not key:
        return None
    if ref and ref != EXPECTED_REF and EXPECTED_REF not in url:
        return None
    return url, key


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts
    except ValueError:
        return None


def fetch_registry_rows() -> dict:
    cfg = noetfield_supabase_cfg()
    if not cfg:
        return {"ok": False, "skipped": True, "reason": "noetfield_supabase_not_configured", "rows": []}
    url, key = cfg
    params = urllib.parse.urlencode(
        {
            "select": "loop_id,name,host,interval_seconds,last_fired_at,last_ok,last_receipt_id,value_class",
            "order": "last_fired_at.desc.nullslast",
        }
    )
    req = urllib.request.Request(
        f"{url}/rest/v1/{TABLE}?{params}",
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "row_count": len(rows), "rows": rows}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": exc.read().decode()[:400], "rows": []}


def stale_threshold_minutes(row: dict) -> float:
    loop_id = str(row.get("loop_id") or "")
    if loop_id in LOOP_STALE_MINUTES:
        return LOOP_STALE_MINUTES[loop_id]
    interval = row.get("interval_seconds")
    try:
        sec = float(interval) if interval is not None else 300.0
    except (TypeError, ValueError):
        sec = 300.0
    return (sec * 2.0) / 60.0


def classify_row(row: dict, *, now: datetime) -> dict:
    loop_id = str(row.get("loop_id") or "")
    fired = parse_ts(row.get("last_fired_at"))
    last_ok = row.get("last_ok")
    threshold_min = stale_threshold_minutes(row)
    age_min: float | None = None
    if fired:
        age_min = (now - fired).total_seconds() / 60.0

    if last_ok is False:
        status = "red"
        reason = "last_ok=false"
    elif not fired:
        status = "red"
        reason = "missing_last_fired_at"
    elif age_min is not None and age_min > threshold_min:
        status = "yellow" if loop_id == GATE_48H_LOOP_ID and age_min <= threshold_min * 1.5 else "red"
        reason = f"stale age_min={age_min:.1f} threshold_min={threshold_min:.1f}"
    elif age_min is not None and age_min > threshold_min * 0.75:
        status = "yellow"
        reason = f"aging age_min={age_min:.1f} threshold_min={threshold_min:.1f}"
    else:
        status = "green"
        reason = "fresh"

    return {
        "loop_id": loop_id,
        "name": row.get("name"),
        "host": row.get("host"),
        "value_class": row.get("value_class"),
        "last_ok": last_ok,
        "last_fired_at": row.get("last_fired_at"),
        "interval_seconds": row.get("interval_seconds"),
        "age_minutes": round(age_min, 2) if age_min is not None else None,
        "stale_threshold_minutes": round(threshold_min, 2),
        "deadman_watched": loop_id in DEADMAN_WATCH_IDS or loop_id == DEADMAN_LOOP_ID,
        "status": status,
        "reason": reason,
    }


def observe() -> dict:
    now = datetime.now(timezone.utc)
    fetch = fetch_registry_rows()
    rows = fetch.get("rows") or []
    classified = [classify_row(r, now=now) for r in rows]

    by_status = {"green": [], "yellow": [], "red": []}
    for row in classified:
        by_status.setdefault(str(row["status"]), []).append(row["loop_id"])

    probe = next((r for r in classified if r["loop_id"] == PROBE_LOOP_ID), None)
    deadman = next((r for r in classified if r["loop_id"] == DEADMAN_LOOP_ID), None)
    gate48 = next((r for r in classified if r["loop_id"] == GATE_48H_LOOP_ID), None)
    deadman_stale = [r for r in classified if r["deadman_watched"] and r["status"] == "red"]

    fails: list[str] = []
    if not fetch.get("ok"):
        if not fetch.get("skipped"):
            fails.append(f"registry read failed: {fetch.get('error', fetch.get('reason'))}")
    if not probe:
        fails.append(f"missing probe row {PROBE_LOOP_ID}")
    elif probe["status"] == "red":
        fails.append(f"probe row red: {probe['reason']}")
    if deadman and deadman["status"] == "red":
        fails.append(f"deadman row red: {deadman['reason']}")
    for sid in deadman_stale:
        fails.append(f"deadman-watched motor red: {sid['loop_id']} ({sid['reason']})")

    repair_commands = []
    if not probe:
        repair_commands.append(
            "TrustField worker: cd TrustField-Technologies && ./scripts/verify_tf_supabase_receipt_sink.sh"
        )
    repair_commands.append(
        "TrustField worker: cd TrustField-Technologies && ./scripts/verify_tf_loop_registry_liveness.sh"
    )
    repair_commands.append(
        "TrustField worker: cd TrustField-Technologies && ./scripts/verify_cf_deadman_v1.sh"
    )

    overall = "green"
    if fails:
        overall = "red" if any("deadman" in f or "last_ok=false" in f for f in fails) else "yellow"
    elif by_status.get("red"):
        overall = "yellow"

    return {
        "schema": "noos-trustfield-loop-registry-observe-v1.1",
        "at": utc_now(),
        "read_only": True,
        "one_law": "NOOS observes TrustField registry; TrustField worker owns writes and probe seed.",
        "plane": "TrustField-Technologies",
        "table": TABLE,
        "supabase_project_ref": EXPECTED_REF,
        "registry_read_ok": bool(fetch.get("ok")),
        "row_count": len(rows),
        "overall_status": overall,
        "summary": {
            "green": len(by_status["green"]),
            "yellow": len(by_status["yellow"]),
            "red": len(by_status["red"]),
            "last_ok_false": sum(1 for r in classified if r.get("last_ok") is False),
            "missing_last_fired_at": sum(1 for r in classified if not r.get("last_fired_at")),
            "probe_present": probe is not None,
            "deadman_status": deadman["status"] if deadman else "missing",
            "gate_48h_status": gate48["status"] if gate48 else "missing",
            "deadman_watched_red": [r["loop_id"] for r in deadman_stale],
        },
        "gates": {
            "w3_probe": {
                "loop_id": PROBE_LOOP_ID,
                "present": probe is not None,
                "row": probe,
                "closure": "TF_LOOP_REGISTRY_LIVENESS: pass"
                if probe and probe["status"] != "red"
                else "TF_LOOP_REGISTRY_LIVENESS: fail",
            },
            "w5_deadman": {
                "loop_id": DEADMAN_LOOP_ID,
                "row": deadman,
                "watched_motors_red": [r["loop_id"] for r in deadman_stale],
            },
            "w10_48h_gate": {
                "loop_id": GATE_48H_LOOP_ID,
                "row": gate48,
                "note": "W10 uses 72h stale warn — 2.5h age is green under W10 SLO.",
            },
        },
        "rows": classified,
        "fails": fails,
        "repair_commands": repair_commands,
        "closure_token": f"NOOS_TF_LOOP_REGISTRY_OBSERVE: {overall}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    row = observe()
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        RUNTIME.mkdir(parents=True, exist_ok=True)
        (RUNTIME / "loop-registry-observe-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        s = row.get("summary") or {}
        print(
            f"tf_loop_registry observe overall={row.get('overall_status')} "
            f"rows={row.get('row_count')} green={s.get('green')} yellow={s.get('yellow')} red={s.get('red')} "
            f"probe={s.get('probe_present')} fails={len(row.get('fails') or [])}"
        )
        print(row.get("closure_token"))

    if row.get("registry_read_ok") is False and row.get("fails"):
        return 1 if not any("not_configured" in str(f) for f in row["fails"]) else 0
    return 0 if row.get("overall_status") == "green" else 1


if __name__ == "__main__":
    raise SystemExit(main())
