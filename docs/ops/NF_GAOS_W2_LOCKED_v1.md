# NF-GAOS W2 — Production Ship Lane (LOCKED v1)

```yaml
agent_tag: nf-local-repo-agent
authored_at: "2026-06-18"
status: LOCKED
schema_version: nf-gaos-w2-v1
parents:
  - docs/ops/NF_GAOS_W1_LOCKED_v1.md
  - docs/ops/NF_GAOS_W2_UPGRADE_10_STEP_LOCKED_v1.md
  - docs/ops/NF_VERIFY_TIERS_LOCKED_v1.md
```

## One sentence

> **Green T0→T3 on ship branch · merge · live platform · Wave 0 RID · panel visibility — machines lock production truth.**

## W2 machines

| Machine | Command |
|---------|---------|
| Verify tiers (Step 1) | `make verify-all-tiers` |
| Governance runtime lock | `make verify-final-lock` |
| Factory spine (W3) | `make verify-nf-gaos-w3` |
| Full W2 gate (light) | `make verify-nf-gaos-w2` |
| Full W2 gate (heavy) | `NF_W2_VERIFY_FULL=1 make verify-nf-gaos-w2` |
| Platform smoke | `PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh` |
| Panel export | `make nf-panel-export` |
| www auto-heal | `bash scripts/auto-heal-www.sh` |

## Ten-step status (2026-06-18)

| Step | Title | Status | Blocker |
|------|-------|--------|---------|
| 1 | Verify all tiers green | **DONE** | — |
| 2 | Merge ship PR | **PENDING** | Push + merge `ship/nf-gaos-w2-production` |
| 3 | Platform production host | **PENDING** | Cloud container host + vault secrets |
| 4 | Platform DNS + smoke | **PENDING** | Step 3 · not Vercel bridge |
| 5 | Wave 0 RID proof | **PENDING** | Step 4 live API |
| 6 | Queue 057 + 058 | **PARTIAL** | 058 wired · 057 spec only |
| 7 | Routing Panel ship | **PENDING** | Mono PR · `:8780` |
| 8 | NF-GAOS W2 lock | **DONE** | This doc + `verify-nf-gaos-w2.sh` |
| 9 | Staging regression | **PENDING** | `NF_STAGING_URL` unset |
| 10 | Closeout + Hub handoff | **PENDING** | Steps 2–5 |

## Production truth (live checks)

| Surface | Healthy when | Current |
|---------|--------------|---------|
| Canonical Vercel deploy | `project-gc7lm.vercel.app` intake `www_email_configured: true` | **OK** (resend) |
| Live www domain | `www.noetfield.com` aliases canonical project | **FAIL** — domain not under `noetfield-systems` scope |
| Platform API | `platform.noetfield.com` evaluate + audit-export | **NOT LIVE** |

## Founder Actions (Hub one-tap)

| Action | Command |
|--------|---------|
| Attach www domain | Vercel → `noetfield-systems/www` → add `www.noetfield.com` |
| Set Resend key | `RESEND_API_KEY=re_…` in `~/.sina/secrets.env` → `bash scripts/auto-heal-www.sh` |
| Merge ship PR | GitHub merge after CI green |
| Platform smoke | `PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh` |

*NF-GAOS W2 · locked 2026-06-18*
