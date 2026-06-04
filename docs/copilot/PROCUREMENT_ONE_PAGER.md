# Noetfield — Copilot Procurement One-Pager

**Positioning:** AI Governance & Evidence layer for Microsoft 365 Copilot adoption.

**Buyer line:** *We produce the audit trail your Copilot deployment will be asked for later.*

## What you get

- Pre-execution **governance evaluate** (allow / deny / review) with RID lineage
- **Evidence Index** — metadata-only ingest (Purview, Entra ID, Audit, SharePoint)
- **Trust Ledger Entry (TLE v1)** — signed go/no-go with confidence score and approval chain
- **Board pack export** — JSON + HTML for diligence

## Out of scope

No payments, custody, settlement, or money transmission.

## Verify locally

```bash
make dev-local
make verify-local-dev
./scripts/tle-smoke.sh
```

Demo: http://localhost:13080/workspace

## Artifacts

- TLE samples: `/trust-ledger/sample-report/`
- Pilot runbook: `docs/spec/copilot-readiness-pilot-runbook.md`
- Staging: `docs/ops/STAGING_DEMO.md`
