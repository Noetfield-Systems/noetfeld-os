# Trust Ledger v1.2 — 60-day sprint backlog

**Authority:** [NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md](../docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md)  
**Rule:** One `os/plan.json` task per implement turn — queue in `os/SHIP_NOW.md`. Required ingest YAML after VERIFY; do not edit SinaPromptOS.

---

## P0 — Weeks 0–2 (Market clarity + schema)

| ID | Story | Acceptance | Status |
|----|-------|------------|--------|
| P0-1 | Publish TLE v1 schema + 3 examples | Schema validates samples; linked from www | **Done** |
| P0-2 | Evidence Intake Contract v1 | Doc + JSON schema; procurement-ready | **Done** |
| P0-3 | Homepage v1.2 rewrite | Hero buyer line; TLE example; integration scope; CTA Go/No-Go | **Done** |
| P0-4 | Sample Ledger download | Public PDF/YAML from `/trust-ledger/sample-report/` aligned to TLE v1 | **Done** |

---

## P1 — Weeks 3–6 (Minimal product layer)

| ID | Story | Acceptance | Status |
|----|-------|------------|--------|
| P1-1 | Trust Ledger Core (DB) | `tle_entries` table; append-only; `audit_digest` on write | **Done** |
| P1-2 | Evidence Index API | `POST /evidence/ingest`, `GET /evidence/{id}` per OpenAPI | **Done** |
| P1-3 | Connector registry | `POST /connectors`; manifest stored; status field | **Done** |
| P1-4 | TLE Generator | `POST /tle/draft` from template + evidence refs; Confidence Score | **Done** |
| P1-5 | Trust Ledger Workspace UI | List/search TLEs; viewer (evidence + approvals); read-only RBAC | **Done** |
| P1-6 | M365 metadata ingest (stub) | Purview + Entra ID sample payloads → Evidence Index | **Done** |

---

## P1 — Weeks 7–8 (Procurement + pilot)

| ID | Story | Acceptance | Status |
|----|-------|------------|--------|
| P1-7 | Approval chain API + UI | `POST /tle/{id}/approve`; 2+ signers; immutable after final sign | **Done** |
| P1-8 | PDF / Board Pack export | `GET /tle/{id}/export`; evidence index + signatures | **Done** |
| P1-9 | Pilot runbook execution | 1–2 design partners; Go/No-Go + Procurement Authorization Pack | **Done** |
| P1-10 | KMS digest stub | `audit_digest` + `signature_hash` verifiable in dev | **Done** |

---

## Verification commands

```bash
# Schema + samples
python3 scripts/validate-tle-samples.py

# Local stack
make dev-local && make verify-local-dev

# TLE API (when implemented)
./scripts/tle-smoke.sh
```

---

## Dependency order

```
P0-3 homepage → P1-5 workspace UI
P1-1 ledger DB → P1-4 generator → P1-7 approvals → P1-8 export
P1-2 evidence → P1-4 generator
P1-3 connectors → P1-6 M365 stub
```
