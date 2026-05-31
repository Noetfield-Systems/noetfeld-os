# Market entry — 30 days (execution)

**Status:** Active on `main` · **Narrative:** [POSITIONING.md](../POSITIONING.md) · **Surfaces:** [public-surface-map.md](strategy/public-surface-map.md)

This is the runnable checklist for the Real Market GTM plan. Founder actions are marked **(founder)**; repo/agent actions are marked **(repo)**.

---

## Phase 0 — Unblock (repo + founder)

| Step | Owner | Action |
|------|-------|--------|
| 0.1 | repo | `main` includes MSB channel, institutional API, public surfaces (merged from `cursor/msb-partner-revenue-37f0`) |
| 0.2 | founder | Deploy www + platform per [GO_LIVE.md](./GO_LIVE.md) |
| 0.3 | founder | Production env: `GOVERNANCE_PILOT_AUTH_REQUIRED=true`, `GOVERNANCE_PILOT_API_KEYS` — see [PRODUCTION_PILOT_KEYS.md](./PRODUCTION_PILOT_KEYS.md) |
| 0.4 | repo | `make verify-final-lock` · `PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh` |
| 0.5 | founder | `./scripts/market-entry-bootstrap.sh` → `ops/private/msb/` |

**Done when:** Shadow Week runs on production with a real pilot key and one RID ([SHADOW_WEEK_DEMO.md](./SHADOW_WEEK_DEMO.md)).

---

## Phase 1 — Relationships (founder, weeks 1–2)

**Primary ICP (locked default):** Licensed **MSB / PSP** in Canada · secondary: any buyer via **Trust Brief** $10k.

| Step | Action |
|------|--------|
| 1.1 | Fill `ops/private/msb/OUTREACH_TRACKER.md` — 10 named contacts |
| 1.2 | Send 5 emails from `ops/private/msb/OUTREACH_EMAILS.md` |
| 1.3 | Book ≥1 Shadow Week demo; use one RID end-to-end |
| 1.4 | Every reply &lt;24h using `ops/private/msb/INTAKE_RESPONSE_TEMPLATES.md` |

**Pitch line:** [GO_FORWARD_NOW.md](strategy/GO_FORWARD_NOW.md) — governance-first; send `/docs/api/` only on technical follow-up.

---

## Phase 2 — Revenue (weeks 3–8)

| Close | Checklist |
|-------|-----------|
| Trust Brief $10k | `ops/private/msb/TRUST_BRIEF_CLOSE_CHECKLIST.md` |
| Shadow Pack | `SHADOW_PACK_SOW_TEMPLATE.md` in `ops/private/msb/` |

**Targets:** ≥10 meetings · ≥2 Trust Brief and/or ≥1 Shadow Pack ([msb-partner-playbook.md](strategy/msb-partner-playbook.md)).

---

## Phase 3 — Staging proof (after first paid deal)

Follow `ops/private/msb/STAGING_PROOF_RUNBOOK.md` (from template) — shadow evaluate + audit-export in partner environment.

---

## Quick links

| Item | URL |
|------|-----|
| Intake | https://www.noetfield.com/trust-brief/intake/ |
| MSB intake | `?vector=partner-msb` |
| Partners | https://www.noetfield.com/partners/ |
| Governance API | https://www.noetfield.com/docs/api/ |
| Status | https://www.noetfield.com/status/ |
| Ops inbox | operations@noetfield.com |
