# Production go-live (public summary)

Engineering artifacts are on `main`. Use [WAVE0_SHIP_CHECKLIST.md](./WAVE0_SHIP_CHECKLIST.md) for the post-merge founder checklist, [RUNBOOK.md](./RUNBOOK.md), and [PRACTICAL_PLAYBOOK.md](./PRACTICAL_PLAYBOOK.md) for roles and endpoints.

**Founder checklist (detailed, private):** copy [ops/README.md](../ops/README.md) → local `ops/private/` or use GitHub Issues labeled `launch`.

---

## Checklist (summary)

1. **Secrets** — API keys only on the platform host; never in git ([`.env.example`](../.env.example))
2. **DNS + TLS** — `platform.noetfield.com` (API, port 8001), `www.noetfield.com` (static site)
3. **Platform** — `make platform-migrate`, `make platform-up` (or production container)
4. **LLM** — `OPENROUTER_API_KEY` and/or `GEMINI_API_KEY`; `PUBLIC_CHAT_PROVIDER=auto`
5. **www** — deploy static root + `assets/noetfield-ecosystem.json`
6. **Status page** — deploy `status/index.html`; link from www footer; monitors `GET /api/status` ([STATUS.md](./STATUS.md))
7. **Verify**

```bash
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh
```

Exit code **0** means health checks passed.

8. **Pilot API** — [PRODUCTION_PILOT_KEYS.md](./PRODUCTION_PILOT_KEYS.md) · publish [docs/api/](./api/)
9. **Market entry (30 days)** — [MARKET_ENTRY_30_DAY.md](./MARKET_ENTRY_30_DAY.md) · `./scripts/market-entry-bootstrap.sh`
10. **Intake ops** — `INTAKE_OPS_WEBHOOK_URL` · [INTAKE_OPS.md](./INTAKE_OPS.md)

Optional: Telegram ([TELEGRAM_BOT_SETUP.md](./TELEGRAM_BOT_SETUP.md)).
