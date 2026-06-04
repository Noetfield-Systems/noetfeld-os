# Sprint backlog — Weeks 0–8 (SHIP)

**Plane:** DELIVERY · **Source:** Trust Ledger blueprint v1.2

## Week 0–2 (P0 — market + schema) — IN PROGRESS

| ID | Story | Acceptance | Status |
|----|-------|------------|--------|
| W02-1 | Publish 3 TLE YAML examples | Files in `docs/spec/examples/` + linked from www | done |
| W02-2 | Homepage Copilot buyer line | Hero or trust-ledger mentions audit trail for Copilot | done |
| W02-3 | Evidence Intake Contract v1 | `docs/diligence/EVIDENCE_INTAKE_CONTRACT_v1.md` | done |
| W02-4 | SHIP_NOW + sprint doc | This file + `docs/SHIP_NOW.md` | done |
| W02-5 | Merge PR #15 to main | CI + `make ship-verify` | todo |
| W02-6 | Founder GO_LIVE steps | WAVE0 checklist production smoke | todo (founder) |

## Week 3–4 (P1 — ledger core)

| ID | Story | Acceptance |
|----|-------|------------|
| W34-1 | `tle_entries` table + append API | POST draft → immutable write after approve |
| W34-2 | Evidence Index ingest API | POST metadata; hash stored |
| W34-3 | Connector manifest Purview/Entra | Register + last_sync status |

## Week 5–6 (P1 — workspace)

| ID | Story | Acceptance |
|----|-------|------------|
| W56-1 | Trust Ledger Workspace list/search | Read-only TLE viewer |
| W56-2 | TLE Generator v0 | Template + evidence refs → draft TLE |
| W56-3 | Confidence Score v0 | Deterministic score + factors in UI |

## Week 7–8 (P1 — pilot)

| ID | Story | Acceptance |
|----|-------|------------|
| W78-1 | Approval chain + signer stub | 2+ approvers; signed TLE immutable |
| W78-2 | PDF Board Pack export | GET export returns PDF |
| W78-3 | Pilot engagement | 1–2 Copilot Go/No-Go + Procurement Pack delivered |
