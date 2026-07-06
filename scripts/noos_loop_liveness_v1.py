#!/usr/bin/env python3
"""Phase B — upsert loop liveness rows to Supabase (fail-open)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _supabase_creds() -> tuple[str, str] | None:
    url = (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or "").strip()
    key = (
        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    if url and key:
        return url.rstrip("/"), key
    return None


def detect_execution_host() -> str:
    fly_app = (os.environ.get("FLY_APP") or "").strip()
    if fly_app:
        return f"fly:{fly_app}"
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        return "railway:noos-loop-runner"
    if os.environ.get("DISPATCH_SOURCE", "").startswith("cf"):
        return "cf:loop-motor"
    if os.environ.get("GITHUB_EVENT_NAME") == "http_loop":
        return "railway:noos-loop-runner"
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "gha"
    return "local"


def upsert_loop_liveness(
    *,
    loop_id: str,
    event_type: str | None = None,
    interval_minutes: int = 5,
    last_cycle_status: str = "COMPLETE",
    host: str | None = None,
    last_fired_at: str | None = None,
) -> dict[str, Any]:
    creds = _supabase_creds()
    if not creds:
        return {"ok": False, "skipped": True, "reason": "supabase_not_configured"}
    base, key = creds
    fired = last_fired_at or utc_now()
    row = {
        "loop_id": loop_id,
        "event_type": event_type,
        "interval_minutes": int(interval_minutes),
        "last_fired_at": fired,
        "last_cycle_status": last_cycle_status,
        "host": host or detect_execution_host(),
        "updated_at": fired,
    }
    req = urllib.request.Request(
        f"{base}/rest/v1/noos_loop_registry",
        data=json.dumps(row).encode("utf-8"),
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": 200 <= resp.status < 300, "loop_id": loop_id, "last_fired_at": fired}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:400]
        return {"ok": False, "loop_id": loop_id, "error": f"http_{exc.code}", "detail": body}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "loop_id": loop_id, "error": str(exc)}
