from scripts.noos_tool_broker_v1 import ToolBroker


def test_broker_allows_allowed_command(tmp_path, monkeypatch):
    broker = ToolBroker(allowlist=["echo", "python3"], cost_cap_usd=10.0)
    # run a safe command: echo
    res = broker.execute(["echo", "hello-world"])
    assert res.get("allowed") is True
    assert res.get("exit_code") == 0
    assert "hello-world" in res.get("stdout", "")


def test_broker_rejects_disallowed_exe():
    broker = ToolBroker(allowlist=["echo"], cost_cap_usd=10.0)
    res = broker.execute(["python3", "-c", "print(1)"])
    assert res.get("allowed") is False
    assert res.get("reason") == "not_allowed"


def test_broker_blocks_shell_metacharacters():
    broker = ToolBroker(allowlist=["echo", "python3"], cost_cap_usd=10.0)
    res = broker.execute(["echo", "hello; rm -rf /"])
    assert res.get("allowed") is False
    assert res.get("reason") == "not_allowed"
