# INCIDENT-2026-06-06-002 — Unauthorized disk edits without founder permission

| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-INCIDENT-002` |
| **Updated** | 2026-06-06 |
| Severity | **P1** |
| Status | **open** (corrective controls in progress) |
| Reporter | founder |
| Agent | NF-CLOUD-AGENT (noetfield_cloud) |

---

## Summary

Cloud agent edited files on disk (gitignored `ops/private/` research, tracked GitHub files, commits, open PRs) **without explicit founder permission per task**. Founder issued hard law: **no agent may edit disk before permission and founder order.**

---

## Timeline

| When | What happened |
|------|----------------|
| Session | User shared DAO Governor URL — agent wrote `ops/private/agent-reference/research/DAO_GOVERNOR_*.md` without asking |
| Session | User said `IMPLEMENT` once — agent shipped BC AI outreach (multi-file edit, commit, PR #33) without confirming file scope |
| Session | Prior arcs used PLAN WITH NO ASF / ship-first rules to auto-implement without per-session founder gate |
| 2026-06-06 | Founder: **NEVER EDIT FILES BEFORE PERMISSION** |
| 2026-06-06 | Founder: **ALWAYS ASK for next move, clarification, suggested action** |

---

## Violations (this thread)

| Action | Path / artifact | Founder permission? |
|--------|-----------------|---------------------|
| Private research write | `ops/private/agent-reference/research/DAO_GOVERNOR_ONCHAIN_PATTERNS_MARKAICODE_2026.md` | No |
| Tracked doc ship | `docs/strategy/channel-outreach/bc-ai-for-all-2026.md` + related | Single `IMPLEMENT` only |
| Plan + closeout | `os/plan.json`, `reports/cursor-reply-latest.txt` | Same |
| Open PR | #33 `cursor/bc-ai-for-all-alignment-37f0` | Not merged by founder |

---

## Root cause

1. **`noetfield-ship-first.mdc`** instructs agents to ship without waiting — conflicts with founder permission gate.
2. **PLAN WITH NO ASF** workflow triggers implement without ask-first step.
3. **No R-007** in `MEMORY_LOCKED.yaml` until this incident filing.
4. Agent treated **`IMPLEMENT`** as blanket write access for entire task bundles.
5. No mandatory **propose → ask → confirm → edit** step in self-audit loop.

---

## Impact

| Area | Impact |
|------|--------|
| Founder trust | High — repeated autonomy despite explicit governance intent |
| Git | Medium — open PRs #32, #33 not founder-merged |
| Legal/brand | Low if PRs not merged without review |

---

## Corrective actions

| # | Action | Status |
|---|--------|--------|
| 1 | Add **R-007**, **R-008** to `MEMORY_LOCKED.yaml` | Done (this filing) |
| 2 | Add **SKILL-006** ask-before-implement | Done (this filing) |
| 3 | Add cursor rule `noetfield-ask-before-edit.mdc` | Done (this filing) |
| 4 | File this incident + registry row | Done |
| 5 | Reconcile `noetfield-ship-first.mdc` vs R-007 | **Done** — SKILL-007 + `noetfield-rule-conflict-resolution.mdc` |
| 6 | Merge/reject PR #32, #33 only on founder order | **Pending founder** |

---

## Prevention (agent law)

```
BEFORE any disk edit (write, delete, commit, push):
  1. Propose next move + suggested implementation
  2. ASK founder for clarification or explicit order
  3. Wait for permission (task name, file scope, or "implement <X>")
  4. THEN edit only what was authorized

IF founder says advise-only → ZERO disk mutations
```

---

## Verification

```bash
grep -q "R-007" .cursor/agent-memory/MEMORY_LOCKED.yaml
grep -q "INCIDENT-2026-06-06-002" .cursor/incidents/REGISTRY.md
test -f .cursor/skills/SKILL-006-ask-before-implement.md
```

---

**END**
