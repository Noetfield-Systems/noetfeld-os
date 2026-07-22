#!/usr/bin/env python3
"""Supabase sink for unified plan-completion events + derived backlog (migration 0021).

Append-only events are authored truth. Backlog rows are CAS projections.
Fails soft when Supabase env is absent so local/CI file-backed path still works.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

HTTP_TIMEOUT = 30


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def supabase_env() -> dict[str, str]:
    url = (
        os.environ.get("NOETFIELD_SUPABASE_URL")
        or os.environ.get("SUPABASE_URL")
        or ""
    ).strip().rstrip("/")
    key = (
        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    return {"url": url, "key": key, "configured": "1" if url and key else ""}


def _headers(key: str, *, prefer: str | None = None) -> dict[str, str]:
    h = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "noos-plan-completion-supabase-sink-v1",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _request(
    method: str,
    url: str,
    *,
    key: str,
    body: bytes | None = None,
    prefer: str | None = None,
) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers=_headers(key, prefer=prefer),
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
            parsed: Any = json.loads(raw) if raw else None
            return {"ok": True, "status": resp.status, "body": parsed}
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")[:500]
        return {"ok": False, "status": exc.code, "error": err}
    except OSError as exc:
        return {"ok": False, "status": 0, "error": str(exc)[:240]}


def append_event(
    *,
    op_key: str,
    event_type: str,
    plan_id: str,
    item_id: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    env = supabase_env()
    if not env["configured"]:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    row = {
        "op_key": op_key,
        "event_type": event_type,
        "plan_id": plan_id,
        "item_id": item_id,
        "payload": payload or {},
    }
    return _request(
        "POST",
        f"{env['url']}/rest/v1/noos_plan_completion_events",
        key=env["key"],
        body=json.dumps(row).encode("utf-8"),
        prefer="resolution=merge-duplicates,return=representation",
    )


def upsert_backlog_row(item: dict[str, Any]) -> dict[str, Any]:
    env = supabase_env()
    if not env["configured"]:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    row = {
        "op_key": item["op_key"],
        "plan_id": item["plan_id"],
        "item_id": item["item_id"],
        "status": item.get("status") or "READY",
        "role": item.get("role"),
        "value_class": item.get("value_class"),
        "job_id": item.get("job_id"),
        "content_hash": item.get("content_hash") or item.get("payload_hash") or item["op_key"],
        "fencing_token": int(item.get("fencing_token") or 1),
        "updated_at": utc_now(),
    }
    return _request(
        "POST",
        f"{env['url']}/rest/v1/noos_plan_completion_backlog",
        key=env["key"],
        body=json.dumps(row).encode("utf-8"),
        prefer="resolution=merge-duplicates,return=representation",
    )


def sync_compile(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Project compiler output into Supabase (events + backlog rows)."""
    env = supabase_env()
    if not env["configured"]:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured", "synced": 0}
    synced = 0
    errors: list[dict[str, Any]] = []
    for item in items:
        ev = append_event(
            op_key=item["op_key"],
            event_type="compiled",
            plan_id=item["plan_id"],
            item_id=item["item_id"],
            payload={
                "status": item.get("status"),
                "role": item.get("role"),
                "value_class": item.get("value_class"),
                "title": item.get("title"),
            },
        )
        up = upsert_backlog_row(item)
        if ev.get("ok") and up.get("ok"):
            synced += 1
        else:
            errors.append({"op_key": item.get("op_key"), "event": ev, "upsert": up})
            if len(errors) >= 5:
                break
    return {
        "ok": not errors,
        "synced": synced,
        "errors": errors,
        "at": utc_now(),
    }


def record_dispatch(*, item: dict[str, Any], job_id: str | None, dry_run: bool) -> dict[str, Any]:
    ev = append_event(
        op_key=item["op_key"],
        event_type="dispatched",
        plan_id=item["plan_id"],
        item_id=item["item_id"],
        payload={"job_id": job_id, "dry_run": dry_run},
    )
    row = dict(item)
    row["status"] = "DISPATCHED"
    row["job_id"] = job_id
    row["fencing_token"] = int(item.get("fencing_token") or 1) + 1
    up = upsert_backlog_row(row)
    return {"ok": bool(ev.get("ok") or ev.get("skipped")) and bool(up.get("ok") or up.get("skipped")), "event": ev, "upsert": up}


def record_complete(*, item: dict[str, Any], observation: dict[str, Any] | None = None) -> dict[str, Any]:
    ev = append_event(
        op_key=item["op_key"],
        event_type="complete",
        plan_id=item["plan_id"],
        item_id=item["item_id"],
        payload=observation or {},
    )
    row = dict(item)
    row["status"] = "COMPLETE"
    row["fencing_token"] = int(item.get("fencing_token") or 1) + 1
    up = upsert_backlog_row(row)
    return {"ok": bool(ev.get("ok") or ev.get("skipped")) and bool(up.get("ok") or up.get("skipped")), "event": ev, "upsert": up}
