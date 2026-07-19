#!/usr/bin/env python3
"""NOOS supervision adapter for the canonical NOETFIELD-RUNWAY runtime (Mission 5).

NOOS only OBSERVES and SUPERVISES the Runway. It never copies a Runway recipe or
Motor implementation into this repo (ownership is NOETFIELD-RUNWAY).

Pipeline:
  Runway job/event  → durable NOOS observation
                    → stale / budget / provider detection
                    → machine repair / fallback dispatch decision
                    → terminal receipt observation
                    → founder escalation ONLY for genuine authority.

If the canonical Runway API is not deployed (no ``NOETFIELD_RUNWAY_API_URL``),
``preflight`` returns BLOCKED_RUNWAY_API_NOT_LIVE with the exact required URL,
auth interface and event schema. The detection functions are PURE and are proven
offline against the frozen contract; no live connection is simulated.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/noetfield-runway-contract-v1.json"

BLOCKED_RUNWAY_API_NOT_LIVE = "BLOCKED_RUNWAY_API_NOT_LIVE"


def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


def preflight() -> dict[str, Any]:
    """Verify the canonical Runway API is live; else exact blocker."""
    contract = load_contract()
    req = contract.get("required_runtime") or {}
    url = (os.environ.get(str(req.get("url_env") or "NOETFIELD_RUNWAY_API_URL")) or "").strip()
    if url:
        return {"ok": True, "verdict": "RUNWAY_API_CONFIGURED", "base_url_present": True}
    return {
        "ok": False,
        "verdict": BLOCKED_RUNWAY_API_NOT_LIVE,
        "required_url_env": req.get("url_env"),
        "required_auth_env": req.get("auth_env"),
        "auth_interface": req.get("auth_interface"),
        "endpoints": req.get("endpoints"),
        "event_schema": contract.get("job_event_schema"),
        "owner_repository": contract.get("owner_repository"),
        "unblock_action": (
            "Deploy NOETFIELD-RUNWAY and set NOETFIELD_RUNWAY_API_URL + "
            "NOETFIELD_RUNWAY_API_TOKEN in the noetfeld-os supervision environment."
        ),
    }


def observe_job(job_event: dict[str, Any]) -> dict[str, Any]:
    """Map a Runway job/event into a durable NOOS observation record."""
    return {
        "schema": "noos-runway-observation-v1",
        "observed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "job_id": job_event.get("job_id"),
        "recipe_id": job_event.get("recipe_id"),
        "state": job_event.get("state"),
        "started_at": job_event.get("started_at"),
        "updated_at": job_event.get("updated_at"),
        "budget": job_event.get("budget") or {},
        "provider": job_event.get("provider") or {},
        "terminal_receipt": job_event.get("terminal_receipt"),
    }


def detect_conditions(observation: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Pure stale/budget/provider detection → dispatch decision.

    Returns findings + a single dispatch decision:
      - repair          (stale or FAILED)
      - fallback        (provider unhealthy or budget stop)
      - none            (healthy / terminal COMPLETE)
    and whether founder escalation is genuinely required (budget ceiling breach).
    """
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
        if age_min > stale_after and state not in ("COMPLETE",):
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

    # Decision precedence: budget stop → fallback+founder; provider → fallback;
    # stale/FAILED → repair; BLOCKED → founder; else none.
    decision = "none"
    founder = False
    if budget_stop:
        decision = "fallback"
        founder = True  # genuine authority: spend ceiling breached
    elif provider_unhealthy:
        decision = "fallback"
    elif stale or state == "FAILED":
        decision = "repair"
    elif state == "BLOCKED":
        decision = "none"
        founder = True

    return {
        "schema": "noos-runway-detection-v1",
        "job_id": observation.get("job_id"),
        "findings": findings,
        "dispatch_decision": decision,
        "founder_escalation": founder,
        "budget_ratio": round(ratio, 4),
    }


def supervise(job_event: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Full offline supervision pass over one job event (no live connection)."""
    obs = observe_job(job_event)
    det = detect_conditions(obs, now=now)
    return {"observation": obs, "detection": det}


def main() -> int:
    pf = preflight()
    print(json.dumps(pf, indent=2))
    return 0 if pf.get("ok") else 3


if __name__ == "__main__":
    raise SystemExit(main())
