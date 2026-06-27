# NOETFIELD CLOUD INVENTORY — LOCKED v1

**Status:** LOCKED  
**Date:** 2026-06-26  
**Witnessed:** Phase 6 verify gates green

---

## DNS

| Host | Target | Role |
|------|--------|------|
| `www.noetfield.com` | Vercel (`210ae8d5…vercel-dns-017.com`) | Public www |
| `noetfield.com` | Vercel apex | Apex redirect/site |
| `platform.noetfield.com` | Railway `9e1kt78m.up.railway.app` | Platform API + Postgres |
| `api.noetfield.com` | **Not provisioned** | GEL hosted API (backlog) |

---

## Vercel

| Field | Value |
|-------|--------|
| Team | `the-777-foundation` |
| Project | **`noetfield`** |
| Dashboard | https://vercel.com/the-777-foundation/noetfield |
| GitHub | `kazemnezhadsina144-dot/Noetfield` → `main` auto-deploy |
| Runbook | `docs/ops/VERCEL_WWW_DEPLOY_LOCKED_v1.md` |

---

## Railway

| Project | Services | URL |
|---------|----------|-----|
| `noetfield-platform` | `platform-api`, Postgres | https://platform.noetfield.com |
| `mergepack-api` | SourceA lane (out of scope) | — |

---

## Cloudflare

| Worker | Route | State |
|--------|-------|-------|
| `noetfield-www-proxy` | `www.noetfield.com/*` | Deployed; **dormant** (www = direct Vercel) |
| Runbook | `docs/ops/CF_WWW_PROXY_LOCKED_v1.md` | |

---

## GitHub repos

| Repo | Visibility | Lane |
|------|------------|------|
| `Noetfield` | Public | www + platform spine |
| `noetfeld-os` | Private | GEL prototype port 8001 |
| `noetfield-studio-ide` | Private | Agent IDE port 3005 |
| `SinaaiMonoRepo` | Public | **Legacy** — do not use for live delivery |

---

## Supabase

Not in active Noetfield production path (`SUPABASE_URL=missing_or_local` in ops reports). Optional activation: `docs/ops/UPG_SUPABASE_001_ACTIVATION.md`.

---

## Local-only (never commit)

| Path | Purpose |
|------|---------|
| `~/.noetfield/` | Gate receipts, studio launch log |
| `studio-ide/.noetfield/studio-store.json` | Chat history |
| `studio-ide/macos/Noetfield Studio IDE.app` | Built desktop shell |

---

## Phase 6 verify (2026-06-26)

| Gate | Result |
|------|--------|
| Studio unit | 96 passed |
| Studio E2E | 33 passed |
| GEL pytest | 23 passed |
| www E2E | PASS |
| platform /health | 200 |
| api.noetfield.com | Expected fail |
| `noetfield gate` | PASS |

**Locked by:** noetfeld-os-cursor-chat
