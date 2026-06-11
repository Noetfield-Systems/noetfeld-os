# Lane A sprint map (Noetfield cloud — Week 0–2 + P1)

**Lane:** `noetfield_cloud` · **Thread:** `THREAD-PORTFOLIO`  
**Authority:** [os/plan.json](../../os/plan.json) · detail: [docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md](../spec/SPRINT_BACKLOG_WEEKS_0-8.md)

| Step | Task id | Outcome | Verify | Status |
|------|---------|---------|--------|--------|
| A1 | ship-p0-gtm-002 | Copilot positioning + TLE docs + evidence contract | Pages + docs paths | done |
| A2 | ship-p0-merge-001 | Merge PR #15 → `main`, ship-verify green | `make ship-verify` | done |
| A3 | — | **ASF only** — WAVE0 production smoke | `docs/WAVE0_SHIP_CHECKLIST.md` | blocked (ASF) |
| A4 | ship-p1-ledger-003 | Trust Ledger MVP (4 routes) | `tle-smoke.sh --api` | done |
| A5 | W34-3 | Connectors API | `POST/GET /api/v1/connectors` | done |
| A6 | W56-1 | List TLE + evidence | `GET /api/v1/tle`, `GET /api/v1/evidence` | done |
| A7 | W78-1 | Multi-approver (`TLE_REQUIRED_APPROVALS=2`) | pytest multi-approve | done |
| A8 | W78-2 | PDF export stub | `GET /api/v1/tle/{id}/export` | done |
| A9 | — | **ASF only** — live pilot W78-3 | customer engagement | blocked (ASF) |

**Agent verify (no ASF):** `./scripts/tle-smoke.sh` · `./scripts/tle-smoke.sh --api` · `pytest tests/unit/test_trust_ledger_v1.py`
