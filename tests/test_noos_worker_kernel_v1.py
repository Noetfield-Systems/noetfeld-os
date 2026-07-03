"""Tests for NOOS Cheap Worker Kernel v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_model_router_v1 as router  # noqa: E402
import noos_patch_sandbox_v1 as sandbox  # noqa: E402
import noos_receipt_writer_v1 as receipt_writer  # noqa: E402
import noos_worker_kernel_v1 as kernel  # noqa: E402

TEST_CONFIG = {
    "budget": {"max_usd_per_run": 0.05, "max_usd_per_day": 0.50},
    "tiers": {
        "T0": {
            "name": "deterministic",
            "providers": ["local_shell"],
            "models": [],
            "max_usd": 0.0,
            "requires_founder_approval": False,
            "task_kinds": ["grep", "check", "validate", "lint"],
        },
        "T1": {
            "name": "cheap_summary",
            "providers": ["openrouter_free"],
            "models": [{"id": "free/model", "provider": "openrouter_free", "unit_cost_usd_per_1k_tokens": 0.0}],
            "max_usd": 0.01,
            "requires_founder_approval": False,
            "task_kinds": ["summarize", "classify", "triage"],
        },
        "T2": {
            "name": "bounded_patch",
            "providers": ["deepseek_cheap"],
            "models": [{"id": "deepseek/chat", "provider": "deepseek_cheap", "unit_cost_usd_per_1k_tokens": 0.00014}],
            "max_usd": 0.03,
            "requires_founder_approval": False,
            "task_kinds": ["patch_proposal", "kaizen_proposal"],
        },
        "T3": {
            "name": "premium_exception",
            "providers": ["openrouter_premium"],
            "models": [{"id": "anthropic/claude", "provider": "openrouter_premium", "unit_cost_usd_per_1k_tokens": 0.003}],
            "max_usd": 0.05,
            "requires_founder_approval": True,
            "task_kinds": ["premium_analysis"],
        },
    },
    "routing": {"default_tier": "T0", "unknown_task_kind": "T0"},
    "governance": {
        "no_direct_main_edits": True,
        "allowed_patch_prefixes": ["scripts/", "docs/_NOOS_AGENT/", "tests/"],
        "forbidden_patch_paths": ["noetfield_gate/", "scripts/verify_"],
        "patch_sandbox_root": ".noos-runtime/worker-kernel/patches",
    },
    "secret_redaction": {
        "patterns": [r"(?i)(api_key|secret|token)\s*[:=]\s*\S+", r"sk-[a-zA-Z0-9]{20,}"],
        "replacement": "[REDACTED]",
    },
    "deterministic_checks": {
        "patch_apply_requires": {"max_files": 5, "max_lines_changed": 200},
    },
}


def test_routes_grep_check_to_t0():
    for kind in ("grep", "check"):
        row = router.route_task(task_kind=kind, config=TEST_CONFIG)
        assert row["tier"] == "T0"
        assert row["mode"] == "deterministic"
        assert not row["blocked"]


def test_routes_summary_classification_to_t1():
    for kind in ("summarize", "classify"):
        row = router.route_task(task_kind=kind, config=TEST_CONFIG)
        assert row["tier"] == "T1"
        assert row["mode"] == "llm_proposal"


def test_routes_bounded_patch_to_t2():
    row = router.route_task(task_kind="patch_proposal", config=TEST_CONFIG)
    assert row["tier"] == "T2"
    assert row["mode"] == "llm_proposal"


def test_blocks_t3_without_founder_approval():
    row = router.route_task(task_kind="premium_analysis", config=TEST_CONFIG)
    assert row["tier"] == "T3"
    assert row["blocked"]
    assert row["blocker_reason"] == "t3_requires_founder_approval"


def test_allows_t3_with_founder_token():
    row = router.route_task(
        task_kind="premium_analysis",
        founder_approval_token="FOUNDER_APPROVED_T3",
        config=TEST_CONFIG,
    )
    assert row["tier"] == "T3"
    assert not row["blocked"]


def test_enforces_max_cost():
    cost = router.estimate_cost(tier="T3", tokens_in=500_000, tokens_out=500_000, config=TEST_CONFIG)
    assert cost["within_budget"] is False
    budget = router.enforce_budget(cost, config=TEST_CONFIG)
    assert budget["ok"] is False
    assert budget["blocker_reason"] == "max_cost_exceeded"


def test_redacts_secrets():
    text = "api_key=sk-abcdefghijklmnopqrstuvwxyz12345 secret=abc"
    redacted, count = router.redact_secrets(text, config=TEST_CONFIG)
    assert "[REDACTED]" in redacted
    assert "sk-abc" not in redacted
    assert count >= 1


def test_writes_receipt(tmp_path: Path):
    row = receipt_writer.write_receipt(
        {"op_key": "test-op", "status": "ok", "task_kind": "grep"},
        receipt_dir=tmp_path,
        op_key="test-op",
    )
    written = list(tmp_path.glob("noos-worker-kernel-*.json"))
    assert len(written) == 1
    assert row["receipt_path"] == str(written[0])
    doc = json.loads(written[0].read_text(encoding="utf-8"))
    assert doc["schema"] == "noos-worker-kernel-receipt-v1"


def test_rejects_direct_main_mutation():
    proposal = {
        "target_branch": "main",
        "files": [{"path": "scripts/foo.py", "content": "x = 1\n"}],
    }
    verdict = sandbox.validate_patch_proposal(proposal, config=TEST_CONFIG)
    assert verdict["verdict"] == "BLOCKED_WITH_REASON"
    assert any("main" in e for e in verdict["errors"])


def test_kernel_run_grep_writes_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(kernel, "load_router_config", lambda: TEST_CONFIG)
    monkeypatch.setattr(
        receipt_writer,
        "write_receipt",
        lambda row, **kw: {**row, "receipt_path": "receipts/proof/test-receipt.json"},
    )
    row = kernel.run_task(task_kind="grep", payload={"pattern": "noos_worker_kernel", "path": "scripts"})
    assert row["routing"]["tier"] == "T0"
    assert row["status"] == "ok"
    assert row.get("receipt_path")


def test_kernel_blocks_t3_without_approval(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(kernel, "load_router_config", lambda: TEST_CONFIG)
    monkeypatch.setattr(
        receipt_writer,
        "write_receipt",
        lambda row, **kw: {**row, "receipt_path": "receipts/proof/blocked.json"},
    )
    row = kernel.run_task(task_kind="premium_analysis", payload={"text": "analyze"})
    assert row["status"] == "blocked"
    assert row["result"]["blocker_reason"] == "t3_requires_founder_approval"


def test_kernel_patch_sandbox_allowed_prefix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg = {**TEST_CONFIG, "governance": {**TEST_CONFIG["governance"], "patch_sandbox_root": str(tmp_path / "patches")}}
    monkeypatch.setattr(sandbox, "_router_config", lambda: cfg)

    proposal = {
        "target_branch": "cursor/test",
        "files": [{"path": "scripts/kernel_helper_v1.py", "content": "# helper\n"}],
    }
    manifest = sandbox.write_sandbox_patch(proposal, op_key="test-patch-1", config=cfg)
    assert manifest["verdict"]["verdict"] == "PASS"
    assert (tmp_path / "patches" / "test-patch-1" / "proposal-v1.json").is_file()


def test_kernel_rejects_forbidden_patch_path():
    proposal = {
        "target_branch": "cursor/test",
        "files": [{"path": "noetfield_gate/cli.py", "content": "hack\n"}],
    }
    verdict = sandbox.validate_patch_proposal(proposal, config=TEST_CONFIG)
    assert verdict["verdict"] == "BLOCKED_WITH_REASON"
    assert any("forbidden" in e for e in verdict["errors"])
