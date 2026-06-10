# Open PR policy — Noetfield GTM ship

**Agent tag:** `NF-CLOUD-AGENT`

## Merge rule

Only merge **Noetfield GTM / PLAN WITH NO ASF** ship PRs from branches matching:

`cursor/no-asf-*-37f0`, `cursor/10-phase-audit-fix-37f0`, `cursor/post-audit-10-phase-fix-37f0`, `cursor/third-audit-10-phase-fix-37f0`, or `cursor/fourth-audit-iter12-37f0`

## Do not merge from cloud agent

- TrustField scope PRs
- Stale governance-console experiments unless founder re-opens
- Any PR touching `ops/private/` or TrustField implementation

## Pending ship PR

| PR | Branch | Notes |
|----|--------|-------|
| (open) | cursor/fourth-audit-iter12-37f0 | Fourth audit — third-audit bundle + iter 12 (036–038) + coherence |

Manual compare if automation fails: `main...cursor/fourth-audit-iter12-37f0`

## Recently merged

| PR | Branch | Notes |
|----|--------|-------|
| #41 | cursor/no-asf-iter11-37f0 | Iter 11 — trust-brief, drift sources, demo rehearsal hub |
| #40 | cursor/post-audit-10-phase-fix-37f0 | Post-audit workflow + paths + verify hardening |
| #39 | cursor/10-phase-audit-fix-37f0 | 10-phase audit — R-011, www 030–032, coherence verify |

## Stale PRs (open until founder closes)

| PR | Branch | Reason |
|----|--------|--------|
| #2 | cursor/governance-console-v1-37f0 | Superseded by main console path |
| #7 | cursor/trustfield-scope-37f0 | Out of scope — R-001 |

**Founder action:** Close #2 and #7 on GitHub (cloud agent token cannot close).
