# Bank-grade checklist (internal)

**Definition:** A regulated buyer can complete diligence and a pilot without confusion, boundary violations, or amateur surfaces — not a core banking build.

**Related:** Full-stack plan (pillars 1–5) · [GOVERNANCE_PILOT_RUNBOOK.md](./GOVERNANCE_PILOT_RUNBOOK.md) · [diligence/](./diligence/)

---

## Pillar 1 — Experience (www + console)

- [x] www v3 tokens + shell ([DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md))
- [x] Platform console loads `noetfield-tokens.css` + `noetfield-console.css`
- [x] Pilot API key field (sessionStorage) + `Authorization: Bearer` on evaluate/ledger/export
- [x] RID copy / new RID / audit-export link in console UI
- [x] Public site health: tier pages + viewport; partials excluded from viewport scan
- [x] GTM copybook: console row uses engagement intake (not procurement)
- [ ] Founder: P0 responsive check at 320 / 768 / 1280 on device lab

---

## Pillar 2 — Institutional API

- [x] PR #14 merged: pilot auth, rate limits, determinism test, trust-brief export script
- [ ] Regenerate OpenAPI when routes change (`make generate-openapi`)
- [x] Pilot story documented: evaluate → audit-export by RID

---

## Pillar 3 — Production & security (ops)

- [ ] Founder: [WAVE0_SHIP_CHECKLIST.md](./WAVE0_SHIP_CHECKLIST.md) — DNS, TLS, pilot keys, Shadow Week
- [ ] `PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh` exit 0
- [ ] Staging: `staging-platform` smoke green ([STAGING.md](./STAGING.md))
- [ ] Postgres backup drill quarterly ([POSTGRES_OPERATIONS.md](./POSTGRES_OPERATIONS.md))
- [x] www `/status/` aligned with `GET /api/status`
- [ ] WAF / CDN rate limits when traffic warrants ([PRODUCT_DEFERRED.md](./PRODUCT_DEFERRED.md) NF-ENG-16)

---

## Pillar 4 — Diligence & GTM

- [x] [docs/diligence/](./diligence/) — sample export, OpenAPI pointer, RPAA one-pager
- [x] MSB templates under `ops/templates/msb/`
- [x] Print CSS: `assets/noetfield-print.css`

---

## Pillar 5 — Quality gates

```bash
make verify-final-lock
make site-health
make console-smoke
python3 scripts/verify_sitemap_committed.py
```

- [x] `scripts/smoke_bank_grade_html.py` (P0 pages + console HTML markers)
- [ ] Optional: Playwright in `governance-console/` for full browser E2E

---

## Anti-goals (do not schedule)

- L2 microservice mesh from internal design docs as production topology
- `apps/web` as canonical www without ASF decision
- `governance-console/` Next app as production pilot UI
- Public payment / fintech hero copy
