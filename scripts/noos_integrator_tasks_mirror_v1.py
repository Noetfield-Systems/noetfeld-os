#!/usr/bin/env python3
"""ICL-P2-02 — optional mirror of integrator tasks to Supabase (repo-local SSOT)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".noos-runtime/integrator/noos-integrator-state-v1.json"
RECEIPT = ROOT / "receipts/proof/noos-integrator-tasks-mirror-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from noos_vault_paths_v1 import supabase_creds  # noqa: E402


def mirror(*, dry_run: bool = False) -> dict:
    if not STATE.is_file():
        return {"ok": False, "error": "integrator state missing", "path": str(STATE)}
    state = json.loads(STATE.read_text(encoding="utf-8"))
    tasks = state.get("tasks") or []
    url, key = supabase_creds()
    if not url or not key:
        return {
            "ok": True,
            "skipped": True,
            "reason": "no_supabase_creds",
            "task_count": len(tasks),
            "note": "repo-local integrator state remains SSOT",
        }
    row = {
        "schema": "noos-integrator-tasks-mirror-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": True,
        "dry_run": dry_run,
        "task_count": len(tasks),
        "supabase_url": url,
        "note": "Mirror table optional; implement when noetfield.integrator_tasks exists",
    }
    return row


def main() -> int:
    dry = "--dry-run" in sys.argv
    row = mirror(dry_run=dry)
    if "--write-receipt" in sys.argv:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
