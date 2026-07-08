# NF PR Conflict Resolver — LOCKED v1

**Status:** LOCKED · **Law ID:** `NF-PR-CONFLICT-RESOLVER-v1`  
**SSOT:** `data/nf-pr-conflict-resolver-v1.json`  
**Upstream skill:** `sina-governance-SSOT/skills/pr-conflict-resolver/SKILL.md`  
**Agent skill:** `.cursor/skills/SKILL-011-pr-conflict-resolver.md`  
**Machine gate:** `python3 scripts/verify_pr_conflict_resolver_v1.py`

---

## Purpose

Git merge conflicts in Noetfield are **governance questions first, text diffs second**. Blindly picking a side on registries, receipts, LOCKED docs, or www copy creates silent policy violations.

## Mandatory triggers

Agents **must** load SKILL-011 before:

- Any PR shows `CONFLICTING` / `DIRTY` merge state
- `git merge` / `git rebase` / `git cherry-pick` produces conflict markers
- Two branches touched the same `data/*.json`, receipt, or LOCKED doc
- Founder says "resolve PR conflict", "merge main into branch", or "solve all PRs"

## File-class law (summary)

| Class | Examples | Rule |
|-------|----------|------|
| Receipt | `reports/www-audit/receipts/*`, `receipts/*.json` | Append-only — never drop proof |
| Registry | `data/*_v1.json`, `governance/*_LOCKED.json` | Structural JSON merge — escalate duplicate owners |
| LOCKED canon | `*LOCKED*.md` | Founder sign-off — do not unilaterally resolve |
| Generated | `reports/agent-auto/*`, `sitemap.xml` | Regenerate — do not hand-merge |
| WWW copy | `index.html`, `rebuild-www-v6.py` | Verdict matrix + `verify-ui-build-checklist` |
| Ordinary code | scripts, workflows, console | Standard merge + scoped validators |

## Machine enforcement

```bash
python3 scripts/verify_pr_conflict_resolver_v1.py   # wiring + no stray conflict markers
python3 scripts/nf_pr_conflict_classify_v1.py --git   # classify conflicted paths
bash tools/pr-conflict-resolver-report/open-report.sh # eval review UI (founder Mac)
```

Wired into: `make verify-pr-conflict-resolver`, `scripts/plan-with-no-asf-verify.sh`, `make validate`.

## Receipt

After resolving conflicts, write:

`reports/pr-conflict-resolution/pr-conflict-resolution-<UTC>.json`

using schema `nf-pr-conflict-resolution-receipt-v1` from data SSOT.

## Hard rule

**R-013** — No PR merge-ready claim without SKILL-011 classification + `verify_pr_conflict_resolver_v1.py` PASS.

---

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-07-08
