"""Ten real-world client scenarios — retrieval must surface correct knowledge."""

from __future__ import annotations

import pytest

from noetfield_governance.chatbot_knowledge import (
    build_query_with_subject,
    detect_question_lanes,
    infer_subject_phrase,
    select_relevant_excerpt,
)
from noetfield_governance import chatbot_knowledge

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


def test_model_context_uses_public_source_labels() -> None:
    ctx = select_relevant_excerpt("What should I read before applying?")
    assert "## Source: Public product brief" in ctx
    assert "## Source: Public offerings" in ctx
    assert "PRODUCT_BRIEF.md" not in ctx
    assert "OFFERINGS_LOCKED.md" not in ctx


def test_knowledge_does_not_introduce_payment_custody_framing() -> None:
    ctx = select_relevant_excerpt("What is Noetfield?").lower()
    for phrase in ("move money", "hold custody", "execute transactions"):
        assert phrase not in ctx


def test_follow_up_question_tracks_active_subject() -> None:
    state = {
        "recent": [
            {
                "message": "Should the Intelligence tab stay in the main nav?",
                "reply_preview": "If Intelligence only points home, make it Home or create a real hub.",
            }
        ]
    }

    query, subject, follow_up = build_query_with_subject("why retired?", conversation_state=state)

    assert subject == "Intelligence"
    assert follow_up is True
    assert query == "Intelligence: why retired?"


def test_follow_up_retrieval_marks_conversation_kernel() -> None:
    state = {
        "recent": [
            {
                "message": "Should the Intelligence tab stay in the main nav?",
                "reply_preview": "Intelligence needs a distinct job or it should become Home.",
            }
        ]
    }

    ctx = select_relevant_excerpt("why retired?", conversation_state=state)

    assert "## Conversation Kernel" in ctx
    assert "Active subject: Intelligence" in ctx
    assert "Retrieval query: Intelligence: why retired?" in ctx


@pytest.mark.parametrize(
    ("entity", "prior_message", "follow_up"),
    (
        ("Federal", "What happened to the federal tab?", "why retired?"),
        ("Pricing", "Did the old pricing change?", "why changed?"),
        ("Trust Brief", "Was Trust Brief renamed?", "why renamed?"),
        ("Developer Sandbox", "Is the outdated intake path still used for the sandbox?", "why outdated?"),
        ("Copilot Governance Pack", "Was this SKU removed?", "why removed?"),
        ("Bank Pilot", "Is the deprecated program still sold?", "why deprecated?"),
        ("Templates", "Did the templates route change?", "why changed?"),
    ),
)
def test_lifecycle_follow_ups_resolve_any_active_entity(
    entity: str,
    prior_message: str,
    follow_up: str,
) -> None:
    state = {"recent": [{"message": prior_message, "reply_preview": f"We were discussing {entity}."}]}

    query, subject, resolved = build_query_with_subject(follow_up, conversation_state=state)

    assert subject == entity
    assert resolved is True
    assert query == f"{entity}: {follow_up}"


def test_lifecycle_follow_up_does_not_rank_unrelated_retired_record(monkeypatch) -> None:
    synthetic_kb = """## Source: knowledge/site-surfaces.md
# Website routes

## Federal tab
The Federal route is a public buyer path. The public knowledge does not state why it changed.

## Retired email aliases
The retired email aliases were removed because operations@noetfield.com is canonical.

## Retired SKU
The retired SKU was removed after offer consolidation.
"""

    monkeypatch.setattr(chatbot_knowledge, "build_knowledge_context", lambda: synthetic_kb)
    state = {
        "recent": [
            {
                "message": "What happened to the federal tab?",
                "reply_preview": "We were discussing the Federal tab.",
            }
        ]
    }

    ctx = select_relevant_excerpt("why retired?", conversation_state=state, max_chars=2500)

    assert "Active subject: Federal" in ctx
    assert "Federal route is a public buyer path" in ctx
    assert "retired email aliases were removed" not in ctx
    assert "retired SKU was removed" not in ctx
    assert "Missing detail rule" in ctx


@pytest.mark.parametrize(
    ("prior_message", "expected_subject", "follow_up"),
    (
        ("What happened to the retired page?", "Page", "why retired?"),
        ("Tell me about the retired email aliases.", "email aliases", "why retired?"),
        ("Did the intake route change?", "intake route", "why changed?"),
        ("Was the advisory offer renamed?", "advisory offer", "why renamed?"),
        ("Was the old pricing replaced?", "Pricing", "why changed?"),
        ("Is the deprecated program still available?", "program", "why deprecated?"),
    ),
)
def test_generic_subject_phrase_follow_ups(
    prior_message: str,
    expected_subject: str,
    follow_up: str,
) -> None:
    state = {"recent": [{"message": prior_message, "reply_preview": "We were discussing it."}]}

    query, subject, resolved = build_query_with_subject(follow_up, conversation_state=state)

    assert subject == expected_subject
    assert resolved is True
    assert query == f"{expected_subject}: {follow_up}"


@pytest.mark.parametrize(
    ("text", "expected"),
    (
        ("Tell me about the retired email aliases.", "email aliases"),
        ("Did the intake route change?", "intake route"),
        ("Was the advisory offer renamed?", "advisory offer"),
    ),
)
def test_infer_subject_phrase_without_entity_map(text: str, expected: str) -> None:
    assert infer_subject_phrase(text) == expected
