# INCIDENT-2026-06-06-005 — Founder law: always ask before action

| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-INCIDENT-005` |
| **Updated** | 2026-06-06 |
| Severity | **P0** (operating law) |
| Status | **closed** (R-007/R-008/R-010 + SKILL-006/007 on main) |
| Closed | 2026-06-06 |
| Closed by | founder order |
| Reporter | founder |
| Agent | ALL agents |

---

## Summary

Founder issued portfolio-wide law for **every agent**:

> You must **always ask** for next move, clarification, and suggested implementation or other action before acting.

This supersedes implicit auto-ship behavior unless founder explicitly orders a bounded task (e.g. "PLAN WITH NO ASF implement iter N" or "implement X").

---

## Required agent behavior (every session)

1. **Read** memory, incidents, mandatory handoffs (if on disk).
2. **Summarize** understanding and open items.
3. **Propose** suggested next move(s) with options.
4. **ASK** founder to choose or clarify.
5. **Wait** for explicit order before disk edits.
6. **Closeout** with full incident-aware summary + YAML footer when research/ship occurred.

---

## Relationship to other incidents

| Incident | Link |
|----------|------|
| 001 | Scope — Noetfield only |
| 002 | Permission before edit |
| 003 | SourceA read integrity |
| 004 | Open backlog honesty |
| **005** | **Ask-first operating law (this)** |

---

## Corrective actions

| # | Action | Status |
|---|--------|--------|
| 1 | R-008 in MEMORY_LOCKED.yaml | Done |
| 2 | SKILL-006 ask-before-implement | Done |
| 3 | `noetfield-ask-before-edit.mdc` cursor rule | Done |
| 4 | Full summary report on disk | `.cursor/reports/2026-06-06-full-incident-summary.md` |

---

**END**
