#!/usr/bin/env python3
"""Signed Unified Motor Event API client for NOOS portfolio-owner bridge.

Call site (integration): ``scripts/noos_loop_runner_v1.py`` → ``execute_loop()``
after durable local state + Supabase liveness upsert (see ``maybe_emit_loop_cycle_event``).

Gateway contract (sandbox): POST ``/v1/events`` with headers:
  - ``x-motor-timestamp`` (unix seconds)
  - ``x-motor-signature`` (``sha256=`` HMAC over ``{timestamp}.{raw_body}``)
  - ``Idempotency-Key``

Env:
  - ``MOTOR_EVENT_GATEWAY_URL`` — base URL (e.g. https://nf-unified-motor-foundation-v1...workers.dev)
  - ``MOTOR_EVENT_API_SECRET`` — shared HMAC secret
  - ``NOOS_UNIFIED_MOTOR_EVENT_BRIDGE`` — ``1`` to enable emission (default off)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_MAP = ROOT / "data/noos-unified-motor-event-bridge-v1.json"

EVENT_SCHEMA_VERSION = "motor.event.v1"
DEFAULT_ROLE_ID = "noetfield:noos.portfolio-owner"
DEFAULT_ROUTE = "noos.portfolio.loop_cycle"
MAX_TIMESTAMP_SKEW_SEC = 300


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_bridge_map() -> dict[str, Any]:
    if not BRIDGE_MAP.is_file():
        return {}
    return json.loads(BRIDGE_MAP.read_text(encoding="utf-8"))


def bridge_enabled() -> bool:
    return os.environ.get("NOOS_UNIFIED_MOTOR_EVENT_BRIDGE", "").strip() in ("1", "true", "yes")


def gateway_config() -> tuple[str, str] | None:
    base = (os.environ.get("MOTOR_EVENT_GATEWAY_URL") or "").strip().rstrip("/")
    secret = (os.environ.get("MOTOR_EVENT_API_SECRET") or "").strip()
    if base and secret:
        return base, secret
    return None


def gateway_source_id() -> str:
    doc = load_bridge_map()
    return str(doc.get("gateway_source") or "api.motor")


def noos_source_id() -> str:
    doc = load_bridge_map()
    return str(doc.get("noos_source_id") or "noos.portfolio")


def sign_motor_event_body(*, secret: str, timestamp: str, raw_body: str) -> str:
    """Return ``sha256=`` HMAC signature for Unified Motor Event API."""
    signed = f"{timestamp}.{raw_body}"
    digest = hmac.new(secret.encode("utf-8"), signed.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def build_idempotency_key(*, loop_id: str, cycle_number: int, op_key: str | None = None) -> str:
    """Stable idempotency key for a loop cycle emission."""
    if op_key:
        return f"{noos_source_id()}:{op_key}"
    return f"{noos_source_id()}:{loop_id}:cycle:{cycle_number}"


def build_event_id(*, loop_id: str, cycle_number: int) -> str:
    suffix = secrets.token_hex(4)
    return f"evt_noos_{loop_id}_{cycle_number:06d}_{suffix}"


def build_motor_event_payload(
    *,
    loop_id: str,
    cycle_number: int,
    event_type: str,
    state_after: str,
    op_key: str | None = None,
    extra_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    doc = load_bridge_map()
    routes = doc.get("routes") or {}
    route = str(routes.get(loop_id) or routes.get("default") or DEFAULT_ROUTE)
    payload: dict[str, Any] = {
        "noos_source_id": noos_source_id(),
        "loop_id": loop_id,
        "cycle_number": cycle_number,
        "event_type": event_type,
        "state_after": state_after,
        "emitted_at": utc_now(),
    }
    if op_key:
        payload["op_key"] = op_key
    if extra_payload:
        payload.update(extra_payload)
    event: dict[str, Any] = {
        "event_id": build_event_id(loop_id=loop_id, cycle_number=cycle_number),
        "source": gateway_source_id(),
        "schema_version": EVENT_SCHEMA_VERSION,
        "role_id": str(doc.get("role_id") or DEFAULT_ROLE_ID),
        "route": route,
        "consequential": False,
        "payload": payload,
    }
    if doc.get("recipe_id"):
        event["recipe_id"] = doc.get("recipe_id")
    if doc.get("recipe_version"):
        event["recipe_version"] = doc.get("recipe_version")
    return event


def post_signed_event(
    event: dict[str, Any],
    *,
    gateway_url: str | None = None,
    secret: str | None = None,
    idempotency_key: str | None = None,
    timeout_sec: int = 30,
) -> dict[str, Any]:
    cfg = gateway_config()
    if not cfg and (not gateway_url or not secret):
        return {"ok": False, "skipped": True, "reason": "motor_event_gateway_not_configured"}
    base, api_secret = cfg if cfg else (gateway_url or "", secret or "")
    raw_body = json.dumps(event, separators=(",", ":"), sort_keys=True)
    timestamp = str(int(time.time()))
    signature = sign_motor_event_body(secret=api_secret, timestamp=timestamp, raw_body=raw_body)
    loop_id = str((event.get("payload") or {}).get("loop_id") or "unknown")
    cycle_number = int((event.get("payload") or {}).get("cycle_number") or 0)
    op_key = (event.get("payload") or {}).get("op_key")
    idem = idempotency_key or build_idempotency_key(
        loop_id=loop_id,
        cycle_number=cycle_number,
        op_key=str(op_key) if op_key else None,
    )
    url = f"{base.rstrip('/')}/v1/events"
    req = urllib.request.Request(
        url,
        data=raw_body.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "noos-unified-motor-event-client-v1",
            "x-motor-timestamp": timestamp,
            "x-motor-signature": signature,
            "Idempotency-Key": idem,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            body_raw = resp.read().decode("utf-8")
            try:
                body = json.loads(body_raw)
            except json.JSONDecodeError:
                body = {"raw": body_raw[:400]}
            return {
                "ok": 200 <= resp.status < 300,
                "status": resp.status,
                "idempotency_key": idem,
                "event_id": event.get("event_id"),
                "body": body,
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw[:400]}
        return {
            "ok": False,
            "status": exc.code,
            "idempotency_key": idem,
            "event_id": event.get("event_id"),
            "body": body,
            "error": f"http_{exc.code}",
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "ok": False,
            "skipped": False,
            "idempotency_key": idem,
            "event_id": event.get("event_id"),
            "error": str(exc),
        }


def maybe_emit_loop_cycle_event(cycle: dict[str, Any]) -> dict[str, Any]:
    """Emit portfolio-owner event after durable NOOS loop cycle write (fail-open)."""
    if not bridge_enabled():
        return {"ok": False, "skipped": True, "reason": "bridge_disabled"}
    state_after = str(cycle.get("state_after") or "")
    if state_after not in ("COMPLETE", "IDLE_NO_WORK"):
        return {"ok": False, "skipped": True, "reason": f"state_not_emittable:{state_after}"}
    loop_id = str(cycle.get("loop_id") or "")
    cycle_number = int(cycle.get("cycle_number") or 0)
    if not loop_id or cycle_number <= 0:
        return {"ok": False, "skipped": True, "reason": "missing_loop_identity"}
    event = build_motor_event_payload(
        loop_id=loop_id,
        cycle_number=cycle_number,
        event_type=str(cycle.get("event_type") or ""),
        state_after=state_after,
        op_key=str(cycle.get("op_key") or "") or None,
        extra_payload={
            "factory_id": cycle.get("factory_id"),
            "status": cycle.get("status"),
            "sink_acked": (cycle.get("supabase_sink") or {}).get("ok"),
        },
    )
    result = post_signed_event(event)
    if result.get("ok"):
        try:
            from noos_loop_liveness_v1 import upsert_loop_liveness

            doc = load_bridge_map()
            result["liveness_upsert"] = upsert_loop_liveness(
                loop_id=str(doc.get("loop_id") or "unified_motor_event_bridge"),
                event_type=str(doc.get("event_type") or "noos_unified_motor_event_bridge_tick"),
                interval_minutes=int(doc.get("interval_minutes") or 15),
                last_cycle_status="COMPLETE",
                host="noos:unified-motor-event-bridge",
            )
        except Exception as exc:
            result["liveness_upsert"] = {"ok": False, "error": str(exc)}
    return result


def verify_timestamp_fresh(timestamp: str, *, now_sec: int | None = None) -> bool:
    now = now_sec if now_sec is not None else int(time.time())
    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return False
    return abs(now - ts) <= MAX_TIMESTAMP_SKEW_SEC
