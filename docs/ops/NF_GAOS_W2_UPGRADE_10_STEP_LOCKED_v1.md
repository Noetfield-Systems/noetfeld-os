# NF-GAOS W2 — 10-Step Upgrade to Next Level (LOCKED v1)

```yaml
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-17"
status: LOCKED
schema_version: nf-gaos-w2-upgrade-v1
supersedes: "Ad-hoc ship session plan · verify whack-a-mole loop"
parents:
  - docs/ops/NF_GAOS_W0_LOCKED_v1.md
  - docs/ops/NF_GAOS_W1_LOCKED_v1.md
  - docs/ops/NF_VERIFY_TIERS_LOCKED_v1.md
  - docs/WAVE0_SHIP_CHECKLIST.md
  - DEPLOYMENT_ARCHITECTURE.md
source_a_refs:
  - NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md
  - RESEARCH-ACQUISITOR-20260608-NF-002 (Worker Blueprint V3)
  - SINA_24_7_PARALLEL_ENGINE (Vercel=www · Railway=MergePack lane only)
```

## One sentence

> **Green T0→T3 · merge ship PR · live platform.noetfield.com · Wave 0 RID proof · W2 machines locked — then revenue motion on Hub, not chat.**

## Current baseline (2026-06-18)

| Signal | State |
|--------|--------|
| NF-GAOS W0/W1/W2 lock | On disk · `make verify-nf-gaos-w2` (light) |
| Verify tiers | **Step 1 DONE** · `make verify-all-tiers` green on ship branch |
| Governance Runtime 10-step | LOCKED + implemented · `make verify-final-lock` |
| Portfolio N-P1…N-P8 | Done on disk |
| Git ship lane | Branch `ship/nf-gaos-w2-production` · **4 commits unpushed** |
| www production | Canonical deploy intake OK · **live domain mis-aliased** |
| platform production | **Not live** — bridge DNS only until API host |
| Queue head | `ship-sandbox-server-side-057` (spec) · **058 done** |
| Routing Panel Noetfield tab | Mono repo · code on disk · **mono PR pending** |

## Anti-goals (SourceA factory law)

- Railway for `platform.noetfield.com` (Railway = MergePack lane 6, not Noetfield API)
- Mac Docker Desktop as **production** host (local proof only)
- Fourth contract SKU · payment/custody claims · vendor names on www
- Merge SourceA FBE engine into ship repo
- Ship with red T3 or unmerged drift on `main`

---

## Ten steps

| Step | Title | Deliverable | Verify gate |
|------|-------|-------------|-------------|
| **1** | **Verify all tiers green** | T0→T3 pass on ship branch; reconcile static-www ↔ gtm-ops needles; commit 8-file drift | `make verify-all-tiers` exit 0 |
| **2** | **Merge ship PR** | PR from `ship/nf-gaos-w2-production` → `main`; CI green | `git log main -1` matches merge |
| **3** | **Platform production host** | Postgres migrate · Docker platform stack on **cloud container host** (not Mac prod); secrets on host only | `make platform-migrate` · stack up |
| **4** | **Platform DNS + smoke** | `platform.noetfield.com` → real API (replace Vercel bridge); prod smoke | `PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh` exit 0 |
| **5** | **Wave 0 RID proof** | One production path: intake → `POST /api/v1/governance/evaluate` → `GET audit-export` | Document RID in closeout · `docs/WAVE0_SHIP_CHECKLIST.md` |
| **6** | **Queue 057 + 058** | Server-side sandbox persistence · agentic workflow manifest wire | Queue head advances · `make ship-verify` |
| **7** | **Routing Panel ship** | Mono PR: Noetfield tab + `/api/panel/noetfield` · panel export receipt | `:8780` tab · `make nf-panel-export` |
| **8** | **NF-GAOS W2 lock** | `NF_GAOS_W2_LOCKED_v1.md` · `verify-nf-gaos-w2.sh` · stale guard + BAVT in tier T0 | `make verify-nf-gaos-w2` |
| **9** | **Staging + regression** | `staging-platform.noetfield.com` optional; `NF_STAGING_URL` smoke in T3 | `./scripts/staging-smoke.sh` when URL set |
| **10** | **Closeout + commercial handoff** | `ship-closeout.sh` · `reports/cursor-reply-latest.txt` · LIVE-STATUS refresh · Hub agentic queue only for outreach | `make nf-onboard` · founder Hub tap |

---

## Step detail

### 1 — Verify all tiers green

```bash
make verify-tier0   # nf-gaos-w1
make verify-tier1   # ship-verify
make verify-tier2   # verify-gtm  (auto-boot :13080)
make verify-tier3   # plan-with-no-asf-verify
make verify-final-lock   # governance runtime regression
```

Commit any post-push drift (pipeline doc rename, gtm-ops needles) before merge.

### 2 — Merge ship PR

- URL: https://github.com/kazemnezhadsina144-dot/Noetfield/pull/new/ship/nf-gaos-w2-production
- Two commits: (1) NF-GAOS W0/W1 + governance runtime (2) www + GTM + portfolio

### 3 — Platform production host

Per `DEPLOYMENT_ARCHITECTURE.md` + `docs/RUNBOOK.md`:

```bash
docker compose -f infrastructure/docker/docker-compose.yml \
  -f infrastructure/docker/docker-compose.platform.yml up -d --build
make platform-migrate
```

Production: same stack on cloud container host · `RUNTIME_EVENT_STORE=postgres` · `DATABASE_URL` + `REDIS_URL` from vault.

### 4 — Platform DNS + smoke

```bash
# After API host live — not Vercel bridge
PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh
```

Interim bridge (`scripts/setup-platform-dns.sh` → Vercel www) is **not** Wave 0 exit.

### 5 — Wave 0 RID proof

Blueprint V3 goal **g4_platform**: one production RID on `platform.noetfield.com`.  
Script: `docs/SHADOW_WEEK_DEMO.md` · export: `./scripts/trust_brief_audit_export.sh --request-id RID-...`

### 6 — Queue 057 + 058

| ID | Scope |
|----|--------|
| `ship-sandbox-server-side-057` | Optional server-side sandbox · `governance-console/backend/` |
| `ship-agentic-workflow-manifest-058` | Agentic manifest wire · `os/plan.json` |

Heal `os/SHIP_NOW.md` + stale guard after each ship.

### 7 — Routing Panel ship

Mono repo `SinaaiMonoRepo/routing-panel/`:

- `build_noetfield_panel()` · `/api/panel/noetfield` · Noetfield tab UI
- Founder visibility without editing SourceA from cloud chat

### 8 — NF-GAOS W2 lock

W2 machines (target):

| Machine | Command |
|---------|---------|
| Tier bundle | `make verify-all-tiers` |
| Production platform receipt | `deploy_platform_smoke.sh` on live URL |
| Panel export | `make nf-panel-export` |
| Full W2 verify | `make verify-nf-gaos-w2` |

W3 (orientation · hospital · maze) stays **deferred** — not session boot.

### 9 — Staging + regression

```bash
export NF_STAGING_URL=https://staging-platform.noetfield.com
make verify-tier3   # runs staging-smoke when set
```

### 10 — Closeout + commercial handoff

```bash
./scripts/ship-closeout.sh
make nf-onboard
```

Outbound (`ship-design-partner-outreach-026`, `ship-sandbox-nurture-060`): **Hub agentic layer only** — product ships disk + www + platform.

---

## Success criteria (W2 complete)

1. `main` contains NF-GAOS W0/W1/W2 locks + verify scripts
2. `www.noetfield.com` + `platform.noetfield.com` both healthy (intake + evaluate API)
3. One documented production RID (Wave 0 exit)
4. Routing Panel Noetfield row live for founder
5. Queue past 057/058 · stale guard PASS
6. `reports/agent-auto/LIVE-STATUS.md` reflects production truth

---

## Founder Actions (Hub one-tap — document only)

| Action | Command |
|--------|---------|
| NF Onboard | `make nf-onboard` |
| Verify all tiers | `make verify-all-tiers` |
| Platform smoke | `PLATFORM_HEALTH_BASE=https://platform.noetfield.com ./scripts/deploy_platform_smoke.sh` |
| Merge PR | GitHub PR merge (after CI green) |

*NF-GAOS W2 upgrade · locked 2026-06-17*
