# Wave 0 — Ship and prove (founder checklist)

**Status:** Active after PR #10 merge to `main`.  
**Repo verification:** `make verify-final-lock` · `python3 scripts/verify_sitemap_committed.py`

---

## Repo (done on `main`)

- Merge [PR #10](https://github.com/Noetfield-Systems/Noetfield/pull/10)
- Merge [PR #14](https://github.com/Noetfield-Systems/Noetfield/pull/14) — governance pilot runbook, rate limits, export script
- Merge [PR #15](https://github.com/Noetfield-Systems/Noetfield/pull/15) — bank-grade stack, `docs/ops/` `noetfield_cloud`, dev `:13080`, Trust Ledger P0 docs
- `make ship-verify` on `main` (tle-smoke + verify-local-dev + bank-grade HTML)
- Bank-grade repo deliverables — [BANK_GRADE_CHECKLIST.md](./BANK_GRADE_CHECKLIST.md) · [diligence/](./diligence/)
- Procurement visible-copy warnings cleared (engagement intake wording)
- Agent read order — [docs/ops/AGENT_READ_LINKS_LOCKED_v1.md](./ops/AGENT_READ_LINKS_LOCKED_v1.md) · [os/plan.json](../os/plan.json)

## Founder — SourceA sync (optional, Mac)

```bash
./scripts/sync-sourceA-desktop.sh
# → ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md
```

Hub `http://127.0.0.1:13020/` is **Mac loopback only** — not required for cloud ship.

---

## Founder — production (required before Wave 1 revenue)


| Step | Action                                                                         | Doc                                                    |
| ---- | ------------------------------------------------------------------------------ | ------------------------------------------------------ |
| 0.2  | DNS + TLS for `www.noetfield.com` and `platform.noetfield.com`                 | [GO_LIVE.md](./GO_LIVE.md)                             |
| 0.2  | `make platform-migrate` · deploy platform (`make platform-up` or host process) | [RUNBOOK.md](./RUNBOOK.md)                             |
| 0.3  | `GOVERNANCE_PILOT_AUTH_REQUIRED=true` + `GOVERNANCE_PILOT_API_KEYS`            | [PRODUCTION_PILOT_KEYS.md](./PRODUCTION_PILOT_KEYS.md) |
| 0.3  | LLM keys: `OPENROUTER_API_KEY` and/or `GEMINI_API_KEY`                         | [CHATBOT_SETUP.md](./CHATBOT_SETUP.md)                 |
| 0.4  | One **Shadow Week** demo with real RID                                         | [SHADOW_WEEK_DEMO.md](./SHADOW_WEEK_DEMO.md)           |
| 0.5  | `./scripts/market-entry-bootstrap.sh` → 5 MSB outreaches                       | [MARKET_ENTRY_30_DAY.md](./MARKET_ENTRY_30_DAY.md)     |


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