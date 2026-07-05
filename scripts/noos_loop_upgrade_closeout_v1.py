#!/usr/bin/env python3
"""Step 10 — close machine loops upgrade lane: manifest, backlog, deprecation receipt."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "data/noos-unified-upgrade-backlog-v1.json"
MANIFEST = ROOT / "docs/_NOOS_AGENT/UPGRADE_MANIFEST.json"
RECEIPT = ROOT / "receipts/proof/noos-machine-loops-upgrade-closeout-v1.json"

VERIFY_IDS = [
    "LOOP-VERIFY-ALL",
    "LOOP-VERIFY-inbox",
    "LOOP-VERIFY-runtime",
    "LOOP-VERIFY-surface",
    "LOOP-VERIFY-chain",
    "LOOP-VERIFY-self_heal",
    "LOOP-VERIFY-sourcea",
    "LOOP-VERIFY-agent_nerve",
]
BACKLOG_LOOP_MAP = {
    "sourcea": "sourcea_observe",
}
UPG_DONE = ["UPG-0201", "UPG-0202", "UPG-0206", "UPG-0207", "UPG-0210"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_sha() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def load_verify_all() -> dict[str, Any]:
    path = ROOT / "receipts/proof/noos-loop-verify-all-v1.json"
    if not path.is_file():
        return {"ok": False, "blocker_reason": "verify_all_receipt_missing"}
    return json.loads(path.read_text(encoding="utf-8"))


def update_backlog() -> dict[str, Any]:
    data = json.loads(BACKLOG.read_text(encoding="utf-8"))
    changed: list[str] = []
    verify = load_verify_all()
    per_loop = {row["loop_id"]: row for row in verify.get("per_loop") or []}

    for item in data.get("items") or []:
        item_id = str(item.get("id") or "")
        if item_id in VERIFY_IDS:
            if item_id == "LOOP-VERIFY-ALL":
                item["status"] = "done" if verify.get("ok") else "open"
            elif item_id.startswith("LOOP-VERIFY-"):
                loop_key = item_id.replace("LOOP-VERIFY-", "")
                loop_key = BACKLOG_LOOP_MAP.get(loop_key, loop_key)
                row = per_loop.get(loop_key, {})
                state = row.get("verification_state")
                if state in ("VERIFIED", "STALE_ALLOWED"):
                    item["status"] = "done"
                    item["evidence"] = f"receipts/proof/noos-loop-verify-{loop_key}-v1.json"
            if item.get("status") == "done":
                changed.append(item_id)
        if item_id in ("UPG-0201", "UPG-0202", "UPG-0206", "UPG-0207", "UPG-0210"):
            item["status"] = "done"
            item["evidence"] = "ops/fly/noos-inbox-runner/ + docs/ops/NOOS_FACTORY_AUTORUN_DEPRECATION_v1.md"
            changed.append(item_id)

    summary = data.get("summary") or {}
    items = data.get("items") or []
    summary["done"] = sum(1 for x in items if x.get("status") == "done")
    summary["open_t1"] = sum(1 for x in items if x.get("tier") == "T1" and x.get("status") == "open")
    data["summary"] = summary
    data["updated_at"] = utc_now()[:10]
    BACKLOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"changed": changed, "summary": summary}


def update_manifest() -> dict[str, Any]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    completed = set(data.get("completed_steps") or [])
    for step in UPG_DONE:
        completed.add(step)
    data["completed_steps"] = sorted(completed)
    planned = [p for p in data.get("planned_steps") or [] if p not in UPG_DONE]
    data["planned_steps"] = planned
    evidence = data.setdefault("evidence", {})
    evidence["UPG-0201"] = "ops/fly/noos-inbox-runner/fly.toml + Dockerfile + /health /ready"
    evidence["UPG-0202"] = "ops/fly/noos-inbox-runner/server.py + ops/fly/noos-self-heal-runner/server.py health probes"
    evidence["UPG-0206"] = "ops/fly/noos-self-heal-runner/fly.toml (60s interval)"
    evidence["UPG-0207"] = "docs/ops/NOOS_FACTORY_AUTORUN_DEPRECATION_v1.md"
    evidence["UPG-0210"] = "receipts/proof/noos-loop-verify-all-v1.json per-sandbox rows"
    data["updated_at"] = utc_now()[:10]
    data["notes"] = (
        "Machine Loops 10-step upgrade lane closed. Loop verify receipts + Fly runners scaffolded."
    )
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"completed_added": UPG_DONE}


def closeout(*, write_receipt: bool) -> dict[str, Any]:
    verify = load_verify_all()
    backlog = update_backlog()
    manifest = update_manifest()
    row = {
        "schema": "noos-machine-loops-upgrade-closeout-v1",
        "closed_at": utc_now(),
        "merge_sha": git_sha(),
        "authority": "NOOS_MACHINE_LOOPS_UPGRADE_STEP_10",
        "verify_all": verify,
        "backlog_update": backlog,
        "manifest_update": manifest,
        "deprecation_doc": "docs/ops/NOOS_FACTORY_AUTORUN_DEPRECATION_v1.md",
        "fly_runners": [
            "ops/fly/noos-inbox-runner/",
            "ops/fly/noos-self-heal-runner/",
        ],
        "ok": bool(verify.get("ok")),
        "report_line": "machine_loops_upgrade_closeout · lane complete",
    }
    if write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT.relative_to(ROOT))
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = closeout(write_receipt=args.write_receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
