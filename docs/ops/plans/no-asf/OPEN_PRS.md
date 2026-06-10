# Open PR policy — Noetfield GTM ship

**Agent tag:** `NF-CLOUD-AGENT`

## Merge rule

Only merge **Noetfield GTM / PLAN WITH NO ASF** ship PRs from branches matching:

`cursor/no-asf-*-37f0` or `cursor/10-phase-audit-fix-37f0`

## Do not merge from cloud agent

- TrustField scope PRs
- Stale governance-console experiments unless founder re-opens
- Any PR touching `ops/private/` or TrustField implementation

## Stale PRs (closed 2026-06-10)

| PR | Branch | Reason |
|----|--------|--------|
| #2 | governance-console-v1 | Superseded by main console path |
| #7 | trustfield-scope | Out of scope — R-001 |
