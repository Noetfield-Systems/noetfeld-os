import pytest
from scripts.noos_tool_wrappers_v1 import git_push_task_branch, open_pr_task_branch, WrapperError


class DummyBroker:
    def __init__(self):
        self.calls = []

    def execute(self, cmd):
        self.calls.append(cmd)
        return {"allowed": True, "exit_code": 0, "cmd": cmd}


@pytest.fixture(autouse=True)
def patch_broker(monkeypatch):
    # Patch the module-level broker with a dummy that doesn't call git/gh
    from scripts import noos_tool_wrappers_v1 as w
    dummy = DummyBroker()
    monkeypatch.setattr(w, "broker", dummy)
    return dummy


def test_push_valid_branch(patch_broker):
    res = git_push_task_branch("task/my-feature")
    assert res["allowed"] is True
    assert "git" in res["cmd"]


def test_push_invalid_branch_rejected():
    with pytest.raises(WrapperError):
        git_push_task_branch("invalid/BranchName")


def test_open_pr_requires_title():
    with pytest.raises(WrapperError):
        open_pr_task_branch("task/one", "")


def test_open_pr_calls_broker(patch_broker):
    res = open_pr_task_branch("task/one", "My PR title", body="desc")
    assert res["allowed"] is True
    assert res["cmd"][0] == "gh"
