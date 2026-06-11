# Noetfield — Copilot Procurement One-Pager

**Positioning:** AI Governance & Evidence layer for Microsoft 365 Copilot adoption.

**Buyer line:** *We produce the audit trail your Copilot deployment will be asked for later.*

## What you get

- Pre-execution **governance evaluate** (allow / deny / review) with RID lineage
- **Evidence Index** — metadata-only ingest (Purview, Entra ID, Audit, SharePoint)
- **Trust Ledger Entry (TLE v1)** — signed go/no-go with **confidence score** and approval chain
- **Board pack export** — JSON, HTML, PDF
- **Procurement pack (ZIP)** — one-click diligence bundle (JSON + PDF + README + optional audit slice)

## Framework orientation

Primary citations: `docs/reference/GOVERNANCE_SOURCES_BOOK_v1.md` (NIST AI RMF, ISO 42001, EU AI Act, Microsoft Purview Part B). Purview/M365: we index metadata evidence into TLE — what you configured, not what we replace. Orientation only — not legal advice.

## Out of scope

No payments, custody, settlement, or money transmission.

## Verify locally

```bash
make dev-local
make verify-gtm
```

Share external demo:

```bash
make dev-local-tunnel-bg && make demo-url
```

## Artifacts

- Buyer pack page: `/copilot/procurement/`
- 5-minute demo: `/copilot/demo/`
- TLE samples: `/trust-ledger/sample-report/`
- Pilot runbook: `docs/spec/copilot-readiness-pilot-runbook.md`
- Staging: `docs/ops/STAGING_DEMO.md`
