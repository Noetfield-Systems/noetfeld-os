#!/usr/bin/env python3
"""ICL-P2 closeout verify — integrator-status, tasks mirror, manifest publish."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts/proof/noos-integrator-icl-p2-closeout-v1.json"


def _run_json(cmd: list[str], *, timeout: int = 180) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if not proc.stdout.strip():
        return {"ok": False, "exit_code": proc.returncode, "stderr": proc.stderr[-400:]}
    try:
        doc = json.loads(proc.stdout)
        if isinstance(doc, dict):
            doc.setdefault("exit_code", proc.returncode)
        return doc
    except json.JSONDecodeError:
        return {"ok": False, "exit_code": proc.returncode, "raw": proc.stdout[-500:]}


def verify_icl_p2_01() -> dict:
    script = ROOT / "scripts/noos_integrator_status_v1.py"
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    row = _run_json([sys.executable, str(script)], timeout=240)
    surfaces = row.get("surfaces") or {}
    return {
        "id": "ICL-P2-01",
        "title": "integrator-status CLI",
        "ok": bool(script.is_file() and "integrator-status" in makefile and row.get("ok")),
        "surfaces": surfaces,
        "exit_code": row.get("exit_code"),
    }


def verify_icl_p2_02() -> dict:
    script = ROOT / "scripts/noos_integrator_tasks_mirror_v1.py"
    row = _run_json(
        [sys.executable, str(script), "--apply", "--write-receipt"],
        timeout=90,
    )
    return {
        "id": "ICL-P2-02",
        "title": "Supabase integrator_tasks mirror",
        "ok": bool(script.is_file() and row.get("ok")),
        "task_count": row.get("task_count"),
        "home_mirror_ok": (row.get("home_mirror") or {}).get("ok"),
        "tasks_table": row.get("tasks_table"),
        "dry_run": row.get("dry_run"),
    }


def verify_icl_p2_03() -> dict:
    script = ROOT / "scripts/noos_upgrade_manifest_publish_v1.py"
    row = _run_json([sys.executable, str(script)], timeout=60)
    exports = row.get("export_paths") or {}
    export_ok = all(Path(p).is_file() for p in exports.values()) if exports else False
    return {
        "id": "ICL-P2-03",
        "title": "Cross-repo upgrade manifest sync",
        "ok": bool(script.is_file() and row.get("ok") and export_ok),
        "planes": row.get("planes"),
        "export_paths": exports,
        "integrator_sync_ok": (row.get("integrator_sync") or {}).get("ok"),
    }


def verify(*, write_receipt: bool = False) -> dict:
    steps = {
        "ICL-P2-01": verify_icl_p2_01(),
        "ICL-P2-02": verify_icl_p2_02(),
        "ICL-P2-03": verify_icl_p2_03(),
    }
    ok = all(s.get("ok") for s in steps.values())
    row = {
        "schema": "noos-integrator-icl-p2-closeout-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "phase": "ICL-P2",
        "status": "done" if ok else "degraded",
        "ok": ok,
        "steps": steps,
    }
    if write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)
    return row


def main() -> int:
    write = "--write-receipt" in sys.argv
    row = verify(write_receipt=write)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
