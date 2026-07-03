# Copilot Instructions for Noetfield-Systems/noetfeld-OS

**Last Updated:** 2026-07-03  
**Org:** Noetfield-Systems  
**Repo:** noetfeld-OS  
**Tier:** T1/T3 (code + advanced reasoning)  

## Critical Rules

### 1. Slug Enforcement
- **REQUIRED:** Use only `Noetfield-Systems` org slug in all workflows and configs.
- **FORBIDDEN:** Any active reference to the legacy personal slug listed in `noetfield-org/FORBIDDEN_MARKERS.txt`.
- **Verification:** `grep -rFf noetfield-org/FORBIDDEN_MARKERS.txt .` must return 0 results outside the marker file.

### 2. Org-Sync Anchors (Mandatory)
This repo is the sync-plane hub. Always respect:
- `noetfield-org/REPO_REGISTRY.md` (foundational — do not delete)
- `noetfield-org/AGENT_REGISTRY.md` (mission stack reference)
- `noetfield-org/ROUTING_MATRIX.md` (L17 tool routing — canonical)
- `noetfield-org/LOOP_STATE.json` (machine-readable mission + tick state)
- `noetfield-org/SYNC_RECEIPTS.md` (verified windows, restart points)

## Parallel agent law (read before any edit)

Living-system governance: `docs/_NOOS_AGENT/[NOOS-AGENT-20260703-003]_PARALLEL_AGENT_GOVERNANCE_v1.md`

Registry: `data/noos-parallel-agent-registry-v1.json`

| Tier | Who | Rule |
|------|-----|------|
| T0 | GitHub Actions, CF cron, worker kernel | Deterministic machine execution only |
| T1 | **You (Copilot coding agent)** | Kaizen patches inside fenced paths |
| T2 | Cursor chat / Copilot CLI | Must integrator-claim before shared paths |
| T3 | Cursor Automations, integrator | Read/narrate; delegate machine proof to GHA |

### L-P5 — integrator claim (T1/T2)

Before editing shared scope files, the human operator or local agent runs:

```bash
python3 scripts/noos_integrator_sync_v1.py claim --agent-id <id> --task-id <id> --scope-file <path>
```

Use `data/noos-integrator-role-v1.json` only as coordination support; do not create a second coordination doctrine.

### L-P7 — Copilot fences (you)

- **Allowed:** `scripts/` (except `scripts/verify_*`), `docs/_NOOS_AGENT/`, `tests/`, `config/` — machine_safe Kaizen only.
- **Forbidden:** `scripts/verify_*`, `noetfield_gate/`, `docs/GOVERNED_AUTORUN_LAWS_v3.md`, trigger/mission/parallel registries, CODEOWNERS-fenced verifier paths.
- Open PRs only; never merge. `gel-ci` + scoped tests must pass.
- Use issue template: `.github/ISSUE_TEMPLATE/copilot-kaizen-machine-safe.yml` with `op_key` + `mission_id`.

### Conflict check (boot)

```bash
python3 scripts/noos_agent_conflict_check_v1.py --json
python3 scripts/verify_living_system_governance_v1.py --json
```

Do not duplicate work owned by GHA loops, self-heal pipeline stages, or Cursor Automations listed in the parallel registry.

## GHA + integrator coordination

- GHA owns schedules, deploy chains, loop fleet, and self-heal pipeline (audit → heal → research → specialist → orchestrator).
- Integrator arbitration: one writer to `.noos-runtime/integrator/`; hourly sync audit is **read-only**.
- Worker kernel (`scripts/noos_worker_kernel_v1.py`) routes one-shot T0 tasks; it does not replace GHA or automations.

### 3. Read Repo State First
- Always read `LOOP_STATE.json` before modifying factory/loop logic.
- Check mission priorities: M1 buyer-proof is always priority.
- M6 (AI Station) is parked — do NOT allocate T0 resources to M6.
- Do NOT treat June status files as current truth.

### 4. No Background Waiting
- Do NOT wait indefinitely on receipts or external workflows.
- If blocked: report condition and commit work.
- Loop tick operates on T0 schedule — you prepare code, T0 orchestrates.

### 5. Forbidden Actions
- No force push.
- No direct main mutation without PR + approval.
- No retroactive mutation of receipt archive.
- No M6 spend without M1 >99% determinism gate pass.

## Workflow Integration

### noetfeld-OS Execution Flows
1. **Factory Tick (T0 Dispatch)**
   - T0 executes `noos-factory-autorun-tick-v1`
   - You: ensure factory code is ready, passes tests
   - Receipt: `factory_tick_receipt_v1.json` → sina-governance-SSOT

2. **Loop Fleet Tick (T0 Orchestration)**
   - T0 executes `noos-loop-fleet-tick-v1`
   - You: maintain loop state machine logic
   - Receipt: `loop_fleet_state_receipt_v1.json`

3. **Autonomous Verification (T3 Reasoning)**
   - `verify_noos_autonomous_24h_v1.py` runs independently
   - You: ensure script syntax correct, metrics collected
   - Receipt: `autonomous_verification_receipt_v1.json`

### Your T1/T3 Responsibilities
- Implement factory/loop logic (T1)
- Maintain receipt schemas (T1)
- Update governance registries (T1)
- Validate cross-repo sync (T3)
- Report via GitHub issues (no waiting)

## Repo State Checklist (Before Any Work)

```bash
# 1. Verify org slug
grep -rFf noetfield-org/FORBIDDEN_MARKERS.txt . && echo "ERROR: Forbidden slug in active config!" || echo "✓ No forbidden slug"

# 2. Read current LOOP_STATE
cat noetfield-org/LOOP_STATE.json | jq '.loop_state, .mission_stack | keys'

# 3. Check mission M6 constraint
cat noetfield-org/LOOP_STATE.json | jq '.mission_stack.M6.constraint'

# 4. Verify branch
git branch

# 5. Validate org-sync anchors exist
ls -la noetfield-org/REPO_REGISTRY.md noetfield-org/ROUTING_MATRIX.md noetfield-org/LOOP_STATE.json
```

## Updating LOOP_STATE.json (Critical Task)

Never edit LOOP_STATE manually outside of proper receipt flow:
1. Factory tick writes `tick_number`, `factory_state`
2. Loop fleet tick updates `loop_state` receipt
3. Verification updates verified windows
4. Only T1 (you) updates mission priorities in special cases (must PR)

**Safe to edit:**
- Mission priorities (with PR)
- Receipt schemas (with PR)

**Never edit:**
- Tick numbers (T0 only)
- Verified SHA (T3 only)

## Signing Off (Before PR)

When changes are ready:
1. Run checklist above
2. Commit: `feat: [description] — Noetfield-Systems org migration`
3. Push to branch
4. Open PR with:
   - **Title:** Feature description
   - **Description:**
     ```
     **Repo:** Noetfield-Systems/noetfeld-OS
     **Tier:** T1/T3 orchestrator
     **Mission:** M2 autonomy + M3 governance
     
     **Changes:**
     - [File changes summary]
     - [Org-sync anchor updates if any]
     
     **LOOP_STATE Updated:** [yes/no — which fields]
     **Registries Updated:** [yes/no — which docs]
     **SHA:** [git rev-parse HEAD]
     **Files Changed:** [git diff --stat HEAD~1 HEAD]
     ```
   - **Reviewers:** Request 2 approvals

## Escalation Path

- **T0 needs to execute:** File issue `needs-t0-dispatch`
- **Receipt validation needed:** File issue `needs-t3-verification`
- **Sync plane update:** File PR, describe changes to registries
- **M6 budget needed:** File issue, explain how M1 constraint still satisfied

## Related Docs

- **Manifest:** `.noetfield/agent_manifest.yml` (your orchestrator role)
- **Tool Routing:** `noetfield-org/ROUTING_MATRIX.md` (L17 access — canonical)
- **Repo Registry:** `noetfield-org/REPO_REGISTRY.md` (foundational)
- **Agent Registry:** `noetfield-org/AGENT_REGISTRY.md` (M1-M6 assignments)
- **Loop State:** `noetfield-org/LOOP_STATE.json` (mission stack + ticks)
- **Verification:** `noetfield-org/SYNC_RECEIPTS.md` (verified windows)

---

**Last Rule:** Before pushing: "Is LOOP_STATE consistent? Is M1 still top priority? Am I using Noetfield-Systems slug? Am I on a branch? Ready for PR?" If yes to all, proceed.
