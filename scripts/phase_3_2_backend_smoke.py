"""Phase 3.2 backend runtime smoke harness.

Default mode runs with in-memory stores for fast CI validation. Use
`--postgres` after applying migrations to exercise PostgreSQL as the system of
record.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from uuid import UUID, uuid4

import asyncpg

from noetfield_copilot_governance import (
    CopilotGovernanceCommand,
    CopilotGovernanceDemoRuntime,
    InMemoryCopilotGovernanceRunStore,
    PostgresCopilotGovernanceRunStore,
)
from noetfield_events import (
    AsyncEventBus,
    EventReplayCursor,
    InMemoryDeadLetterStore,
    InMemoryEventStore,
    PostgresDeadLetterStore,
    PostgresEventStore,
)
from noetfield_governance import (
    GovernanceActionCommand,
    GovernanceRuntime,
    HumanApprovalQueue,
    PostgresApprovalQueueStore,
)
from noetfield_graph import (
    GraphMutationCommand,
    InMemoryGraphReflectionStore,
    InMemoryGraphStore,
    LiveGraphMutationEngine,
    PostgresGraphReflectionStore,
    PostgresGraphStore,
    TemporalGraphReflectionCycle,
)
from noetfield_inspectors import (
    InMemoryInspectorRunStore,
    InspectorCollaborationCommand,
    InspectorCollaborationRuntime,
    InspectorExecutionLoop,
    LeadScoutInspector,
    OpportunityHunterInspector,
    PostgresInspectorRunStore,
    ThreatMonitorInspector,
)
from noetfield_ledger import AuditLedgerRuntime, InMemoryAuditLedgerStore, PostgresAuditLedgerStore
from noetfield_signals import (
    InMemorySignalStore,
    IngestSignalCommand,
    PostgresSignalStore,
    SignalIngestionPipeline,
)
from noetfield_types import WorkflowState
from noetfield_workflow import (
    InMemoryWorkflowStore,
    PostgresWorkflowStore,
    WorkflowInstance,
    WorkflowStateMachine,
    WorkflowTransitionCommand,
)


def normalize_database_url(database_url: str) -> str:
    return database_url.replace("postgresql+asyncpg://", "postgresql://")


async def seed_postgres_tenant(database_url: str) -> tuple[UUID, UUID]:
    organization_id = uuid4()
    tenant_id = uuid4()
    connection = await asyncpg.connect(normalize_database_url(database_url))
    try:
        await connection.execute(
            """
            insert into noetfield.organizations (id, name, legal_name, primary_domain)
            values ($1, 'Phase 3.2 Smoke Org', 'Phase 3.2 Smoke Org', 'smoke.noetfield.local')
            on conflict (id) do nothing
            """,
            organization_id,
        )
        await connection.execute(
            """
            insert into noetfield.tenants (id, organization_id, name, deployment_mode, data_region)
            values ($1, $2, 'Phase 3.2 Smoke Tenant', 'saas', 'local')
            on conflict (id) do nothing
            """,
            tenant_id,
            organization_id,
        )
    finally:
        await connection.close()
    return tenant_id, organization_id


async def run_smoke(*, use_postgres: bool, database_url: str | None) -> None:
    tenant_id: UUID
    organization_id: UUID

    if use_postgres:
        if not database_url:
            raise SystemExit("DATABASE_URL is required for --postgres")
        tenant_id, organization_id = await seed_postgres_tenant(database_url)
        event_store = PostgresEventStore(database_url)
        dead_letter_store = PostgresDeadLetterStore(database_url)
        signal_store = PostgresSignalStore(database_url)
        graph_store = PostgresGraphStore(database_url)
        reflection_store = PostgresGraphReflectionStore(database_url)
        audit_store = PostgresAuditLedgerStore(database_url)
        workflow_store = PostgresWorkflowStore(database_url)
        inspector_store = PostgresInspectorRunStore(database_url)
        approval_queue = PostgresApprovalQueueStore(database_url)
        copilot_store = PostgresCopilotGovernanceRunStore(database_url)
        stores = [
            event_store,
            dead_letter_store,
            signal_store,
            graph_store,
            reflection_store,
            audit_store,
            workflow_store,
            inspector_store,
            approval_queue,
            copilot_store,
        ]
    else:
        tenant_id, organization_id = uuid4(), uuid4()
        event_store = InMemoryEventStore()
        dead_letter_store = InMemoryDeadLetterStore()
        signal_store = InMemorySignalStore()
        graph_store = InMemoryGraphStore()
        reflection_store = InMemoryGraphReflectionStore()
        audit_store = InMemoryAuditLedgerStore()
        workflow_store = InMemoryWorkflowStore()
        inspector_store = InMemoryInspectorRunStore()
        approval_queue = HumanApprovalQueue()
        copilot_store = InMemoryCopilotGovernanceRunStore()
        stores = []

    event_bus = AsyncEventBus(event_store=event_store, dead_letter_store=dead_letter_store)
    audit_runtime = AuditLedgerRuntime(audit_store)
    await event_bus.subscribe(
        name="audit-ledger-runtime",
        event_types={"*"},
        handler=audit_runtime.record_event,
    )

    signal_pipeline = SignalIngestionPipeline(event_bus, signal_store)
    graph_mutations = LiveGraphMutationEngine(event_bus, graph_store)
    graph_reflections = TemporalGraphReflectionCycle(event_bus, graph_store, reflection_store)
    workflow_state_machine = WorkflowStateMachine(workflow_store, event_bus)
    governance_runtime = GovernanceRuntime(event_bus, approval_queue)

    signal, _trace = await signal_pipeline.ingest(
        IngestSignalCommand(
            tenant_id=tenant_id,
            organization_id=organization_id,
            signal_type="manual_signal",
            payload={"phase": "3.2", "source": "backend-smoke"},
            actor_id="phase-3-2-smoke",
        )
    )

    mutation = await graph_mutations.mutate_relationship(
        GraphMutationCommand(
            tenant_id=tenant_id,
            organization_id=organization_id,
            source_entity_id=uuid4(),
            target_entity_id=uuid4(),
            relationship_type="smoke_signal_for",
            confidence_delta=0.15,
            reason="Phase 3.2 backend smoke mutation",
            actor_id="phase-3-2-smoke",
        )
    )
    reflection = await graph_reflections.run(tenant_id, organization_id)

    workflow = await workflow_state_machine.start(
        WorkflowInstance(
            tenant_id=tenant_id,
            organization_id=organization_id,
            workflow_type="phase_3_2_smoke_review",
            target_entity_type="signal",
            target_entity_id=str(signal.signal_id),
            created_by="phase-3-2-smoke",
        )
    )
    workflow = await workflow_state_machine.transition(
        WorkflowTransitionCommand(
            workflow_id=workflow.workflow_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            actor_id="phase-3-2-smoke",
            next_state=WorkflowState.PENDING_REVIEW,
            reason="Phase 3.2 smoke requires review",
        )
    )

    governed = await governance_runtime.execute(
        GovernanceActionCommand(
            tenant_id=tenant_id,
            organization_id=organization_id,
            action="publish_report",
            resource_type="graph_reflection",
            resource_id=str(reflection.reflection_id),
            actor_id="phase-3-2-smoke",
            confidence=0.7,
        )
    )

    inspector_runtime = InspectorCollaborationRuntime(event_bus)
    inspector_runtime.register(OpportunityHunterInspector())
    inspector_runtime.register(ThreatMonitorInspector())
    inspector_runtime.register(LeadScoutInspector())
    inspector_loop = InspectorExecutionLoop(inspector_runtime, inspector_store)
    inspector_run = await inspector_loop.run_once(
        InspectorCollaborationCommand(
            tenant_id=tenant_id,
            organization_id=organization_id,
            invoked_by="phase-3-2-smoke",
            objective="verify backend inspector execution loop",
        )
    )

    copilot_runtime = CopilotGovernanceDemoRuntime(
        signal_pipeline=signal_pipeline,
        graph_mutations=graph_mutations,
        graph_reflections=graph_reflections,
        workflow_state_machine=workflow_state_machine,
        run_store=copilot_store,
    )
    copilot = await copilot_runtime.run(
        CopilotGovernanceCommand(
            tenant_id=tenant_id,
            organization_id=organization_id,
            submitted_by="phase-3-2-smoke",
            signal_payload={"copilot": "governance-smoke", "risk": "oversharing"},
        )
    )

    replayed = await event_bus.replay(EventReplayCursor(after_sequence=0))
    pending = await approval_queue.list_pending(tenant_id)
    dead_letters = await dead_letter_store.recent(limit=10)

    assert signal.signal_id
    assert mutation.relationship.relationship_id
    assert reflection.relationship_count >= 1
    assert workflow.state == WorkflowState.PENDING_REVIEW
    assert governed.approval_id is not None
    assert pending
    assert inspector_run.status == "completed"
    assert copilot.workflow_state == WorkflowState.PENDING_REVIEW
    assert len(replayed) >= 10
    assert dead_letters == []

    for store in stores:
        close = getattr(store, "close", None)
        if close is not None:
            await close()

    mode = "postgres" if use_postgres else "memory"
    print(f"phase 3.2 backend smoke ok ({mode}) events={len(replayed)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postgres", action="store_true", help="Use PostgreSQL-backed stores.")
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL URL. Defaults to DATABASE_URL.",
    )
    args = parser.parse_args()
    asyncio.run(run_smoke(use_postgres=args.postgres, database_url=args.database_url))


if __name__ == "__main__":
    main()
