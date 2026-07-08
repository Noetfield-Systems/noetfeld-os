"""deploy_git_sha — runtime GIT_SHA must win over baked .deploy_git_sha stamp."""

from __future__ import annotations

from noetfield_governance.api import deploy_git_sha


def test_deploy_git_sha_from_env(monkeypatch) -> None:
    monkeypatch.setenv("GIT_SHA", "d8bb0e16194ef65acb8d356acbf143d539ff3145")
    assert deploy_git_sha() == "d8bb0e16194ef65acb8d356acbf143d539ff3145"
