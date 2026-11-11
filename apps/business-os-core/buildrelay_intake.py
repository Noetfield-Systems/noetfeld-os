"""Dedicated BuildRelay intake into the *existing* Company OS product queue.

No separate tenant, job registry, scheduler, model, token economy, customer
ledger or portfolio-wide credential. Only aggregate observations for one
Founder-portfolio project are accepted. Outputs remain source-reported.
"""
from __future__ import annotations

import hmac
import json
import os
import re
from pathlib import Path
from typing import Any

import core
import product_loops

COMPANY = "founder-portfolio"
PROJECT = "buildrelay-bridge-economy"
SOURCE_URL = "https://buildrelay-staging-staging.up.railway.app/api/v1/growth-ops/snapshot"
SIGNALS = {
    "member_accounts": "acquisition",
    "ready_profiles": "activation",
    "bilateral_receipts": "community",
    "pending_moderation": "support",
    "d7_play_return_pct": "retention",
}
TOKEN_ENV = "BUILDRELAY_COMPANY_OS_BEARER"
SCHEMA = "buildrelay.company-os.observation.v1"
EVENT_ID = re.compile(r"^br-[0-9]{8}-[a-z0-9-]{3,45}$")


def authorized(header: str | None) -> bool:
    expected = os.getenv(TOKEN_ENV, "").strip()
    supplied = (header or "").removeprefix("Bearer ").strip()
    return bool(40 <= len(expected) <= 256 and supplied and
                hmac.compare_digest(supplied, expected))


def ensure_project() -> None:
    """Register only canonical BuildRelay projection when not already present."""
    with core.connect() as db:
        found = db.execute(
            "SELECT status FROM product_programs WHERE company_id=? AND project_id=?",
            (COMPANY, PROJECT)).fetchone()
    if found:
        if found["status"] not in product_loops.ACTIVE_STATES:
            raise ValueError("buildrelay_program_not_operational")
        return
    manifest = json.loads((Path(__file__).parent / "product_portfolio_seed_v1.json").read_text())
    entry = next((x for x in manifest["programs"] if
                  x["company_id"] == COMPANY and x["project_id"] == PROJECT), None)
    if not entry:
        raise ValueError("canonical_buildrelay_program_missing")
    product_loops.register(entry)


def accept(body: dict[str, Any]) -> dict:
    """No arbitrary project/metric, no identities, no synthetic customer claims."""
    if not isinstance(body, dict) or set(body) != {
        "schema", "source_event_id", "metric", "value", "observed_at"}:
        raise ValueError("buildrelay_payload_shape_invalid")
    event_id, metric = body["source_event_id"], body["metric"]
    value, observed_at = body["value"], body["observed_at"]
    if body["schema"] != SCHEMA or not isinstance(event_id, str) or not EVENT_ID.fullmatch(event_id):
        raise ValueError("buildrelay_event_invalid")
    if metric not in SIGNALS or not event_id.endswith("-" + metric.replace("_", "-")):
        raise ValueError("buildrelay_metric_invalid")
    if type(value) not in (int, float) or not 0 <= value <= 100000000:
        raise ValueError("buildrelay_value_invalid")
    if metric != "d7_play_return_pct" and type(value) is not int:
        raise ValueError("buildrelay_count_requires_integer")
    if not isinstance(observed_at, str):
        raise ValueError("buildrelay_observed_at_invalid")
    if metric == "d7_play_return_pct" and value > 100:
        raise ValueError("buildrelay_percentage_invalid")
    ensure_project()
    summary = (
        "BuildRelay source-reported aggregate " + metric + " = " + str(value) +
        ". Counts can include test registrations; external impact and real-user "
        "qualification are NOT independently verified."
    )
    result = product_loops.observe(COMPANY, PROJECT, {
        "source_event_id": event_id,
        "source_kind": "REPORTED_OPERATIONAL",
        "source_ref": SOURCE_URL,
        "signal": SIGNALS[metric],
        "metric_name": metric,
        "metric_value": value,
        "sample_count": 1,
        "summary": summary,
        "severity": 2 if metric == "pending_moderation" and value > 0 else 1,
        "observed_at": observed_at,
    })
    return {
        "accepted": True, "schema": SCHEMA, "company_id": COMPANY, "project_id": PROJECT,
        **result, "real_users_independently_verified": False,
        "token_or_financial_authority": False,
    }


def status() -> dict:
    with core.connect() as db:
        observations = [dict(x) for x in db.execute(
            "SELECT source_event_id,signal,metric_name,metric_value,verification,recorded_at "
            "FROM product_observations WHERE company_id=? AND project_id=? "
            "AND source_event_id LIKE 'br-%' ORDER BY recorded_at DESC LIMIT 12",
            (COMPANY, PROJECT)).fetchall()]
        total = db.execute(
            "SELECT COUNT(*) AS n FROM product_observations WHERE company_id=? AND project_id=? "
            "AND source_event_id LIKE 'br-%'", (COMPANY, PROJECT)).fetchone()["n"]
        states = [dict(x) for x in db.execute(
            "SELECT status,COUNT(*) AS count FROM tasks "
            "WHERE company_id=? AND project_id=? GROUP BY status",
            (COMPANY, PROJECT)).fetchall()]
        latest = [dict(x) for x in db.execute(
            "SELECT t.id,t.role,t.status,t.updated_at FROM tasks t "
            "WHERE t.company_id=? AND t.project_id=? ORDER BY t.updated_at DESC LIMIT 12",
            (COMPANY, PROJECT)).fetchall()]
    return {
        "schema": "buildrelay.company-os.execution-status.v1",
        "company_scope": COMPANY, "project_scope": PROJECT,
        "observation_count": total, "observations": observations,
        "task_states": {x["status"]: x["count"] for x in states},
        "latest_tasks": latest, "worker_queue": "EXISTING_COMPANY_OS_EVENTS_TASKS",
        "independent_business_outcome_verification": False,
    }
