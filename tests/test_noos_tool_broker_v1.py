"""Negative-proof tests for NOOS Tool Broker v1 — isolated fixture, cycle 0 gate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_tool_broker_v1 as broker  # noqa: E402


@pytest.fixture
def broker_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "broker@test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "broker"], cwd=repo, check=True)
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True)

    cfg = broker.load_config()
    tainted_path = tmp_path / "tainted.json"
    tainted_path.write_text(
        json.dumps({"schema": "tainted-commits-v1", "shas": []}),
        encoding="utf-8",
    )
    cfg_path = tmp_path / "broker-config.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")

    monkeypatch.setattr(broker, "ROOT", repo)
    monkeypatch.setattr(broker, "CONFIG_PATH", cfg_path)
    monkeypatch.setattr(broker, "TAINTED_PATH", tainted_path)
    monkeypatch.setattr(
        broker,
        "write_receipt",
        lambda row, **kw: {**row, "receipt_path": "dry-run"},
    )
    return {"repo": repo, "tainted_path": tainted_path, "cfg_path": cfg_path}


def test_negative_proof_raw_shell_param_forbidden(broker_env):
    row = broker.invoke(agent_id="healer-l2", tool="grep", params={"shell": "rm -rf /"}, dry_run=True)
    assert row["ok"] is False
    assert row["result"]["blocker_reason"] == "shell_string_forbidden"


def test_negative_proof_tool_not_in_allowlist(broker_env):
    row = broker.invoke(agent_id="p1-agent", tool="curl_fetch", params={"url": "https://evil.test"}, dry_run=True)
    assert row["ok"] is False
    assert row["result"]["blocker_reason"] == "tool_not_in_allowlist"


def test_negative_proof_protected_branch_push(broker_env):
    repo = broker_env["repo"]
    row = broker.invoke(
        agent_id="p1-agent",
        tool="git_push_task_branch",
        params={"branch_name": "main"},
        worktree_root=repo,
        dry_run=True,
    )
    assert row["ok"] is False
    assert row["result"]["blocker_reason"] == "protected_branch"


def test_negative_proof_branch_pattern_violation(broker_env):
    repo = broker_env["repo"]
    row = broker.invoke(
        agent_id="p1-agent",
        tool="open_pr_task_branch",
        params={"branch_name": "random/illegal branch"},
        worktree_root=repo,
        dry_run=True,
    )
    assert row["ok"] is False
    assert row["result"]["blocker_reason"] == "branch_pattern_violation"


def test_negative_proof_tainted_commit_descendant(broker_env):
    repo = broker_env["repo"]
    bad = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    broker_env["tainted_path"].write_text(
        json.dumps({"schema": "tainted-commits-v1", "shas": [bad]}),
        encoding="utf-8",
    )
    row = broker.invoke(
        agent_id="healer-l2",
        tool="git_push_task_branch",
        params={"branch_name": "cursor/task-001"},
        worktree_root=repo,
        dry_run=True,
    )
    assert row["ok"] is False
    assert row["result"]["blocker_reason"] == "tainted_commit"


def test_allowlist_open_pr_task_branch_ok(broker_env):
    repo = broker_env["repo"]
    row = broker.invoke(
        agent_id="p1-agent",
        tool="open_pr_task_branch",
        params={"branch_name": "cursor/task-001"},
        worktree_root=repo,
        dry_run=True,
    )
    assert row["ok"] is True
    assert row["result"]["action"] in {"created_branch", "checked_out_existing"}


def test_allowlist_grep_ok(broker_env):
    repo = broker_env["repo"]
    (repo / "scripts").mkdir()
    (repo / "scripts" / "foo.py").write_text("broker_marker = 1\n", encoding="utf-8")
    row = broker.invoke(
        agent_id="healer-l2",
        tool="grep",
        params={"pattern": "broker_marker", "path": "scripts"},
        worktree_root=repo,
        dry_run=True,
    )
    assert row["ok"] is True


def test_aider_auto_commit_requires_worktree(broker_env):
    row = broker.invoke(agent_id="aider", tool="aider_auto_commit", params={"message": "x"}, dry_run=True)
    assert row["ok"] is False
    assert row["result"]["blocker_reason"] == "missing_worktree_path"


def test_receipt_has_l11_cost_fields(broker_env):
    repo = broker_env["repo"]
    row = broker.invoke(
        agent_id="healer-l2",
        tool="git_status",
        params={},
        worktree_root=repo,
        dry_run=True,
    )
    assert "cost" in row
    assert "total_usd" in row["cost"]
    assert row["cost"].get("mission_id") == "M4"


def test_config_declares_broker_only_agents():
    cfg = broker.load_config()
    assert cfg["agents_required"]["healer_layer_2"] == "broker_only"
    assert cfg["agents_required"]["p1_agents"] == "broker_only"
    assert "open_pr_task_branch" in cfg["allowlist"]
    assert "git_push_task_branch" in cfg["allowlist"]


def test_aider_config_disables_shell():
    text = (ROOT / "config/aider-broker-v1.yml").read_text(encoding="utf-8")
    assert "suggest_shell_commands: false" in text
    assert "auto_commits: false" in text
