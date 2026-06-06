# Copilot Readiness Pilot Runbook

**Audience:** 1–2 SME design partners (M365 Copilot Governance Pack).  
**Prerequisite:** `make dev-local` + `make verify-local-dev` on Mac (`:13080`).

## Pre-flight

- [ ] Phase 1B complete: `tenants` + `audit_events`, `POST /evaluate` returns `tenant_id`
- [ ] `GET /audit/export` returns bundle with `integrity_hash`
- [ ] Policy samples validated: `scripts/validate-compliance-schemas.sh`
- [ ] PR #15 merged to staging per `docs/GO_LIVE.md` (deploy owner)

## Day 0 — Intake

1. Partner completes `/trust-brief/intake/?vector=copilot-governance`
2. Assign pilot tenant slug `copilot-pilot-01` (or dedicated UUID)
3. Send RID email flow from trust brief automation

## Day 1–3 — QuickScan

1. Run questionnaire (www `copilot/quickscan` surface)
2. `POST /evaluate` with sample oversharing context; capture RID
3. `GET /audit/{rid}` — confirm tenant isolation
4. Optional: `scripts/run_copilot_governance_demo.py` for platform workflow path

## Day 4–10 — Readiness

1. Execute control catalog tests (`docs/spec/copilot-control-catalog.md`)
2. Bind `copilot-oversharing-v1` policy pack (manual v1)
3. Workflow: `CopilotReadiness.workflow.json` → dual signoff (mock or real roles)
4. Deliver redacted `audit-export` sample to `docs/diligence/`

## Day 11–14 — Evidence bundle

| Artifact | Location |
|----------|----------|
| Audit export JSON | `/audit/export` |
| Control heatmap spec | `docs/spec/compliance-dashboard-v1.md` |
| Conflict matrix | `docs/spec/trustfield-noetfield-conflict-matrix.md` |
| Agent run replay | `make phase35-demo` (when platform DB up) |

## Success criteria (90-day)

- QuickScan → evaluate → RID → export in &lt; 5 min demo
- 100% tool calls logged on agent demo path
- Zero payment-rail code in repo (`make verify-final-lock`)
- `make verify-local-dev` green on canonical stack

## Bank Pilot

Maintain shadow evaluate docs only; **do not** reorder ahead of Copilot pilot completion.

## Escalation

- Connection refused on `:13080` → `make dev-local` (see `docs/LOCAL_DEV.md`)
- Missing `tenant_id` on evaluate → restart gov API on `:18002` with SQLite `DATABASE_URL`
