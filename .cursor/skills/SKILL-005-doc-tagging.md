# SKILL-005 — Doc tagging (mandatory)

**When:** Creating a **new** document you write, or adding **your** new sections when the user explicitly asks you to edit a file.

**Do not** add headers to existing docs you did not author. Do not retag founder or locked files.

## Header (required top block)

```markdown
| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-<AREA>-<NNN>` |
| **Updated** | YYYY-MM-DD |
```

Use **today's UTC or local date** for `Updated` on every edit.

## Doc trace

- New file: pick `<AREA>` + next `<NNN>` or use `YYYY-MM-DD` suffix for reports
- Edit existing: bump `Updated` date; bump trace version if structural change

## Commits

```
[NF-CLOUD-AGENT] <message>
```

## Reference

[docs/ops/AGENT_DOC_TAGGING_LOCKED_v1.md](../../docs/ops/AGENT_DOC_TAGGING_LOCKED_v1.md)
