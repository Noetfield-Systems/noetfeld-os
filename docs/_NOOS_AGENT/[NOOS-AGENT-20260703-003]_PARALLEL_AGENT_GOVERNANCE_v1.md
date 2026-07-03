# [NOOS-AGENT-20260703-003] Parallel Agent Governance v1

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260703-003
doc_type: PARALLEL_AGENT_GOVERNANCE
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — living-system parallel worker law
related_registry: data/noos-parallel-agent-registry-v1.json
-->

**Status:** ACTIVE · 2026-07-03  
**Problem:** GitHub Actions, Copilot agents, Cursor Automations, loop fleet, self-heal pipeline, integrator, and worker kernel all run **in parallel** — without law they duplicate work and fight for the same files.

**Solution:** One registry, seven laws, one conflict check. Machines execute; agents observe or implement in fenced lanes.

---

## 1. Living system map (who does what)

```
┌─────────────────────────────────────────────────────────────────┐
│  T0 MACHINE (writes receipts, no prose authority)               │
│  GHA loop fleet · self-heal pipeline · trigger sweep · CF cron  │
│  Worker kernel T0 (grep/check)                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ handoff JSON / receipts
┌───────────────────────────▼─────────────────────────────────────┐
│  T1 IMPLEMENT (branch-scoped code, tests, PR)                     │
│  Copilot Kaizen agent · Worker kernel T2 patch sandbox            │
└───────────────────────────┬─────────────────────────────────────┘
                            │ claims + PRs
┌───────────────────────────▼─────────────────────────────────────┐
│  T2 LOCAL (Cursor chat, fast edits)                               │
│  Must integrator-claim before shared paths                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │ digests + arbitration
┌───────────────────────────▼─────────────────────────────────────┐
│  T3 REASON (Cursor Automations — read-mostly, narrative)          │
│  Daily autorun digest · proof drift narrative · PR readiness      │
└─────────────────────────────────────────────────────────────────┘
```

**Registry:** `data/noos-parallel-agent-registry-v1.json` lists every worker from your Automations grid + GHA + Copilot + kernel.

---

## 2. Seven parallel laws (L-P1–L-P7)

| Law | Rule |
|-----|------|
| **L-P1 Territory** | One primary writer per territory cell (`public-urls`, `integrator-state`, `trigger-registry`, …). |
| **L-P2 Mutex** | At most one mutating actor per `mutex_group` (see registry). |
| **L-P3 Pipeline** | Self-heal stages 1→5 are sequential: audit → heal → research → specialist → orchestrator. Never re-run upstream from downstream. |
| **L-P4 Delegate** | Cursor **daily/weekly** automations **read** machine proof from `delegates_machine_to` — they do not re-curl or re-sweep. |
| **L-P5 Claim** | Before editing shared paths, run `noos_integrator_sync_v1.py claim`. |
| **L-P6 Kernel** | Worker kernel routes **one-shot** tasks only; it does not replace loops or automations. |
| **L-P7 Copilot** | Copilot agent stays in Kaizen fenced paths; never `scripts/verify_*`, laws, or `noetfield_gate/`. |

---

## 3. Your Cursor Automations — deduped roles

| Automation | Tier | Territory | Machine delegate | Do NOT |
|------------|------|-----------|------------------|--------|
| Issue triage (daily) | T3 | `sourcea-github-issues` | — | Edit NOOS product paths |
| Integrator arbitration (manual) | T3 | `integrator-state` | — | Code without claim |
| Integrator sync audit (hourly) | T3 | `integrator-state` | — | **Write** integrator state (read-only) |
| Bug triage (manual) | T3 | `noetfeld-os-repo` | — | Ship fixes without claim |
| Implementation planner (manual) | T3 | plans in `docs/_NOOS_AGENT/` | — | Overlap active claim scope |
| Workflow effectiveness (weekly) | T3 | workflow portfolio | GHA audit workflow | Re-run audit scripts |
| Evidence pack audit (manual) | T3 | `receipts/proof` | — | Mutate verifiers |
| PR readiness (manual) | T3 | open PRs | CI checks | Merge (founder only) |
| Deployment boundary (manual) | T3 | deploy surfaces | `deploy-noos-cloud-workers` | Deploy |
| Security dependency (weekly) | T3 | dependencies | `gel-ci` pip-audit | Bump without PR |
| **Production surfaces (daily)** | T3 | `public-urls` | **`noos-surface-loop`** | Re-run curl smoke |
| Roadmap reconciliation (weekly) | T3 | backlog/planes | — | Edit planes without claim |
| **Proof drift (daily)** | T3 | cross-lane proof | **trigger sweep + determinism** | Re-run sweep |
| Runtime contract (manual) | T3 | runtime contracts | — | Change verifiers |
| **Autorun status (daily)** | T3 | autorun dashboard | **self-heal heartbeat step** | Re-run `autorun_status` as writer |

---

## 4. Mutex groups (conflict prevention)

| Group | Rule |
|-------|------|
| `integrator-coordination` | Arbitration writes; hourly audit reads only |
| `public-health-nerve` | GHA surface loop curls; Cursor narrates failures |
| `autorun-observability` | Self-heal owns machine heartbeat; Cursor owns human digest |
| `drift-proof` | Sweep/gate own machine drift; Cursor owns cross-lane story |
| `deploy-boundary` | Deploy workflow mutates; boundary automation audits only |
| `pr-merge` | Copilot opens PRs; readiness automation reviews only |
| `self-heal-pipeline` | Five GHA workflows are sequential handoffs |

---

## 5. Boot sequence (any agent, any surface)

```bash
# 1. Conflict check (read-only)
python3 scripts/noos_agent_conflict_check_v1.py --json

# 2. Integrator summary (who owns what now)
python3 scripts/noos_integrator_sync_v1.py summary --json

# 3. Claim before mutate (T1/T2/T3 with writes)
python3 scripts/noos_integrator_sync_v1.py claim --agent-id <id> --task-id <id> --scope-file <path>

# 4. One-shot routed task (optional)
python3 scripts/noos_worker_kernel_v1.py --task-kind check --payload '{"path":"scripts/noos_agent_conflict_check_v1.py"}' --json
```

---

## 6. Enforcement

| Check | Command | Receipt |
|-------|---------|---------|
| Parallel conflict | `python3 scripts/noos_agent_conflict_check_v1.py --write-receipt --json` | `receipts/proof/noos-parallel-agent-conflict-*.json` |
| Integrator overlap | `noos_integrator_sync_v1.py claim` (fails on overlap) | integrator state |
| Trigger drift | `sandbox_health_sweep_v1.py` | heartbeat |
| Worker budget | `noos_worker_kernel_v1.py` | `noos-worker-kernel-*.json` |

---

## 7. What this does NOT do

- Does not stop parallel execution — **parallel is the design**.
- Does not create a second reconciler (L1) — integrator coordinates; GHA executes.
- Does not let Cursor Automations replace GHA loops — **delegate, don't duplicate**.

---

## 8. Related docs

- `noetfield-org/ROUTING_MATRIX.md` — T0–T3 route tiers
- `noetfield-org/AGENT_REGISTRY.md` — agent surfaces
- `[NOOS-AGENT-20260703-001]_INTEGRATOR_AGENT_PROTOCOL_v1.md` — claim protocol
- `[NOOS-AGENT-20260703-002]_CHEAP_WORKER_KERNEL_v1.md` — one-shot router
- `docs/WORKFLOW_SELF_HEALING_ECOSYSTEM_v1.md` — pipeline stages
