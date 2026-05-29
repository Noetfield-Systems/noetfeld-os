# Next moves — Noetfield only

**Last reviewed:** 2026-05-29 · **Scope:** This file is **only** for the Noetfield repository (`noetfield.com` / platform API).

**Strategy:** [../docs/strategy/noetfield-future-path.md](../docs/strategy/noetfield-future-path.md) · **Boundaries:** [../PROJECT_BOUNDARIES_LOCKED.md](../PROJECT_BOUNDARIES_LOCKED.md) (TrustField and VIRLUX are external — do not mix).

---

## Roadmap (Noetfield)

| Horizon | Goal |
|---------|------|
| **Now** | Go live: www + platform, assistant, intake, optional Telegram |
| **Next** | Ops (backups, alerts), legal clean, staging, CI deploy |
| **Later** | RAG, pilot auth, console hardening |

---

## P0 — Noetfield launch blockers

> **Founder/ops runbook:** [docs/GO_LIVE_CHECKLIST.md](../docs/GO_LIVE_CHECKLIST.md)

### Founder / ops

- [ ] **NF-SECRET-01** — Rotate keys pasted in chat; platform env only
- [ ] **NF-DEPLOY-02** — DNS + TLS: `www` + `platform`
- [ ] **NF-DEPLOY-01** — Deploy API (`make platform-migrate`, `make platform-up`)
- [ ] **NF-LLM-01** — `OPENROUTER_API_KEY` (+ `GEMINI_API_KEY` fallback); `./scripts/deploy_platform_smoke.sh`
- [ ] **NF-WWW-01** — Deploy static www + `noetfield-ecosystem.json`

### Telegram (optional)

- [ ] **NF-TG-01** — Token + register webhook → `ready: true`
- [ ] **NF-TG-02** — Publish `@username` via `publish_ecosystem_config.py`

### Legal

- [ ] **NF-WWW-02** — Review `privacy/`, `terms/` (3 SKUs, no custody/payments)
- [ ] **NF-WWW-05** — No MSB/regulatory claims unless registered

---

## P1 — Fix in this repo

| # | ID | Task |
|---|-----|------|
| 1 | NF-WWW-04 | Regenerate `sitemap.xml` + CI | done — `scripts/generate_sitemap.py`, www CI |
| 2 | NF-WWW-03 | API-only intake (Formspree removed) | done — `noetfield-intake-api.js` |
| 3 | NF-WWW-14 | `/gate/intake/` Copilot + Bank Pilot cards | done |
| 4 | NF-ENG-10 | Intake Postgres backup/retention docs | done — `docs/INTAKE_BACKUP_RETENTION.md` |
| 5 | NF-ENG-14 | CI/CD deploy platform on `main` | done — `platform-deploy.yml` (validate + smoke) |
| 6 | NF-ENG-15 | Staging + CORS | done — `docs/STAGING.md` |
| 7 | NF-WWW-02 | Remove “procurement” on intake pages | done — gate/intake + trust-brief links |
| 8 | NF-ENG-17 | Telegram structured intake → API | done — `INTAKE: org \| email \| msg` |
| 9 | NF-WWW-13 | Static www canonical | done — `docs/CANONICAL_WWW.md` |

---

## P2 — Later (Noetfield)

- NF-ENG-12 pgvector RAG · NF-ENG-11 CRM · NF-ENG-13 Langfuse · NF-ENG-16 WAF · NF-WWW-10 pricing page

---

## Verify (Noetfield)

```bash
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh
```
