# UPG-SUPABASE-001 — Noetfield Systems Supabase activation

**Project:** Noetfield Systems · ref `tkgpapowwplupyekpivy` · org `kazemnezhadsina144-dot's Org`  
**Dashboard:** https://supabase.com/dashboard/project/tkgpapowwplupyekpivy  
**Trigger:** Supabase inactivity email (2026-06-26) — auto-pause if no activity continues.

## Current state

| Layer | Where it runs today |
|-------|---------------------|
| **www** | Vercel (`www.noetfield.com`) |
| **platform API** | Railway `noetfield-platform` / `platform-api` |
| **Postgres (live)** | Railway managed Postgres (`DATABASE_URL=${{Postgres.DATABASE_URL}}`) |
| **Supabase cloud** | **Provisioned but idle** — migrations live in repo only |

Migrations are authored under `infrastructure/supabase/migrations/` (0001–0008) and applied on **Railway** at deploy. The **Supabase project** has not received queries → inactivity warning.

## Priority plan (do in order)

### P0 — Unblock pause (today, ~15 min)

1. Open [Supabase dashboard → Noetfield Systems](https://supabase.com/dashboard/project/tkgpapowwplupyekpivy).
2. **Settings → Database** — copy **Connection string** (URI, pooler port 6543 recommended for Railway).
3. **Settings → API** — copy `URL` + **service_role** key (server-side only).
4. Add to `~/.sina/secrets.env` **or** ensure `~/.sourcea-secrets/noetfield.env` has API keys + database URL:

```bash
NOETFIELD_SUPABASE_REF=tkgpapowwplupyekpivy
NOETFIELD_SUPABASE_URL=https://tkgpapowwplupyekpivy.supabase.co
NOETFIELD_SUPABASE_ANON_KEY=<anon-key>
NOETFIELD_SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
NOETFIELD_SUPABASE_DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

The script auto-loads `~/.sourcea-secrets/noetfield.env` when present.

5. Run:

```bash
./scripts/supabase_activate_noetfield.sh --migrations --heartbeat
```

### P1 — Schema parity (same day)

Apply all migrations to Supabase so cloud DB matches Railway:

| Migration | Purpose |
|-----------|---------|
| 0001 | v3.1 foundation schema |
| 0002 | Phase 3 runtime activation |
| 0003 | Backend core |
| 0004 | Source-of-truth registry |
| 0005 | Public intake + ecosystem |
| 0006–0007 | Trust ledger TLE |
| 0008 | Observability tables |

Verify: script prints `applied` / `skipped` for each file; no errors.

### P2 — Wire platform to Supabase Postgres (recommended, ~30 min)

Point live platform at Supabase for **continuous activity** (best anti-pause):

```bash
./scripts/supabase_activate_noetfield.sh --wire-railway
```

This sets Railway `platform-api` `DATABASE_URL` to `NOETFIELD_SUPABASE_DATABASE_URL` and redeploys. Intake + event store then live on Supabase.

**Rollback:** restore Railway Postgres reference:  
`railway variable set --service platform-api 'DATABASE_URL=${{Postgres.DATABASE_URL}}'`

### P3 — Ongoing heartbeat (automation)

- **Option A (free):** GitHub Action `.github/workflows/supabase-heartbeat.yml` — weekly `SELECT 1` + REST ping (add repo secrets).
- **Option B:** Supabase **Pro** ($25/mo) — no auto-pause; use when pilot revenue justifies.

### P4 — Planned upgrades (from master plan)

| Track | Steps | When |
|-------|-------|------|
| TLE receipt store | MCP plan T08 · migrations 0006–0007 production use | Phase 3 evidence |
| Edge functions | Public webhooks / intake fan-out | After P2 stable |
| pgvector / RAG | Ambient intelligence SOT (future) | Post-pilot |
| Auth + RLS policies | Tenant isolation | First design partner |

Maps to upgrade plan **UPG-0101+** (Phase 3 evidence) and **UPG-0151+** (tenant production).

## What NOT to do

- Do **not** pause/delete the project — 90-day unpause window only.
- Do **not** expose `service_role` key to www or browsers.
- Do **not** merge Supabase into SinaaiRuntime `:8000` (port law).

## Verification

```bash
# After P0–P1
./scripts/supabase_activate_noetfield.sh --heartbeat

# Platform still healthy
PLATFORM_HEALTH_BASE=https://platform.noetfield.com python3 scripts/verify_platform_health.py
python3 scripts/check_noetfield_com_e2e.py
```

## Related docs

- `DEPLOYMENT_ARCHITECTURE.md` — Postgres as system of record
- `docs/INTAKE_BACKUP_RETENTION.md` — `public_intakes` table (0005)
- `UPG-WWW-001` — platform spine (Railway; separate from Supabase ref)
