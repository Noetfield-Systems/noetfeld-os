# SKILL-006 — Ask before implement (founder law)

**When:** Every session — before first disk mutation and at session end.

**Authority:** INCIDENT-2026-06-06-005 · MEMORY_LOCKED R-007 · R-008

**On rule conflict:** Run [SKILL-007-auto-conflict-resolution.md](./SKILL-007-auto-conflict-resolution.md) first.

---

## Before any disk edit

1. State what you understood from the user message.
2. List **suggested** next moves (options A/B/C).
3. **ASK** founder: which option, or provide clarification.
4. Wait for explicit order: task name, file scope, or `implement <bounded task>`.
5. Only then: edit, commit, push (if authorized).

## Default mode

**Advise-only** — no writes until founder orders.

## Exceptions (still bounded)

| Trigger | Meaning |
|---------|---------|
| `implement <task>` | Permission for **named** task only — confirm scope if ambiguous |
| `PLAN WITH NO ASF` + founder iter order | Ship bundle per that workflow — still one bounded iter |
| `WRITE DOWN incident reports` | Permission to write `.cursor/incidents/` + registry + memory bump |

## Session end (mandatory)

1. Full summary: done / open / blocked.
2. Open incidents table from `REGISTRY.md`.
3. **ASK:** "What is your next move?"
4. Optional: `reports/cursor-reply-latest.txt` + YAML footer **only if founder ordered closeout**.

## Fail response

If user message is ambiguous:

```
I will not edit disk yet.
Suggested options: [A] [B] [C]
Which should I do, or clarify scope?
```

---

**END**
