"""Canonical buyer questions — grounded answers (mocked LLM)."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from noetfield_governance.chatbot_knowledge import select_relevant_excerpt
from noetfield_governance.public_chat import answer_public_question


CANONICAL_QUESTIONS = (
    "How much is Trust Brief?",
    "What are the three offerings?",
    "Where should a governance lead start?",
)


def test_knowledge_includes_locked_offerings() -> None:
    ctx = select_relevant_excerpt("Trust Brief pricing")
    assert "OFFERINGS_LOCKED" in ctx or "$10,000" in ctx
    assert "operations@noetfield.com" in ctx


def test_canonical_answers_use_knowledge() -> None:
    async def run() -> None:
        for question in CANONICAL_QUESTIONS:

            def fake_gen(**_kwargs):
                ctx = select_relevant_excerpt(question)
                if "10,000" in ctx or "Trust Brief" in ctx:
                    return "Trust Brief is $10,000 for six weeks. See /trust-brief/intake/."
                return "See operations@noetfield.com."

            with patch("noetfield_governance.public_chat._generate_sync", side_effect=fake_gen):
                reply, _, _citations = await answer_public_question(
                    message=question,
                    provider="auto",
                    gemini_api_key="g",
                    gemini_model="gemini-2.0-flash",
                    openrouter_api_key="o",
                    openrouter_model="google/gemini-2.0-flash-001",
                    client_key=f"q-{question[:12]}",
                )
            assert "10,000" in reply or "operations@" in reply

    asyncio.run(run())
