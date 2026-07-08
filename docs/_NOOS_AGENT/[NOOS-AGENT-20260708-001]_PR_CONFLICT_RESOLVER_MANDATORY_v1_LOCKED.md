<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260708-001
doc_type: LOCKED_LAW
status: LOCKED
locked_at: 2026-07-08
-->

# PR Conflict Resolver — MANDATORY v1 (LOCKED)

**Status:** LOCKED — 2026-07-08  
**Authority:** NOOS integrator + SG SSSOT  
**Unlock:** Founder gate only

## One law

PR merge conflicts are **governance questions first**, text diffs second. Agents MUST load `pr-conflict-resolver` before picking sides on sensitive paths.

## Locked artifacts (NOOS)

| Artifact | Path |
|---|---|
| Lock manifest | `data/noos-pr-conflict-skill-lock-v1.json` |
| Lane skill stub | `.cursor/skills/pr-conflict-resolver/SKILL.md` |
| Cursor rule | `.cursor/rules/noos-pr-conflict-resolver-mandatory.mdc` |
| Fail-closed hook | `.cursor/hooks/noos-pr-conflict-guard.py` |
| CI verifier | `scripts/verify_pr_conflict_resolution_v1.py` |

## Locked artifacts (SG canonical)

| Artifact | Path |
|---|---|
| Canonical skill | `sina-governance-SSOT/skills/pr-conflict-resolver/SKILL.md` |
| LOCK doc | `skills/pr-conflict-resolver/PR_CONFLICT_RESOLVER_SKILL_LOCKED_v1.md` |
| Eval app (SSOT) | `desktop-app/PR-Conflict-Resolver-Report.app` |
| Desktop shortcut | `~/Desktop/PR-Conflict-Resolver-Report.app` |

## Mandatory workflow

```
conflict detected
  → load skill + open eval app
  → classify each file (§1 skill table)
  → resolve OR stop+escalate (L1 / LOCKED)
  → verify_pr_conflict_resolution_v1.py
  → resolution receipt
  → pytest governance subset
  → merge-ready claim
```

## File-class quick reference

| Pattern | Class | Action |
|---|---|---|
| `data/noos-*-v1.json`, `*registry*` | Registry | Structural JSON merge; same-key different-owner → STOP |
| `receipts/proof/*.json` | Receipt | Keep both; rename on collision |
| `*_LOCKED.md` | LOCKED canon | Founder escalation only |
| `*.language_gate_review.json` | Generated | Regenerate or poisoned temp stand-in |
| `scripts/`, workflows | Code | Normal merge + pytest |

## Eval benchmark (why this is locked)

Desktop app report shows **+24% pass rate** with skill on governance conflicts; baseline agents still commit "final" LOCKED merges while recommending founder follow-up — the exact trap this law prevents.

## Verification

```bash
python3 scripts/verify_pr_conflict_resolution_v1.py --json
python3 scripts/verify_pr_conflict_resolution_v1.py --mac-desktop --json   # Mac only
make pr-conflict-verify
```
