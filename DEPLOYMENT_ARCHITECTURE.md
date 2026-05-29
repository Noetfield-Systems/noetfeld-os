# Noetfield Deployment Architecture — FINAL LOCK

## Domain split (mandatory)

| Host | Purpose | Content |
|------|---------|---------|
| **`https://www.noetfield.com`** | Institutional surface | GCIP v4 narrative, Trust Brief, Copilot Readiness, Gate **engagement intake**, legal pages. **No** agent-loop demos, **no** treasury UI, **no** payment product. |
| **`https://platform.noetfield.com`** (preferred) or **`https://console.noetfield.com`** | Technical / pilot surface | FastAPI Golden Edge v3 (`/v3/evaluate`, `/v3/agent-loop`), governance console, event replay, bank pilot dashboards. |

### Hard rules

1. Never embed demo runtime widgets on the institutional homepage.
2. Never serve cross-border payment / FX calculator / payment intent UI on `noetfield.com`.
3. CORS and cookies: demo subdomain may use separate cookie namespace from marketing site.
4. Stripe checkout links on institutional pages include commercial-licensing disclaimer only.

## Static site (institutional)

- **Source:** repository root HTML (`index.html`, `gate/`, `trust-brief/`, `copilot/`, …)
- **Deploy:** static host (Cloudflare Pages, S3+CDN, or nginx) → `noetfield.com`
- **Branch:** `main`

## Backend runtime

- **Service:** `noetfield_governance.api:app`
- **Port:** `8001` via `make api-v3` (Golden Edge v3)
- **Persistence:** `RUNTIME_EVENT_STORE=postgres` (required production)
- **Deploy target:** `platform.noetfield.com` (container or VM behind TLS)

### Governance Console v1 (only product UI)

Thin client served by the API — **no mock data**, no Next.js product:

| Route | Purpose |
|-------|---------|
| `GET /console` or `GET /` | Minimal evaluate + decision + ledger UI |
| `POST /v3/evaluate` | Golden Edge policy decision |
| `GET /v3/ledger` | Immutable audit log entries |

Local: http://127.0.0.1:8001/console

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
make apply-migrations
RUNTIME_EVENT_STORE=postgres make api-v3
```

## PostgreSQL (system of record)

- Migrations: `infrastructure/supabase/migrations/`
- Event store + audit ledger projections
- Replay: `GET /events/replay`
- Integrity: Golden Edge v3 REJECT before forbidden financial actions; immutable audit subscriber on event bus

## Environment

See `.env.example` — `RUNTIME_EVENT_STORE=postgres` is the production default.

## Verification

```bash
python3 scripts/final_semantic_lock_public.py   # after copy changes
python3 scripts/audit_final_system_lock.py    # must exit 0
pytest tests
```

Report: `docs/PRODUCTION_READINESS_REPORT.md`
