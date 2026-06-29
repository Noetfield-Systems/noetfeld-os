# [NOOS-AGENT-20260615-006] 90-Day Execution Plan — Noetfield OS

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260615-006
doc_type: EXECUTION_PLAN
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — canonical Q3 2026 execution plan
related_docs: NOOS-AGENT-20260529-002, NOOS-AGENT-20260608-004, NOOS-AGENT-20260608-005
-->

**Window:** 2026-06-15 → 2026-09-12 (12 weeks)  
**Product:** Noetfield OS — Governance Execution Layer (GEL)  
**Parent:** Noetfield Systems Inc. (`noetfield.com`)  
**Status:** Active — supersedes informal priority lists

---

## 1. Strategic thesis (90 days)

**Win condition:** One credible **Design Partner conversation** backed by a **5-minute demo** that shows pre-execution governance evidence — not a feature-complete platform.

Three parallel tracks (portfolio SSOT energy law adapted for GEL):

| Track | Energy | Outcome by day 90 |
|-------|--------|-------------------|
| **A — Revenue** | 30% | 10 ICP targets contacted · 3 discovery calls · 1 DP LOI or paid sandbox |
| **B — Product** | 45% | Auth + `request_id` + `rule_set_version` + board export on `/v1/decision` |
| **C — Category** | 25% | Phase 1 exit · `noetfield.com/gel` draft live or staged · GEL vocabulary locked |

**Non-negotiables:** non-custodial · pre-execution only · fail closed · version everything · Canada first.

---

## 2. External one-liner (Step 0002 — use everywhere)

> **Noetfield OS** evaluates policy, scores risk, and produces audit-ready evidence before your systems execute.

**30-second elevator:** See `NOOS-AGENT-20260529-002` §7.

---

## 3. Week-by-week plan

### Weeks 1–2 · Phase 1 exit (Declare & baseline)

**Goal:** Repo and positioning are production-credible on paper; Phase 1 steps 0001–0020 complete.

| Deliverable | Owner | Exit check |
|-------------|-------|------------|
| Ratify product truth (`NOOS-AGENT-20260529-002`) | Agent + ASF sign-off (0009) | Recorded in `ROADMAP_MANIFEST.json` |
| Glossary + plane tags (`NOOS-AGENT-20260615-007`) | Agent | GEL defined; anti-ICP listed |
| GEL web URL structure (`NOOS-AGENT-20260615-008`) | Agent | ASF picks hero + pricing frame |
| Pitch alignment notes (`NOOS-AGENT-20260615-009`) | Agent | SQLite vs Postgres drift flagged in PDFs |
| CI: `NOOS-AGENT-DOC` tag enforcement | Agent | `scripts/check_noos_agent_docs.sh` green |
| Pinned `requirements.txt` | Agent | Reproducible venv |
| `LICENSE` + `CONTRIBUTING.md` | Agent | Proprietary + vault rules |

**Code:** None required beyond hygiene scripts.

---

### Weeks 3–4 · Phase 2 core (Pre-execution gate)

**Goal:** API is demo-ready for a compliance meeting.

| Deliverable | Roadmap | Exit check |
|-------------|---------|------------|
| API key auth (tenant stub) | Phase 2 | 401 without key; tenant_id in audit row |
| `request_id` on every decision | Phase 2 | Client-supplied or server UUID; indexed |
| `rule_set_version` on every response + audit | Phase 2 | Matches hashed policy pack |
| Policy baseline hashes at startup | Phase 1.4 (0031–0032) | Logged in `/health` or `/v1/meta` |
| Deterministic replay test | Phase 2 | Same input → same score + outcome (pytest) |
| Fail-closed middleware | Phase 2 | 503 if DB/policy load fails |

**Demo script (5 min):**

1. Send credit-intent JSON → `POST /v1/decision`
2. Show APPROVE / REVIEW / DECLINE + factor breakdown
3. Open `GET /portal/audits` → same row with `request_id` + policy version
4. Change corridor rule → new version → show version bump on next call

---

### Weeks 5–6 · Evidence pack (Phase 3 seeds)

**Goal:** Boards buy proof, not dashboards.

| Deliverable | Exit check |
|-------------|------------|
| `GET /portal/audits/{id}/export` (JSON bundle) | Includes inputs, scores, policy hash, timestamp |
| PDF export (optional) | One-click board appendix from audit row |
| Sample CU policy pack | Conservative corridors in `policy_packs/cu_pilot_v1.json` |
| PRODUCT_TRUTH.md (Step 0021+) | Scope in/out documented at repo root |

---

### Weeks 7–8 · GTM launch prep

**Goal:** Outbound ready; website stub aligned.

| Deliverable | Exit check |
|-------------|------------|
| ICP target list (10 orgs) | BC CU + lending fintech + 1 enterprise |
| Design Partner one-pager | $2K–$10K · 90-day pilot · links to GEL sandbox |
| `noetfield.com/gel` content draft | From `NOOS-AGENT-20260615-008` |
| Recorded demo (NW1/W1 lane) | 5-min screen capture; no live mono `:8000` |
| IRAP / grant PDFs reconciled | Postgres claims fixed or footnoted |

---

### Weeks 9–12 · First pilot motion

**Goal:** One paid or LOI engagement in pipeline.

| Deliverable | Exit check |
|-------------|------------|
| 3 discovery calls completed | Notes in `.agent-private/` (not vault) |
| Read-only pilot environment | Separate port or tenant; no execution authority |
| Postgres migration plan ADR | Phase 3 — timeline + rollback |
| Phase 2 exit review | Auth + versioning + export demo passes checklist |
| ROADMAP_MANIFEST update | Phase 1 complete · Phase 2 ≥50% |

**Win codes targeted:** NW1 (DP signed) · internal GEL demo film · 100K decisions not required yet.

---

## 4. What we deliberately defer (post day 90)

| Item | Phase | Reason |
|------|-------|--------|
| Full multi-tenant RLS | 4 | Stub sufficient for first DP |
| `GET /drift` engine | 5 | Differentiator, not blocker for NW1 |
| `api.noetfield.com` production hardening | 7 | Host is live; rate limits, partner key flow, metering, and scale/SLA hardening remain |
| Trust Ledger full integration | 3–8 | Export bundle sufficient for pilot |
| SourceA engine merge | Never | Isolation from mono `:8000` |

---

## 5. Metrics dashboard (track weekly)

| Metric | W4 target | W8 target | W12 target |
|--------|-----------|-----------|------------|
| Phase 1 steps complete | 20/100 | 40/100 | 50/100 |
| Phase 2 steps complete | 5/100 | 25/100 | 40/100 |
| Decisions logged (dev/demo) | 100 | 1,000 | 5,000 |
| ICP outreach sent | 0 | 5 | 10 |
| Discovery calls | 0 | 1 | 3 |
| DP LOI / paid sandbox | 0 | 0 | 1 |
| Replay test pass rate | 100% | 100% | 100% |

---

## 6. Risk register

| Risk | Mitigation |
|------|------------|
| Grant PDFs claim Postgres; code uses SQLite | Flag in `NOOS-AGENT-20260615-009`; footnote in external PDFs |
| Scope creep into TrustField / mono runtime | `CONTRIBUTING.md` + plane tags; reject cross-lane PRs |
| No ASF sign-off on positioning (0009) | Block external site copy only; internal execution continues |
| Buyer wants full LOS | Anti-ICP script in glossary doc |
| Competing with OneTrust breadth | Stay GEL-narrow; partner path for GRC |

---

## 7. Daily agent checklist (DELIVERY lane)

- [ ] Read `ORIENTATION_START_HERE` if new session
- [ ] Confirm task is `noetfeld-os` not mono `:8000`
- [ ] Mark completed roadmap steps in `ROADMAP_MANIFEST.json`
- [ ] Tag new docs `NOOS-AGENT-DOC` + update `MANIFEST.json`
- [ ] Run `bash scripts/check_noos_agent_docs.sh` before vault edits merge

---

## 8. Related artifacts

| trace_id | Document |
|----------|----------|
| `NOOS-AGENT-20260529-002` | Business & ICP definition |
| `NOOS-AGENT-20260615-007` | Glossary + plane tags + anti-ICP |
| `NOOS-AGENT-20260615-008` | `noetfield.com/gel` URL structure |
| `NOOS-AGENT-20260615-009` | Pitch / PDF alignment notes |
| `NOOS-AGENT-20260608-004` | Full 1000-step roadmap |

---

*End of 90-day plan — `NOOS-AGENT-20260615-006`*
