"""Unit tests for Copilot workflow DSL loaders."""

from __future__ import annotations

import asyncio
from uuid import uuid4

from noetfield_workflow.copilot_workflows import (
    COPILOT_QUICKSCAN,
    load_workflow_spec,
    mock_signoff_to_approved,
    start_copilot_quickscan,
)
from noetfield_workflow.state_machine import InMemoryWorkflowStore, WorkflowStateMachine
from noetfield_events import AsyncEventBus, InMemoryDeadLetterStore, InMemoryEventStore
from noetfield_types import WorkflowState


def test_load_copilot_quickscan_spec() -> None:
    spec = load_workflow_spec("CopilotQuickScan.workflow.json")
    assert spec.workflow_type == COPILOT_QUICKSCAN
    assert spec.sla_hours >= 24
    assert "states" in spec.raw


def test_copilot_quickscan_to_mock_signoff() -> None:
    async def run() -> None:
        bus = AsyncEventBus(
            event_store=InMemoryEventStore(),
            dead_letter_store=InMemoryDeadLetterStore(),
        )
        machine = WorkflowStateMachine(InMemoryWorkflowStore(), bus)
        tenant_id = uuid4()
        org_id = uuid4()
        wf = await start_copilot_quickscan(
            machine=machine,
            tenant_id=tenant_id,
            organization_id=org_id,
            actor_id="test-actor",
            rid="RID-TEST-001",
            signal_payload={"source": "unit"},
        )
        assert wf.state == WorkflowState.PENDING_REVIEW
        done = await mock_signoff_to_approved(
            machine=machine,
            tenant_id=tenant_id,
            organization_id=org_id,
            workflow_id=wf.workflow_id,
        )
        assert done.state == WorkflowState.COMPLETED

    asyncio.run(run())
