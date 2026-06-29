---
doc_type: baseline_receipt
status: locked
repo_scope: NOOS
lane: Baseline
plan_ids:
  - PLAN-0007
  - PLAN-0008
captured_at: "2026-06-28"
---

# NOOS Baseline Receipt — PLAN-0007 / PLAN-0008

## Scope

This receipt captures NOOS baseline evidence only:

- `PLAN-0007` — NOOS clean-tree transcript.
- `PLAN-0008` — NOOS repo-policy receipt.

No SourceA, Noetfield website, or TrustField repo was touched. No factory process was started or stopped. No generated runtime receipt was edited.

## Evidence

| Field | Value |
|---|---|
| Repo | `noetfeld-os` |
| Branch | `main` |
| HEAD SHA | `d750da4c37054670df1d7bf965a0d4e038d53341` |
| Dirty count before receipt | `0` |
| `git status --short` before receipt | empty output |

## Commands

```bash
git branch --show-current
# main

git rev-parse HEAD
# d750da4c37054670df1d7bf965a0d4e038d53341

git status --short
# empty output

python3 scripts/check_noos_repo_policy.py
# OK: repo-policy.json

bash scripts/check_noos_clean_tree.sh
# OK: NOOS working tree clean; no factory writer detected
```

## Completion

- `PLAN-0007`: complete. The NOOS baseline clean-tree state was captured before lane execution, with branch and empty status output.
- `PLAN-0008`: complete. The NOOS repo-policy validator returned PASS output.
