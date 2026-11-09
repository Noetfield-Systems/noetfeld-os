"""Commercial role commissioning on the existing Business OS task queue.

No autonomous outreach, helpdesk replies, publishing or new scheduler is created.
Task preparation follows the existing role executor and Founder approval rules.
"""
from __future__ import annotations

import json
from typing import Any

import core

SCHEMA = "noetfield.commercial-team.v1"
BRANDS = {
    "noetfield": {
        "project": "noetfield-commercial",
        "offer": "Bounded governed execution, workflow review and agent assurance",
        "claims": "Founder-operated alpha; first-party proof is not customer certification",
    },
    "trustfield": {
        "project": "trustfield-commercial",
        "offer": "FINTRAC case operations and engineer-reviewed workflow configuration",
        "claims": "Human FILE/NO-FILE authority, no custody/settlement or auto-filing",
    },
    "signalforge": {
        "project": "signalforge-commercial",
        "offer": "Research terminal, explainable signals and historical backtests",
        "claims": "Research-only, no broker execution or investment-performance guarantee",
    },
}

ROLE_TASKS = {
    "sales_qualification": {
        "seat": "N-05",
        "title": "Commercial lead qualification and proposal preparation",
        "objective": "Review approved website offers and genuine opt-in inbound interest. Distinguish qualified buyers from experiments and prepare one evidence-grounded discovery brief. Never claim pipeline or revenue without real records.",
        "next_action": "Produce a draft discovery plan, a qualification checklist and a human-approvable follow-up. Do not contact anyone.",
    },
    "customer_success": {
        "seat": "N-07",
        "title": "Support intake classification and knowledge-grounded response",
        "objective": "Inspect available support intake routing and approved product knowledge. Define a first-line classification tree, response evidence requirements, urgent escalation and identity checks before replying.",
        "next_action": "Produce a support triage rubric and an approval-ready reply template. No customer reply or ticket transmission is authorized.",
    },
    "marketing_editorial": {
        "seat": "N-06",
        "title": "Marketing content production from verified product evidence",
        "objective": "Prepare an evidence-based campaign brief, webpage copy improvements and one social draft using approved product facts. Explicitly label alpha status and reject invented customers, performance and ROI.",
        "next_action": "Produce a claims matrix, a proposed content draft and a review checklist. Do not publish or distribute.",
    },
}


def _state_key(brand: str) -> str:
    return "company_os_commercial_team_v1:" + brand


def _require_brand(brand: str) -> None:
    if brand not in BRANDS:
        raise ValueError("Unsupported commercial project brand.")


def commission(brand: str) -> dict[str, Any]:
    """Idempotently enqueue one bounded internal task for each existing role."""
    _require_brand(brand)
    for role, spec in ROLE_TASKS.items():
        if core.company_role_for_runtime(role)["role_id"] != spec["seat"]:
            raise RuntimeError("Role registry / runtime authority mismatch.")
    with core.connect() as db:
        existing = db.execute("SELECT value FROM state WHERE key=?", (_state_key(brand),)).fetchone()
        if existing:
            recorded = json.loads(existing["value"])
            return {
                "schema": SCHEMA,
                "brand": brand,
                "already_commissioned": True,
                "task_ids": recorded["task_ids"],
                "external_actions": 0,
                "autonomy": "internal_draft_only",
            }
        task_ids = {}
        for role, spec in ROLE_TASKS.items():
            role_objective = spec["objective"] + " Product boundary: " + BRANDS[brand]["claims"]
            task_ids[role] = core.add_task(
                db, None, None, brand, role,
                spec["title"],
                role_objective,
                spec["next_action"],
            )
        db.execute(
            "INSERT INTO state(key,value) VALUES(?,?)",
            (_state_key(brand), json.dumps({
                "schema": SCHEMA,
                "project": BRANDS[brand]["project"],
                "task_ids": task_ids,
                "commissioned_at": core.now(),
                "offer": BRANDS[brand]["offer"],
            }, sort_keys=True)),
        )
    return {
        "schema": SCHEMA,
        "brand": brand,
        "already_commissioned": False,
        "task_ids": task_ids,
        "external_actions": 0,
        "autonomy": "internal_draft_only",
    }


def status(brand: str) -> dict[str, Any]:
    """Return evidence from existing task storage, not a synthetic active badge."""
    _require_brand(brand)
    with core.connect() as db:
        row = db.execute("SELECT value FROM state WHERE key=?", (_state_key(brand),)).fetchone()
        if not row:
            return {
                "schema": SCHEMA,
                "brand": brand,
                "state": "not_commissioned",
                "roles": [{
                    "runtime_role": role,
                    "company_seat": spec["seat"],
                    "task_state": "not_created",
                } for role, spec in ROLE_TASKS.items()],
                "external_actions": 0,
            }
        saved = json.loads(row["value"])
        roles = []
        for role, spec in ROLE_TASKS.items():
            task_id = saved["task_ids"][role]
            task = db.execute(
                "SELECT id,status,updated_at FROM tasks WHERE id=? AND brand=? AND role=?",
                (task_id, brand, role),
            ).fetchone()
            roles.append({
                "runtime_role": role,
                "company_seat": spec["seat"],
                "task_id": task_id,
                "task_state": task["status"] if task else "missing",
                "last_updated": task["updated_at"] if task else None,
                "live_connector_verified": False,
            })
    return {
        "schema": SCHEMA,
        "brand": brand,
        "state": "internal_commissioning",
        "project": saved["project"],
        "roles": roles,
        "external_actions": 0,
        "note": "A drafted internal task is not an active customer-facing agent.",
    }
