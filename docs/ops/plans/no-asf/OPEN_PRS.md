# Open PR policy — Noetfield GTM ship

**Agent tag:** `NF-CLOUD-AGENT`

## Merge rule

Only merge **Noetfield GTM / PLAN WITH NO ASF** ship PRs from branches matching:

`cursor/no-asf-*-37f0`, `cursor/10-phase-audit-fix-37f0`, `cursor/post-audit-10-phase-fix-37f0`, `cursor/fourth-audit-iter12-37f0`, `cursor/fifth-audit-iter13-37f0`, `cursor/sixth-audit-iter14-37f0`, `cursor/seventh-audit-iter15-37f0`, or `cursor/eighth-audit-iter16-37f0`

**Superseded (do not merge):** `cursor/third-audit-10-phase-fix-37f0` (PR #42), `cursor/fourth-audit-iter12-37f0` (PR #42), `cursor/fifth-audit-iter13-37f0` (PR #43), `cursor/sixth-audit-iter14-37f0` (PR #44), `cursor/seventh-audit-iter15-37f0` (PR #45).

**Coherence verify:** `verify-no-asf-coherence.sh` enforces pending rows vs `gh pr list` and FAIL if `## Recently merged` has fewer than 4 ship PR rows (rolling window).

**Rolling merged window:** coherence verify FAILs if the top 4 rows in `## Recently merged` are missing (dynamic parse, not hardcoded list).

## Do not merge from cloud agent

- TrustField scope PRs
- Stale governance-console experiments unless founder re-opens
- Any PR touching `ops/private/` or TrustField implementation

## Pending ship PR

| PR | Branch | Notes |
|----|--------|-------|
| #46 | cursor/eighth-audit-iter16-37f0 | Eighth audit — iter 16 (048–050) + post-merge truth |

## Recently merged

| PR | Branch | Notes |
|----|--------|-------|
| #45 | cursor/seventh-audit-iter15-37f0 | Seventh audit — iter 15 (045–047) @ 80ad8a7 |
| #44 | cursor/sixth-audit-iter14-37f0 | Sixth audit — iter 14 (042–044) @ c2543b5 |
| #43 | cursor/fifth-audit-iter13-37f0 | Fifth audit — iter 13 (039–041) @ 9f0e3f7 |
| #42 | cursor/fourth-audit-iter12-37f0 | Fourth audit — third-audit bundle + iter 12 (036–038) @ 43715a4 |
| #41 | cursor/no-asf-iter11-37f0 | Iter 11 — trust-brief, drift sources, demo rehearsal hub |
| #40 | cursor/post-audit-10-phase-fix-37f0 | Post-audit workflow + paths + verify hardening |
| #39 | cursor/10-phase-audit-fix-37f0 | 10-phase audit — R-011, www 030–032, coherence verify |

## Stale PRs (open until founder closes)

| PR | Branch | Reason |
|----|--------|--------|
| #2 | cursor/governance-console-v1-37f0 | Superseded by main console path |
| #7 | cursor/trustfield-scope-37f0 | Out of scope — R-001 |

**Founder action:** Close #2 and #7 on GitHub (cloud agent token cannot close).
