#!/usr/bin/env python3
"""NOOS supervision adapter for canonical NOETFIELD-RUNWAY (HMAC cloud runtime).

NOOS observes and submits intake. It never copies Motor/provider routing/sandbox
execution. DeepSeek calls stay inside Runway ResilientRouter.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/noetfield-runway-contract-v1.json"
BLOCKED_RUNWAY_API_NOT_LIVE = "BLOCKED_RUNWAY_API_NOT_LIVE"
HTTP_TIMEOUT = 30


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


def sign_hmac_request(
    *,
    secret: str,
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
) -> str:
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body_hash}"
    return hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()


def runtime_env() -> dict[str, str]:
    contract = load_contract()
    req = contract.get("required_runtime") or {}
    url = (os.environ.get(str(req.get("url_env") or "NOETFIELD_RUNWAY_API_URL")) or "").strip().rstrip("/")
    secret = (os.environ.get(str(req.get("auth_env") or "NOETFIELD_RUNWAY_API_SECRET")) or "").strip()
    if not secret:
        secret = (os.environ.get(str(req.get("auth_legacy_env") or "NOETFIELD_RUNWAY_API_TOKEN")) or "").strip()
    key_id = (
        os.environ.get(str(req.get("key_id_env") or "NOETFIELD_RUNWAY_API_KEY_ID"))
        or str(req.get("key_id_default") or "staging-proof")
    ).strip()
    return {"url": url, "secret": secret, "key_id": key_id}


def preflight() -> dict[str, Any]:
    contract = load_contract()
    req = contract.get("required_runtime") or {}
    env = runtime_env()
    pin = contract.get("deepseek_pin") or {}
    if not env["url"]:
        return {
            "ok": False,
            "verdict": BLOCKED_RUNWAY_API_NOT_LIVE,
            "required_url_env": req.get("url_env"),
            "required_auth_env": req.get("auth_env"),
            "auth_interface": req.get("auth_interface"),
            "endpoints": req.get("endpoints"),
            "deepseek_pin": pin,
            "owner_repository": contract.get("owner_repository"),
            "unblock_action": (
                "Deploy runway-cloud-runtime and set NOETFIELD_RUNWAY_API_URL + "
                "NOETFIELD_RUNWAY_API_SECRET (+ KEY_ID) in the NOOS supervision environment."
            ),
        }
    if not env["secret"]:
        return {
            "ok": False,
            "verdict": "BLOCKED_RUNWAY_HMAC_SECRET_MISSING",
            "required_auth_env": req.get("auth_env"),
            "auth_interface": req.get("auth_interface"),
            "base_url_present": True,
        }
    return {
        "ok": True,
        "verdict": "RUNWAY_API_CONFIGURED",
        "base_url_present": True,
        "auth_mode": "NOETFIELD-HMAC",
        "key_id": env["key_id"],
        "deepseek_pin": pin,
        "endpoints": req.get("endpoints"),
    }


def hmac_request(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: int = HTTP_TIMEOUT,
) -> dict[str, Any]:
    env = runtime_env()
    if not env["url"] or not env["secret"]:
        return {"ok": False, "error": BLOCKED_RUNWAY_API_NOT_LIVE}
    body = b"" if payload is None else json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    timestamp = utc_now()
    nonce = secrets.token_hex(16)
    signature = sign_hmac_request(
        secret=env["secret"],
        method=method,
        path=path,
        timestamp=timestamp,
        nonce=nonce,
        body=body,
    )
    url = urljoin(env["url"] + "/", path.lstrip("/"))
    headers = {
        "Authorization": f"NOETFIELD-HMAC {env['key_id']}:{signature}",
        "x-noetfield-timestamp": timestamp,
        "x-noetfield-nonce": nonce,
        "Content-Type": "application/json",
        "User-Agent": "noos-runway-supervision-adapter-v2",
    }
    req = urllib.request.Request(url, data=body if method.upper() != "GET" else None, method=method.upper(), headers=headers)
    if method.upper() == "GET":
        req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw) if raw else {}
            return {"ok": resp.status < 300, "status": resp.status, "body": data}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")[:500]
        try:
            parsed = json.loads(err_body)
        except json.JSONDecodeError:
            parsed = {"raw": err_body}
        return {"ok": False, "status": exc.code, "body": parsed, "error": err_body[:240]}
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:240]}


def queue_summary() -> dict[str, Any]:
    return hmac_request("GET", "/v1/queue/summary")


def get_job(job_id: str) -> dict[str, Any]:
    return hmac_request("GET", f"/v1/jobs/{job_id}")


def submit_intake(intake: dict[str, Any]) -> dict[str, Any]:
    """POST /v1/intake with a validated job-intake envelope. Advance only on ack."""
    contract = load_contract()
    defaults = contract.get("intake_defaults") or {}
    payload = {
        "schema": "noetfield.job-intake.v0.1",
        "tenant_id": intake.get("tenant_id") or defaults.get("tenant_id") or "noetfield.noos",
        "entitlement_id": intake.get("entitlement_id") or defaults.get("entitlement_id") or "noos.plan-completion.v1",
        "runway_id": intake["runway_id"],
        "recipe_id": intake["recipe_id"],
        "recipe_version": intake["recipe_version"],
        "idempotency_key": intake["idempotency_key"],
        "requested_at": intake.get("requested_at") or utc_now(),
        "caller_site": intake.get("caller_site") or defaults.get("caller_site") or "internal",
        "budget_usd": float(intake.get("budget_usd") or defaults.get("budget_usd_default") or 0.25),
        "input": intake.get("input") or {},
    }
    if intake.get("callback_url"):
        payload["callback_url"] = intake["callback_url"]
    result = hmac_request("POST", "/v1/intake", payload=payload)
    result["op_key"] = payload["idempotency_key"]
    result["intake"] = payload
    return result


def observe_job(job_event: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "noos-runway-observation-v1",
        "observed_at": utc_now(),
        "job_id": job_event.get("job_id"),
        "recipe_id": job_event.get("recipe_id"),
        "state": job_event.get("state") or job_event.get("status"),
        "started_at": job_event.get("started_at"),
        "updated_at": job_event.get("updated_at"),
        "budget": job_event.get("budget") or {},
        "provider": job_event.get("provider") or {},
        "terminal_receipt": job_event.get("terminal_receipt"),
        "op_key": job_event.get("op_key") or job_event.get("idempotency_key"),
    }


def detect_conditions(observation: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    contract = load_contract()
    d = contract.get("detection_defaults") or {}
    stale_after = float(d.get("stale_after_minutes") or 30)
    warn_ratio = float(d.get("budget_warn_ratio") or 0.8)
    stop_ratio = float(d.get("budget_stop_ratio") or 1.0)
    now = now or datetime.now(timezone.utc)

    findings: list[str] = []
    state = str(observation.get("state") or "").upper()

    updated = _parse_iso(observation.get("updated_at"))
    stale = False
    if updated is not None:
        age_min = (now - updated).total_seconds() / 60.0
        if age_min > stale_after and state not in ("COMPLETE", "DONE"):
            stale = True
            findings.append(f"stale:{int(age_min)}m>{int(stale_after)}m")

    budget = observation.get("budget") or {}
    spent = float(budget.get("spent_usd") or 0.0)
    ceiling = float(budget.get("ceiling_usd") or 0.0)
    ratio = (spent / ceiling) if ceiling > 0 else 0.0
    budget_stop = ceiling > 0 and ratio >= stop_ratio
    budget_warn = ceiling > 0 and warn_ratio <= ratio < stop_ratio
    if budget_stop:
        findings.append(f"budget_stop:{ratio:.2f}")
    elif budget_warn:
        findings.append(f"budget_warn:{ratio:.2f}")

    provider = observation.get("provider") or {}
    provider_unhealthy = provider.get("healthy") is False
    if provider_unhealthy:
        findings.append(f"provider_unhealthy:{provider.get('name')}")

    decision = "none"
    founder = False
    if budget_stop:
        decision = "fallback"
        founder = True
    elif provider_unhealthy:
        decision = "fallback"
    elif stale or state in ("FAILED", "FAILED_WITH_RECEIPT"):
        decision = "repair"
    elif state in ("BLOCKED", "BLOCKED_WITH_REASON"):
        decision = "none"
        founder = True

    return {
        "schema": "noos-runway-detection-v1",
        "job_id": observation.get("job_id"),
        "findings": findings,
        "dispatch_decision": decision,
        "founder_escalation": founder,
        "budget_ratio": round(ratio, 4),
        "note": "repair/fallback are internal Runway RPCs; NOOS records the decision and re-intakes with same op_key when authorized",
    }


def supervise(job_event: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    obs = observe_job(job_event)
    det = detect_conditions(obs, now=now)
    return {"observation": obs, "detection": det}


def verify_deepseek_pin() -> dict[str, Any]:
    """Fail-closed pin check against the locked contract (no live DeepSeek call from NOOS)."""
    contract = load_contract()
    pin = contract.get("deepseek_pin") or {}
    cheap = str(pin.get("cheap_primary") or "")
    standard = str(pin.get("standard_fallback") or "")
    forbidden = set(pin.get("forbidden") or [])
    ok = (
        cheap == "deepseek-v4-flash"
        and standard == "deepseek-v4-pro"
        and "deepseek-chat_as_production_pin" in forbidden
        and pin.get("fail_closed_if_unavailable") is True
    )
    return {
        "schema": "noos-deepseek-pin-verify-v1",
        "ok": ok,
        "cheap_primary": cheap,
        "standard_fallback": standard,
        "fail_closed_if_unavailable": pin.get("fail_closed_if_unavailable"),
        "report_line": "deepseek_pin_ok" if ok else "deepseek_pin_drift",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight").set_defaults(func=lambda _a: preflight())
    sub.add_parser("queue-summary").set_defaults(func=lambda _a: queue_summary())
    sub.add_parser("verify-deepseek-pin").set_defaults(func=lambda _a: verify_deepseek_pin())
    g = sub.add_parser("get-job")
    g.add_argument("--job-id", required=True)
    g.set_defaults(func=lambda a: get_job(a.job_id))
    args = parser.parse_args(argv)
    row = args.func(args)
    print(json.dumps(row, indent=2) if args.json or True else row)
    return 0 if row.get("ok") is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())
