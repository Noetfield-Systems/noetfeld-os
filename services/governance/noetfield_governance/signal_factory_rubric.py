"""Signal Factory rubric — classify operations inbox signals for agentic handoff.

Maps inbound email payloads to commercial routes (COMMERCIAL_INBOX_PACKAGING_LOCKED_v1)
and ALLOW / ESCALATE / BLOCK style verdicts aligned with AI Factory gate lanes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

RUBRIC_VERSION = "signal-factory-v1"

Verdict = Literal["PROCEED", "REQUIRE_HUMAN_REVIEW", "REJECT"]

_SPAM_HINTS = (
    "unsubscribe",
    "no-reply@",
    "noreply@",
    "mailer-daemon",
    "postmaster@",
)
_BLOCK_HINTS = ("prohibited", "bypass policy", "wire fraud", "money mule")
_ESCALATE_HINTS = (
    "regulated",
    "msb",
    "compliance",
    "production key",
    "api key",
    "trust brief",
    "bank pilot",
    "investor",
    "federal",
    "sow",
    "contract",
    "payment",
    "transfer",
    "withdraw",
)

_WORKFLOW_GUARDRAILS: dict[str, dict[str, list[str]]] = {
    "sandbox_nurture": {
        "agent_may": ["Send async demo link", "/start/", "/copilot/demo/"],
        "agent_must_not": ["Claim production keys issued"],
    },
    "pilot_qualify": {
        "agent_may": ["Book debrief", "Attach board PDF sample"],
        "agent_must_not": ["Sign SOW without founder"],
    },
    "trust_brief": {
        "agent_may": ["Confirm $10k scope", "Schedule kickoff"],
        "agent_must_not": ["Discount or SKU creep"],
    },
    "production_keys": {
        "agent_may": ["Route to Copilot Governance Pack intake"],
        "agent_must_not": ["Bypass M365 readiness story"],
    },
    "bank_pilot": {
        "agent_may": ["Route to bank pilot gate intake"],
        "agent_must_not": ["Promise live bank connector without pilot scope"],
    },
    "investor": {
        "agent_may": ["Attach public investor brief links"],
        "agent_must_not": ["Share private financials without founder approve"],
    },
    "federal": {
        "agent_may": ["Route to federal lane hub intake"],
        "agent_must_not": ["Invent certification or ATO status"],
    },
    "contact": {
        "agent_may": ["Acknowledge receipt", "Link sandbox / pricing"],
        "agent_must_not": ["Mandatory sales call for sandbox"],
    },
    "unknown": {
        "agent_may": ["Ask clarifying question via founder-approved channel"],
        "agent_must_not": ["Auto-send contract pricing or production keys"],
    },
}


@dataclass(frozen=True)
class SignalFactoryVerdict:
    verdict: Verdict
    route: str
    label: str
    sku: str | None
    risk_score: int
    reasons: tuple[str, ...] = ()
    agent_may: tuple[str, ...] = ()
    agent_must_not: tuple[str, ...] = ()
    rubric_version: str = RUBRIC_VERSION
    dimensions: dict[str, Any] = field(default_factory=dict)

    def to_rubric_json(self) -> dict[str, Any]:
        return {
            "rubric_version": self.rubric_version,
            "verdict": self.verdict,
            "route": self.route,
            "label": self.label,
            "sku": self.sku,
            "risk_score": self.risk_score,
            "reasons": list(self.reasons),
            "agent_may": list(self.agent_may),
            "agent_must_not": list(self.agent_must_not),
            "dimensions": self.dimensions,
        }


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _extract_rid(text: str) -> str | None:
    match = re.search(r"\bRID-[A-Z0-9-]+\b", text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def classify_operations_inbox_payload(payload: dict[str, object]) -> SignalFactoryVerdict:
    """Apply Signal Factory rubric to an operations_inbox_email signal payload."""
    subject = str(payload.get("subject") or "")
    body = str(payload.get("body_text") or payload.get("snippet") or "")
    from_addr = str(payload.get("from_addr") or payload.get("from") or "")
    channel = str(payload.get("channel") or "")
    combined = _norm(f"{subject}\n{body}")
    reasons: list[str] = []
    risk = 12

    if channel and channel != "operations_inbox":
        reasons.append(f"channel={channel}")

    for hint in _SPAM_HINTS:
        if hint in _norm(from_addr) or hint in combined:
            risk += 35
            reasons.append(f"spam_hint:{hint}")

    if len(combined) < 20:
        risk += 18
        reasons.append("minimal_context")

    for hint in _BLOCK_HINTS:
        if hint in combined:
            return _verdict(
                verdict="REJECT",
                route="blocked",
                label="Blocked request",
                sku=None,
                risk_score=min(100, risk + 40),
                reasons=(*reasons, f"block_hint:{hint}"),
            )

    route, label, sku = _classify_route(subject, body, combined)
    guardrails = _WORKFLOW_GUARDRAILS.get(route, _WORKFLOW_GUARDRAILS["unknown"])

    for hint in _ESCALATE_HINTS:
        if hint in combined:
            risk += 14
            reasons.append(f"escalate_hint:{hint}")

    if route in {"trust_brief", "bank_pilot", "investor", "federal", "production_keys"}:
        risk += 22
        reasons.append(f"contract_route:{route}")

    rid = _extract_rid(f"{subject}\n{body}")
    if rid:
        reasons.append(f"rid:{rid}")

    risk = min(100, max(0, risk))

    if risk >= 70 or route == "blocked":
        verdict: Verdict = "REJECT"
    elif route in {"sandbox_nurture"} and risk < 45 and len(combined) >= 20:
        verdict = "PROCEED"
    elif route in {"unknown", "contact"} and risk < 35:
        verdict = "PROCEED"
    else:
        verdict = "REQUIRE_HUMAN_REVIEW"

    return SignalFactoryVerdict(
        verdict=verdict,
        route=route,
        label=label,
        sku=sku,
        risk_score=risk,
        reasons=tuple(reasons),
        agent_may=tuple(guardrails["agent_may"]),
        agent_must_not=tuple(guardrails["agent_must_not"]),
        dimensions={
            "from_domain": from_addr.split("@")[-1] if "@" in from_addr else "",
            "has_rid": bool(rid),
            "subject_len": len(subject),
            "body_len": len(body),
        },
    )


def _classify_route(subject: str, body: str, combined: str) -> tuple[str, str, str | None]:
    sub = _norm(subject)
    if "sandbox" in combined or "upgrade" in combined and "limit" in combined:
        return "sandbox_nurture", "Sandbox nurture", None
    if "investor" in combined or "diligence" in combined:
        return "investor", "Investor brief", None
    if "trust brief" in combined or "trust-brief" in combined:
        return "trust_brief", "Trust Brief Intake", "trust_brief"
    if "bank pilot" in combined or "bank-pilot" in combined:
        return "bank_pilot", "Bank Pilot inquiry", "bank_pilot"
    if "copilot" in combined or "governance pack" in combined or "pilot" in sub:
        return "pilot_qualify", "Governance Pack apply", "copilot"
    if "production" in combined and ("key" in combined or "api" in combined):
        return "production_keys", "Production API keys", None
    if "federal" in combined or "msp" in combined:
        return "federal", "Federal Brief", None
    if "feedback" in combined:
        return "contact", "Site feedback", None
    if sub.startswith("re:") or sub.startswith("fwd:"):
        return "contact", "Inbox thread", None
    return "unknown", "Operations inbox", None


def _verdict(
    *,
    verdict: Verdict,
    route: str,
    label: str,
    sku: str | None,
    risk_score: int,
    reasons: tuple[str, ...],
    agent_may: tuple[str, ...] = (),
    agent_must_not: tuple[str, ...] = (),
) -> SignalFactoryVerdict:
    guardrails = _WORKFLOW_GUARDRAILS.get(route, _WORKFLOW_GUARDRAILS["unknown"])
    return SignalFactoryVerdict(
        verdict=verdict,
        route=route,
        label=label,
        sku=sku,
        risk_score=risk_score,
        reasons=reasons,
        agent_may=agent_may or tuple(guardrails["agent_may"]),
        agent_must_not=agent_must_not or tuple(guardrails["agent_must_not"]),
    )
