"""Run the Phase 3.5 Copilot Governance demo package.

The demo uses the backend runtime directly and produces a board-ready JSON
brief plus an audit package summary. It is intentionally backend-only.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5, NAMESPACE_URL

from noetfield_copilot_governance import (
    CopilotGovernanceCommand,
    CopilotGovernanceDemoRuntime,
    InMemoryCopilotGovernanceRunStore,
)
from noetfield_events import AsyncEventBus, EventReplayCursor, InMemoryDeadLetterStore, InMemoryEventStore
from noetfield_governance import GovernanceRuntime, HumanApprovalQueue
from noetfield_graph import (
    InMemoryGraphReflectionStore,
    InMemoryGraphStore,
    LiveGraphMutationEngine,
    TemporalGraphReflectionCycle,
)
from noetfield_inspectors import (
    InMemoryInspectorRunStore,
    InspectorCollaborationCommand,
    InspectorCollaborationRuntime,
    InspectorExecutionLoop,
    LeadScoutInspector,
    OpportunityHunterInspector,
    ThreatMonitorInspector,
)
from noetfield_ledger import AuditLedgerRuntime, InMemoryAuditLedgerStore
from noetfield_signals import InMemorySignalStore, SignalIngestionPipeline
from noetfield_workflow import InMemoryWorkflowStore, WorkflowStateMachine


DEFAULT_INPUT = Path("demos/copilot-governance/sample_copilot_signal.json")


def stable_uuid(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"https://noetfield.local/demo/{name}")


def load_signal(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


async def build_demo_package(signal_payload: dict[str, Any]) -> dict[str, Any]:
    tenant_id = stable_uuid("tenant")
    organization_id = stable_uuid("organization")

    event_bus = AsyncEventBus(
        event_store=InMemoryEventStore(),
        dead_letter_store=InMemoryDeadLetterStore(),
    )
    audit_store = InMemoryAuditLedgerStore()
    audit_runtime = AuditLedgerRuntime(audit_store)
    await event_bus.subscribe(
        name="audit-ledger-runtime",
        event_types={"*"},
        handler=audit_runtime.record_event,
    )

    signal_pipeline = SignalIngestionPipeline(event_bus, InMemorySignalStore())
    graph_store = InMemoryGraphStore()
    graph_mutations = LiveGraphMutationEngine(event_bus, graph_store)
    graph_reflections = TemporalGraphReflectionCycle(
        event_bus,
        graph_store,
        InMemoryGraphReflectionStore(),
    )
    workflow_state_machine = WorkflowStateMachine(InMemoryWorkflowStore(), event_bus)
    governance_runtime = GovernanceRuntime(event_bus, HumanApprovalQueue())

    copilot_runtime = CopilotGovernanceDemoRuntime(
        signal_pipeline=signal_pipeline,
        graph_mutations=graph_mutations,
        graph_reflections=graph_reflections,
        workflow_state_machine=workflow_state_machine,
        governance_runtime=governance_runtime,
        run_store=InMemoryCopilotGovernanceRunStore(),
    )

    copilot_result = await copilot_runtime.run(
        CopilotGovernanceCommand(
            tenant_id=tenant_id,
            organization_id=organization_id,
            submitted_by="demo.governance.lead@noetfield.local",
            signal_payload=signal_payload,
            source_entity_id=stable_uuid("microsoft-copilot"),
            target_entity_id=stable_uuid("customer-tenant"),
        )
    )

    inspector_runtime = InspectorCollaborationRuntime(event_bus)
    inspector_runtime.register(OpportunityHunterInspector())
    inspector_runtime.register(ThreatMonitorInspector())
    inspector_runtime.register(LeadScoutInspector())
    inspector_loop = InspectorExecutionLoop(inspector_runtime, InMemoryInspectorRunStore())
    inspector_run = await inspector_loop.run_once(
        InspectorCollaborationCommand(
            tenant_id=tenant_id,
            organization_id=organization_id,
            invoked_by="demo.governance.lead@noetfield.local",
            objective="Assess Copilot governance opportunity, threat, and readiness signals.",
            inspector_names=["opportunity_hunter", "threat_monitor", "lead_scout"],
            graph_scope={"module": "copilot_governance", "relationship_id": str(copilot_result.relationship_id)},
        )
    )

    replayed_events = await event_bus.replay(EventReplayCursor(after_sequence=0))
    pending_approvals = await governance_runtime.approvals.list_pending(tenant_id)
    relationships = await graph_store.relationships_for_tenant(tenant_id)

    event_types = [event.event_type for event in replayed_events]
    board_brief = {
        "title": "Copilot Governance Readiness Brief",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "positioning": "AI Trust Infrastructure for regulated enterprises",
        "executive_summary": (
            "The demo signal was ingested, linked into the governance graph, "
            "evaluated by policy, moved into workflow review, and preserved in "
            "a replayable audit trail."
        ),
        "risk_findings": [
            "Copilot usage creates oversharing and evidence-readiness exposure.",
            "Governance policy requires human review before publication or board use.",
            "Audit replay is available for signal, graph, workflow, and approval events.",
        ],
        "governance_state": {
            "workflow_state": copilot_result.workflow_state.value,
            "approval_required": copilot_result.approval_id is not None,
            "approval_id": str(copilot_result.approval_id) if copilot_result.approval_id else None,
            "policy_enforced": "POLICY_EVALUATED" in event_types,
        },
        "graph_state": {
            "relationship_count": len(relationships),
            "relationship_id": str(copilot_result.relationship_id),
            "reflection_id": str(copilot_result.reflection_id),
        },
        "inspector_state": {
            "run_id": str(inspector_run.run_id),
            "status": inspector_run.status,
            "finding_count": len(inspector_run.findings),
            "requires_human_review": inspector_run.requires_human_review,
        },
    }

    audit_package = {
        "tenant_id": str(tenant_id),
        "organization_id": str(organization_id),
        "signal_id": str(copilot_result.signal_id),
        "workflow_id": str(copilot_result.workflow_id),
        "event_count": len(replayed_events),
        "audit_record_count": len(audit_store.records),
        "event_types": event_types,
        "pending_approval_count": len(pending_approvals),
        "events": [event.model_dump(mode="json") for event in replayed_events],
    }

    return {
        "demo": "noetfield-copilot-governance-phase-3.5",
        "status": "ready_for_demo",
        "input_signal": signal_payload,
        "board_brief": board_brief,
        "audit_package": audit_package,
        "runtime_result": copilot_result.model_dump(mode="json"),
    }


def write_output(payload: dict[str, Any], output_path: Path | None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True)
    if output_path is None:
        print(text)
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text + "\n", encoding="utf-8")
    print(f"wrote {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to Copilot signal JSON.")
    parser.add_argument("--output", help="Optional path to write JSON demo output.")
    args = parser.parse_args()

    payload = load_signal(Path(args.input))
    result = asyncio.run(build_demo_package(payload))
    write_output(result, Path(args.output) if args.output else None)


if __name__ == "__main__":
    main()
