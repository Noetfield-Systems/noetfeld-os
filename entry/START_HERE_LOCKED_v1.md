# Noetfield — START HERE (LOCKED v1)

```yaml
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-17"
status: LOCKED
```

**Path:** repo root · **Law:** `docs/ops/NF_GAOS_W0_LOCKED_v1.md` · **Daily pin:** `ROUTING_CARD.md`

---

## Pick your role (read only your row)

| You are | Open folder | Boot | Then read |
|---------|-------------|------|-----------|
| **Founder** | Hub `:13020` (Mac) | Essentials → Noetfield | Hub card only — no Terminal |
| **noetfield_cloud** | This repo (product git) | `make nf-onboard` | `ROUTING_CARD.md` § Cloud |
| **noetfield_local** | `Noetfield-All-Documents` | `make nf-onboard-local` | `ROUTING_CARD.md` § Local |
| **Brain / Worker** | `~/Desktop/SourceA` | SourceA session gate | **Not this repo** for default build |
| **Governance advocate** | Mono / private YAML | Goal Specialist §2 | Output YAML only — no product edits |
| **Commercial agentic** | Hub + private workspace | Hub approve | `AGENTIC_COMMERCIAL_HANDOFF_v1.md` |

**Wrong folder = wrong edits.**

---

## noetfield_cloud — minimum read (after onboard)

1. `reports/agent-auto/LIVE-STATUS.md` — machine snapshot (**trust over prose**)
2. `ROUTING_CARD.md`
3. `.cursor/agent-memory/MEMORY_LOCKED.yaml`
4. `os/SHIP_NOW.md` → `os/plan.json` first pending `next_tasks`
5. `PROJECT_BOUNDARIES_LOCKED.md`

Deep chain: `docs/ops/AGENT_READ_LINKS_LOCKED_v1.md` § Cloud ship — when task needs it.

---

## noetfield_local — minimum read

1. `ROUTING_CARD.md` § Local
2. `Noetfield-All-Documents/HIERARCHY_INDEX.md` (if present)
3. **Never** edit product code in this repo from local chat

---

## Ship trigger (cloud only)

Founder must say **`implement`** after propose (R-007). Optional phrase: **`PLAN WITH NO ASF`**.

Pick: `make pick-wise` · verify: `make plan-with-no-asf-verify`

---

## Live machines (run — do not memorize tables)

```bash
make nf-onboard
make nf-live-orient
python3 scripts/nf_session_gate_run_v1.py --json
bash scripts/nf_routing_card.sh --json
```

---

*START_HERE v1 · NF-GAOS W0 · 2026-06-17*
