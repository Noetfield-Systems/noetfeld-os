"""Signal Factory rubric tests."""

from __future__ import annotations

from noetfield_governance.signal_factory_rubric import classify_operations_inbox_payload


def test_rubric_trust_brief_requires_human_review() -> None:
    verdict = classify_operations_inbox_payload(
        {
            "channel": "operations_inbox",
            "subject": "Trust Brief Intake RID-ABC-123",
            "from_addr": "cio@bank.example.com",
            "body_text": "We want the Trust Brief scope for our AI governance program.",
        }
    )
    assert verdict.route == "trust_brief"
    assert verdict.verdict == "REQUIRE_HUMAN_REVIEW"
    assert verdict.sku == "trust_brief"
    assert verdict.risk_score >= 30


def test_rubric_sandbox_nurture_can_proceed() -> None:
    verdict = classify_operations_inbox_payload(
        {
            "channel": "operations_inbox",
            "subject": "Sandbox upgrade question",
            "from_addr": "dev@startup.example.com",
            "body_text": "We hit the sandbox evaluate limit and want the demo link for /start/.",
        }
    )
    assert verdict.route == "sandbox_nurture"
    assert verdict.verdict == "PROCEED"


def test_rubric_blocks_prohibited_language() -> None:
    verdict = classify_operations_inbox_payload(
        {
            "channel": "operations_inbox",
            "subject": "Urgent",
            "from_addr": "bad@example.com",
            "body_text": "Please bypass policy and wire transfer immediately — prohibited.",
        }
    )
    assert verdict.verdict == "REJECT"
