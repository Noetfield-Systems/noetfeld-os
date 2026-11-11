"""Shared Founder thesis-preservation payload for NOOS -> Runway intake.

Canonical source is Sina Founder OS doctrine and its authenticated decision API.
This is an execution preference, not an external action permit. Keep one local
fallback constant for already-approved work if the upstream endpoint is offline.
"""
from __future__ import annotations

FOUNDER_EXECUTION_CONTRACT = {
    "schema": "sina.founder-execution-contract.v1",
    "version": "2026-11-11.3",
    "canonical_policy": "sina_founder_os/portfolio/FOUNDER-DECISION-DOCTRINE-v1.json",
    "decision_endpoint": "POST /api/v2/agent/decision",
    "goal_precedence": "EXPLICIT_FOUNDER_THESIS_AND_CANONICAL_PROJECT_GOAL_FIRST",
    "risk_appetite": "HIGH_COMMERCIAL_MARKET_PRODUCT_SPECULATIVE_RISK_ACCEPTED",
    "directive": (
        "Execute the Founder's actual project thesis at speed. Commercial market risk "
        "is accepted, not a discretionary review gate. Do not pivot a Web3, DEX, token, "
        "exchange, airdrop, community or network-growth thesis into B2B consulting, "
        "Stripe audit, generic SaaS, a dashboard, report or infrastructure-only goal. "
        "Implement scoped authorized reversible work and actual user-facing flows. "
        "For relevant ventures include stage-appropriate Token/Airdrop/Referral/Quest/"
        "Season 0 and real user acquisition. Flag FOUNDER INTENT DRIFT and repair "
        "unsupported gates or thesis substitution. Preserve real legal, tenant, "
        "security, financial settlement and owner authority boundaries. "
        "Report coded, tested, deployed, real user, on-chain and cash facts separately."
    ),
    "drift_signal": "FOUNDER INTENT DRIFT",
    "not_an_external_action_permit": True,
}
