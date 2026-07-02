#!/usr/bin/env python3
"""Cloud inbox dispatch — runs in GitHub Actions, not Cursor.

Picks the oldest pending P0 item from Supabase worker_inbox_queue, writes a
cloud execution receipt into item payload, and advances queue status without
local agent intervention.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _config() -> tuple[str, str]:
    url = os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""
    key = os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    if not url or not key:
        raise RuntimeError("Supabase not configured")
    return url.rstrip("/"), key


def _request(method: str, path: str, *, body: dict[str, Any] | None = None) -> Any:
    base, key = _config()
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["Prefer"] = "return=representation"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{base}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else None


def _fetch_pending_p0() -> dict[str, Any] | None:
    rows = _request(
        "GET",
        "/rest/v1/noetfield_worker_inbox_queue"
        "?status=eq.pending&priority=eq.P0&order=enqueued_at.asc&limit=1&select=*",
    )
    return rows[0] if rows else None


def _receipt_for_item(item: dict[str, Any]) -> tuple[dict[str, Any], str]:
    item_id = item["item_id"]
    owner = (item.get("payload") or {}).get("owner")
    now = utc_now()
    cloud_meta = {
        "processor": "cloud_inbox_dispatch_v1",
        "processed_at": now,
        "github_event": os.environ.get("GITHUB_EVENT_NAME"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_workflow": os.environ.get("GITHUB_WORKFLOW"),
    }

    if item_id == "NOOS-C-01":
        receipt = {
            "schema": "noos-cloud-inbox-receipt-v1",
            "item_id": item_id,
            "title": item["title"],
            "success_signal": "Intake receipt + follow-up",
            "briefing_pack": {
                "primary_surface": "https://www.noetfield.com/ai-value-governance-os/",
                "gel_demo": "https://www.noetfield.com/gel/",
                "follow_up": "Founder: deliver Trust Brief briefing within 48h of warm lead.",
            },
            "cloud_meta": cloud_meta,
        }
        # Founder-owned — cloud prepares pack and dispatches; founder completes briefing.
        return receipt, "dispatched"

    receipt = {
        "schema": "noos-cloud-inbox-receipt-v1",
        "item_id": item_id,
        "title": item["title"],
        "payload": item.get("payload") or {},
        "cloud_meta": cloud_meta,
    }
    return receipt, "completed" if owner != "founder" else "dispatched"


def dispatch_one_p0() -> dict[str, Any]:
    item = _fetch_pending_p0()
    if not item:
        return {"ok": True, "skipped": True, "reason": "no_pending_p0"}

    receipt, next_status = _receipt_for_item(item)
    now = utc_now()
    payload = dict(item.get("payload") or {})
    payload["cloud_execution_receipt"] = receipt

    body: dict[str, Any] = {
        "status": next_status,
        "payload": payload,
        "dispatched_at": now,
    }
    if next_status == "completed":
        body["completed_at"] = now

    updated = _request(
        "PATCH",
        f"/rest/v1/noetfield_worker_inbox_queue?item_id=eq.{item['item_id']}",
        body=body,
    )
    row = updated[0] if isinstance(updated, list) and updated else updated
    return {
        "ok": True,
        "item_id": item["item_id"],
        "status": next_status,
        "receipt_id": item["item_id"],
        "inbox_row_id": row.get("id") if isinstance(row, dict) else None,
    }


def main() -> int:
    try:
        result = dispatch_one_p0()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        print(json.dumps({"ok": False, "error": detail, "status": exc.code}), file=sys.stderr)
        return 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
