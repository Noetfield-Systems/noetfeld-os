#!/usr/bin/env python3
"""Nightly Kaizen — one highest-ROI machine_safe queue item: fix → verify → receipt, rollback on regression."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from nf_improvement_queue_client import (  # noqa: E402
    fetch_open_machine_safe,
    insert_probe_receipt,
    patch_row,
)

PLATFORM_BASE = "https://platform.noetfield.com"

# check_id or metadata.kaizen_recipe → bounded fix/verify commands
KAIZEN_RECIPES: dict[str, dict[str, list[list[str]]]] = {
    "greeting_coupling": {
        "fix": [["python3", "scripts/sync_chat_greeting_asset.py"]],
        "verify": [
            ["python3", "scripts/verify_chat_greeting_coupling.py"],
            [
                "python3",
                "scripts/verify_chat_greeting_coupling.py",
                "--live",
                "--platform-base",
                PLATFORM_BASE,
            ],
        ],
    },
    "drift_alignment": {
        "fix": [["python3", "scripts/sync_chat_greeting_asset.py"]],
        "verify": [
            [
                "python3",
                "scripts/verify_chat_greeting_coupling.py",
                "--live",
                "--platform-base",
                PLATFORM_BASE,
            ],
        ],
    },
}


def _run_steps(steps: list[list[str]]) -> tuple[bool, list[dict[str, Any]]]:
    log: list[dict[str, Any]] = []
    for cmd in steps:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
        entry = {
            "command": cmd,
            "exit_code": proc.returncode,
            "tail": (proc.stdout or proc.stderr or "").strip().splitlines()[-3:],
        }
        log.append(entry)
        if proc.returncode != 0:
            return False, log
    return True, log


def _git_rollback() -> None:
    subprocess.run(["git", "checkout", "--", "."], cwd=ROOT, check=False)
    subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=False)


def _recipe_key(row: dict[str, Any]) -> str | None:
    meta = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    if meta.get("kaizen_recipe"):
        return str(meta["kaizen_recipe"])
    source = str(row.get("source") or "")
    if ":" in source:
        return source.rsplit(":", 1)[-1]
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    candidates = fetch_open_machine_safe(limit=30)

    if not candidates:
        receipt = {
            "schema": "nf-kaizen-tick-v1",
            "run_id": run_id,
            "at": ts,
            "status": "skipped",
            "reason": "no_open_machine_safe_items",
        }
        if args.dry_run:
            print(json.dumps(receipt, indent=2))
            return 0
        insert_probe_receipt(run_id=run_id, status="pass", receipt=receipt)
        if args.json:
            print(json.dumps(receipt, indent=2))
        else:
            print("nf_kaizen_nightly: SKIP no_open_machine_safe_items")
        return 0

    row = candidates[0]
    row_id = str(row["id"])
    recipe_key = _recipe_key(row)
    recipe = KAIZEN_RECIPES.get(recipe_key or "")

    if recipe is None:
        receipt = {
            "schema": "nf-kaizen-tick-v1",
            "run_id": run_id,
            "at": ts,
            "status": "skipped",
            "reason": "no_kaizen_recipe",
            "queue_id": row_id,
            "recipe_key": recipe_key,
            "finding": row.get("finding"),
        }
        if args.dry_run:
            print(json.dumps(receipt, indent=2))
            return 0
        insert_probe_receipt(run_id=run_id, status="pass", receipt=receipt)
        if args.json:
            print(json.dumps(receipt, indent=2))
        else:
            print(f"nf_kaizen_nightly: SKIP no_recipe for {recipe_key}")
        return 0

    if args.dry_run:
        print(
            json.dumps(
                {
                    "schema": "nf-kaizen-tick-v1",
                    "run_id": run_id,
                    "dry_run": True,
                    "queue_id": row_id,
                    "recipe_key": recipe_key,
                    "fix": recipe["fix"],
                    "verify": recipe["verify"],
                },
                indent=2,
            )
        )
        return 0

    fix_ok, fix_log = _run_steps(recipe["fix"])
    verify_ok, verify_log = _run_steps(recipe["verify"])
    rolled_back = False

    if fix_ok and not verify_ok:
        _git_rollback()
        rolled_back = True

    status = "pass" if fix_ok and verify_ok else "fail"
    receipt = {
        "schema": "nf-kaizen-tick-v1",
        "run_id": run_id,
        "at": ts,
        "status": status,
        "queue_id": row_id,
        "recipe_key": recipe_key,
        "finding": row.get("finding"),
        "expected_roi": row.get("expected_roi"),
        "fix_ok": fix_ok,
        "verify_ok": verify_ok,
        "rolled_back": rolled_back,
        "fix_log": fix_log,
        "verify_log": verify_log,
    }

    insert_probe_receipt(run_id=run_id, status="pass" if status == "pass" else "fail", receipt=receipt)

    if status == "pass":
        patch_row(
            row_id,
            status="resolved",
            metadata_patch={
                **(row.get("metadata") or {}),
                "kaizen_resolved_at": ts,
                "kaizen_run_id": run_id,
            },
        )
    else:
        patch_row(
            row_id,
            status="open",
            metadata_patch={
                **(row.get("metadata") or {}),
                "kaizen_last_fail_at": ts,
                "kaizen_run_id": run_id,
                "kaizen_rolled_back": rolled_back,
            },
        )

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(
            f"nf_kaizen_nightly: {status.upper()} recipe={recipe_key} "
            f"rolled_back={rolled_back} queue_id={row_id}"
        )
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
