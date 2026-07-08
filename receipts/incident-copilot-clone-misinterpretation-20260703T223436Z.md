# Incident — Copilot clone misinterpretation

**ID:** `incident-copilot-clone-misinterpretation-20260703T223436Z`  
**When:** 2026-07-03 22:34 UTC  
**Severity:** medium

## What happened

A NOOS Copilot GitHub session treated a non-canonical clone/worktree as the control-panel authority and attempted dispatcher-scoped actions outside the canonical repo path.

## Canonical truth

- **Repo:** `Noetfield-Systems/noetfeld-OS`
- **Local path:** `/Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS`
- **Integrator protocol:** `data/noos-integrator-role-v1.json`

## Non-canonical (do not use as authority)

- `/Users/sinakazemnezhad/Projects/noetfeld-os` (feature/WIP branches)
- External Copilot workspace clones

## Impact

No direct writes to `main`. Cost-lock and dispatcher-mode work remained on branch `copilot/cost-locks-v1` (PR #24).

## Remediation

1. Incident receipt filed (JSON + this note)
2. Integrator pointer verified intact — not replaced with external team slug
3. `fleet_rollout` and `main_write` blocked in `data/noos-copilot-dispatcher-mode-v1.json`
4. Merge gated on cost-policy scanner PASS + bounded PR review

## Status

**Remediated** — operator acceptance by cursor-local-mac integrator, 2026-07-06.
