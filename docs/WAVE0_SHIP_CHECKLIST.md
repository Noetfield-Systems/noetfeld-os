# Wave 0 — Ship and prove (founder checklist)

**Status:** Active after PR #10 merge to `main`.  
**Repo verification:** `make verify-final-lock` · `python3 scripts/verify_sitemap_committed.py`

---

## Repo (done on `main`)

- [x] Merge [PR #10](https://github.com/kazemnezhadsina144-dot/Noetfield/pull/10)
- [x] Merge [PR #14](https://github.com/kazemnezhadsina144-dot/Noetfield/pull/14) — governance pilot runbook, rate limits, export script
- [x] Bank-grade repo deliverables — [BANK_GRADE_CHECKLIST.md](./BANK_GRADE_CHECKLIST.md) · [diligence/](./diligence/)
- [x] Procurement visible-copy warnings cleared (engagement intake wording)

---

## Founder — production (required before Wave 1 revenue)

| Step | Action | Doc |
|------|--------|-----|
| 0.2 | DNS + TLS for `www.noetfield.com` and `platform.noetfield.com` | [GO_LIVE.md](./GO_LIVE.md) |
| 0.2 | `make platform-migrate` · deploy platform (`make platform-up` or host process) | [RUNBOOK.md](./RUNBOOK.md) |
| 0.3 | `GOVERNANCE_PILOT_AUTH_REQUIRED=true` + `GOVERNANCE_PILOT_API_KEYS` | [PRODUCTION_PILOT_KEYS.md](./PRODUCTION_PILOT_KEYS.md) |
| 0.3 | LLM keys: `OPENROUTER_API_KEY` and/or `GEMINI_API_KEY` | [CHATBOT_SETUP.md](./CHATBOT_SETUP.md) |
| 0.4 | One **Shadow Week** demo with real RID | [SHADOW_WEEK_DEMO.md](./SHADOW_WEEK_DEMO.md) |
| 0.5 | `./scripts/market-entry-bootstrap.sh` → 5 MSB outreaches | [MARKET_ENTRY_30_DAY.md](./MARKET_ENTRY_30_DAY.md) |

---

## Verify (exit criteria)

```bash
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh
make verify-final-lock
```

**Done when:** smoke exit **0**; one production RID from intake → `POST /api/v1/governance/evaluate` → `GET /api/v1/governance/audit-export`.

---

## Next

Wave 1: [GOVERNANCE_PILOT_RUNBOOK.md](./GOVERNANCE_PILOT_RUNBOOK.md)
