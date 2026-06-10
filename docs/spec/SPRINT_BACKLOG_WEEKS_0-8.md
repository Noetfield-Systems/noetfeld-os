# Sprint backlog — Weeks 0–8 (SHIP)

**Plane:** DELIVERY · **Source:** Trust Ledger blueprint v1.2

## Week 0–2 (P0 — market + schema) — IN PROGRESS

| ID | Story | Acceptance | Status |
|----|-------|------------|--------|
| W02-1 | Publish 3 TLE YAML examples | Files in `docs/spec/examples/` + linked from www | done |
| W02-2 | Homepage Copilot buyer line | Hero or trust-ledger mentions audit trail for Copilot | done |
| W02-3 | Evidence Intake Contract v1 | `docs/diligence/EVIDENCE_INTAKE_CONTRACT_v1.md` | done |
| W02-4 | SHIP_NOW + sprint doc | This file + `os/SHIP_NOW.md` (`docs/SHIP_NOW.md` pointer) | done |
| W02-5 | Merge PR #15 to main | CI + `make ship-verify` | done |
| W02-6 | Founder GO_LIVE steps | WAVE0 checklist production smoke | todo (founder) |

## Week 3–4 (P1 — ledger core)

| ID | Story | Acceptance | Status |
|----|-------|------------|--------|
| W34-1 | `tle_entries` table + append API | POST draft → immutable write after approve | done (MVP) |
| W34-2 | Evidence Index ingest API | POST metadata; hash stored | done (MVP) |
| W34-3 | Connector manifest Purview/Entra | Register + last_sync status | done (API) |

## Week 5–6 (P1 — workspace)

| ID | Story | Acceptance | Status |
|----|-------|------------|--------|
| W56-1 | Trust Ledger Workspace list/search | `GET /api/v1/tle` + evidence list | done (API) |
| W56-2 | TLE Generator v0 | Template + evidence refs → draft TLE | done (API + `/trust-ledger/new`) |
| W56-3 | Confidence Score v0 | Deterministic score + factors in UI | done |

## Week 7–8 (P1 — pilot)

| ID | Story | Acceptance | Status |
|----|-------|------------|--------|
| W78-1 | Approval chain + signer stub | 2+ approvers; signed TLE immutable | done |
| W78-2 | PDF Board Pack export | GET export returns PDF | done (stub) |
| W78-3 | Pilot engagement | 1–2 Copilot Go/No-Go + Procurement Pack delivered | **ASF only** |
