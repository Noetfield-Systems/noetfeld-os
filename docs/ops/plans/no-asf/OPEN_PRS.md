# Open PR policy — Noetfield GTM ship

**Agent tag:** `NF-CLOUD-AGENT`

## Merge rule

Only merge **Noetfield GTM / PLAN WITH NO ASF** ship PRs from branches matching:

`cursor/no-asf-*-37f0`, `cursor/10-phase-audit-fix-37f0`, or `cursor/post-audit-10-phase-fix-37f0`

## Do not merge from cloud agent

- TrustField scope PRs
- Stale governance-console experiments unless founder re-opens
- Any PR touching `ops/private/` or TrustField implementation

## Recently merged

| PR | Branch | Notes |
|----|--------|-------|
| #39 | cursor/10-phase-audit-fix-37f0 | 10-phase audit — R-011, www 030–032, coherence verify |

## Stale PRs (open until founder closes)

| PR | Branch | Reason |
|----|--------|--------|
| #2 | governance-console-v1 | Superseded by main console path |
| #7 | trustfield-scope | Out of scope — R-001 |

**Founder action:** Close #2 and #7 on GitHub (cloud agent token cannot close).
