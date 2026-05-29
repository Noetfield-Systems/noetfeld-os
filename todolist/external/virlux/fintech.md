# VIRLUX — fintech / payments

> **SEPARATE PROJECT — not Noetfield.** Implement only in the VIRLUX repository.  
> This file lives in the Noetfield repo as **reference notes** so chat ideas are not lost.

Product: Canadian B2B FX / payments · Demo: `demo@virlux.com` / `demo12345` (dev seed only)

## Launch blockers before real money

> These are **not code bugs** — founder, compliance, and bank/partner wiring.

| ID | Item | Status | Owner | Type | Notes |
|----|------|--------|-------|------|-------|
| VL-FIN-01 | **Interac confirmation** — real banking webhook; deposits stay pending until wired | todo | founder | launch_blocker | No production confirmation path yet |
| VL-FIN-02 | **KYC review UI** — admin approve/reject for compliance ops | todo | engineering | launch_blocker | Production compliance workflow |
| VL-FIN-03 | **httpOnly cookie auth** — move JWT off `localStorage` (XSS risk) | todo | engineering | launch_blocker | BFF or cookie-based session for prod |
| VL-FIN-04 | **Legal review** — Terms, full privacy policy | todo | legal | launch_blocker | |
| VL-FIN-05 | **MSB registration** — copy/UI only when actually registered | blocked | legal | launch_blocker | Do not claim status prematurely |
| VL-FIN-06 | **Circle production** — sandbox done; prod webhook/polling for transfer status | todo | founder | launch_blocker | |

## Local dev checklist (VIRLUX repo)

| ID | Item | Status | Notes |
|----|------|--------|-------|
| VL-DEV-01 | `unset DATABASE_URL` if shell has stale sqlite URL | todo | |
| VL-DEV-02 | `docker compose up -d postgres` | todo | |
| VL-DEV-03 | `npm run db:migrate && npm run db:seed` | todo | `AUTO_SETTLE=true` for demo flow |
| VL-DEV-04 | `npm run dev` — build + 10 tests pass | todo | |
| VL-DEV-05 | TrustField codebase untouched for VIRLUX work | done | Per prior session note |

## Trust boundaries

| ID | Item | Status | Notes |
|----|------|--------|-------|
| VL-TF-01 | TrustField / Noetfield not modified by VIRLUX UI work | done | Separate products |
