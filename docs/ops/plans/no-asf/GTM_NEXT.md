# GTM_NEXT — Tier A queue (post–1000-pack)

When the NF-PLAN registry is fully synced (`1000/1000 done`), pick the next **≤3** agent tasks from here or `os/plan.json` `next_tasks`.

**Authority:** [NOETFIELD_GTM_60_DAY_LOCKED_v1.md](../../../strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md) · [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](../../../WWW_V16_PACKAGING_PLAN_LOCKED_v1.md)  
**Verify:** `./scripts/plan-with-no-asf-verify.sh`

**Commercial P0:** Outreach/calls = agentic layer (founder Hub). NF-CLOUD-AGENT = validators + www/GTM assets only.

**Packaging P0 (shipped v16):** Self-serve `/start/` · `/pricing/` · agentic strip · sandbox JS · inbox routing doc.

**WWW client guard (shipped 2026-06-18):** Four language layers on public www · mandatory `make nf-ui-checklist` · stable CTAs only (no invitation) · `docs/www/NF_WWW_LANGUAGE_LAYERS_LOCKED_v1.md`.

**Factory Round 16 (shipped 2026-06-19):** Portfolio **260/300** · XF-P2 + CA-P2 + PL-P1 done · ship-063–066 — `docs/ops/NF_FACTORY_ROUND_16_PREP_LOCKED_v1.md`.

**Factory Round 15 (shipped 2026-06-18):** Portfolio **197/300** · XF-P1 + V-P2 + CA-P1 done · ship-057 · GTM 059–062 — `docs/ops/NF_FACTORY_ROUND_15_PREP_LOCKED_v1.md`.

## Registry 1000/1000 semantics

`python3 scripts/sync-prompt-pack-status.py` marks all NF-PLAN rows `done` via `expand_done_by_pattern()` — this is **dedup / pattern propagation**, not “all engineering complete.” Real queue lives here and in `os/plan.json` `next_tasks`.

## ID namespace note

`ship-*-NNN` = GTM Tier A queue (`next_tasks`). `nf-*-NNN` in engineering manifest = product waves — numeric suffix overlap is intentional.

## Portfolio N-P1 wave (2026-06-17)

Founder bounded `implement` — disk queue head from `os/plan.json`:

1. **ship-portfolio-np1-funnel-metrics-061** · Sandbox funnel metrics spec S0→S5 for Hub weekly rollup — **done**  
   Plan: [`SANDBOX_FUNNEL_METRICS_SPEC_v1.md`](../../../copilot/SANDBOX_FUNNEL_METRICS_SPEC_v1.md)

1. **ship-portfolio-np1-hub-intake-062** · Copilot-governance intake Hub report template — **done**  
   Plan: [`INTAKE_COPILOT_GOVERNANCE_HUB_REPORT_v1.md`](../../../copilot/INTAKE_COPILOT_GOVERNANCE_HUB_REPORT_v1.md)

## Next GTM Tier A (NF-CLOUD disk) — iter 21 proposals

Founder pick or bounded `implement`:

1. **Phase 17 LOCK** · OPS-P1 pf-0291–0300 + XF-P2b + CA-P2b + PL-P2
1. **OPS-P1 verify wave** · `verify-final-lock` green on every ship
1. **Platform PL-P2** · pf-0276–pf-0290 entity routing memos

## Shipped iter 20 (Phase 16 closeout)

| ID | Shipped |
|----|---------|
| ship-anti-staleness-verify-063 | Anti-staleness needles in verify-doc-ssot + factory spine |
| ship-status-phase16-064 | `/status/` + `/next/` Phase 17 queue head (260/300) |
| ship-portfolio-registry-sync-065 | Phase 16 LOCK + registry sync in verify-doc-ssot |
| ship-pl-entity-readme-066 | `docs/platform/NF_PLATFORM_ENTITY_SPLIT_INDEX_v1.md` |

## Prior iter 20 proposals (superseded)

~~1. **TrustField backlog pick**~~ · **N/A** — TrustField lane 50/50 done

~~1. **Platform PL-P1**~~ · **DONE** — pf-0266–pf-0275

~~1. **Phase 16 LOCK**~~ · **DONE** — XF-P2 + CA-P2 + PL-P1 **30/30**

## Shipped iter 19 (Phase 15 closeout)

| ID | Shipped |
|----|---------|
| ship-sandbox-server-side-057 | Server-side sandbox sessions API + client fallback |
| ship-pricing-verify-doc-ssot-059 | v16 + Phase 15 needles in verify-doc-ssot |
| ship-procurement-openapi-verify-060 | `/openapi.json` 200 in verify-gtm-ops-docs |
| ship-services-governance-readme-openapi-061 | services/governance README cites `/openapi.json` |
| ship-tenth-audit-merge-rule-062 | ENGINEERING_DONE_MANIFEST tenth-audit template |

## Prior iter 19 proposals (all done)

~~1. **ship-sandbox-server-side-057**~~ · **DONE**

~~1. **ship-agentic-workflow-manifest-058**~~ · **DONE** — `/start/` links `docs/schemas/agent-manifest.schema.json`

~~1. **ship-pricing-verify-doc-ssot-059**~~ · **DONE**

~~1. **ship-procurement-openapi-verify-060**~~ · **DONE**

~~1. **ship-services-governance-readme-openapi-061**~~ · **DONE**

~~1. **ship-tenth-audit-merge-rule-062**~~ · **DONE**

## Agentic only — Hub (not NF-CLOUD implement)

| ID | Owner | Outcome |
|----|-------|---------|
| **ship-design-partner-outreach-026** | Agentic layer | One named CIO contact + demo URL sent; tracker row updated |
| **ship-sandbox-nurture-060** | Agentic layer | Email template for sandbox → design partner upgrade (founder approve) |

Evidence: [DESIGN_PARTNER_PIPELINE_v1.md](../../../copilot/DESIGN_PARTNER_PIPELINE_v1.md) · [AGENTIC_COMMERCIAL_HANDOFF_v1.md](../../AGENTIC_COMMERCIAL_HANDOFF_v1.md) · [COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md](../../COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md)

## Recently shipped (iter 18 — v16 packaging)

| ID | Shipped |
|----|---------|
| ship-v16-packaging-www-057 | `/start/` · `/pricing/` · self-serve rail · agentic block · v16 CSS/JS |
| ship-v16-prompt-pack-058 | WISE/500/inbox/memory/docs aligned to packaging funnel |
| ship-v16-verify-e2e-059 | verify-ui-e2e + verify-static-www v16 needles |

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

## Prior shipped (iter 16 and earlier)

See git history · [SHIP_NOW.md](../../../os/SHIP_NOW.md)
