#!/usr/bin/env python3
"""DECLARED→VERIFIED 24h window for NOOS loops.

Proof receipt: receipts/proof/noos-loop-verified-window-v1.json

Valid autonomous triggers (primary motor = CF repository_dispatch):
  - schedule
  - repository_dispatch where client_payload.source in (cf-cron, cloudflare_cron)

Invalid: workflow_dispatch, manual local runs.
make schedule-verify = native-cron diagnostic only; does NOT gate window close.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/noos-24-7-loops-v1.json"
sys.path.insert(0, str(ROOT / "scripts"))
from noos_proof_receipt_paths_v1 import proof_receipt  # noqa: E402
from noos_vault_paths_v1 import load_platform_env  # noqa: E402

PROOF_RECEIPT = proof_receipt("noos-loop-verified-window-v1.json")
WINDOW_HOURS = 24

VALID_DISPATCH_SOURCES = frozenset({"cf-cron", "cloudflare_cron"})
VALID_TRIGGERS = frozenset({"schedule", "repository_dispatch"})
INVALID_TRIGGERS = frozenset({"workflow_dispatch", "manual"})


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def git_sha() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def close_criteria() -> dict[str, Any]:
    return {
        "per_loop": "24h autonomous cycles + sink invariant PASS",
        "valid_triggers": sorted(VALID_TRIGGERS),
        "repository_dispatch_requires": {
            "client_payload.source": sorted(VALID_DISPATCH_SOURCES),
            "note": "cf-cron is canonical; cloudflare_cron accepted for legacy rows",
        },
        "invalid_triggers": sorted(INVALID_TRIGGERS),
        "zero_manual": True,
        "schedule_verify_role": "native_cron_diagnostic_only",
        "schedule_verify_gates_window": False,
        "primary_motor": "cf-cron → repository_dispatch",
    }


def open_window(*, merge_sha: str | None = None) -> dict[str, Any]:
    sha = merge_sha or git_sha()
    started = utc_now()
    closes = started + timedelta(hours=WINDOW_HOURS)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    loops = [
        {
            "loop_id": str(loop["id"]),
            "github_workflow": loop.get("github_workflow"),
            "interval_minutes": loop.get("interval_minutes"),
            "verification_state": "DECLARED",
            "verified_at": None,
        }
        for loop in registry.get("loops") or []
    ]
    return {
        "schema": "noos-loop-verified-window-v1",
        "merge_sha": sha,
        "window_hours": WINDOW_HOURS,
        "window_started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_closes_at": closes.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "overall_state": "DECLARED",
        "law": (
            "Primary motor = CF repository_dispatch. schedule = backup. "
            "Manual/workflow_dispatch green ≠ autonomous green (L4)."
        ),
        "founder_blocked_note": "NOOS-C-01 remains founder_blocked; does not block window.",
        "loops": loops,
        "loop_count": len(loops),
        "close_criteria": close_criteria(),
    }


def load_env() -> dict[str, str]:
    vals = load_platform_env()
    for key in ("NOETFIELD_SUPABASE_URL", "SUPABASE_URL", "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_ROLE_KEY"):
        if os.environ.get(key):
            vals[key] = os.environ[key].strip()
    return vals


def supabase_cfg() -> tuple[str, str] | None:
    vals = load_env()
    url = vals.get("NOETFIELD_SUPABASE_URL") or vals.get("SUPABASE_URL")
    key = vals.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or vals.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return url.rstrip("/"), key
    return None


def _trigger_from_row(row: dict[str, Any]) -> str:
    ro = row.get("runner_output") or {}
    if isinstance(ro, str):
        try:
            ro = json.loads(ro)
        except json.JSONDecodeError:
            ro = {}
    meta = ro.get("cloud_meta") or {}
    event = meta.get("github_event") or ro.get("cloud_trigger") or "unknown"
    source = meta.get("dispatch_source") or meta.get("client_payload_source") or ""
    if event == "repository_dispatch" and source in VALID_DISPATCH_SOURCES:
        return f"repository_dispatch:{source}"
    if event in VALID_TRIGGERS:
        return event
    if event in INVALID_TRIGGERS:
        return event
    return str(event)


def fetch_cycle_rows(*, window_started_at: str, factory_id: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    cfg = supabase_cfg()
    if not cfg:
        return {"ok": False, "blocker_reason": "supabase_not_configured"}
    base, key = cfg
    query: dict[str, str] = {
        "select": "factory_id,status,exit_code,recorded_at,runner_output",
        "recorded_at": f"gte.{window_started_at}",
        "order": "recorded_at.desc",
        "limit": "500",
    }
    if factory_id:
        query["factory_id"] = f"eq.{factory_id}"
    params = urllib.parse.urlencode(query)
    req = urllib.request.Request(
        f"{base}/rest/v1/noetfield_factory_cycle_runs?{params}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": exc.read().decode("utf-8", errors="replace")[:300]}


def loop_factory_map() -> dict[str, str]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {str(loop["id"]): str(loop.get("factory_id") or f"loop-{loop['id']}") for loop in registry.get("loops") or []}


def evaluate_loop(*, loop_id: str, rows: list[dict[str, Any]], min_cycles: int = 2) -> dict[str, Any]:
    factory_id = loop_factory_map().get(loop_id, f"loop-{loop_id}")
    loop_rows = [r for r in rows if str(r.get("factory_id")) == factory_id]
    invalid = 0
    for row in loop_rows:
        trig = _trigger_from_row(row)
        event = trig.split(":")[0]
        if event in INVALID_TRIGGERS:
            invalid += 1
        elif event == "repository_dispatch" and ":" in trig:
            source = trig.split(":", 1)[1]
            if source not in VALID_DISPATCH_SOURCES:
                invalid += 1
    latest = loop_rows[0] if loop_rows else None
    sink_ok = bool(latest) and str(latest.get("status") or "") in ("ok", "degraded")
    ready = len(loop_rows) >= min_cycles and invalid == 0 and sink_ok
    blockers: list[str] = []
    if len(loop_rows) < min_cycles:
        blockers.append(f"insufficient_cycles:{len(loop_rows)}<{min_cycles}")
    if invalid:
        blockers.append(f"invalid_triggers:{invalid}")
    if not sink_ok:
        blockers.append("latest_sink_not_ok")
    return {
        "loop_id": loop_id,
        "factory_id": factory_id,
        "cycle_count": len(loop_rows),
        "invalid_trigger_count": invalid,
        "latest_status": latest.get("status") if latest else None,
        "ready": ready,
        "blockers": blockers,
    }


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def close_window(*, force: bool = False) -> dict[str, Any]:
    if not PROOF_RECEIPT.is_file():
        return {"ok": False, "blocker_reason": "window_receipt_missing"}
    data = json.loads(PROOF_RECEIPT.read_text(encoding="utf-8"))
    started_at = data["window_started_at"]
    closes_at = data["window_closes_at"]
    now = utc_now()
    window_elapsed = now >= parse_ts(closes_at)
    if not window_elapsed and not force:
        data["window_progress"] = window_report(window_started_at=started_at)
        data["loop_evaluations"] = []
        data["close_blocker"] = "window_not_elapsed"
        data["evaluated_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        PROOF_RECEIPT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return {"ok": False, "blocker_reason": "window_not_elapsed", "window_closes_at": closes_at}

    rows = fetch_cycle_rows(window_started_at=started_at)
    if isinstance(rows, dict) and not rows.get("ok", True):
        return rows

    evaluations = [evaluate_loop(loop_id=str(loop["loop_id"]), rows=rows) for loop in data.get("loops") or []]
    verified_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    all_ready = all(ev["ready"] for ev in evaluations)
    for loop_entry, ev in zip(data.get("loops") or [], evaluations, strict=False):
        if ev["ready"] and (window_elapsed or force):
            loop_entry["verification_state"] = "VERIFIED"
            loop_entry["verified_at"] = verified_at
        loop_entry["evaluation"] = ev

    data["loop_evaluations"] = evaluations
    data["window_progress"] = window_report(window_started_at=started_at)
    data["evaluated_at"] = verified_at
    data.pop("close_blocker", None)
    if all_ready and (window_elapsed or force):
        data["overall_state"] = "VERIFIED"
        data["verified_at"] = verified_at
        close_proof = proof_receipt("noos-loop-verified-window-close-v1.json")
        close_row = {
            "schema": "noos-loop-verified-window-close-v1",
            "closed_at": verified_at,
            "overall_state": "VERIFIED",
            "loops_verified": sum(1 for loop in data.get("loops") or [] if loop.get("verification_state") == "VERIFIED"),
            "loop_count": data.get("loop_count"),
            "window_started_at": started_at,
            "window_closes_at": closes_at,
        }
        close_proof.write_text(json.dumps(close_row, indent=2) + "\n", encoding="utf-8")
        data["close_receipt_path"] = str(close_proof.relative_to(ROOT))
    else:
        data["overall_state"] = "DECLARED"
        data["close_blocker"] = "loops_not_ready" if not all_ready else "window_not_elapsed"

    PROOF_RECEIPT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    data["receipt_path"] = str(PROOF_RECEIPT.relative_to(ROOT))
    data["receipt_tier"] = "proof"
    data["ok"] = data["overall_state"] == "VERIFIED"
    return data


def window_report(*, window_started_at: str) -> dict[str, Any]:
    cfg = supabase_cfg()
    if not cfg:
        return {"ok": False, "blocker_reason": "supabase_not_configured"}
    base, key = cfg
    params = urllib.parse.urlencode(
        {
            "select": "factory_id,status,exit_code,recorded_at,runner_output",
            "recorded_at": f"gte.{window_started_at}",
            "order": "recorded_at.desc",
            "limit": "500",
        }
    )
    req = urllib.request.Request(
        f"{base}/rest/v1/noetfield_factory_cycle_runs?{params}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": exc.read().decode("utf-8", errors="replace")[:300]}

    by_trigger: Counter[str] = Counter()
    by_factory: Counter[str] = Counter()
    autonomous = 0
    invalid = 0
    for row in rows:
        trig = _trigger_from_row(row)
        by_trigger[trig] += 1
        by_factory[str(row.get("factory_id") or "unknown")] += 1
        event = trig.split(":")[0]
        if event == "schedule":
            autonomous += 1
        elif event == "repository_dispatch":
            if ":" in trig:
                source = trig.split(":", 1)[1]
                if source in VALID_DISPATCH_SOURCES:
                    autonomous += 1
                else:
                    invalid += 1
            else:
                autonomous += 1
        elif event in INVALID_TRIGGERS:
            invalid += 1

    return {
        "ok": True,
        "window_started_at": window_started_at,
        "reported_at": utc_now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "row_count": len(rows),
        "by_trigger_source": dict(sorted(by_trigger.items())),
        "by_factory_id": dict(sorted(by_factory.items())),
        "autonomous_row_count": autonomous,
        "invalid_or_unknown_trigger_count": invalid,
    }


def align_existing_receipt() -> dict[str, Any]:
    if not PROOF_RECEIPT.is_file():
        return {"ok": False, "blocker_reason": "window_receipt_missing"}
    data = json.loads(PROOF_RECEIPT.read_text(encoding="utf-8"))
    data["law"] = (
        "Primary motor = CF repository_dispatch. schedule = backup. "
        "Manual/workflow_dispatch green ≠ autonomous green (L4)."
    )
    data["close_criteria"] = close_criteria()
    data["criteria_aligned_at"] = utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")
    report = window_report(window_started_at=data["window_started_at"])
    data["window_progress"] = report
    closes_at = data.get("window_closes_at", "")
    data["passive_observation"] = {
        "observed_at": utc_now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_elapsed": bool(closes_at) and utc_now() >= parse_ts(closes_at),
        "note": "Passive autonomous run until window_closes_at; no polling",
    }
    PROOF_RECEIPT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    data["receipt_path"] = str(PROOF_RECEIPT.relative_to(ROOT))
    data["receipt_tier"] = "proof"
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--merge-sha", help="Merge commit SHA (default: HEAD)")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--align-criteria", action="store_true", help="Patch existing window receipt criteria + progress")
    ap.add_argument("--close-window", action="store_true", help="Evaluate loops; VERIFIED when window elapsed + gates pass")
    ap.add_argument("--window-report", action="store_true", help="Print trigger_source counts for open window")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.align_criteria:
        row = align_existing_receipt()
    elif args.close_window:
        row = close_window()
    elif args.window_report:
        if not PROOF_RECEIPT.is_file():
            print(json.dumps({"ok": False, "blocker_reason": "window_receipt_missing"}))
            return 1
        started = json.loads(PROOF_RECEIPT.read_text(encoding="utf-8")).get("window_started_at", "")
        row = window_report(window_started_at=started)
    else:
        row = open_window(merge_sha=args.merge_sha)
        if args.write_receipt:
            PROOF_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            row["receipt_path"] = str(PROOF_RECEIPT.relative_to(ROOT))
            row["receipt_tier"] = "proof"

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        if args.window_report or args.align_criteria or args.close_window:
            print(f"rows={row.get('row_count', 0)} triggers={row.get('by_trigger_source', {})}")
        else:
            print(
                f"verified_window state={row['overall_state']} sha={row['merge_sha'][:8]} "
                f"closes={row['window_closes_at']} loops={row['loop_count']}"
            )
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
