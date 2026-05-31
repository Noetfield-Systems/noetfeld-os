from services.governance_engine import evaluate_intent


def test_empty_actor_denies() -> None:
    result = evaluate_intent(actor="", action="read", context="routine access")
    assert result.decision == "deny"
    assert result.risk_score == 100


def test_transfer_in_action_raises_risk() -> None:
    result = evaluate_intent(
        actor="user:alice",
        action="initiate_transfer",
        context="payroll batch for verified employees",
    )
    assert result.decision in {"review", "deny"}
    assert result.risk_score >= 40


def test_low_risk_allow() -> None:
    result = evaluate_intent(
        actor="service:reporting",
        action="generate_audit_summary",
        context="monthly governance report for board pack with policy refs",
    )
    assert result.decision == "allow"
    assert result.risk_score < 40
    assert result.rid.startswith("RID-")
