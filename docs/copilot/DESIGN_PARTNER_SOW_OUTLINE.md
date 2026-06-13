# Copilot Governance Pack SOW Outline — 90-day pilot

**Audience:** Founder + buyer legal/procurement  
**GTM lock:** One contracted org uses a board PDF in a real governance meeting ($2k–10k · Copilot Governance Pack)  
**Not legal advice** — customize per engagement.

## One-line scope

Noetfield provides the **AI Governance & Evidence layer** for a Microsoft 365 Copilot readiness pilot: evaluate operational intent, index metadata-only M365 evidence, produce signed **Trust Ledger Entries (TLE v1)**, and export board-ready diligence artifacts.

**Buyer line:** *We produce the audit trail your Copilot deployment will be asked for later.*

## In scope (pilot)

| Deliverable | Description |
|-------------|-------------|
| Governance evaluate | Pre-execution allow/deny/review with RID lineage |
| Evidence index | Metadata-only Purview, Entra ID, Audit, SharePoint connectors (read-only); indexes configured controls |
| TLE v1 | Signed go/no-go with confidence score + sequential approval chain |
| Board pack | JSON, HTML, PDF export |
| Procurement pack | One-click ZIP (JSON + PDF + README + audit slice) |
| Audit export | Tenant-scoped `GET /audit/export` bundle |

## Out of scope

- Payment initiation, custody, settlement, money transmission
- Production Azure AD secrets management (founder vault)
- TrustField / VIRLUX / member portal execution
- Lane C features

## Success signals (GTM locked)

1. Partner uploads or connects evidence (M365 metadata).
2. Partner generates at least one **approved TLE** with visible confidence score.
3. Partner exports **board pack PDF** and uses it in a governance meeting (board, risk, or legal).
4. Optional: partner shares procurement ZIP with diligence reviewers.

## Suggested pilot terms (template)

| Term | Example |
|------|---------|
| Duration | 4–6 weeks (up to 90-day program band) |
| Fee | $2,000–$10,000 (Copilot Governance Pack) |
| Data | Metadata only; no content exfiltration |
| Support | Weekly check-in + `make verify-gtm` demo environment |
| Reference | Case study rights (optional, by mutual agreement) |

## Artifacts to attach

- `docs/copilot/PROCUREMENT_ONE_PAGER.md`
- `docs/copilot/DESIGN_PARTNER_PIPELINE_v1.md` (internal ops name — public SKU: Copilot Governance Pack)
- Sample TLE: `/trust-ledger/sample-report/`

**Intake:** `/trust-brief/intake/?interest=pilot&vector=copilot-governance`
