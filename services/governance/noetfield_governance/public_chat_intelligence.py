"""Intent telemetry and alignment helpers for the public chatbot."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from noetfield_config import CANONICAL_INTAKE_EMAIL
from noetfield_governance.chatbot_knowledge import detect_question_lanes


_PRIVACY_RE = re.compile(
    r"\b(store|save|log|record|history|transcript|conversation|privacy|data retention)\b",
    re.I,
)
_CONTACT_RE = re.compile(r"\b(contact|engage|start|get started|book|apply|email|intake)\b", re.I)
_OFF_TOPIC_RE = re.compile(r"\b(weather|recipe|sports|celebrity|homework|dating|joke)\b", re.I)


@dataclass(frozen=True)
class PublicChatIntent:
    primary_intent: str
    lanes: list[str] = field(default_factory=list)
    outcome_goal: str = "answer"
    risk_flags: list[str] = field(default_factory=list)
    required_terms: list[str] = field(default_factory=list)
    forbidden_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def analyze_public_chat_intent(message: str) -> PublicChatIntent:
    text = (message or "").strip()
    lanes = detect_question_lanes(text)

    from noetfield_governance.chatbot_knowledge import is_greeting_message

    if is_greeting_message(text):
        return PublicChatIntent(
            primary_intent="greeting",
            lanes=lanes,
            outcome_goal="welcome_and_orient",
            risk_flags=[],
            required_terms=["Noetfield"],
        )
    if _PRIVACY_RE.search(text):
        return PublicChatIntent(
            primary_intent="privacy_history",
            lanes=lanes,
            outcome_goal="explain_tracking_and_safe_use",
            risk_flags=["privacy_disclosure", "trust"],
            forbidden_terms=["we do not store"],
        )
    if _OFF_TOPIC_RE.search(text):
        return PublicChatIntent(
            primary_intent="off_topic",
            lanes=lanes,
            outcome_goal="redirect_to_noetfield_scope",
            risk_flags=["off_topic"],
            required_terms=["Noetfield", CANONICAL_INTAKE_EMAIL],
        )
    if _CONTACT_RE.search(text):
        return PublicChatIntent(
            primary_intent="intake",
            lanes=lanes,
            outcome_goal="route_to_intake",
            risk_flags=["conversion"],
            required_terms=[CANONICAL_INTAKE_EMAIL, "RID"],
        )
    if "developer" in lanes or "gel" in lanes:
        return PublicChatIntent(
            primary_intent="developer_gel",
            lanes=lanes,
            outcome_goal="give_public_docs_and_commands",
            risk_flags=["developer_truth"],
            required_terms=["GEL"],
            forbidden_terms=["unknown"],
        )
    if "investor" in lanes:
        return PublicChatIntent(
            primary_intent="investor",
            lanes=lanes,
            outcome_goal="route_to_investor_diligence",
            risk_flags=["investor_claims"],
            required_terms=["/investors/diligence/"],
        )

    if not text.lower():
        return PublicChatIntent(
            primary_intent="empty",
            lanes=[],
            outcome_goal="reject_empty",
            risk_flags=["bad_request"],
        )
    return PublicChatIntent(
        primary_intent="general_product",
        lanes=lanes,
        outcome_goal="answer_with_public_product_truth",
        risk_flags=[],
        required_terms=["Noetfield"],
    )


def evaluate_intent_alignment(
    *,
    intent: PublicChatIntent,
    reply: str,
    citations: list[str],
) -> dict[str, Any]:
    text = (reply or "").lower()
    missing_required = [term for term in intent.required_terms if term.lower() not in text]
    forbidden_hits = [term for term in intent.forbidden_terms if term.lower() in text]
    citation_present = bool(citations)
    aligned = not missing_required and not forbidden_hits
    if intent.primary_intent not in {"privacy_history", "off_topic"}:
        aligned = aligned and citation_present
    return {
        "aligned": aligned,
        "primary_intent": intent.primary_intent,
        "outcome_goal": intent.outcome_goal,
        "missing_required_terms": missing_required,
        "forbidden_hits": forbidden_hits,
        "citation_present": citation_present,
    }


def build_decision_path(
    *,
    intent: PublicChatIntent,
    provider: str | None,
    citations: list[str],
    knowledge_chars: int | None = None,
    error_type: str | None = None,
) -> list[dict[str, Any]]:
    path: list[dict[str, Any]] = [
        {"step": "input_validated", "status": "ok"},
        {
            "step": "intent_classified",
            "status": "ok",
            "intent": intent.primary_intent,
            "lanes": intent.lanes,
            "outcome_goal": intent.outcome_goal,
        },
    ]
    path.append({"step": "knowledge_retrieval", "status": "used", "knowledge_chars": knowledge_chars})
    path.append({"step": "llm_provider", "status": "used", "provider": provider})
    path.append({"step": "citations", "status": "ok" if citations else "missing", "citations": citations})
    if error_type:
        path.append({"step": "error", "status": "failed", "error_type": error_type})
    else:
        path.append({"step": "response_returned", "status": "ok"})
    path.append({"step": "telemetry_recorded", "status": "attempted"})
    return path
