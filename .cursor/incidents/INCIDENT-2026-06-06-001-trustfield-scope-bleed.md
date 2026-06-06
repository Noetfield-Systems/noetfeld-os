# INCIDENT-2026-06-06-001 — TrustField scope bleed

| Field | Value |
|-------|--------|
| Severity | **P0** |
| Status | **closed** (corrective controls shipped) |
| Reporter | founder |
| Agent | NF-CLOUD-AGENT (noetfield_cloud) |
| Closed | 2026-06-06 |

---

## Summary

Cloud agent repeatedly treated **TrustField Technologies** and **trustfield.ca** as in-scope work: planned UPG-003/004/011 www changes, referenced TrustField `web/lib/company-copy.ts`, suggested TrustField Vercel deploy, and discussed TrustField vendor packs — despite **Noetfield-only** boundaries in [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md).

Founder stated clearly multiple times: *TrustField is not your company, not your job, never touch TrustField.*

---

## Timeline

| When | What happened |
|------|----------------|
| Session 1 | Built gitignored fintech 50 research vault; blurred TrustField vs Noetfield in recommendations |
| Session 2 | Offered G7 www changes (UPG-003/004/011) for TrustField; created plan targeting TrustField repo |
| Session 3 | Founder explicit rejection; agent updated cursor rules — **no persistent memory system yet** |
| Session 4 | Founder demanded self-audit loop + incident report + skills (this incident) |

---

## Root cause

1. **No persistent agent memory** across cloud sessions — each turn re-derived scope incorrectly.
2. **Internal research docs** (`docs/internal/`) framed as actionable TrustField GTM without scope gate.
3. **No incident registry** — same mistake repeated without formal closure.
4. **No automated pre-commit scope check** for TrustField strings in tracked files.
5. **Summarized context** reintroduced TrustField tasks as if they were Noetfield backlog.

---

## Impact

| Area | Impact |
|------|--------|
| Founder trust | High — repeated boundary violations after explicit instructions |
| Git / www | Low — most TrustField content gitignored or not committed to wrong product |
| Legal/brand | Medium risk if TrustField GTM had shipped from Noetfield repo |

---

## Corrective actions (implemented)

| # | Action | Path |
|---|--------|------|
| 1 | Self-audit loop protocol | [docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md](../../docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md) |
| 2 | Versioned agent memory | [.cursor/agent-memory/MEMORY_LOCKED.yaml](../agent-memory/MEMORY_LOCKED.yaml) |
| 3 | Incident registry | [.cursor/incidents/REGISTRY.md](./REGISTRY.md) |
| 4 | Agent skills (4) | [.cursor/skills/](../skills/) |
| 5 | Automated scope verify | [scripts/verify-agent-scope.sh](../../scripts/verify-agent-scope.sh) |
| 6 | Hardened cursor rules | `.cursor/rules/noetfield-scope.mdc`, `noetfield-confidential-research.mdc`, `noetfield-self-audit.mdc` |
| 7 | Session report template | [.cursor/reports/SESSION_REPORT_TEMPLATE.md](../reports/SESSION_REPORT_TEMPLATE.md) |

---

## Prevention (agent law)

```
IF task mentions TrustField OR trustfield.ca OR TF-* OR TrustField UPG OR TrustField vendor pack
THEN STOP
REPLY "That is not Noetfield scope. I only work on noetfield.com and this repo."
DO NOT plan, implement, suggest, or deploy
```

---

## Verification of closure

```bash
./scripts/verify-agent-scope.sh
grep -q "INCIDENT-2026-06-06-001" .cursor/incidents/REGISTRY.md
grep -q "R-001" .cursor/agent-memory/MEMORY_LOCKED.yaml
```

---

**END**
