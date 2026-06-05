# Agent read links (LOCKED v1 — in-repo mirror)

| Field | Value |
|-------|--------|
| Plane | `[DELIVERY]` — Noetfield GitHub ship repo (`~/Desktop/Noetfield`) |
| Agent id | `noetfield_cloud` |
| Thread | `THREAD-PORTFOLIO` |
| Canonical (founder Mac) | `~/Desktop/SourceA/founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md` |
| This file | **In-repo mirror** — § Cloud ship only is authoritative here for git agents |

**SSOT layers:** SourceA (Mac) → sync → `ops/private/sourceA/` (gitignored). **Git never newer than SourceA** for ecosystem law. **Ship** from `os/plan.json` + `docs/ops/` locks in this repo.

**Forbidden as primary workspace:** `Noetfield-All-Documents`, `SourceA`, `SinaPromptOS`, wire, MergePack, Cursor OS Pro.

| Wrong lane artifact | Right (`noetfield_cloud`) |
|---------------------|---------------------------|
| `ready_to_paste_noetfield.txt` | `docs/ops/ready_to_paste_noetfield_cloud.txt` |
| `REPO_NOTICE_noetfield_v1.md` | `SEMI_NOTICE_noetfield_cloud_v1.md` (after sync under `ops/private/sourceA/founder/repo-agent-notices/`) |
| `REPO_NOTICE_noetfield` | **`noetfield_local`** (All-Documents) only — not this chat |

---

## § Cloud ship (read this in cloud / Cursor VM)

**No hub required.** Do not assume `http://127.0.0.1:13020/` or `~/Desktop/SourceA` unless founder confirms **Mac session active**.

### Read order

1. This file — § Cloud ship (below)
2. [AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md](./AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md) — memory, incidents, scope gate
3. [.cursor/agent-memory/MEMORY_LOCKED.yaml](../../.cursor/agent-memory/MEMORY_LOCKED.yaml)
4. [NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md](./NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md) — local↔cloud bridge
5. [NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](./NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md)
6. [os/SHIP_NOW.md](../../os/SHIP_NOW.md) → [os/plan.json](../../os/plan.json) · [os/LOCKED_REFERENCE_INDEX.md](../../os/LOCKED_REFERENCE_INDEX.md)
7. **PLAN WITH NO ASF:** [plans/no-asf/QUICK_PICK.md](./plans/no-asf/QUICK_PICK.md) · full bank [plans/README.md](./plans/README.md) (1000 plans)
8. [os/sprint-trust-ledger-v1.2.md](../../os/sprint-trust-ledger-v1.2.md) or [lane_a_sprint_map.md](./lane_a_sprint_map.md)
9. After founder sync: `ops/private/agent-reference/IN_CHARGE_NOW.md` · `ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md`

### In-repo links (`noetfield_cloud`)

| What | Path |
|------|------|
| Paste pack | [ready_to_paste_noetfield_cloud.txt](./ready_to_paste_noetfield_cloud.txt) |
| Team sync (cloud bridge) | [NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md](./NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md) |
| Agent context | [NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](./NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md) |
| Locked index | [os/LOCKED_REFERENCE_INDEX.md](../../os/LOCKED_REFERENCE_INDEX.md) |
| Drift blueprints (cloud) | [NOETFIELD_DRIFT_BLUEPRINTS_CLOUD_READ_ORDER_LOCKED_v1.md](./NOETFIELD_DRIFT_BLUEPRINTS_CLOUD_READ_ORDER_LOCKED_v1.md) |
| Ship now | [os/SHIP_NOW.md](../../os/SHIP_NOW.md) · [docs/SHIP_NOW.md](../SHIP_NOW.md) |
| Ship plan | [os/plan.json](../../os/plan.json) |
| Trust Ledger | [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md) |
| Product locks | [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) · [POSITIONING.md](../../POSITIONING.md) · [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md) |
| Boundaries | [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md) |
| Agent workflow | [.cursor/AGENT_TRACKING.md](../../.cursor/AGENT_TRACKING.md) |
| Self-audit loop | [AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md](./AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md) |
| Agent memory | [.cursor/agent-memory/MEMORY_LOCKED.yaml](../../.cursor/agent-memory/MEMORY_LOCKED.yaml) |
| Incidents | [.cursor/incidents/REGISTRY.md](../../.cursor/incidents/REGISTRY.md) |
| Sprint backlog | [docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md](../spec/SPRINT_BACKLOG_WEEKS_0-8.md) |
| Lane A map | [lane_a_sprint_map.md](./lane_a_sprint_map.md) |
| Ingest YAML | [docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](../spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md) |
| TLE schema | [docs/spec/schemas/tle-v1.schema.yaml](../spec/schemas/tle-v1.schema.yaml) |
| **Governance references (LOCKED)** | [docs/references/README.md](../references/README.md) · [GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md](../references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md) · [GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md](../references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md) |

### Verify (this week)

| Command | When |
|---------|------|
| `./scripts/verify-local-dev.sh` | Dev stack / unified proxy `:13080` |
| `./scripts/tle-smoke.sh` | TLE examples + schema sanity |
| `make ship-verify` | Merge / deploy readiness |

### Semi notice (not in git)

Sync from SourceA only:

`ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md`

Founder: `./scripts/sync-sourceA-desktop.sh` — **SourceA → mirror**, never repo → SourceA.

---

## § Mac founder only (hub + ecosystem)

| What | Open |
|------|------|
| Hub UI | http://127.0.0.1:13020/ — `~/Desktop/SourceA/scripts/serve-sina-command.sh` |
| Essentials | http://127.0.0.1:13020/?tab=essentials |
| Agent hub pack | `noetfield_cloud` |
| Full link index | `~/Desktop/SourceA/founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md` |

Mandatory read chain 1→14: under `~/Desktop/SourceA/` — see canonical index on Desktop. Mirror subset: `ops/private/sourceA/` after sync.

---

## § Other repos (pointer only)

| Entity | Role |
|--------|------|
| SinaaiMonoRepo | `[DESIGN]` + `[EXECUTION]` |
| Sina Prompt OS | Coordinate — **do not edit** from Noetfield |
| Noetfield-All-Documents | `noetfield_local` — **not** this lane |

---

| Version | Date |
|---------|------|
| v1 | 2026-06-03 — founder correction: `docs/ops/` only; no root index |
