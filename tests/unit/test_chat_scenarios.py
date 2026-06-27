"""Ten real-world client scenarios — retrieval must surface correct knowledge."""

from __future__ import annotations

import pytest

from noetfield_governance.chatbot_knowledge import (
    detect_question_lanes,
    select_relevant_excerpt,
)

SCENARIOS = (
    {
        "id": "sme_mortgage_broker",
        "question": "We are a mortgage broker in Toronto — what do you offer and what does it cost?",
        "lanes": ["sme"],
        "must_include": ("Diagnostic Sprint", "$2,500", "Copilot Governance Pack", "Trust Brief"),
    },
    {
        "id": "gel_vs_homepage",
        "question": "What is GEL and how is it different from your homepage?",
        "lanes": ["gel"],
        "must_include": ("Governance Execution Layer", "/gel/", "www.noetfield.com"),
    },
    {
        "id": "pypi_org_form",
        "question": "I need to fill out PyPI organization form — anticipated usage for noetfield-gate?",
        "lanes": ["developer"],
        "must_include": ("noetfield-gate", "PyPI Organization", "Anticipated usage"),
    },
    {
        "id": "copilot_rollout",
        "question": "We run Microsoft Copilot — can you help with governance before rollout?",
        "lanes": [],
        "must_include": ("Copilot Governance Pack", "$2,000", "board PDF"),
    },
    {
        "id": "bank_shadow",
        "question": "Our bank wants read-only shadow mode — no execution rights. Do you have that?",
        "lanes": [],
        "must_include": ("Bank Pilot", "shadow", "read-only"),
    },
    {
        "id": "sandbox_limits",
        "question": "How do I start the free sandbox and what are the limits?",
        "lanes": [],
        "must_include": ("/start/", "14 days", "50 evaluate"),
    },
    {
        "id": "no_custody",
        "question": "Do you hold customer funds or process payments?",
        "lanes": [],
        "must_include": ("do not move money", "custody"),
    },
    {
        "id": "investor_diligence",
        "question": "We are an investor — where is diligence material?",
        "lanes": ["investor"],
        "must_include": ("/investors/diligence/", "investor"),
    },
    {
        "id": "trust_ledger_vs_brief",
        "question": "What is Trust Ledger and how is it different from Trust Brief?",
        "lanes": ["trust"],
        "must_include": ("Trust Ledger", "Trust Brief", "$10,000"),
    },
    {
        "id": "contact_rid",
        "question": "How do I contact you and what should I put in the email subject?",
        "lanes": [],
        "must_include": ("operations@noetfield.com", "RID"),
    },
)


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario_retrieval(scenario: dict) -> None:
    lanes = detect_question_lanes(scenario["question"])
    for expected_lane in scenario["lanes"]:
        assert expected_lane in lanes, f"expected lane {expected_lane}, got {lanes}"

    ctx = select_relevant_excerpt(scenario["question"]).lower()
    for phrase in scenario["must_include"]:
        assert phrase.lower() in ctx, f"missing {phrase!r} in context for {scenario['id']}"


def test_knowledge_corpus_size() -> None:
    ctx = select_relevant_excerpt("overview")
    assert len(ctx) > 20_000
    assert "gel-runtime.md" in ctx.lower() or "Governance Execution Layer" in ctx
