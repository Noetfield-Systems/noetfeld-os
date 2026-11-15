"""One-shot, credential-redacted live HMAC probe for the EXISTING Runway gateway.

No new job, token exposure, queues, writes, or provider call; status is
evidence only for this caller's configured runtime key and the nonce backend.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
import urllib.error
import urllib.request
from urllib.parse import urlsplit

ALLOWED_ERRORS = {
    "AUTH_FAILED", "AUTH_SIGNATURE_INVALID", "AUTH_KEY_UNKNOWN",
    "AUTH_TIMESTAMP_INVALID", "AUTH_NONCE_REPLAY", "AUTHZ_DENIED",
    "AUTH_BACKEND_UNAVAILABLE",
}
SCHEMA = "company-os.runway-hmac-observation.v1"


def classify(status: int, error: str | None, detail: str) -> str:
    if status == 200:
        return "HMAC_AUTHENTICATED"
    if status == 403 and error == "AUTHZ_DENIED":
        return "HMAC_VALID_PERMISSION_DENIED"
    if status == 503 and error == "AUTH_BACKEND_UNAVAILABLE":
        return "HMAC_VALID_NONCE_BACKEND_UNAVAILABLE"
    if status == 401 and error == "AUTH_FAILED" and "consume_runway_runtime_nonce_v1" in detail:
        return "HMAC_VALID_NONCE_BACKEND_UNAVAILABLE"
    if status == 401 and error == "AUTH_SIGNATURE_INVALID":
        return "HMAC_SIGNATURE_MISMATCH"
    if status == 401 and error == "AUTH_KEY_UNKNOWN":
        return "HMAC_KEY_ID_NOT_FOUND"
    return "AUTH_UNCONFIRMED"


def probe() -> dict:
    url = (os.getenv("NOETFIELD_RUNWAY_API_URL") or "").rstrip("/")
    key_id = (os.getenv("NOETFIELD_RUNWAY_API_KEY_ID") or "staging-proof").strip()
    secret = (os.getenv("NOETFIELD_RUNWAY_API_SECRET") or "").strip()
    out = {
        "schema": SCHEMA,
        "mode": "SIGNED_READ_ONLY",
        "configured_url": bool(url),
        "configured_secret": bool(secret),
        "key_id": key_id if key_id == "staging-proof" else "OTHER_CONFIGURED_KEY",
        "http_status": None,
        "auth_error_code": None,
        "verdict": "NOT_CONFIGURED",
    }
    if not url or not secret:
        return out
    if secret.startswith("${{"):
        out["verdict"] = "REFERENCE_UNRESOLVED"
        return out
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path:
        out["verdict"] = "INVALID_GATEWAY_URL"
        return out
    path = "/v1/queue/summary"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    nonce = secrets.token_hex(16)
    digest = hashlib.sha256(b"").hexdigest()
    canonical = f"GET\n{path}\n{timestamp}\n{nonce}\n{digest}"
    signature = hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    request = urllib.request.Request(
        url + path, method="GET", headers={
            "Authorization": f"NOETFIELD-HMAC {key_id}:{signature}",
            "x-noetfield-timestamp": timestamp,
            "x-noetfield-nonce": nonce,
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=9) as response:
            out["http_status"] = response.status
            out["verdict"] = classify(response.status, None, "")
    except urllib.error.HTTPError as exc:
        out["http_status"] = exc.code
        try:
            payload = json.loads(exc.read(1024))
        except (ValueError, OSError):
            payload = {}
        code = payload.get("error") if isinstance(payload, dict) else None
        code = code if isinstance(code, str) and code in ALLOWED_ERRORS else None
        detail = payload.get("detail") if isinstance(payload, dict) else None
        out["auth_error_code"] = code
        out["verdict"] = classify(exc.code, code, detail if isinstance(detail, str) else "")
    except (OSError, TimeoutError):
        out["verdict"] = "GATEWAY_UNREACHABLE"
    return out


def run_and_log() -> None:
    try:
        result = probe()
    except Exception as exc:  # noqa: BLE001
        result = {"schema": SCHEMA, "verdict": "PROBE_EXCEPTION", "error_code": type(exc).__name__}
    print("COMPANY_OS_RUNWAY_HMAC_PROBE=" + json.dumps(result, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    run_and_log()
