# ROUTING CARD — Noetfield NF-GAOS (LOCKED)

**Status:** LOCKED operational card · **Pin:** repo root · read every cloud session  
**Authority:** `docs/ops/NF_GAOS_W0_LOCKED_v1.md` · `entry/START_HERE_LOCKED_v1.md`  
**Supersedes for daily boot:** overlapping prose in agent context docs (those remain appendices)

---

## One sentence

> **Gate → live orient → routing card → stale guard → one pending task → founder `implement` → verify → ingest — chat is never SSOT.**

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

Steps inside onboard:

1. `nf_session_gate_run_v1.py` — never skip  
2. `nf-live-orient-v1.sh` — `LIVE-STATUS.md` + events JSON  
3. `nf_routing_card.sh --json` — queue head + scope  
4. `nf_stale_guard_v1.py` — stop if `context_stale=true`  
5. Print first pending `next_tasks` row from live probe  

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
| Am I allowed to edit? | Gate PASS + founder **`implement`** |
| Ecosystem big picture? | Routing Panel `:8780` (Mac) · SourceA Worker routing law |
| Orient / lost? | Re-run `make nf-onboard` · read LIVE-STATUS |
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
