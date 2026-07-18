#!/usr/bin/env python3
"""NOOS Software Repair — three independent health domains (§1) + product-specific
canonical producer provenance (§2).

NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 activation. This module makes Software Repair
PRODUCT health independent of the legacy Railway/Fly ``http_loop`` PLATFORM loop:

  A. platform_loop  — legacy general NOOS cloud loop (Railway/Fly http_loop). May
                      remain degraded; tracked as a SEPARATE operations incident.
  B. product        — the deployed Software Repair execution chain.
  C. customer_job   — one specific customer commission.

A failure in (A) must not invalidate a healthy (B). A successful (B) job must not
falsely mark (A) healthy. All three are exposed separately.

PRODUCT canonical producer (§2):
  producer:        github_actions_software_repair_v1
  execution_plane: github_actions

A Software Repair receipt is receipt_origin=organic ONLY when all 15 conditions
below hold (authoritative commission + correlated job lineage determine organic —
NOT the GitHub event name alone). A workflow_dispatch diagnostic without an
authoritative job is receipt_origin=manual; a test run is test; a local run is
local_reference; a synthetic writer is repair.
"""

from __future__ import annotations

from typing import Any

# ---- Product canonical producer / plane (§2) -------------------------------
PRODUCT_PRODUCER = "github_actions_software_repair_v1"
PRODUCT_EXECUTION_PLANE = "github_actions"
PRODUCT_PRODUCERS = frozenset({PRODUCT_PRODUCER})
PRODUCT_PLANES = frozenset({PRODUCT_EXECUTION_PLANE})

# Origins that can never establish PRODUCT organic liveness.
NON_PRODUCT_ORGANIC_ORIGINS = frozenset(
    {"manual", "test", "local_reference", "repair", "replay", "migration", "legacy_unknown"}
)

# The 15 conditions (§2) — every one must be provable from the authoritative
# store + workflow evidence before a receipt may be receipt_origin=organic.
ORGANIC_CONDITIONS = (
    "commission_persisted",           # 1 commission exists in the authoritative store
    "job_persisted",                  # 2 job exists in the authoritative store
    "dispatch_id_unique",             # 3 unique dispatch id
    "idempotency_key_unique",         # 4 unique idempotency key
    "workflow_received_job",          # 5 workflow received that exact job+dispatch
    "workflow_run_id_captured",       # 6 workflow run id captured
    "workflow_commit_sha_captured",   # 7 workflow commit sha captured
    "recipe_and_schema_versions",     # 8 recipe + schema versions captured
    "claimed_under_valid_lease",      # 9 job claimed under a valid lease
    "valid_lifecycle_ordering",       # 10 valid lifecycle ordering
    "tests_actually_ran",             # 11 tests/verification actually ran
    "artifacts_produced",             # 12 artifacts produced
    "output_hashes_verified",         # 13 output hashes verify
    "callback_authenticated",         # 14 completion callback authenticated
    "authoritative_terminal_persisted",  # 15 authoritative terminal state persisted
)


def product_organic_confirmed(evidence: dict[str, Any]) -> dict[str, Any]:
    """Return the PRODUCT-organic decision. receipt_origin may be 'organic' ONLY
    when the producer + plane are canonical AND all 15 conditions are proven true.

    ``evidence`` supplies the producer, execution_plane, and each condition flag.
    Missing/false conditions are reported explicitly; nothing is guessed."""
    producer = evidence.get("producer")
    plane = evidence.get("execution_plane")
    conds = {c: bool(evidence.get(c)) for c in ORGANIC_CONDITIONS}
    producer_ok = producer in PRODUCT_PRODUCERS
    plane_ok = plane in PRODUCT_PLANES
    all_conditions = all(conds.values())
    organic = producer_ok and plane_ok and all_conditions
    failed = [c for c, v in conds.items() if not v]
    if not producer_ok:
        failed = ["producer_not_canonical", *failed]
    if not plane_ok:
        failed = ["plane_not_canonical", *failed]
    return {
        "product_organic_confirmed": organic,
        "receipt_origin": "organic" if organic else _fallback_origin(evidence),
        "producer_canonical": producer_ok,
        "plane_canonical": plane_ok,
        "conditions": conds,
        "failed_conditions": failed,
    }


def _fallback_origin(evidence: dict[str, Any]) -> str:
    """Honest origin when the organic gate is not met. A github_actions run
    WITHOUT an authoritative commission is a diagnostic -> manual; a test -> test;
    a local run -> local_reference."""
    declared = str(evidence.get("declared_origin") or "").strip().lower()
    if declared in NON_PRODUCT_ORGANIC_ORIGINS:
        return declared
    if not evidence.get("commission_persisted"):
        return "manual"   # §2: workflow_dispatch/diagnostic without an authoritative job
    return "manual"


# ---- Three independent health domains (§1) ---------------------------------
def health_domains(
    *,
    platform_loop: dict[str, Any] | None = None,
    product: dict[str, Any] | None = None,
    customer_job: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose the three SEPARATE health states for the cockpit. Each domain is
    reported independently; one does not overwrite another."""
    return {
        "schema": "noos-software-repair-health-v1",
        "domains": {
            "A_platform_loop": _platform_health(platform_loop or {}),
            "B_product": _product_health(product or {}),
            "C_customer_job": _customer_job_health(customer_job or {}),
        },
        "invariants": [
            "platform_loop degradation does NOT invalidate a healthy product chain",
            "a healthy product job does NOT mark the platform loop healthy",
        ],
    }


def _platform_health(p: dict[str, Any]) -> dict[str, Any]:
    return {
        "producer": p.get("producer", "railway/fly:http_loop"),
        "state": p.get("state", "SEPARATE_OPERATIONS_INCIDENT"),
        "note": "legacy general NOOS cloud loop; may remain degraded; tracked separately",
        "last_organic_completion_at": p.get("last_organic_completion_at"),
    }


def _product_health(p: dict[str, Any]) -> dict[str, Any]:
    # Product is RUNNING_CONFIRMED only from product-organic evidence.
    org = p.get("last_product_organic")
    confirmed = bool(org and product_organic_confirmed(org)["product_organic_confirmed"])
    return {
        "producer": PRODUCT_PRODUCER,
        "execution_plane": PRODUCT_EXECUTION_PLANE,
        "state": "RUNNING_CONFIRMED" if confirmed else p.get("state", "NOT_YET_PROVEN"),
        "authoritative_persistence": p.get("authoritative_persistence", "unknown"),
        "last_product_organic_confirmed": confirmed,
    }


def _customer_job_health(c: dict[str, Any]) -> dict[str, Any]:
    state = str(c.get("state") or "unknown")
    valid = {"completed", "failed", "timed_out", "cancelled", "dead_lettered", "awaiting_customer_approval", "unknown"}
    return {
        "commission_id": c.get("commission_id"),
        "state": state if state in valid else "unknown",
        "job_id": c.get("job_id"),
    }
