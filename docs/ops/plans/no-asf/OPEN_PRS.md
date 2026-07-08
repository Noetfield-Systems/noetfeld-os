<!-- ADVISOR_ARCHITECT_CHECKLIST_STUB (auto-inserted) -->
Advisor / Architect Minimal Checklist (AUTO-STUB)
-----------------------------------------------

- protects: Which founder goal does this protect? (pick one)
- sina_workload: reduces / increases + short rationale
- permission_loop: yes / no + explanation
- sandbox_autonomy: yes / no + where/how (sandbox lane path)
- target_to_blocker: yes / no + mitigation
- canon_version: (string)
- sandbox_evidence: link(s) to sandbox receipt(s)

# Open PR policy — Noetfield GTM ship

**Agent tag:** `NF-CLOUD-AGENT`

## Merge rule

Only merge **Noetfield GTM / PLAN WITH NO ASF** ship PRs from branches matching:

`cursor/no-asf-*-37f0`, `cursor/10-phase-audit-fix-37f0`, `cursor/post-audit-10-phase-fix-37f0`, `cursor/fourth-audit-iter12-37f0`, `cursor/fifth-audit-iter13-37f0`, `cursor/sixth-audit-iter14-37f0`, `cursor/seventh-audit-iter15-37f0`, `cursor/eighth-audit-iter16-37f0`, `cursor/ninth-audit-iter17-37f0`, or `cursor/tenth-audit-iter18-37f0`

**Superseded (do not merge):** `cursor/third-audit-10-phase-fix-37f0` (PR #42), `cursor/fourth-audit-iter12-37f0` (PR #42), `cursor/fifth-audit-iter13-37f0` (PR #43), `cursor/sixth-audit-iter14-37f0` (PR #44), `cursor/seventh-audit-iter15-37f0` (PR #45), `cursor/eighth-audit-iter16-37f0` (PR #46), `cursor/ninth-audit-iter17-37f0` (PR #47), `cursor/tenth-audit-iter18-37f0` (PR #48 merged).

**MERGED_WINDOW:** 5

**Coherence verify:** `verify-no-asf-coherence.sh` reads `MERGED_WINDOW` from this header and FAIL if `## Recently merged` has fewer than that many ship PR rows.

**Rolling merged window:** coherence verify FAILs if the top `MERGED_WINDOW` rows in `## Recently merged` are missing (dynamic parse, not hardcoded list).

## Do not merge from cloud agent

- TrustField scope PRs
- Stale governance-console experiments unless founder re-opens
- Any PR touching `ops/private/` or out-of-scope TrustField product repos

## Pending ship PR

_None — queue cleared 2026-07-08; main @ d8bb0e16; gov-sandbox + www audit blockers shipped (#90–#93)._

## Recently merged

| PR | Branch | Notes |
|----|--------|-------|
| #76 | cursor/google-workspace-intake-37f0 | Ops witness R-013 · Workspace inbox · Stripe hub · 10-step ship |
| #48 | cursor/tenth-audit-iter18-37f0 | Tenth audit — iter 18 (054–056) @ b822423 |
| #47 | cursor/ninth-audit-iter17-37f0 | Ninth audit — iter 17 (051–053) @ 46a36a3 |
| #46 | cursor/eighth-audit-iter16-37f0 | Eighth audit — iter 16 (048–050) @ f2103d3 |
| #45 | cursor/seventh-audit-iter15-37f0 | Seventh audit — iter 15 (045–047) @ 80ad8a7 |
| #44 | cursor/sixth-audit-iter14-37f0 | Sixth audit — iter 14 (042–044) @ c2543b5 |
| #43 | cursor/fifth-audit-iter13-37f0 | Fifth audit — iter 13 (039–041) @ 9f0e3f7 |
| #42 | cursor/fourth-audit-iter12-37f0 | Fourth audit — third-audit bundle + iter 12 (036–038) @ 43715a4 |
| #41 | cursor/no-asf-iter11-37f0 | Iter 11 — trust-brief, drift sources, demo rehearsal hub |
| #40 | cursor/post-audit-10-phase-fix-37f0 | Post-audit workflow + paths + verify hardening |
| #39 | cursor/10-phase-audit-fix-37f0 | 10-phase audit — R-011, www 030–032, coherence verify |

## Closed stale queue (2026-07-08 sweep)

| PR | Branch | Reason |
|----|--------|--------|
| #86 | ci/production-ci-upgrade | Superseded by #87 + #88 on main |
| #81 | workflow-hardening-v1 | Superseded by #82 + #88 |
| #89 | cursor/www-audit-homepage-upgrade | Tech split merged #90; copy awaits verdict |
| #77 | cursor/charter-lock-internal-37f0 | Stale draft |
| #75 | cursor/sandbox-v2-37f0 | Superseded by gov-sandbox #91–#92 |
| #74 | cursor/legal-aml-factories-37f0 | Stale factory draft |
| #73 | cursor/stripe-gtm-setup-37f0 | Superseded by #76 |
| #65–#53 | cursor/*-37f0 | June UI/commercial/forward-queue drafts |
| #52 | cursor/eleventh-audit-iter19-37f0 | Superseded by later ship waves |
| #50 | cursor/plan-with-no-asf-upgrade-37f0 | Superseded by iter 18 merge |
| #49 | cursor/design-token-migration-37f0 | Conflicts with current console |
| #7 | cursor/trustfield-scope-37f0 | Out of scope — R-001 |
| #2 | cursor/governance-console-v1-37f0 | Superseded by main console path |

**Open PR count:** 0 (verified `gh pr list --state open` 2026-07-08).
