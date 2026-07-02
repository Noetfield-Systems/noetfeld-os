#!/usr/bin/env python3
"""A1 — verify native GitHub schedule proof for noos-factory-autorun.

Success (governed-autorun L4):
  >=2 consecutive schedule-event success runs on noos-factory-autorun.yml
  on consecutive */10 cron slots (~10m apart). Canary alone does not count.

Proof receipt: receipts/proof/noos-github-schedule-a1-v1.json
Runtime mirror (optional): .noos-runtime/factory/receipts/ (not cited as proof)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_proof_receipt_paths_v1 import proof_receipt  # noqa: E402

REPO = "kazemnezhadsina144-dot/noetfeld-os"
FACTORY_WORKFLOW = "noos-factory-autorun.yml"
CANARY_WORKFLOW = "noos-schedule-canary.yml"
PROOF_RECEIPT = proof_receipt("noos-github-schedule-a1-v1.json")
CRON_INTERVAL_SECONDS = 600
CONSECUTIVE_TOLERANCE_SECONDS = 120


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    text = str(ts).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def _github_token() -> str | None:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0:
        return None
    vals = dict(line.split("=", 1) for line in proc.stdout.splitlines() if "=" in line)
    return vals.get("password")


def _api(path: str, *, method: str = "GET", data: dict | None = None) -> tuple[int, Any]:
    token = _github_token()
    if not token:
        return 0, {"error": "github_token_not_configured"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            **({"Content-Type": "application/json"} if body else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"error": raw[:300]}


def schedule_runs(*, per_page: int = 30) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"event": "schedule", "per_page": str(per_page)})
    status, data = _api(f"/repos/{REPO}/actions/runs?{params}")
    if status != 200:
        return []
    return list(data.get("workflow_runs") or [])


def enable_workflow(workflow_file: str) -> dict[str, Any]:
    status, data = _api(f"/repos/{REPO}/actions/workflows/{workflow_file}/enable", method="PUT")
    return {"workflow": workflow_file, "status": status, "ok": status in (204, 200)}


def _run_row(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": r.get("id"),
        "name": r.get("name"),
        "workflow": (r.get("path") or "").split("/")[-1],
        "event": r.get("event"),
        "conclusion": r.get("conclusion"),
        "created_at": r.get("created_at"),
    }


def factory_schedule_successes(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = [
        _run_row(r)
        for r in runs
        if r.get("event") == "schedule"
        and r.get("conclusion") == "success"
        and (r.get("path") or "").endswith(FACTORY_WORKFLOW)
    ]
    out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return out


def consecutive_factory_pair(factory: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]] | None:
    if len(factory) < 2:
        return None
    newer, older = factory[0], factory[1]
    t_new = parse_iso(newer.get("created_at"))
    t_old = parse_iso(older.get("created_at"))
    if t_new is None or t_old is None:
        return None
    delta = (t_new - t_old).total_seconds()
    lo = CRON_INTERVAL_SECONDS - CONSECUTIVE_TOLERANCE_SECONDS
    hi = CRON_INTERVAL_SECONDS + CONSECUTIVE_TOLERANCE_SECONDS
    if lo <= delta <= hi:
        return newer, older
    return None


def verify() -> dict[str, Any]:
    runs = schedule_runs()
    factory = factory_schedule_successes(runs)
    pair = consecutive_factory_pair(factory)
    canary = [
        _run_row(r)
        for r in runs
        if r.get("event") == "schedule"
        and r.get("conclusion") == "success"
        and (r.get("path") or "").endswith(CANARY_WORKFLOW)
    ]
    ok = pair is not None
    result: dict[str, Any] = {
        "schema": "noos-github-schedule-a1-v1",
        "verified_at": utc_now(),
        "repo": REPO,
        "ok": ok,
        "a1_criterion": (
            f"2 consecutive schedule success runs on {FACTORY_WORKFLOW} "
            f"(~{CRON_INTERVAL_SECONDS}s apart); canary does not substitute"
        ),
        "factory_schedule_success_count": len(factory),
        "canary_schedule_success_count": len(canary),
        "factory_runs_success": factory[:5],
        "canary_runs_success": canary[:3],
        "blocker_reason": None if ok else "insufficient_consecutive_factory_schedule_runs",
        "ui_backup_note": (
            "Private repo: Settings → Actions → General → allow Actions + scheduled workflows. "
            "Native schedule is backup when CF repository_dispatch bridge is down."
        ),
    }
    if pair:
        newer, older = pair
        result["consecutive_factory_pair"] = {
            "newer_run_id": newer.get("id"),
            "older_run_id": older.get("id"),
            "newer_at": newer.get("created_at"),
            "older_at": older.get("created_at"),
            "delta_seconds": round(
                (parse_iso(newer.get("created_at")) - parse_iso(older.get("created_at"))).total_seconds(), 1
            ),
        }
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true", help="Write proof receipt to receipts/proof/")
    ap.add_argument("--enable-workflows", action="store_true", help="PUT enable on factory + canary workflows")
    ap.add_argument("--wait-minutes", type=float, default=0, help="Poll until consecutive pair or timeout")
    ap.add_argument("--poll-seconds", type=float, default=30)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    enable_results: list[dict[str, Any]] = []
    if args.enable_workflows:
        for wf in (FACTORY_WORKFLOW, CANARY_WORKFLOW):
            enable_results.append(enable_workflow(wf))

    deadline = time.time() + max(0.0, args.wait_minutes * 60)
    result = verify()
    while not result.get("ok") and args.wait_minutes > 0 and time.time() < deadline:
        time.sleep(max(5.0, args.poll_seconds))
        result = verify()
        result["wait_polled_until"] = utc_now()

    if enable_results:
        result["enable_results"] = enable_results

    if args.write_receipt:
        PROOF_RECEIPT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        result["receipt_path"] = str(PROOF_RECEIPT.relative_to(ROOT))
        result["receipt_tier"] = "proof"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        pair = result.get("consecutive_factory_pair") or {}
        print(
            f"a1_ok={result['ok']} factory_success={result['factory_schedule_success_count']} "
            f"pair={pair.get('newer_run_id')}/{pair.get('older_run_id')}"
        )

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
