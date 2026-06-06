"""Agent run guardrails (deny-by-default)."""

from noetfield_copilot_governance.agent_run import guard_tool_call


def test_denied_payment_tool() -> None:
    rec = guard_tool_call("payment_initiate", ["evaluate", "export_audit"])
    assert rec.result_status == "denied"


def test_allowed_evaluate_tool() -> None:
    rec = guard_tool_call("evaluate", ["evaluate", "export_audit"])
    assert rec.result_status == "ok"
