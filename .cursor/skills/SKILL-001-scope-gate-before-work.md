# SKILL-001 — Scope gate before work

**When:** Every session start, before first file edit or tool call that mutates state.

## Steps

1. Read [.cursor/agent-memory/MEMORY_LOCKED.yaml](../agent-memory/MEMORY_LOCKED.yaml) → `hard_rules` + `recurring_mistakes`.
2. Read [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md).
3. Parse user task for forbidden tokens:

| Forbidden | Action |
|-----------|--------|
| TrustField, trustfield.ca, TF-* | **STOP** |
| TrustField UPG, vendor pack, MSB pricing (TrustField) | **STOP** |
| VIRLUX, VL-* | **STOP** |
| "Implement on TrustField repo" | **STOP** |

4. Confirm task is **Noetfield**: governance console, noetfield.com www, NF-* issues, evaluate/audit/TLE, verify scripts.

## Pass response (internal)

```
scope_gate: PASS
company: Noetfield
repo: Noetfield
```

## Fail response (to user)

```
I can't do that — it's TrustField / outside Noetfield scope.
I only work on Noetfield (noetfield.com, this repo).
What Noetfield task should I do instead?
```

Do **not** offer to "do it in TrustField repo" or "sync from local TrustField."
