# GTM_NEXT — Tier A queue (post–1000-pack)

When the NF-PLAN registry is fully synced (`1000/1000 done`), pick the next **≤3** agent tasks from here or `os/plan.json` `next_tasks`.

**Authority:** [NOETFIELD_GTM_60_DAY_LOCKED_v1.md](../../../strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md)  
**Verify:** `./scripts/plan-with-no-asf-verify.sh`

**Commercial P0:** Outreach/calls = agentic layer (founder Hub). NF-CLOUD-AGENT = validators + www/GTM assets only.

## Registry 1000/1000 semantics

`python3 scripts/sync-prompt-pack-status.py` marks all NF-PLAN rows `done` via `expand_done_by_pattern()` — this is **dedup / pattern propagation**, not “all engineering complete.” Real queue lives here and in `os/plan.json` `next_tasks`.

## ID namespace note

`ship-*-NNN` = GTM Tier A queue (`next_tasks`). `nf-*-NNN` in engineering manifest = product waves — numeric suffix overlap is intentional (e.g. `ship-trust-brief-demo-042` ≠ `nf-homepage-design-partner-042`).

## Next GTM Tier A (NF-CLOUD disk) — iter 19 proposals

Founder pick or bounded `implement`:

1. **ship-procurement-openapi-verify-057** · Verify `/openapi.json` returns 200 in gtm-ops bundle  
   Outcome: Production API schema reachable from buyer verify.

1. **ship-services-governance-readme-openapi-058** · services/governance README cites `/openapi.json` path  
   Outcome: Prod README matches procurement buyer link.

1. **ship-tenth-audit-merge-rule-059** · Document tenth-audit branch in ENGINEERING_DONE_MANIFEST closeout template  
   Outcome: Audit iteration naming stays traceable in manifest.

## Agentic only — Hub (not NF-CLOUD implement)

| ID | Owner | Outcome |
|----|-------|---------|
| **ship-design-partner-outreach-026** | Agentic layer | One named CIO contact + demo URL sent; tracker row updated |

Evidence: [DESIGN_PARTNER_PIPELINE_v1.md](../../../copilot/DESIGN_PARTNER_PIPELINE_v1.md) · [AGENTIC_COMMERCIAL_HANDOFF_v1.md](../../AGENTIC_COMMERCIAL_HANDOFF_v1.md)

## Recently shipped (iter 18)

| ID | Shipped |
|----|---------|
| ship-procurement-checkpoint-verify-054 | Hardened checkpoint verify guards on procurement |
| ship-services-governance-openapi-bridge-055 | Procurement OpenAPI + services/governance README links |
| ship-merged-window-config-056 | MERGED_WINDOW constant in OPEN_PRS header |

## Recently shipped (iter 17)

| ID | Shipped |
|----|---------|
| ship-blueprint-services-governance-bridge-051 | services/governance README + blueprint §8.3 prod row |
| ship-procurement-control-checkpoint-copy-052 | Procurement eval+enforce control checkpoint copy |
| ship-merged-pr-window-five-053 | Rolling top-5 merged PR window in coherence verify |

## Recently shipped (iter 16)

| ID | Shipped |
|----|---------|
| ship-blueprint-governance-console-bridge-048 | PLATFORM_BLUEPRINT §8/§13/§21 ↔ governance-console README |
| ship-rehearsal-parity-all-pages-049 | Rehearsal parity loop (hub + pilot ol + demo ol) |
| ship-open-prs-merged-044-gate-050 | Rolling top-4 merged PR window in coherence verify |

## Recently shipped (iter 15)

| ID | Shipped |
|----|---------|
| ship-trust-brief-parity-audit-045 | Single trust-brief parity loop (4 buyer pages) in verify |
| ship-merged-pr-open-prs-gate-046 | OPEN_PRS merged #41–#44 FAIL gate |
| ship-demo-rehearsal-demo-047 | Demo rehearsal link in demo script ol |

## Recently shipped (iter 14)

| ID | Shipped |
|----|---------|
| ship-trust-brief-demo-042 | Trust-brief intake CTA on copilot demo page |
| ship-demo-rehearsal-pilot-043 | Demo rehearsal link in pilot checklist ol |
| ship-open-prs-autocheck-044 | OPEN_PRS pending vs gh pr list FAIL gate |

## Recently shipped (iter 13)

| ID | Shipped |
|----|---------|
| ship-trust-brief-pilot-039 | Trust-brief intake CTA on copilot pilot page |
| ship-procurement-cta-homepage-040 | Homepage hero procurement CTA verify guard |
| ship-cursor-reply-coherence-041 | cursor-reply SHA coherence FAIL gate |

## Recently shipped (iter 12)

| ID | Shipped |
|----|---------|
| ship-trust-brief-procurement-036 | Trust-brief intake CTA on procurement buyer pack |
| ship-drift-blueprints-procurement-037 | Drift blueprints index on procurement |
| ship-demo-url-verify-038 | `make demo-url` guard in plan-with-no-asf-verify |

## Recently shipped (iter 11)

| ID | Shipped |
|----|---------|
| ship-trust-brief-intake-wire-033 | Trust-brief intake CTA on copilot hub + verify |
| ship-drift-sources-procurement-034 | Drift detection sources on procurement |
| ship-demo-rehearsal-hub-wire-035 | Demo rehearsal checklist on copilot hub |

## Prior shipped (iter 9–10 + post-audit)

| ID | Shipped |
|----|---------|
| ship-tunnel-smoke-verify-030 | Optional staging-smoke in plan-with-no-asf-verify |
| ship-governance-sources-handbook-031 | Handbook link on procurement |
| ship-copilot-hub-sources-032 | Sources Book + handbook on copilot hub |
| ship-procurement-one-pager-wire-027 | PROCUREMENT_ONE_PAGER www wire |
| ship-governance-sources-www-028 | Clickable Sources Book on procurement |
| ship-homepage-demo-cta-029 | Homepage demo CTA verify guard |

## Prior shipped (iter 4–8)

| ID | Shipped |
|----|---------|
| ship-gtm-ops-www-wire-013 | GTM ops docs www wire |
| ship-buyer-debrief-template-014 | Buyer debrief template |
| ship-tier-gate-verify-015 | Tier-gate verify guard |
| ship-bc-ai-for-all-outreach-016 | BC AI outreach alignment doc |
| ship-gtm-next-queue-023 | GTM_NEXT queue + QUICK_PICK fallback |
| ship-staging-demo-www-wire-024 | STAGING_DEMO www wire |
| ship-security-buyer-tle-copy-025 | CISO security buyer TLE copy |
| ship-registry-pattern-propagation-020 | QUICK_PICK dedup |
| ship-diligence-procurement-wire-021 | RPAA one-pager www wire |
| ship-design-partner-bc-ai-022 | BC AI pipeline block |
| ship-registry-sync-iter6-017 | Registry sync iter 6 |
| ship-bc-ai-www-wire-018 | BC AI www wire |
| ship-dual-brand-boundary-019 | Dual-brand boundary matrix |
