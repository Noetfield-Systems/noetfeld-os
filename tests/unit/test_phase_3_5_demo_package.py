"""Tests for the Phase 3.5 Copilot Governance demo package."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from scripts.run_copilot_governance_demo import build_demo_package


def test_copilot_governance_demo_package_shape() -> None:
    payload = json.loads(Path("demos/copilot-governance/sample_copilot_signal.json").read_text())
    result = asyncio.run(build_demo_package(payload))

    assert result["demo"] == "noetfield-copilot-governance-phase-3.5"
    assert result["status"] == "ready_for_demo"
    assert result["board_brief"]["title"] == "Copilot Governance Readiness Brief"
    assert result["board_brief"]["governance_state"]["approval_required"] is True
    assert result["board_brief"]["governance_state"]["policy_enforced"] is True
    assert result["board_brief"]["inspector_state"]["status"] == "completed"
    assert result["board_brief"]["inspector_state"]["finding_count"] == 3
    assert result["audit_package"]["event_count"] >= 10
    assert result["audit_package"]["pending_approval_count"] >= 1


def test_copilot_governance_demo_event_trail() -> None:
    payload = json.loads(Path("demos/copilot-governance/sample_copilot_signal.json").read_text())
    result = asyncio.run(build_demo_package(payload))
    event_types = set(result["audit_package"]["event_types"])

    assert "SIGNAL_INGESTED" in event_types
    assert "RELATIONSHIP_INFERRED" in event_types
    assert "GRAPH_REFLECTION_COMPLETED" in event_types
    assert "WORKFLOW_STARTED" in event_types
    assert "POLICY_EVALUATED" in event_types
    assert "HUMAN_APPROVAL_REQUESTED" in event_types
    assert "INSPECTOR_COLLABORATION_STARTED" in event_types
    assert "INSPECTOR_COMPLETED" in event_types
