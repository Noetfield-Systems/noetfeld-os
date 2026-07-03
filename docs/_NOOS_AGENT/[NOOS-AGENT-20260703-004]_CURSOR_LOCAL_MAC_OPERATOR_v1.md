# [NOOS-AGENT-20260703-004] Cursor Local Mac Operator v1

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260703-004
doc_type: CURSOR_LOCAL_OPERATOR
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — Mac T2 operator card
related_registry: data/noos-parallel-agent-registry-v1.json
-->

**Status:** ACTIVE · 2026-07-03  
**Surface:** Cursor Local (T2) on Mac · **Role:** local operator + fast repo edits

---

## 1. Boot (every session)

```bash
make local-boot
# optional audit receipt:
make local-boot WRITE_RECEIPT=1
```

Read-only hook also runs on `sessionStart` via `.cursor/hooks/noos-local-boot.sh`.

**Worktree note:** If `git checkout main` fails (main bound to another worktree), run:

```bash
bash scripts/noos_mac_worktree_sync_v1.sh
```

---

## 2. T2 may write vs T3 automations read-only

| Territory | T2 Cursor chat | T3 Cursor Automation | Machine delegate (do not duplicate) |
|-----------|----------------|----------------------|-------------------------------------|
| `public-urls` | Edits after claim | Daily production surfaces (narrate) | `gha-noos-surface-loop` |
| `autorun-dashboard` | Edits after claim | Daily autorun status (digest) | `gha-self-heal-autorun-step` |
| `cross-lane-proof` | Edits after claim | Daily proof drift (narrative) | `gha-trigger-sweep-heartbeat` |
| `integrator-state` | Claim + arbitration writes | Hourly sync audit (**read-only**) | — |
| `deploy-surfaces` | Never deploy | Deployment boundary (audit) | `gha-deploy-noos-cloud-workers` |
| `open-pull-requests` | Comments after claim | PR readiness (review only) | `gel-ci` |
| `github-workflows-portfolio` | Docs after claim | Weekly workflow effectiveness | `gha-noos-workflow-audit` |
| `sourcea-github-issues` | **Do not** edit NOOS paths | Issue triage (SourceA) | — |

**Rule:** If a T3 automation ran today, read its output — do not re-run the machine delegate (L-P4).

---

## 3. Claim → edit → closeout

```bash
# One command: boot + claim
make local-lane TASK=NOOS-LANE-001 SCOPE=scripts/foo.py,tests/test_foo.py

# Or separate steps
bash scripts/noos_local_claim_lane_v1.sh NOOS-LANE-001 scripts/foo.py tests/test_foo.py
```

# Long session — refresh claim (stale after 30m without heartbeat)
make local-heartbeat TASK=NOOS-LANE-001

# Work: ≤5 files / ≤200 lines direct; larger → kernel
make local-patch-proposal PATHS=scripts/foo.py,tests/test_foo.py

# Closeout
make local-closeout TASK=NOOS-LANE-001
```

**Copilot CLI on same Mac:** register as `copilot-cli-mac`; claim with `AGENT_ID=copilot-cli-mac IDE=copilot-cli bash scripts/noos_local_claim_lane_v1.sh ...`. Both IDEs read `~/.sina/noos-integrator-state-v1.json`.

**Stale lanes:** `make local-sweep-stale` at session start if yesterday's lane was interrupted.

**Mirror drift:** `make local-boot` runs mirror check; repair with `python3 scripts/noos_integrator_sync_v1.py sync`.

First-run Mac registration is automatic via `make local-boot` (idempotent). Manual fallback:

```bash
python3 scripts/noos_integrator_sync_v1.py init
python3 scripts/noos_integrator_sync_v1.py register-agent \
  --agent-id cursor-local-mac --ide cursor --role local-operator
```

Home mirror for other IDEs: `~/.sina/noos-integrator-state-v1.json`

---

## 4. Mutex groups (quick reference)

| Group | T2 rule |
|-------|---------|
| `integrator-coordination` | One writer; hourly audit reads only |
| `public-health-nerve` | GHA curls; T2/T3 narrate |
| `autorun-observability` | GHA heartbeat owns machine status |
| `drift-proof` | Sweep/gate own drift; T3 narrates |
| `deploy-boundary` | GHA deploys; T2 never deploys from chat |
| `pr-merge` | Copilot opens PRs; T2 never merge without founder |
| `self-heal-pipeline` | Five GHA stages sequential — never skip upstream |

---

## 5. Related docs

- Parallel law: `[NOOS-AGENT-20260703-003]_PARALLEL_AGENT_GOVERNANCE_v1.md`
- Integrator: `[NOOS-AGENT-20260703-001]_INTEGRATOR_AGENT_PROTOCOL_v1.md`
- Worker kernel: `[NOOS-AGENT-20260703-002]_CHEAP_WORKER_KERNEL_v1.md`
- Cursor rule: `.cursor/rules/noetfeld-os-cursor-local-t2.mdc`
