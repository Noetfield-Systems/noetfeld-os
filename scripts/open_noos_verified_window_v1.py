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
ENV_PATH = Path.home() / ".sourcea-secrets/noetfield.env"
sys.path.insert(0, str(ROOT / "scripts"))
from noos_proof_receipt_paths_v1 import proof_receipt  # noqa: E402

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
    vals: dict[str, str] = {}
    if ENV_PATH.is_file():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip().strip("'\"")
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
    PROOF_RECEIPT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    data["receipt_path"] = str(PROOF_RECEIPT.relative_to(ROOT))
    data["receipt_tier"] = "proof"
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--merge-sha", help="Merge commit SHA (default: HEAD)")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--align-criteria", action="store_true", help="Patch existing window receipt criteria + progress")
    ap.add_argument("--window-report", action="store_true", help="Print trigger_source counts for open window")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.align_criteria:
        row = align_existing_receipt()
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
        if args.window_report or args.align_criteria:
            print(f"rows={row.get('row_count', 0)} triggers={row.get('by_trigger_source', {})}")
        else:
            print(
                f"verified_window state={row['overall_state']} sha={row['merge_sha'][:8]} "
                f"closes={row['window_closes_at']} loops={row['loop_count']}"
            )
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
