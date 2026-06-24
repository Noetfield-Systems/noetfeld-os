# ROUTING CARD — Noetfield NF-GAOS (LOCKED)

**Status:** LOCKED operational card · **Pin:** repo root · read every cloud session  
**Authority:** `docs/ops/NF_GAOS_W0_LOCKED_v1.md` · `entry/START_HERE_LOCKED_v1.md`  
**Supersedes for daily boot:** overlapping prose in agent context docs (those remain appendices)

---

## One sentence

> **Mono nerve → gate → live orient → routing card → stale guard → one pending task → founder `implement` → verify → ingest — chat is never SSOT.**

---

## Which plane am I in?

| Plane | Path | Build code? | Agent id |
|-------|------|-------------|----------|
| **Noetfield cloud** | This repo | **Yes** — product/www/API | `noetfield_cloud` |
| **Noetfield local** | `~/Desktop/Noetfield-All-Documents` | Docs/hierarchy only | `noetfield_local` |
| **SourceA Worker** | `~/Desktop/SourceA` | sa-* · hub · forge | **Not** default Noetfield ship |
| **Mono Maintainer** | `SinaaiMonoRepo` | mx-* runtime only | **Not** nf-* product |
| **Commercial agentic** | Hub + private | Outreach only | Not disk ship for 026 |

---

## Cloud session boot

```bash
make nf-onboard
```

Steps inside onboard (12 — **skip none**):

1. `nf_mono_nerve_v1.py` — defer + ecosystem + TrustField fleet  
2. `nf_founder_input_sync_v1.py` — cascade → INBOX + SHIP_NOW  
3. `nf_session_gate_run_v1.py`  
4. `nf-live-orient-v1.sh`  
5. `nf_routing_card.sh`  
6. `nf_stale_guard_v1.py`  
7. `nf_voyage_integrity_v1.py`  
8. `nf_live_surfaces_v1.py` — `email_send_defer_line` required  
9. `nf_receipt_cascade_v1.py`  
10. `nf_gatekeeper_v1.py` — advisory until implement  
11. UI build checklist  
12. `nf_orient_read_chain` + `nf_anti_staleness_max`  
13. `verify-nf-agent-report-language` — **FAIL = do not reply to founder**

**Agent sync (internal — not www):** `governance/OPS_LIVE_STATUS_LOCKED.json` on **git main** — both agents read same file after pull.

**Language law:** `data/nf-agent-report-language-standard-v1.json` · gate: `make verify-nf-agent-report-language`

**Law:** `docs/ops/NF_ANTI_STALENESS_MAXIMUM_FIX_SET_LOCKED_v1.md`

**Before first file edit:**

```bash
NF_FOUNDER_IMPLEMENT=1 bash scripts/nf_assert_implement_allowed.sh
```

Quote every substantive reply: **`product_now_line`** + **`email_send_defer_line`** from `~/.sina/nf-live-surfaces-v1.json`.

Then: **ASK** founder unless **`implement`** already given.

---

## Question → read / run first

| Question | Action |
|----------|--------|
| Which workspace? | `entry/START_HERE_LOCKED_v1.md` — your row |
| Live truth? | `reports/agent-auto/LIVE-STATUS.md` or `make nf-live-orient` |
| What ships now? | Live probe → `os/plan.json` pending `next_tasks[0]` |
| Full routing graph? | `bash scripts/nf-unified-routing.sh --json` |
| Pick next GTM task? | `make pick-wise` or `make pick-no-asf-plan` |
| Am I allowed to edit? | Gate PASS + `make nf-gatekeeper` + founder **`implement`** |
| Live one-liner? | `~/.sina/nf-live-surfaces-v1.json` → `product_now_line` |
| **Prove factory spine?** | `make nf-prove-factory-spine` → `~/.sina/nf-factory-spine-proof-v1.json` |
| **UI / www / form change?** | Read `docs/www/NF_UI_BUILD_CHECKLIST_LOCKED_v1.md` → `make nf-ui-checklist` PASS first |
| **Factory Round 15?** | `docs/ops/NF_FACTORY_ROUND_15_PREP_LOCKED_v1.md` · `pick-portfolio-plan.py --path-ref XF-laws` |
| **Both agents same truth?** | `governance/OPS_LIVE_STATUS_LOCKED.json` on git main · `make nf-onboard` |
| **Reply blocked / parrot?** | `make verify-nf-agent-report-language` · rewrite plain English |
| Execution gate? | `make nf-gatekeeper` (FAIL = EXECUTION DENIED) |
| Lost / cascade FAIL? | `make nf-orient` (manual only — not boot) |
| Commercial outreach? | `AGENTIC_COMMERCIAL_HANDOFF_v1.md` — not cursor disk for 026 |

---

## Authority stack (Noetfield)

```text
ASF (human override)
  ↓
Mac Law (founder Mac — mirror only in git)
  ↓
SourceA notices (ops/private/sourceA/ after sync)
  ↓
Noetfield SSOT (this repo — docs/ops/*_LOCKED, os/plan.json)
  ↓
Execution (services/, www, verify scripts — NEVER authority)
```

---

## Lane law

| Prefix | Owner | Mix in one session? |
|--------|-------|---------------------|
| `nf-*` / `ship-*` | This repo | **Yes** — one task |
| `mx-*` | SinaaiMonoRepo | **No** |
| `sa-*` | SourceA Worker | **No** |

---

## Verify closeout

```bash
./scripts/plan-with-no-asf-verify.sh
make verify-gtm
make nf-ui-checklist
./scripts/verify-agent-scope.sh
```

Receipt: `reports/cursor-reply-latest.txt` + ingest YAML footer.

---

## Mac founder — Hub + Routing Panel

| Surface | URL / action |
|---------|----------------|
| Routing Panel | http://127.0.0.1:8780/ → **Noetfield** tab |
| Panel API | http://127.0.0.1:8780/api/panel/noetfield |
| Hub Essentials | http://127.0.0.1:13020/ → Noetfield lanes (Mac only) |
| One-tap boot | `make nf-onboard` (Worker `sa-*` may wire hub Action) |

---

## § Local (noetfield_local)

- Read hierarchy / registry in All-Documents  
- **Forbidden:** edits under product git tree  
- Sync bridge: `NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md`

---

*ROUTING_CARD v1 · NF-GAOS W0 · 2026-06-17*
