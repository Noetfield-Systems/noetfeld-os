# SKILL-011 — PR conflict resolver (mandatory)

**When:** Any merge conflict, PR `CONFLICTING`/`DIRTY` state, or multi-branch overlap on governance-sensitive files.

**Blocks:** `verify_pr_conflict_resolver_v1.py` FAIL → do not claim merge-ready.

**Upstream:** `sina-governance-SSOT/skills/pr-conflict-resolver/SKILL.md` (SG motor law L1–L5)  
**Noetfield SSOT:** `data/nf-pr-conflict-resolver-v1.json`  
**Locked law:** `docs/ops/NF_PR_CONFLICT_RESOLVER_LOCKED_v1.md`

---

## Session start (PR / merge work)

1. Read SKILL-011 (this file) + upstream skill §0–§1
2. Run `python3 scripts/nf_pr_conflict_classify_v1.py --git` on conflicted paths
3. Open eval report: `bash tools/pr-conflict-resolver-report/open-report.sh` (founder Mac) or read bundled `tools/pr-conflict-resolver-report/report.html`

## Classify before resolving

| Pattern | Class | Action |
|---------|-------|--------|
| `receipts/`, `*receipt*.json` | Receipt | Keep both; escalate same-path collisions |
| `data/*_registry_v1.json`, `governance/*_LOCKED.json` | Registry | JSON structural merge; escalate duplicate owners |
| `*LOCKED*.md` | LOCKED canon | Escalate — no unilateral merge |
| `reports/agent-auto/`, generated manifests | Generated | Regenerate via script |
| `index.html`, `rebuild-www-v6.py` | WWW copy | Verdict matrix ACCEPT rows only + UI checklist |
| `scripts/`, `governance-console/`, workflows | Ordinary code | Merge + scoped validators |

## Noetfield-specific stops

- **TrustField / out-of-repo** — R-001; close PR, do not merge
- **Interactive downgrade** — R-012; never resolve conflicts by removing demo/sandbox hooks
- **WWW copy without verdict** — reject per `noetfield-www-verdict-not-research.mdc`
- **Validator vs copy mismatch** — treat as generated-class; update validator + copy together (PR #95 pattern)

## After resolving

```bash
python3 scripts/verify_pr_conflict_resolver_v1.py
bash scripts/verify-agent-scope.sh
git diff --check
# class-specific:
bash scripts/verify-ui-build-checklist.sh    # if www touched
make validate                                 # before merge claim
```

Write receipt: `reports/pr-conflict-resolution/pr-conflict-resolution-<UTC>.json`

## Integration

| Skill | When |
|-------|------|
| SKILL-007 | Rule conflicts between skills |
| **SKILL-011** | **Git/PR file conflicts** |
| SKILL-009 | WWW copy in conflict resolution |
| SKILL-001 | Scope gate after conflict clear |

---

**END**
