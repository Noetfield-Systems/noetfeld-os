#!/usr/bin/env python3
"""Read-only status for 10 upgrade planes (NOOS-AGENT-20260702-028)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from noos_proof_receipt_paths_v1 import proof_receipt  # noqa: E402

PLANES_PATH = ROOT / "data/noos-upgrade-planes-v1.json"
BACKLOG_PATH = ROOT / "data/noos-unified-upgrade-backlog-v1.json"
PROOF = proof_receipt("noos-planes-status-v1.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def first_open_step(steps: list[dict]) -> dict | None:
    for s in steps:
        if s.get("status") not in ("done",):
            return s
    return None


def collect_backlog_ids(planes_doc: dict) -> set[str]:
    ids: set[str] = set()
    for p in planes_doc.get("planes", []):
        ids.update(p.get("backlog_ids", []))
        for s in p.get("steps", []):
            ids.update(s.get("backlog_ids", []))
    return ids


def build_status(planes_doc: dict, backlog_doc: dict | None) -> dict:
    planes_out = []
    total_done = 0
    total_steps = 0

    for p in planes_doc.get("planes", []):
        steps = p.get("steps", [])
        done = sum(1 for s in steps if s.get("status") == "done")
        open_s = first_open_step(steps)
        total_done += done
        total_steps += len(steps)
        planes_out.append(
            {
                "id": p["id"],
                "name": p["name"],
                "tier": p.get("tier"),
                "current_step": p.get("current_step"),
                "progress": f"{done}/{len(steps)}",
                "next_step": open_s,
                "verify_cmd": p.get("verify_cmd"),
                "depends_on": p.get("depends_on", []),
            }
        )

    orphan_warnings: list[str] = []
    if backlog_doc:
        backlog_ids = {item["id"] for item in backlog_doc.get("items", [])}
        plane_refs = collect_backlog_ids(planes_doc)
        # COM / founder items intentionally excluded from planes
        machine_tracks = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "GOV"}
        machine_backlog = {
            i["id"]
            for i in backlog_doc.get("items", [])
            if i.get("track") in machine_tracks and i.get("status") in ("open", "done", "deferred", "blocked", "in_progress")
        }
        unmapped = sorted(machine_backlog - plane_refs)
        if unmapped:
            orphan_warnings = unmapped

    return {
        "schema": "noos-planes-status-v1",
        "checked_at": utc_now(),
        "authority": planes_doc.get("authority"),
        "summary": {
            "planes": len(planes_out),
            "steps_total": total_steps,
            "steps_done": total_done,
            "steps_open": total_steps - total_done,
        },
        "execution_order": planes_doc.get("execution_order", []),
        "planes": planes_out,
        "orphan_backlog_ids": orphan_warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="10 upgrade planes status")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--write-receipt", action="store_true", help="Write proof receipt")
    args = parser.parse_args()

    planes_doc = json.loads(PLANES_PATH.read_text())
    backlog_doc = json.loads(BACKLOG_PATH.read_text()) if BACKLOG_PATH.exists() else None
    status = build_status(planes_doc, backlog_doc)

    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(status, indent=2) + "\n")
        status["receipt_path"] = str(PROOF.relative_to(ROOT))
        status["receipt_tier"] = "proof"

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        for p in status["planes"]:
            nxt = p.get("next_step") or {}
            nxt_id = nxt.get("id", "—")
            nxt_status = nxt.get("status", "complete")
            print(f"{p['id']:4} {p['progress']:5} tier={p['tier']} next={nxt_id} ({nxt_status})")
        print(f"summary: {status['summary']}")
        if status.get("orphan_backlog_ids"):
            print("orphan_backlog_ids:", status["orphan_backlog_ids"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
