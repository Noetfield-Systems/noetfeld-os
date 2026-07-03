# [NOOS-AGENT-20260703-001] Integrator Agent Protocol v1

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260703-001
doc_type: INTEGRATOR_PROTOCOL
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — local cross-IDE coordination protocol
related_code: scripts/noos_integrator_sync_v1.py, scripts/integrator_runtime_paths_v1.py, data/noos-integrator-role-v1.json
-->

**Status:** Active · 2026-07-03  
**Purpose:** Give Copilot CLI plus other IDE agents on the same Mac one place to coordinate tasks, scope, and heartbeats so they do not repeat work or edit the same files blindly.

---

## 1. One law

**Writeable coordination truth lives in the repo-local runtime state.**  
Other copies exist only to widen reach:

- **Primary mutable state:** `.noos-runtime/integrator/noos-integrator-state-v1.json`
- **Lock file:** `.noos-runtime/integrator/noos-integrator-state-v1.lock`
- **Tracked protocol:** `data/noos-integrator-role-v1.json`
- **Home mirror for other worktrees / IDEs:** `~/.sina/noos-integrator-state-v1.json`
- **Optional mirror:** Supabase row in `noos_integrator_agent_state`

This means:

1. Agents on the current checkout mutate the repo-local state through the CLI script.
2. Other IDEs can read the **home mirror** even if they are on another worktree.
3. Supabase is an optional observer/mirror, not the primary control plane.

---

## 2. Integrator role

The **integrator agent** is not a coder-first role. It does four things:

1. **Clarifies tasks** — opens tasks with title, scope, acceptance, and lane.
2. **Arbitrates ownership** — an agent claims a task before editing.
3. **Prevents overlap** — claim fails if requested `scope_files` overlap another active non-stale claim.
4. **Keeps sync fresh** — heartbeat/sync writes a home mirror so other IDE agents can see current ownership.

---

## 3. Commands

Use `python3 scripts/noos_integrator_sync_v1.py ...`

### Boot / registration

```bash
python3 scripts/noos_integrator_sync_v1.py init
python3 scripts/noos_integrator_sync_v1.py register-agent \
  --agent-id copilot-cli \
  --ide copilot-cli \
  --role executor
```

### Open a task for agents to pick up

```bash
python3 scripts/noos_integrator_sync_v1.py open-task \
  --agent-id integrator \
  --task-id NOOS-I-001 \
  --title "Implement integrator sync lane" \
  --priority P1 \
  --scope-file scripts/noos_integrator_sync_v1.py \
  --scope-file tests/test_noos_integrator_sync_v1.py \
  --acceptance "Claims, heartbeats, and completion sync across IDEs"
```

### Claim work before editing

```bash
python3 scripts/noos_integrator_sync_v1.py claim \
  --agent-id copilot-cli \
  --ide copilot-cli \
  --task-id NOOS-I-001 \
  --title "Implement integrator sync lane" \
  --scope-file scripts/noos_integrator_sync_v1.py \
  --scope-file tests/test_noos_integrator_sync_v1.py
```

### Keep heartbeat fresh

```bash
python3 scripts/noos_integrator_sync_v1.py heartbeat \
  --agent-id copilot-cli \
  --ide copilot-cli \
  --task-id NOOS-I-001
```

### Complete or release

```bash
python3 scripts/noos_integrator_sync_v1.py complete \
  --agent-id copilot-cli \
  --ide copilot-cli \
  --task-id NOOS-I-001 \
  --note "merged locally"

python3 scripts/noos_integrator_sync_v1.py release \
  --agent-id copilot-cli \
  --ide copilot-cli \
  --task-id NOOS-I-001 \
  --note "handing back for another IDE"
```

### Read current truth

```bash
python3 scripts/noos_integrator_sync_v1.py summary --json
python3 scripts/noos_integrator_sync_v1.py sync
```

---

## 4. Rules for all local agents

1. **Register once, then claim before editing.**
2. **Declare file scope whenever code paths are known.**
3. **Do not bypass a scope conflict.** If claim returns conflict, pick a different task or wait.
4. **Heartbeat long-running work** so stale claims are real, not accidental.
5. **Complete or release** when done. Do not leave silent ownership behind.

---

## 5. Operational intent

This protocol is intentionally small:

- enough to stop duplicate work
- enough to stop file collisions
- enough to show live ownership across IDEs
- small enough to survive local-only use without needing a daemon

If later needed, the next upgrade is **arbitration workflows + richer task planning**, not a heavier control service first.
