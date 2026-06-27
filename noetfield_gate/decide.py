"""POST /v1/decision client — one command, one receipt on disk."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any
from urllib import error, request


SAMPLE_INTENT: dict[str, Any] = {
    "applicant_id": "gate-demo-001",
    "credit_score": 720,
    "monthly_debt": 1200.0,
    "monthly_income": 6000.0,
    "loan_amount": 250000.0,
    "collateral_value": 320000.0,
    "employment_history_years": 4.0,
    "liquid_reserves_months": 6.0,
}


def api_base() -> str:
    return os.environ.get("NOETFIELD_API_URL", "https://api.noetfield.com").strip().rstrip("/")


def api_key() -> str:
    key = os.environ.get("NOETFIELD_API_KEY", "").strip()
    if key:
        return key
    keys_path = Path(os.environ.get("NOETFIELD_KEYS_PATH", "")).expanduser()
    if not keys_path.is_file():
        root = Path(__file__).resolve().parents[1]
        keys_path = root / "api_keys.local.json"
    if keys_path.is_file():
        # Dev hint only — real keys are hashed; env var required for API call
        pass
    return key


def post_decision(
    payload: dict[str, Any],
    *,
    api_url: str | None = None,
    api_key_value: str | None = None,
) -> dict[str, Any]:
    base = (api_url or api_base()).rstrip("/")
    key = (api_key_value or api_key()).strip()
    if not key:
        raise RuntimeError(
            "NOETFIELD_API_KEY not set — export key from scripts/mint_api_key.py (dev)"
        )
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{base}/v1/decision",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": key,
        },
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"decision API {exc.code}: {detail}") from exc


def build_receipt(api_response: dict[str, Any], *, intent: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "noetfield-decision-receipt-v1",
        "tool": "noetfield-gate",
        "request_id": api_response.get("request_id"),
        "decision": api_response.get("decision"),
        "composite_score": api_response.get("composite_score"),
        "audit_id": api_response.get("audit_id"),
        "rule_set_version": api_response.get("rule_set_version"),
        "policy_hashes": api_response.get("policy_hashes"),
        "intent": intent,
        "api_response": api_response,
    }


def write_receipt(receipt: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return path


def default_out_path() -> Path:
    return Path.cwd() / f"noetfield-decision-{uuid.uuid4().hex[:8]}.json"


__all__ = [
    "SAMPLE_INTENT",
    "post_decision",
    "build_receipt",
    "write_receipt",
    "default_out_path",
    "api_base",
]
