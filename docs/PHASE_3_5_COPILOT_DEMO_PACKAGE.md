# Phase 3.5 Copilot Governance Demo Package

Phase 3.5 packages the backend runtime into a sellable **template** demo flow:

> Copilot signal -> graph update -> policy evaluation -> workflow approval -> audit replay.

This is not a polished SaaS UI. It is a backend-first proof that Noetfield can
operate as governed AI trust infrastructure. Factories are retired as product language — use **templates** and **policy packs**.

## What the demo proves

- A Copilot Governance signal can be ingested.
- The signal mutates the living knowledge graph.
- The graph reflection cycle summarizes governance state.
- The workflow enters human review.
- The policy pack enforces review before publication.
- Inspectors run in a bounded execution loop.
- The audit package can replay the runtime path.

## Run the demo

```bash
PYTHONPATH=packages/types:packages/config:services/events:services/ledger:services/graph:services/governance:services/signals:services/workflow:services/ai-runtime:services/inspectors:services/identity:services/copilot-governance \
  python3 scripts/run_copilot_governance_demo.py \
  --input demos/copilot-governance/sample_copilot_signal.json \
  --output demos/copilot-governance/generated/demo_output.json
```

Or use:

```bash
make phase35-demo
bash scripts/deploy-copilot-template.sh
```

## Demo narrative

1. **Signal ingestion**
   - A Microsoft Copilot readiness signal enters the runtime.
   - Payload hash and provenance are preserved.

2. **Graph mutation**
   - The runtime links the signal to a governed tenant/entity relationship.
   - Confidence evolves from evidence.

3. **Graph reflection**
   - The runtime summarizes relationship count and confidence state.

4. **Workflow governance**
   - A Copilot Governance review workflow starts.
   - It enters `pending_review`.

5. **Policy enforcement**
   - The Phase 3.4 policy pack evaluates the use-case action.
   - Human review is required.
   - A human approval request event is emitted.

6. **Inspector execution**
   - Opportunity Hunter, Threat Monitor, and Lead Scout run through a bounded
     inspector execution loop.

7. **Audit replay**
   - The output includes replayable governance events and audit counts.

## What to sell from this

### Copilot Governance Readiness + Trust Ledger Pilot

Positioning:

> Noetfield gives regulated enterprises a governed Copilot readiness trail:
> signals, graph context, workflow approvals, policy decisions, and replayable
> audit memory.

Pilot deliverables:

- Copilot Governance signal intake
- Trust Ledger event trail
- risk and evidence summary
- workflow approval model
- board-ready governance brief
- audit replay package

## API demo commands

Start the backend:

```bash
make api
```

Manual ingestion:

```bash
curl -X POST http://localhost:8000/ingestion/manual \
  -H "Content-Type: application/json" \
  -d @demos/copilot-governance/sample_copilot_signal.json
```

Run the packaged use case through the API:

```bash
curl -X POST http://localhost:8000/use-cases/copilot-governance/demo \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "organization_id": "22222222-2222-2222-2222-222222222222",
    "submitted_by": "demo.governance.lead@noetfield.local",
    "signal_payload": {
      "signal_type": "copilot_governance_readiness",
      "requested_outcome": "Create a Trust Ledger trail for Copilot readiness."
    }
  }'
```

Replay events:

```bash
curl "http://localhost:8000/events/replay?after_sequence=0&event_type=*"
```

## Demo output

The generated output contains:

- `board_brief`
- `audit_package`
- `runtime_result`
- `input_signal`

See:

- `demos/copilot-governance/sample_copilot_signal.json`
- `demos/copilot-governance/sample_deliverable_shape.json`
