#!/usr/bin/env python3
"""Verify CF→Railway dispatch: each target fires once via POST /loop."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "data/noos-cf-dispatch-table-v1.json"
PROOF = ROOT / "receipts/proof/noos-cf-railway-dispatch-verify-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_table() -> list[dict[str, Any]]:
    doc = json.loads(TABLE.read_text(encoding="utf-8"))
    return list(doc.get("targets") or [])


def post_loop(*, base_url: str, secret: str, event_type: str) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/loop"
    body = json.dumps({"event_type": event_type, "source": "verify_script"}).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "noos-cf-railway-verify-v1"}
    if secret:
        headers["Authorization"] = f"Bearer {secret}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            fired = payload.get("event_type") == event_type and resp.status in (200, 409)
            return {
                "fired": fired,
                "ok": fired and payload.get("ok", False),
                "status": resp.status,
                "body": payload,
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw[:500]}
        fired = payload.get("event_type") == event_type
        return {"fired": fired, "ok": fired and payload.get("ok", False), "status": exc.code, "body": payload}


def verify(*, base_url: str, secret: str, only: str | None) -> dict[str, Any]:
    targets = load_table()
    if only:
        targets = [t for t in targets if t.get("dispatch_id") == only or t.get("event_type") == only]
    rows: list[dict[str, Any]] = []
    for target in targets:
        event_type = str(target.get("event_type"))
        row = {
            "dispatch_id": target.get("dispatch_id"),
            "event_type": event_type,
            "handler": target.get("handler"),
            **post_loop(base_url=base_url, secret=secret, event_type=event_type),
        }
        rows.append(row)
    ok_count = sum(1 for r in rows if r.get("fired"))
    exec_ok_count = sum(1 for r in rows if r.get("ok"))
    return {
        "schema": "noos-cf-railway-dispatch-verify-v1",
        "verified_at": utc_now(),
        "runner_url": base_url,
        "target_count": len(rows),
        "fired_count": ok_count,
        "execution_ok_count": exec_ok_count,
        "targets": rows,
        "ok": ok_count == len(rows) and len(rows) > 0,
        "report_line": f"cf_railway_dispatch_verify · fired={ok_count}/{len(rows)} exec_ok={exec_ok_count}/{len(rows)}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=os.environ.get("LOOP_RUNNER_URL", "http://127.0.0.1:8080"))
    ap.add_argument("--secret", default=os.environ.get("LOOP_RUNNER_SECRET", ""))
    ap.add_argument("--only", default=None, help="dispatch_id or event_type")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = verify(base_url=args.url, secret=args.secret, only=args.only)
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
