#!/usr/bin/env python3
"""Repair fix 7 — minimal persistent incident logging for the NOOS loop pipeline.

Railway stdout is ephemeral and the loop-runner HTTP server no-ops its own
request logging, so before this there was no durable record of what an
unhandled exception or non-200 actually said. log_incident() is the one
deliberately fail-open write in this pipeline: logging must never itself
crash the caller, so every failure mode here is swallowed and returned as
a clean dict instead of raised.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def _supabase_config() -> tuple[str, str] | None:
    url = (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or "").strip()
    key = (
        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    if not url or not key:
        return None
    return url.rstrip("/"), key


def log_incident(
    *,
    source: str,
    message: str,
    severity: str = "error",
    loop_id: str | None = None,
    event_type: str | None = None,
    detail: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    cfg = _supabase_config()
    if not cfg:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    base, key = cfg
    row = {
        "source": source,
        "loop_id": loop_id,
        "event_type": event_type,
        "severity": severity,
        "message": message[:2000],
        "detail": detail or {},
        "run_id": run_id,
    }
    try:
        req = urllib.request.Request(
            f"{base}/rest/v1/noos_incident_log",
            data=json.dumps(row).encode("utf-8"),
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8):
            return {"ok": True}
    except Exception as exc:  # noqa: BLE001 — deliberate: logging must never crash the caller
        return {"ok": False, "error": str(exc)[:300]}
