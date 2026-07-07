#!/usr/bin/env python3
"""ICL-P2-03 — publish UPGRADE_MANIFEST deltas for cross-repo integrator sync."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/_NOOS_AGENT/UPGRADE_MANIFEST.json"
BACKLOG = ROOT / "data/noos-unified-upgrade-backlog-v1.json"
EXPORT_DIR = ROOT / ".noos-runtime/integrator/exports"
RECEIPT = ROOT / "receipts/proof/noos-upgrade-manifest-publish-v1.json"

NOETFIELD_PREFIXES = ("UPG-NF", "UPG-0001", "UPG-0002", "UPG-0003", "UPG-0004", "UPG-0005")


def _filter_ids(ids: list[str], *, plane: str) -> list[str]:
    if plane == "NOOS":
        return [x for x in ids if not x.startswith("UPG-NF")]
    if plane == "Noetfield-contract-surfaces":
        return [x for x in ids if x.startswith(NOETFIELD_PREFIXES)]
    return list(ids)


def _blocked_subset(blocked: dict[str, str], *, plane: str) -> dict[str, str]:
    if plane == "NOOS":
        return {k: v for k, v in blocked.items() if not k.startswith("UPG-NF")}
    if plane == "Noetfield-contract-surfaces":
        return {k: v for k, v in blocked.items() if k.startswith(NOETFIELD_PREFIXES)}
    return dict(blocked)


def _plane_delta(doc: dict[str, Any], plane: str) -> dict[str, Any]:
    completed = doc.get("completed_steps") or []
    in_progress = doc.get("in_progress_steps") or []
    planned = doc.get("planned_steps") or []
    blocked = doc.get("blocked_steps") or {}
    return {
        "plane": plane,
        "updated_at": doc.get("updated_at"),
        "completed_steps": _filter_ids(completed, plane=plane),
        "in_progress_steps": _filter_ids(in_progress, plane=plane),
        "planned_steps": _filter_ids(planned, plane=plane),
        "blocked_steps": _blocked_subset(blocked if isinstance(blocked, dict) else {}, plane=plane),
    }


def _write_exports(delta: dict[str, Any]) -> dict[str, str]:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    full = EXPORT_DIR / "upgrade-manifest-delta-v1.json"
    full.write_text(json.dumps(delta, indent=2) + "\n", encoding="utf-8")
    paths["full"] = str(full)
    for plane in delta.get("planes", {}):
        safe = plane.lower().replace(" ", "-")
        path = EXPORT_DIR / f"upgrade-manifest-delta-{safe}-v1.json"
        path.write_text(json.dumps(delta["planes"][plane], indent=2) + "\n", encoding="utf-8")
        paths[plane] = str(path)
    return paths


def _integrator_sync(delta: dict[str, Any]) -> dict[str, Any]:
    env = os.environ.copy()
    sys.path.insert(0, str(ROOT / "scripts"))
    from noos_vault_paths_v1 import load_platform_env  # noqa: E402

    env.update(load_platform_env())
    marker = ROOT / ".noos-runtime/integrator/upgrade-manifest-delta-v1.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(delta, indent=2) + "\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/noos_integrator_sync_v1.py"), "sync"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        env=env,
    )
    if not proc.stdout.strip():
        return {"ok": False, "exit_code": proc.returncode, "stderr": proc.stderr[-300:]}
    try:
        doc = json.loads(proc.stdout)
        doc["manifest_marker"] = str(marker)
        return doc
    except json.JSONDecodeError:
        return {"ok": False, "raw": proc.stdout[-400:]}


def publish(*, sync_integrator: bool = True) -> dict:
    if not MANIFEST.is_file():
        return {"ok": False, "error": "manifest missing", "path": str(MANIFEST)}
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    backlog_ref = str(BACKLOG) if BACKLOG.is_file() else None
    delta = {
        "schema": "noos-upgrade-manifest-delta-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manifest_path": str(MANIFEST),
        "unified_backlog": backlog_ref,
        "plan_trace_id": doc.get("plan_trace_id"),
        "current_phase": doc.get("current_phase"),
        "updated_at": doc.get("updated_at"),
        "planes": {
            "NOOS": _plane_delta(doc, "NOOS"),
            "Noetfield-contract-surfaces": _plane_delta(doc, "Noetfield-contract-surfaces"),
        },
        "note": "Contract-only SourceA deltas excluded; no product repo writes",
    }
    export_paths = _write_exports(delta)
    sync_row = _integrator_sync(delta) if sync_integrator else {"ok": True, "skipped": True}
    row = {
        "schema": "noos-upgrade-manifest-publish-v1",
        "at": delta["at"],
        "ok": bool(sync_row.get("ok", True)),
        "entry_count": len(doc.get("completed_steps") or []),
        "planes": list(delta["planes"].keys()),
        "export_paths": export_paths,
        "integrator_sync": sync_row,
        "note": delta["note"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    row["receipt_path"] = str(RECEIPT)
    return row


def main() -> int:
    row = publish(sync_integrator="--no-sync" not in sys.argv)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
