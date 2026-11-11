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


# Internal, evidence-bound operating fallback for a saturated specialist provider.
# A rule-derived plan is not model inference, verified achievement, a WorkPacket
# execution permit or permission to publish/outreach/move funds.
ROLE_PLANS = {
    "marketing_content": {
        "action": "Prepare three shareable, accurate 7-day open-ask invitations, each with a distinct signup-source tag. Link only to actual published BuildRelay asks; queue publishing for the authorized operator.",
        "acceptance": "Three source-tagged drafts and a measured comparison of server-created attributed signups; count clicks as views only.",
        "metric": "attributed_signups",
    },
    "product_strategy": {
        "action": "Map join -> builder-card completion -> mutual introduction -> seven-day sprint -> bilateral receipt, then choose the earliest observed low-conversion stage and define one testable improvement.",
        "acceptance": "One written activation hypothesis, exact existing API route, measurable target event and a clear zero-data fallback.",
        "metric": "ready_profiles",
    },
    "engineering_operator": {
        "action": "Build a bounded pull request for the first measured activation friction in BuildRelay itself; preserve anonymous discovery, referral code integrity and source attribution.",
        "acceptance": "Passing signup and mobile Chromium tests, merged reviewable diff and confirmed Railway release SHA; no invented user outcomes.",
        "metric": "activation_critical_tests_pass",
    },
    "customer_success": {
        "action": "Draft a concise first-session sequence: finish an optional profile, join a guild, respond to one relevant ask, and start a 7-day sprint. No unsolicited messages.",
        "acceptance": "Member-facing, consent-respecting onboarding proposal with one first-action CTA and a real D1/D7 return measurement.",
        "metric": "activated_members",
    },
    "market_intelligence": {
        "action": "Compare three currently operating global founder/cofounder/community platforms on onboarding, matching, invite loops and collaboration proof; identify one implementable differentiated experiment.",
        "acceptance": "Dated primary source links, copied mechanics identified, user-benefit hypothesis and one test without invented partnership or market size.",
        "metric": "experiment_activated",
    },
    "chief_of_staff": {
        "action": "Coordinate Engineering, Growth, Community and QA around the next highest-value BuildRelay member activation or verified collaboration milestone; give a single owner and seven-day definition of done.",
        "acceptance": "One prioritized execution packet with owner, repo path, realistic test, rollout evidence and observed versus unverified outcome separated.",
        "metric": "bilateral_receipts_completed",
    },
    "risk_governance": {
        "action": "Check referral anti-farming, moderation queue, tenant separation, bilateral receipt provenance and zero unsupported token/payment claims before publishing new Season 0 copy.",
        "acceptance": "Focused tests or evidence checks tied to the existing BuildRelay database and one actionable issue per genuine failure.",
        "metric": "verified_receipt_integrity",
    },
    "roi_analyst": {
        "action": "Separate actual provider-backed fee records, unreconciled transfers, participation points and potential future token economics. Do not label funding, nonbinding interests or tests as money.",
        "acceptance": "Evidence-classified economics table with real collected revenue explicitly null until independently reconciled.",
        "metric": "independently_confirmed_platform_revenue",
    },
    "partnerships": {
        "action": "Identify founder groups or accelerator pathways suitable for a reciprocal 7-day building challenge; prepare consent-first introduction drafts rather than claiming a partnership.",
        "acceptance": "Three researched candidates, official URLs and a founder-reviewable proposal grounded in an actual BuildRelay opportunity.",
        "metric": "confirmed_mutual_introductions",
    },
}


def specialist_continuity(task: dict) -> dict | None:
    """Bounded, role-specific result from an EXISTING BuildRelay observation.

    Survives rate-limited agent inference and remains an internal, unexecuted
    action candidate. No fake traffic, program award or job execution.
    """
    if (not isinstance(task, dict)
            or task.get("company_id") != COMPANY
            or task.get("project_id") != PROJECT
            or task.get("role") not in ROLE_PLANS
            or not isinstance(task.get("observation_id"), str)):
        return None
    with core.connect() as db:
        row = db.execute(
            "SELECT id,source_event_id,source_ref,signal,metric_name,metric_value,"
            "verification,observed_at FROM product_observations "
            "WHERE id=? AND company_id=? AND project_id=?",
            (task["observation_id"], COMPANY, PROJECT)).fetchone()
    if not row:
        return None
    p = ROLE_PLANS[task["role"]]
    current = {
        "name": row["metric_name"] or "not_reported",
        "value": row["metric_value"],
        "observed_at": row["observed_at"],
        "verification": row["verification"],
        "evidence_ref": row["source_ref"],
    }
    if row["verification"] not in ("SOURCE_REPORTED_UNVERIFIED", "FIRST_PARTY_HTTP_TRANSPORT_OBSERVED"):
        return None
    return {
        "schema": "buildrelay.company-os.internal-specialist-continuity.v1",
        "status": "INTERNAL_DRAFT_NOT_EXECUTED",
        "project_id": PROJECT,
        "company_scope": COMPANY,
        "owner_role": task["role"],
        "source_observation_id": row["id"],
        "observed_metric": current,
        "assessment": (
            "A source-reported BuildRelay metric was recorded. "
            "It may include test accounts. A bounded next step can be drafted "
            "without claiming a model response or real business conversion."
        ),
        "next_best_action": p["action"],
        "success_metric": p["metric"],
        "acceptance_criteria": p["acceptance"],
        "seven_day_window": True,
        "authority": "DRAFT_ONLY_NO_EXTERNAL_EFFECT",
        "founder_intent": (
            "Global pseudonymous startup/community execution network. Keep "
            "quests, referrals, Season 0 and contribution receipts; do not pivot "
            "to consulting, another dashboard, Cairn or another venture."
        ),
        "independent_outcome_verified": False,
        "provider": "deterministic_evidence_rulebook",
        "model_inference_performed_by_fallback": False,
    }
