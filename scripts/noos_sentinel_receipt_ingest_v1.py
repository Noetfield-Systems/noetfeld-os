#!/usr/bin/env python3
"""Sentinel Phase 2 ingest — observer evidence only (never dispatch/repair).

Reads local sentinel_receipts.jsonl (or --path), validates envelope fields,
writes schema-validated copies under receipts/proof/sentinel/, and upserts a
liveness marker for dead-man watch. Does not POST /loop or restart motors.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = Path.home() / ".noos-sentinel/receipts/sentinel_receipts.jsonl"
OUT_DIR = ROOT / "receipts/proof/sentinel"
REQUIRED = {
    "receipt_id",
    "job_id",
    "lane",
    "target",
    "action_taken",
    "evidence",
    "status",
    "next_recommendation",
    "created_at",
    "dedupe_key",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_receipt(row: dict[str, Any]) -> list[str]:
    missing = sorted(REQUIRED - set(row.keys()))
    errors = [f"missing:{k}" for k in missing]
    if row.get("lane") != "local_sentinel":
        errors.append("lane_not_local_sentinel")
    if row.get("action_taken") not in {"endpoint_check", "mac_triage"}:
        errors.append("action_taken_invalid")
    if not isinstance(row.get("evidence"), dict):
        errors.append("evidence_not_object")
    return errors


def ingest(*, path: Path, write: bool = True, limit: int = 200) -> dict[str, Any]:
    if not path.is_file():
        return {
            "ok": False,
            "verdict": "BLOCKED_SENTINEL_RECEIPTS_MISSING",
            "path": str(path),
            "report_line": "sentinel_ingest · missing receipts file",
        }
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen: set[str] = set()
    lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            rejected.append({"error": "invalid_json"})
            continue
        errors = validate_receipt(row)
        dedupe = str(row.get("dedupe_key") or "")
        if dedupe and dedupe in seen:
            rejected.append({"dedupe_key": dedupe, "error": "duplicate"})
            continue
        if dedupe:
            seen.add(dedupe)
        if errors:
            rejected.append({"dedupe_key": dedupe, "errors": errors})
            continue
        accepted.append(row)

    liveness = {
        "schema": "noos-sentinel-liveness-v1",
        "loop_id": "local_sentinel",
        "last_fired_at": utc_now(),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "source_path": str(path),
        "observer_only": True,
        "forbidden": ["dispatch", "repair", "motor_restart"],
    }
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        batch = {
            "schema": "noos-sentinel-ingest-batch-v1",
            "at": utc_now(),
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "accepted": accepted[-50:],
            "rejected": rejected[-50:],
            "liveness": liveness,
            "content_hash": hashlib.sha256(
                json.dumps(accepted, sort_keys=True).encode("utf-8")
            ).hexdigest(),
            "ok": True,
            "report_line": f"sentinel_ingest · accepted={len(accepted)} rejected={len(rejected)}",
        }
        out = OUT_DIR / f"sentinel-ingest-{ts}.json"
        out.write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
        (OUT_DIR / "sentinel-liveness-latest.json").write_text(
            json.dumps(liveness, indent=2) + "\n", encoding="utf-8"
        )
        batch["receipt_path"] = str(out.relative_to(ROOT))
        return batch
    return {
        "ok": True,
        "accepted": len(accepted),
        "rejected": len(rejected),
        "liveness": liveness,
        "report_line": f"sentinel_ingest · accepted={len(accepted)} rejected={len(rejected)}",
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--path", default=str(DEFAULT_PATH))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    row = ingest(path=Path(args.path), write=not args.dry_run)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
