"""Tests for noetfield deploy CLI dry-run."""

from __future__ import annotations

import scripts.noetfield_deploy_v1 as deploy


def test_deploy_dry_run_fly_inbox() -> None:
    row = deploy.deploy_scope("fly-inbox", dry_run=True, write_receipt=False)
    assert row.get("ok") is True
    assert row.get("mode") == "dry_run"


def test_deploy_status_schema() -> None:
    row = deploy.deploy_status()
    assert row["schema"] == "noos-deploy-status-v1"
    assert "scopes" in row
