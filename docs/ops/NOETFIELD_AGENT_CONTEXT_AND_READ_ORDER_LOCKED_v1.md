# Noetfield agent context and read order (LOCKED v1)

| Field | Value |
|-------|--------|
| Workspace | `~/Desktop/Noetfield` — **Noetfield cloud / GitHub ship** |
| Agent id | `noetfield_cloud` |
| **Not** | `noetfield_local` (All-Documents), SourceA, wire, MergePack, Cursor OS Pro |
| Lane | `noetfield_cloud` — semi-separate |
| Thread | `THREAD-PORTFOLIO` |
| Plane | `[DELIVERY]` |
| Authority | ASF — ship from `os/plan.json`; ingest after; do not idle for next order |

**Link index (in-repo):** [AGENT_READ_LINKS_LOCKED_v1.md](./AGENT_READ_LINKS_LOCKED_v1.md) → § Cloud ship  
**Canonical index (Mac):** `~/Desktop/SourceA/founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md`

---

## Read order — every session

### A. Git (cloud-safe)

1. [AGENT_READ_LINKS_LOCKED_v1.md](./AGENT_READ_LINKS_LOCKED_v1.md) — § Cloud ship
2. This file
3. [os/SHIP_NOW.md](../../os/SHIP_NOW.md) → [os/plan.json](../../os/plan.json)
4. **Long-term plans (1000):** [plans/no-asf/QUICK_PICK.md](./plans/no-asf/QUICK_PICK.md) when user says **PLAN WITH NO ASF**
5. [os/sprint-trust-ledger-v1.2.md](../../os/sprint-trust-ledger-v1.2.md) or [lane_a_sprint_map.md](./lane_a_sprint_map.md)
6. [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) · [POSITIONING.md](../../POSITIONING.md) · [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md)
7. [docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](../spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md)
7b. **Diligence / external frameworks (LOCKED):** [docs/references/README.md](../references/README.md) — sources handbook + drift detection book (TLE, Trust Brief, monitoring)
8. [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md)
9. [.cursor/AGENT_TRACKING.md](../../.cursor/AGENT_TRACKING.md)
10. Active task (Issue / PR / Prompt OS task string)

### B. After founder sync (`ops/private/`)

11. `ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md`
12. `ops/private/sourceA/NOETFIELD_REPO_ALIGNMENT.md`
13. `ops/private/sourceA/AUTO_CONFLICT_ENGINE_V3_LOCKED.md` (optional)
14. `ops/private/todolist/NEXT_MOVES.md` (optional)

### C. Mac founder session only

- Hub http://127.0.0.1:13020/ — only when founder says Mac session is active
- SourceA mandatory chain 1→14 — Desktop canonical

---

## Ship vs ingest

| Action | Blocks shipping? |
|--------|------------------|
| Ingest (YAML + `reported_at`) | **No** — after ship |
| Wait for next Prompt OS order | **Yes** — forbidden |

[docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md](../spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md)

---

## Paste / semi notice

| Artifact | Path |
|----------|------|
| Paste | [ready_to_paste_noetfield_cloud.txt](./ready_to_paste_noetfield_cloud.txt) |
| Semi notice | `ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md` (synced) |

**Not** `REPO_NOTICE_noetfield_v1.md` — that is **noetfield_local** only.

---

## Verify

```bash
./scripts/verify-local-dev.sh
./scripts/tle-smoke.sh
make ship-verify
```

---

| v1 | 2026-06-03 | `docs/ops/` only — founder correction |
