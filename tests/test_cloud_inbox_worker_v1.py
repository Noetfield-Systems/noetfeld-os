"""Tests for cloud inbox worker founder_blocked semantics."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cloud_inbox_worker_v1 as worker
import factory_supabase_sink_v1 as sink
from cloud_inbox_constants_v1 import (
    FOUNDER_BLOCKED_REASON,
    FOUNDER_BLOCKED_STATUS,
    NEVER_RUN_STATUS,
    PRESERVED_INBOX_STATUSES,
)
from cloud_inbox_worker_v1 import (
    build_founder_blocked_patch,
    founder_blocked_summary,
    is_founder_only,
    process_cycle,
    select_executable,
)


def test_founder_only_detection():
    assert is_founder_only({"payload": {"owner": "founder"}})
    assert is_founder_only({"payload": {"lane": "commercial"}})
    assert not is_founder_only({"payload": {"upg": "UPG-0152"}})


def test_founder_blocked_patch_status():
    item = {
        "item_id": "NOOS-C-01",
        "priority": "P0",
        "payload": {"owner": "founder", "lane": "commercial"},
    }
    patch = build_founder_blocked_patch(item)
    assert patch["status"] == FOUNDER_BLOCKED_STATUS
    assert "completed_at" not in patch
    assert patch["payload"]["cloud_founder_blocked_receipt"]["reason"] == FOUNDER_BLOCKED_REASON


def test_cancelled_is_never_run_only():
    assert NEVER_RUN_STATUS == "cancelled"
    assert FOUNDER_BLOCKED_STATUS not in {NEVER_RUN_STATUS}


def test_preserved_statuses_include_founder_blocked():
    assert FOUNDER_BLOCKED_STATUS in PRESERVED_INBOX_STATUSES
    assert "pending" not in PRESERVED_INBOX_STATUSES


def test_reenqueue_preserves_founder_blocked():
    existing = {"item_id": "NOOS-C-01", "status": FOUNDER_BLOCKED_STATUS}
    with patch.object(sink, "_get_inbox_item", return_value=existing):
        result = sink.upsert_inbox_item(
            {
                "item_id": "NOOS-C-01",
                "title": "Founder briefing",
                "priority": "P0",
                "status": "pending",
                "payload": {},
            }
        )
    assert result["skipped"] is True
    assert result["status"] == FOUNDER_BLOCKED_STATUS


def test_executable_worker_ignores_founder_pending():
    pending = [
        {"item_id": "NOOS-C-01", "priority": "P0", "payload": {"owner": "founder"}},
        {"item_id": "UPG-0152", "priority": "P1", "payload": {"upg": "UPG-0152"}},
    ]
    selected = select_executable(pending)
    assert selected["item_id"] == "UPG-0152"


def test_founder_blocked_summary_shape():
    now = datetime(2026, 7, 2, 6, 0, tzinfo=timezone.utc)
    items = [
        {
            "item_id": "NOOS-C-01",
            "priority": "P0",
            "enqueued_at": "2026-07-02T04:00:43+00:00",
            "status": FOUNDER_BLOCKED_STATUS,
        }
    ]
    summary = founder_blocked_summary(items, now=now)
    assert summary["founder_blocked_count"] == 1
    assert summary["oldest"] == "NOOS-C-01"
    assert summary["priority"] == "P0"
    assert summary["reason"] == FOUNDER_BLOCKED_REASON
    assert summary["age_seconds"] == 7200 - 43


def test_process_cycle_includes_founder_blocked_summary():
    store = {
        "pending": [
            {
                "item_id": "NOOS-C-01",
                "priority": "P0",
                "enqueued_at": "2026-07-02T04:00:43+00:00",
                "payload": {"owner": "founder"},
            },
            {
                "item_id": "UPG-0152",
                "priority": "P1",
                "enqueued_at": "2026-07-02T05:00:00+00:00",
                "payload": {"upg": "UPG-0152"},
            },
        ],
        "founder_blocked": [],
    }

    def fake_request(method: str, path: str, *, body: dict | None = None):
        if method == "GET" and "status=eq.pending" in path:
            return list(store["pending"])
        if method == "GET" and f"status=eq.{FOUNDER_BLOCKED_STATUS}" in path:
            return list(store["founder_blocked"])
        if method == "PATCH":
            item_id = path.split("item_id=eq.")[1]
            if body and body.get("status") == FOUNDER_BLOCKED_STATUS:
                row = next(item for item in store["pending"] if item["item_id"] == item_id)
                store["pending"] = [item for item in store["pending"] if item["item_id"] != item_id]
                blocked = {**row, **body}
                store["founder_blocked"].append(blocked)
                return [blocked]
            if body and body.get("status") == "completed":
                row = next(item for item in store["pending"] if item["item_id"] == item_id)
                store["pending"] = [item for item in store["pending"] if item["item_id"] != item_id]
                return [{**row, **body}]
        raise AssertionError(f"unexpected request: {method} {path}")

    worker._request_fn = fake_request
    with patch.object(worker, "_exec_upg_0152", return_value={"ok": True, "exit_code": 0}):
        result = process_cycle()

    worker._request_fn = None
    assert result["item_id"] == "UPG-0152"
    assert result["founder_blocked"]["founder_blocked_count"] == 1
    assert result["founder_blocked"]["oldest"] == "NOOS-C-01"
    assert store["founder_blocked"][0]["status"] == FOUNDER_BLOCKED_STATUS
