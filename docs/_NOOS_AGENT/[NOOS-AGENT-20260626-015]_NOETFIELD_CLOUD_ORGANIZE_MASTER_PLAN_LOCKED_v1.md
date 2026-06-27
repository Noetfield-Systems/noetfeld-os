<!-- NOOS-AGENT-DOC -->
# NOETFIELD CLOUD ORGANIZE MASTER PLAN — LOCKED v1

**Status:** LOCKED  
**Date:** 2026-06-26  
**trace_id:** `NOOS-AGENT-20260626-015`  
**agent_lane:** NOETFELD-OS  
**Execution:** Phase 2 + Phase 4 started 2026-06-26  

---

## Purpose

Single ordered checklist for every Noetfield asset (local, GitHub, Vercel, Railway, Cloudflare, DNS, docs, lanes).  
**Default stance:** organize + push + fix stale refs — **do not delete live cloud or repos.**

---

## Phase 0 — Read first

| Step | Action | Path |
|------|--------|------|
| 0.1 | Unified master | `NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md` |
| 0.2 | Product SSOT | `NOETFIELD_OS_SSOT_v1_LOCKED.md` |
| 0.3 | Live product state | `PRODUCT_TRUTH.md` |
| 0.4 | Orientation | `[NOOS-AGENT-20260608-005]_ORIENTATION_START_HERE.md` |
| 0.5 | Desktop map | `~/Desktop/Noetfield/NOETFIELD_OS_WORKSPACE.md` |
| 0.6 | Ops witness | `Noetfield/governance/OPS_LIVE_STATUS_LOCKED.json` |
| 0.7 | Lane law | Noetfield ≠ SourceA |

---

## Phase 1 — Inventory

### Canonical locations

| Step | Path | Role | Remote |
|------|------|------|--------|
| 1.1 | `~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/` | Brand + www + platform | GitHub `Noetfield` |
| 1.2 | `~/Projects/noetfeld-os/` | GEL runtime prototype | Private GitHub `noetfeld-os` |
| 1.3 | `~/Desktop/Noetfield/noetfield-studio-ide/` | Agent IDE port 3005 | Private GitHub `noetfield-studio-ide` |
| 1.4 | `~/Desktop/Noetfield/SinaaiMonoRepo/` | Legacy mono | GitHub — archive lane |

### Local-only (never commit)

| Step | Path |
|------|------|
| 1.12–1.14 | `~/.noetfield/` gate reports + studio launch log |
| 1.15–1.18 | Studio `.noetfield/studio-store.json`, receipts, `.app`, `.next/` |

---

## Phase 2 — Git health (EXECUTE)

### 2A — Noetfield (P0)

| Step | Action |
|------|--------|
| 2.1–2.3 | Review 16-commit drift + dirty tree |
| 2.4 | Run www E2E scripts |
| 2.5 | Commit ops + deploy scripts |
| 2.6 | Push `main` |
| 2.7 | Confirm GitHub SHA = local HEAD |
| 2.8 | Optional tag `nf-www-613-frozen` |

### 2B — noetfield-studio-ide (P0)

| Step | Action |
|------|--------|
| 2.9 | Confirm clean (`5b29859`) |
| 2.10–2.11 | Create private repo + push |
| 2.12 | Port SSOT 3005 in README |
| 2.13 | Fix workspace map handoff path |

### 2C — noetfeld-os (P0)

| Step | Action |
|------|--------|
| 2.14 | Confirm clean |
| 2.15–2.16 | Create private repo + push |
| 2.17 | Keep `.agent-private/` out of public |
| 2.18 | Run tests |

### 2D — SinaaiMonoRepo (P2 — later)

| Step | Action |
|------|--------|
| 2.19–2.22 | Mark legacy; push or archive branch |

---

## Phase 3 — Cloud surfaces

| Step | Surface | Status | Action |
|------|---------|--------|--------|
| 3.1–3.3 | `www.noetfield.com` | Live Vercel | Keep |
| 3.4 | `project-gc7lm.vercel.app` | DEAD | Purge (Phase 4) |
| 3.5–3.7 | Vercel deploy from GitHub main | After 2.6 | Redeploy |
| 3.8–3.14 | Railway `noetfield-platform` | Live | Keep |
| 3.15–3.19 | Railway `mergepack-api` | SourceA lane | Out of scope |
| 3.20–3.21 | DNS www + platform | Correct | Keep |
| 3.22 | `api.noetfield.com` | Not deployed | Backlog |
| 3.25–3.29 | CF `noetfield-www-proxy` | Stale ORIGIN | Fix in Phase 4 |
| 3.31–3.35 | Supabase | Not wired | Skip |
| 3.36–3.39 | PyPI, npm SDK, status page | Gaps | Phase 8 |

---

## Phase 4 — Stale URL purge (EXECUTE)

Replace `project-gc7lm.vercel.app` → `www.noetfield.com` in:

**Noetfield repo:** `infra/cf-www-proxy/*`, `assets/noetfield-intake-core.js`, `trust-brief/intake/index.html`, `scripts/www-vercel-canonical.sh`, `scripts/upgrade-www-production.sh`, `scripts/fix-all-production.sh`, `scripts/diagnose-www-fragmentation.sh`, `scripts/auto-heal-www.sh`, `docs/ops/NF_GAOS_W2_LOCKED_v1.md`

**noetfeld-os repo:** `scripts/check_noetfield_com_e2e.py`, docs 010/011/013/014

Then: commit, push, grep zero matches, re-run E2E.

---

## Phase 5 — Product lanes

| Product | Local | Cloud | Port |
|---------|-------|-------|------|
| www | Noetfield/ | Vercel | 443 |
| platform API | Noetfield/services | Railway platform.noetfield.com | 443 |
| GEL | noetfeld-os | api.noetfield.com (future) | 8001 |
| Studio IDE | noetfield-studio-ide | local/desktop | 3005 |
| Gate CLI | noetfield-gate | ~/.noetfield/receipts | — |

---

## Phase 6 — Verify gates

6.1 Studio unit (96) · 6.2 Studio E2E (33) · 6.3 GEL tests · 6.4 www health · 6.5 platform health · 6.6 api (fail OK) · 6.7 `noetfield gate` · 6.8 GitHub sync · 6.9 Vercel SHA · 6.10 desktop app optional

---

## Phase 7 — Doc organize (later)

7.1 workspace map · 7.2 `CLOUD_INVENTORY_LOCKED_v1.md` · 7.3 studio README · 7.4 sync SSOT · 7.5–7.7 legacy labels + pilot URLs

---

## Phase 8 — Backlog

api.noetfield.com · PyPI noetfield-gate · npm @noetfield/gate · status.noetfield.com · noetfield.com/gel · Studio visual artifacts · Gemini key parity · CI gates

---

## Phase 9 — DO NOT

9.1 Delete Railway noetfield-platform · 9.2 git clean -fd · 9.3 delete studio/os folders · 9.4 delete ~/.noetfield · 9.5 merge SourceA Railway · 9.6 create Supabase to organize · 9.7 force-push blind · 9.8 public noetfeld-os early · 9.9 use project-gc7lm · 9.10 commit studio-store.json

---

## Phase 10 — Execution order

```
0 → 2A push Noetfield → 3.5 Vercel → 2B/2C private push → 4 URL purge → 6 verify → 7 docs → 8 backlog
```

**Locked by:** noetfeld-os-cursor-chat · 2026-06-26
