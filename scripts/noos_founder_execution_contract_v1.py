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
    "crypto_native_market_reality": {
        "canonical_law": "Noetfield-Systems/sina-governance-SSOT/ssot/CRYPTO_NATIVE_MARKET_REALITY_LAW_v1.md",
        "machine_contract": "Noetfield-Systems/sina-governance-SSOT/data/crypto_native_benchmark_contract_v1.json",
        "source_mechanism_candidate_ids": "BuildRelay P01-P20 = mixed tactic/policy references, NEVER twenty proven success patterns",
        "case_sequence_catalog": "Noetfield-Systems/sina-governance-SSOT/data/crypto_native_case_sequences_v1.json",
        "operating_strategy_catalog": "Noetfield-Systems/sina-governance-SSOT/data/crypto_native_derived_operating_patterns_v1.json",
        "semantic_contract": "SOURCE != BENCHMARK != MECHANISM != CHRONOLOGICAL_CASE != REPLICATED_SUCCESS_PATTERN",
        "canonical_typed_ontology": "Noetfield-Systems/sina-governance-SSOT/data/DISCOVERY_STUDIO_ONTOLOGY_v1.json",
        "source_dictionary_precedence": "one SSOT meaning over model interpretation; 13 typed objects",
        "research_admission_rule": "source URL and competitor names are never patterns; pattern requires ordered real actions, date, observed outcome, alternate explanations, venture experiment; unverified AI proposal may not self-promote to observed fact",
        "priority": "FOLLOW_WINNING_CRYPTO_NATIVE_TRAJECTORIES",
        "directive": (
            "For any material crypto-native product, growth, brand, funding, token, community "
            "or UI/UX change, inspect live relevant competitors, especially how their founders "
            "sequence narrative, premium visual design, community, networking, capital, and "
            "technical delivery. Copy lawful success mechanisms and proven flow patterns "
            "without copying protected assets or fabricating market outcomes. Early traction "
            "and brand/community are valid priorities; do not substitute lengthy backend "
            "architecture or generic SaaS for the Founder market objective. Choose a bounded "
            "market-facing original-venture implementation, preserve independent venture "
            "economies, use only existing Company OS and Runway, and write honest source evidence. "
            "Benchmarking is part of the work, not a new launch/approval gate."
        ),
        "spend_and_real_traction_unknown_until_source_verified": True,
        "extra_queue_or_governor_allowed": False,
    },
    "not_an_external_action_permit": True,
}
