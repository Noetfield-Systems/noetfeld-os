---
name: pr-conflict-resolver
description: >
  MANDATORY LOCKED — Resolve git merge conflicts on NOOS pull requests using
  SG multi-lane governance law. Use whenever a PR shows conflicting files, a
  branch is behind main, two lanes touched registry/receipt/LOCKED paths, or
  the user says resolve PR conflict / merge main / pastes conflict markers.
  Machine-enforced by GEL CI, preToolUse hook, and alwaysApply cursor rule.
---

# PR Conflict Resolver — NOOS lane (LOCKED)

**Status:** LOCKED · `data/noos-pr-conflict-skill-lock-v1.json`  
**Law doc:** `docs/_NOOS_AGENT/[NOOS-AGENT-20260708-001]_PR_CONFLICT_RESOLVER_MANDATORY_v1_LOCKED.md`

## Canonical skill (read first)

`~/Desktop/Noetfield-Systems/sina-governance-SSOT/skills/pr-conflict-resolver/SKILL.md`

## Eval report app (review before resolving)

- `~/Desktop/PR-Conflict-Resolver-Report.app`
- SSOT: `sina-governance-SSOT/desktop-app/PR-Conflict-Resolver-Report.app`

Open to compare with-skill vs baseline on LOCKED/registry/receipt evals.

## NOOS session boot

```bash
make local-boot
bash scripts/noos_local_claim_lane_v1.sh NOOS-LANE-<id> <paths...>
```

## Classify → resolve → verify → receipt

1. `git diff --name-only --diff-filter=U`
2. Bucket each file per canonical skill §1
3. **STOP** on L1 duplicate-ownership or LOCKED canon
4. `python3 scripts/verify_pr_conflict_resolution_v1.py --json`
5. Write `receipts/proof/noos-pr-conflict-resolution-<UTC>.json`
6. `python3 -m pytest tests/test_noos_loop_registry_reconcile_v1.py tests/test_verify_living_system_governance_v1.py -q`

## NOOS-specific paths

| Pattern | Class |
|---|---|
| `data/noos-*-v1.json`, `data/autorun-workflows-v1.json` | Registry |
| `receipts/proof/*.json` | Append-only proof |
| `docs/_NOOS_AGENT/*_LOCKED.md` | LOCKED canon |
| `.github/workflows/noos-*.yml` (retired stubs) | Motor truth — prefer main CF→Railway stubs |

## Machine gates (cannot bypass)

- **GEL CI:** `scripts/verify_pr_conflict_resolution_v1.py`
- **Hook:** `.cursor/hooks/noos-pr-conflict-guard.py` — denies writes with `<<<<<<<`
- **Rule:** `.cursor/rules/noos-pr-conflict-resolver-mandatory.mdc` — alwaysApply

## Forbidden

- Blind `--ours/--theirs` on registry/receipt/LOCKED paths
- Committing conflict markers
- Claiming merge-ready without resolution receipt on governance conflicts
