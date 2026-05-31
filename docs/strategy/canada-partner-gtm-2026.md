# Noetfield Canada partner-infra GTM strategy (2026–2027)

**Status:** Active · **Scope:** Noetfield only  
**Supersedes:** Nothing — complements [noetfield-future-path.md](./noetfield-future-path.md) and institutional API work on `main`.

TrustField and VIRLUX are out of scope ([PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md)).

---

## Strategic anchor

| You are | You are not |
|---------|-------------|
| Governance execution + AI policy enforcement (pre-execution) | RPAA registrant, MSB, PSP, stablecoin issuer, exchange operator |
| Client-facing partner infra — APIs, console, audit export, RID | Routing layer, corridor intelligence, “we move money via NDAX/Circle” |
| Trust Brief → Trust Ledger → control layer (`/api/v1/governance/*`) | Fourth retail SKU or Trust Ledger subscription ([GTM_BANK_GRADE_FINAL.md](../GTM_BANK_GRADE_FINAL.md)) |

**Wedge:**

> Before your bank, exchange, or PSP executes — Noetfield evaluates intent, records Trust Ledger evidence, and returns allow/deny for regulators and boards.

---

## Canada market map

| Force | Buyer fear | Noetfield answer |
|-------|------------|------------------|
| OSFI E-23 (May 2027) | Third-party AI without evidence | Bank Pilot shadow + vendor-evidence + audit export (RID) |
| CDB Phase 1–2 | Consent / pre-payment policy | Policy adjacency — evaluate before TPP write; no OB write in Noetfield |
| Stablecoin Act (~2027 in force) | Issuer/PSP auditability | Governance + evidence for issuers/PSPs — never issuance |
| RPAA expansion | PSP supervision | Software vendor outside RPAA perimeter; attach to partner controls |
| API-first digital platforms | Controls bolted on late | Embedded control plane (evaluate in core workflow) |

**Prohibited public language:** NDAX/Circle route comparison, settlement orchestration, MSB/meta-gateway ([NORTH_STAR.md](../../NORTH_STAR.md)).

---

## Layer cake (digital platform)

| Layer | Owner | Noetfield |
|-------|--------|-----------|
| L5 UX | Bank, fintech, exchange | Optional console embed |
| L4 Orchestration | Partner engineering | Webhook `governance.decision.recorded` |
| L3 Control | Noetfield | Evaluate, policy packs, Trust Ledger |
| L2 Execution | FRFI, VASP, PSP, issuer | Orders, transfers, mint/redeem |
| L1 Market infra | Exchanges, BoC | Read-only signals into L3 |

---

## Product story

| Brand | Meaning | Technical |
|-------|---------|-----------|
| Trust Brief | $10k diagnostic | `/trust-brief/intake/` → `POST /api/intake` |
| Trust Ledger | Immutable compliance log | `GET /api/v1/governance/ledger`, `audit-export` |
| Control layer | Partner pilot API | `POST /api/v1/governance/evaluate` (`shadow` \| `enforce`) |

Public pages: [/partners/](../../partners/), [/trust-ledger/](../../trust-ledger/), [/bank-pilot/](../../bank-pilot/).

---

## Exchange adjacency (licensed VASP / exchange)

- Partners retain order placement and custody.
- Noetfield: pre-check evaluate + optional read-only signal ingest ([partner_signal.py](../../services/governance/noetfield_governance/partner_signal.py)).
- Exchange names in NDA decks unless co-marketing is signed.

---

## ICP motions

| Tier | Motion | KPI |
|------|--------|-----|
| A FRFI | Trust Brief → Bank Pilot → pilot API | 1 FRFI production pilot |
| B VASP/exchange | Partner intake → shadow POC | 2 design partners on staging |
| C Enterprise | Copilot + Trust Ledger cross-sell | Evaluate in SOW |
| D Channels | RBCx / FinSec / NCFA education | 3 qualified intakes/quarter |

---

## Messaging (say / don’t say)

| Say | Don’t say |
|-----|-----------|
| Pre-execution governance infrastructure | Payment orchestration |
| Trust Ledger / compliance log | Custody, wallet |
| Partner control layer | Meta-gateway, route via NDAX |
| RPAA-safe software vendor | RPAA registration for Noetfield |

---

## Collateral

- [SHADOW_WEEK_DEMO.md](../SHADOW_WEEK_DEMO.md)
- [collateral/canada-stack-2027-onepager.html](../collateral/canada-stack-2027-onepager.html)
- [channel-outreach/](./channel-outreach/) — incubator narratives (no bank endorsement)

---

## Success metrics

- Partner intakes ≥6/quarter (`vector=partner-*`)
- Shadow evaluate on partner staging ≥2
- `make verify-final-lock` clean; zero MSB/RPPAA claims on www

---

## MSB channel (fast revenue)

- [msb-partner-playbook.md](./msb-partner-playbook.md)
- [MSB_DEPLOY_AND_PILOT.md](../MSB_DEPLOY_AND_PILOT.md)
- [MSB_STAGING_INTEGRATION.md](../MSB_STAGING_INTEGRATION.md)

## Related docs

- [docs/api/PARTNER_PRE_EXECUTION.md](../api/PARTNER_PRE_EXECUTION.md)
- [docs/api/CANADA_TRUST.md](../api/CANADA_TRUST.md)
- [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md)
