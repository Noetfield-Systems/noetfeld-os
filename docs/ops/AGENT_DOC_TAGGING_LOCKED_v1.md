# Agent doc tagging (LOCKED v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-DOCTAG-001` |
| **Updated** | 2026-06-06 |

---

## Law

**Only documents this agent creates or writes** must include the tag header below with **today's date** in `Updated`.

**Do not touch other docs** — no retroactive headers on founder files, locked specs, or docs you did not author. Edit existing files only when the user explicitly asks; then add/update the header on **your** new sections only, not the whole file.

Commits by agents use prefix: `[NF-CLOUD-AGENT]`

---

## Required header (copy into every new/edited agent doc)

```markdown
| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-<AREA>-<NNN>` |
| **Updated** | YYYY-MM-DD |
```

| Placeholder | Rule |
|-------------|------|
| `<AREA>` | Short slug: `AUDIT`, `OPS`, `INCIDENT`, `SKILL`, `MEMORY`, `REPORT` |
| `<NNN>` | 3-digit sequence per area, or date slug `2026-06-06` for one-offs |

---

## Examples

| Doc type | Doc trace example |
|----------|-------------------|
| Incident | `NF-CLOUD-INCIDENT-001` |
| Skill | `NF-CLOUD-SKILL-005` |
| Ops lock | `NF-CLOUD-OPS-012` |
| Session report | `NF-CLOUD-REPORT-2026-06-06` |

---

## Forbidden

- Adding headers to docs you did not write
- Rewriting or retagging founder/locked docs without explicit user request
- Untagged **new** agent-authored docs
- Wrong tag (`NF-LOCAL-AGENT` in cloud workspace)

---

## Skill

[.cursor/skills/SKILL-005-doc-tagging.md](../../.cursor/skills/SKILL-005-doc-tagging.md)

---

**END**
