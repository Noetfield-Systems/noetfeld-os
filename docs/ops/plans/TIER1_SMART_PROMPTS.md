# Tier 1 WISE Prompts (generated)

_Generated 2026-06-13T08:32:34Z by `scripts/generate-tier1-smart-pack.py` · framework: WISE_

**Picker:** `python3 scripts/pick-wise.py --prompt` (auto maturity + bottleneck)

**SSOT:** [NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md](../NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md)

---

## L-01 · Trust Brief conversion copy audit

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | GRC |
| W3 signal | Trust Brief / gate intake path converts |
| Requires | — |
| Unblocks | L-08, L-14 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Trust Brief / gate intake path converts
- **Buyer persona:** GRC
- **Effort:** S · **Mode:** cloud
- **Success reference:** Fixed-fee readiness SKU clarity
- **Buyer proof:** Primary CTA routes to Trust Brief intake with traceable RID.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Trust Brief conversion copy audit. Buyer proof: Primary CTA routes to Trust Brief intake with traceable RID.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- L-08, L-14

## Context budget (max 5 — do not read outside)
- `OFFERINGS_LOCKED.md`
- `docs/GTM_COPYBOOK.md`
- `scripts/rebuild-www-v6.py`

## Task
Audit /trust-brief/ against OFFERINGS_LOCKED ($10k, 6 weeks). PRS block, three SKUs only, CTA → /trust-brief/intake/. Regenerate via rebuild-www-v6.py if drift.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Price band changed without founder approval
- Fourth offering card added

## Verify
```bash
curl -s localhost:13081/trust-brief/ | grep -F '$10,000'
```

## Done when
Trust Brief page price, timeline, and CTA match commercial SSOT.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `OFFERINGS_LOCKED.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-01`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-02 · Homepage §07–10 proof narrative

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | CISO |
| W3 signal | Public www tells receipt-first wedge story |
| Requires | — |
| Unblocks | L-12, P-01 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Public www tells receipt-first wedge story
- **Buyer persona:** CISO
- **Effort:** M · **Mode:** cloud
- **Success reference:** Numbered buyer narrative
- **Buyer proof:** A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Homepage §07–10 proof narrative. Buyer proof: A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- L-12, P-01

## Context budget (max 5 — do not read outside)
- `docs/WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md`
- `scripts/rebuild-www-v6.py`
- `scripts/verify-ui-e2e.sh`

## Task
Verify or implement homepage sections 07–10: pain moment, category zones (no vendor names), CCS stack ladder, FAQ. Regenerate index via rebuild-www-v6.py.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Vendor-named battle grid requested
- Hand-editing index.html without generator

## Verify
```bash
grep -F 'The moment Copilot becomes auditable' www/index.html || grep -F 'Copilot becomes auditable' index.html
```

## Done when
Homepage §07–10 present; no vendor comparison table on public www.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-02`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-03 · Trust center diligence hub

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | Procurement |
| W3 signal | Procurement can diligence without call |
| Requires | L-02 |
| Unblocks | L-04, E-02 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Procurement can diligence without call
- **Buyer persona:** Procurement
- **Effort:** M · **Mode:** cloud
- **Success reference:** Trust center diligence structure
- **Buyer proof:** Procurement finds honest scope table + samples without a sales call.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Trust center diligence hub. Buyer proof: Procurement finds honest scope table + samples without a sales call.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-02

## Unblocks when done
- L-04, E-02

## Context budget (max 5 — do not read outside)
- `docs/DESIGN_REFERENCE_GOALS_LOCKED_v1.md`
- `scripts/rebuild-www-v6.py`
- `trust/index.html`

## Task
Ensure /trust/ has honest cert table (Shipped/Orientation/Roadmap/N/A), metadata-only M365, fail-closed export copy. Link from footer + procurement.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- SOC2 or ISO row marked Shipped without evidence
- Certifier fiction added

## Verify
```bash
grep -F 'fail closed' trust/index.html
```

## Done when
Trust center structurally matches procurement diligence pattern with honest scope rows.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/DESIGN_REFERENCE_GOALS_LOCKED_v1.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-03`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-04 · Procurement pack → trust link

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | Procurement |
| W3 signal | Procurement can diligence without call |
| Requires | L-03 |
| Unblocks | H-05 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Procurement can diligence without call
- **Buyer persona:** Procurement
- **Effort:** S · **Mode:** cloud
- **Success reference:** Procurement ZIP orientation
- **Buyer proof:** Procurement finds honest scope table + samples without a sales call.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Procurement pack → trust link. Buyer proof: Procurement finds honest scope table + samples without a sales call.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-03

## Unblocks when done
- H-05

## Context budget (max 5 — do not read outside)
- `copilot/procurement/index.html`
- `docs/copilot/PROCUREMENT_ONE_PAGER.md`

## Task
/copilot/procurement/ links /trust/ and sample TLE. ZIP orientation only — no fake buyer logos.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Fake customer logo wall
- ZIP contents invented without samples dir

## Verify
```bash
./scripts/verify-ui-e2e.sh 2>&1 | grep -i procurement || test -f copilot/procurement/index.html
```

## Done when
Procurement page cross-links trust center and sample artifacts.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `copilot/procurement/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-04`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-05 · Design partner scarcity copy

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | Investor |
| W3 signal | Scarcity + investor honesty without fiction |
| Requires | — |
| Unblocks | L-15 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Scarcity + investor honesty without fiction
- **Buyer persona:** Investor
- **Effort:** S · **Mode:** cloud
- **Success reference:** Honest pre-revenue investor pages
- **Buyer proof:** Investor/prospect sees honest scarcity — no fake logos or ARR.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Design partner scarcity copy. Buyer proof: Investor/prospect sees honest scarcity — no fake logos or ARR.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- L-15

## Context budget (max 5 — do not read outside)
- `investors/index.html`
- `copilot/pilot/index.html`
- `docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md §5`

## Task
Verify 'Accepting design partners' on /investors/ and /copilot/pilot/ — no fake logo wall or ARR.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Fake traction metrics
- Customer logos without signed release

## Verify
```bash
grep -F 'Accepting design partners' investors/index.html
```

## Done when
Scarcity copy present; investor disclaimer intact.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `investors/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-05`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-06 · Investor 8-zone category map

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | Investor |
| W3 signal | Scarcity + investor honesty without fiction |
| Requires | L-05 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Scarcity + investor honesty without fiction
- **Buyer persona:** Investor
- **Effort:** S · **Mode:** cloud
- **Success reference:** Category positioning without vendor comparisons
- **Buyer proof:** Investor/prospect sees honest scarcity — no fake logos or ARR.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Investor 8-zone category map. Buyer proof: Investor/prospect sees honest scarcity — no fake logos or ARR.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-05

## Context budget (max 5 — do not read outside)
- `docs/WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md`
- `scripts/rebuild-www-v6.py`

## Task
/investors/ category map: zones only, disclaimer 'not a compare page'. Align WWW v12 master map.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Named third-party vendor columns on public www

## Verify
```bash
grep -i 'not a compare' investors/index.html
```

## Done when
Zone map live without vendor teardown language.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-06`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-07 · QuickScan anchor strip

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | CIO |
| W3 signal | Trust Brief / gate intake path converts |
| Requires | — |
| Unblocks | L-01 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Trust Brief / gate intake path converts
- **Buyer persona:** CIO
- **Effort:** S · **Mode:** cloud
- **Success reference:** Copilot QuickScan entry offer
- **Buyer proof:** Primary CTA routes to Trust Brief intake with traceable RID.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: QuickScan anchor strip. Buyer proof: Primary CTA routes to Trust Brief intake with traceable RID.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- L-01

## Context budget (max 5 — do not read outside)
- `docs/WORKER_BLUEPRINT_V3_NOETFIELD_COM_FULL_PROMPT.md`
- `OFFERINGS_LOCKED.md`

## Task
Copilot QuickScan CAD 2–3.5K strip on /copilot/#quickscan — sub-tier A only per Worker Blueprint V3.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- New SKU tier beyond OFFERINGS_LOCKED

## Verify
```bash
grep -F 'quickscan' copilot/index.html -i
```

## Done when
QuickScan tier visible with fixed-fee band; no fourth SKU.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/WORKER_BLUEPRINT_V3_NOETFIELD_COM_FULL_PROMPT.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-07`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-08 · Intake RID threading

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | Ops |
| W3 signal | Trust Brief / gate intake path converts |
| Requires | L-01 |
| Unblocks | L-14 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Trust Brief / gate intake path converts
- **Buyer persona:** Ops
- **Effort:** S · **Mode:** cloud
- **Success reference:** Ops traceability for design partner pipeline
- **Buyer proof:** Primary CTA routes to Trust Brief intake with traceable RID.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Intake RID threading. Buyer proof: Primary CTA routes to Trust Brief intake with traceable RID.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-01

## Unblocks when done
- L-14

## Context budget (max 5 — do not read outside)
- `assets/noetfield-shell.js`
- `trust-brief/intake/index.html`

## Task
All primary CTAs use data-rid-link; footer RID copy; trust-brief intake mailto includes RID.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Removing RID from primary conversion path

## Verify
```bash
grep -r 'data-rid-link' www trust-brief gate --include='*.html' | head -3
```

## Done when
RID threads from CTA through intake path.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `assets/noetfield-shell.js`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-08`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-09 · Federal ADM deadline chip

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | GRC |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | — |
| Unblocks | H-02, H-04, H-09 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** GRC
- **Effort:** M · **Mode:** cloud
- **Success reference:** TBS ADM orientation without certifier fiction
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Federal ADM deadline chip. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- H-02, H-04, H-09

## Context budget (max 5 — do not read outside)
- `docs/FEDERAL_GOVERNANCE_PACK_v1.md`
- `scripts/rebuild-www-v6.py`

## Task
/federal/ official canada.ca + TBS links above fold; AIA↔TLE preview table; 'not a federal certifier'.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Claiming federal certification authority

## Verify
```bash
grep -F 'canada.ca' federal/index.html
```

## Done when
Federal hub cites official sources; certifier disclaimer visible.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/FEDERAL_GOVERNANCE_PACK_v1.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-09`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-10 · MSP Phase 1→2 diagram

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | MSP |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | — |
| Unblocks | H-01, H-07, H-10 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** MSP
- **Effort:** M · **Mode:** cloud
- **Success reference:** MSP Phase 1 complement positioning
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: MSP Phase 1→2 diagram. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- H-01, H-07, H-10

## Context budget (max 5 — do not read outside)
- `docs/MSP_GOVERNANCE_PACK_v1.md`
- `scripts/rebuild-www-v6.py`

## Task
/msp/ hero Readiness → Record; phase ladder; W3-MSP PASS line.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Phase 1+2 collapsed into single SKU
- Vendor comparison page added

## Verify
```bash
grep -F 'Readiness → Record' msp/index.html
```

## Done when
MSP two-tier RACI visible; no vendor names in Phase 1 copy.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/MSP_GOVERNANCE_PACK_v1.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-10`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-11 · Copilot CCS stack block

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | CIO |
| W3 signal | Public www tells receipt-first wedge story |
| Requires | L-02 |
| Unblocks | E-01 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Public www tells receipt-first wedge story
- **Buyer persona:** CIO
- **Effort:** S · **Mode:** cloud
- **Success reference:** Microsoft stack complement lane
- **Buyer proof:** A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Copilot CCS stack block. Buyer proof: A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-02

## Unblocks when done
- E-01

## Context budget (max 5 — do not read outside)
- `docs/GTM_COPYBOOK.md`
- `scripts/rebuild-www-v6.py`

## Task
/copilot/ stack ladder references Learn.microsoft.com CCS — complement Purview, never replace.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- 'Replace Purview' or anti-Microsoft positioning

## Verify
```bash
grep -F 'learn.microsoft.com' copilot/index.html
```

## Done when
CCS complement ladder on copilot hub.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/GTM_COPYBOOK.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-11`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-12 · FAQ alignment

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | Procurement |
| W3 signal | Public www tells receipt-first wedge story |
| Requires | L-02 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Public www tells receipt-first wedge story
- **Buyer persona:** Procurement
- **Effort:** S · **Mode:** cloud
- **Success reference:** Honest FAQ diligence pattern
- **Buyer proof:** A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: FAQ alignment. Buyer proof: A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-02

## Context budget (max 5 — do not read outside)
- `faq/index.html`
- `scripts/rebuild-www-v6.py`

## Task
/faq/ answers: not Purview replacement, three SKUs, no certifier — sync with homepage §10.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- FAQ contradicts OFFERINGS_LOCKED

## Verify
```bash
grep -i 'purview' faq/index.html
```

## Done when
FAQ matches homepage FAQ themes.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `faq/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-12`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-13 · Enterprise offerings grid

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | CISO |
| W3 signal | Trust Brief / gate intake path converts |
| Requires | — |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Trust Brief / gate intake path converts
- **Buyer persona:** CISO
- **Effort:** S · **Mode:** cloud
- **Success reference:** Enterprise hub clarity
- **Buyer proof:** Primary CTA routes to Trust Brief intake with traceable RID.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Enterprise offerings grid. Buyer proof: Primary CTA routes to Trust Brief intake with traceable RID.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Context budget (max 5 — do not read outside)
- `enterprise/index.html`
- `OFFERINGS_LOCKED.md`

## Task
/enterprise/ uses nf-offerings-v5 three SKUs — retire nf-sku legacy markup.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Bank Pilot presented as payment product

## Verify
```bash
grep -F 'nf-offerings-v5' enterprise/index.html
```

## Done when
Enterprise hub shows three locked SKUs only.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `enterprise/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-13`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-14 · Gate intake vectors

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | Ops |
| W3 signal | Trust Brief / gate intake path converts |
| Requires | L-08 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Trust Brief / gate intake path converts
- **Buyer persona:** Ops
- **Effort:** S · **Mode:** cloud
- **Success reference:** Single intake router
- **Buyer proof:** Primary CTA routes to Trust Brief intake with traceable RID.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Gate intake vectors. Buyer proof: Primary CTA routes to Trust Brief intake with traceable RID.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-08

## Context budget (max 5 — do not read outside)
- `gate/intake/index.html`
- `OFFERINGS_LOCKED.md`

## Task
/gate/intake/ routes Trust Brief, Copilot, Bank Pilot, Partner with interest query params + RID mailto.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- New intake vector without offering lock update

## Verify
```bash
grep -F 'interest=' gate/intake/index.html
```

## Done when
Gate intake covers all commercial vectors.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `gate/intake/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-14`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## L-15 · Design partner outreach batch

| Field | Value |
|-------|-------|
| Phase | LAND |
| Persona | Founder |
| W3 signal | Scarcity + investor honesty without fiction |
| Requires | L-05 |
| Unblocks | E-20 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Scarcity + investor honesty without fiction
- **Buyer persona:** Founder
- **Effort:** M · **Mode:** hub
- **Success reference:** Land design partner pipeline
- **Buyer proof:** Investor/prospect sees honest scarcity — no fake logos or ARR.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Design partner outreach batch. Buyer proof: Investor/prospect sees honest scarcity — no fake logos or ARR.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-05

## Unblocks when done
- E-20

## Context budget (max 5 — do not read outside)
- `docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md`
- `docs/ops/AGENTIC_COMMERCIAL_HANDOFF_v1.md`

## Task
Agentic Hub: outreach batch per DESIGN_PARTNER_SOW_OUTLINE — max 5 contacts. NF-CLOUD: templates on disk only; never send email.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- NF-CLOUD sends email/calendar
- PII committed without consent

## Verify
```bash
test -f docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md
```

## Done when
Outreach templates ready OR Hub logged 5 touches with YAML closeout.

## Self-check (all must be yes)
- [ ] Hub-only: NF-CLOUD must NOT send email/calendar/PII.
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] No vendor compare table or certifier fiction on public www?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done L-15`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-01 · 5-minute demo script lock

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | CISO |
| W3 signal | ≤5 min demo on dev or staging URL |
| Requires | L-11 |
| Unblocks | E-05, E-06, E-07, P-05 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** ≤5 min demo on dev or staging URL
- **Buyer persona:** CISO
- **Effort:** M · **Mode:** cloud
- **Success reference:** Receipt-first demo
- **Buyer proof:** A CISO completes evaluate → TLE → export in ≤5 minutes on demo URL.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: 5-minute demo script lock. Buyer proof: A CISO completes evaluate → TLE → export in ≤5 minutes on demo URL.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-11

## Unblocks when done
- E-05, E-06, E-07, P-05

## Context budget (max 5 — do not read outside)
- `copilot/demo/index.html`
- `docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md §4`
- `scripts/verify-ui-e2e.sh`

## Task
Lock copilot/demo narrative: evaluate → confidence → Purview/Entra/audit → TLE → export. Workspace mock in hero. Demo ≤5 min on dev stack.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Demo requires production M365 secrets
- Scope expands beyond metadata-only

## Verify
```bash
./scripts/verify-ui-e2e.sh 2>&1 | grep -i demo || test -f copilot/demo/index.html
```

## Done when
Demo script documented and e2e row passes or demo page complete.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `copilot/demo/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-01`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-02 · TLE verify walkthrough

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | GRC |
| W3 signal | TLE samples + verify path credible |
| Requires | L-03 |
| Unblocks | E-03 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** TLE samples + verify path credible
- **Buyer persona:** GRC
- **Effort:** M · **Mode:** cloud
- **Success reference:** Export verify walkthrough
- **Buyer proof:** Sample TLE + verify page prove fail-closed export integrity.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: TLE verify walkthrough. Buyer proof: Sample TLE + verify page prove fail-closed export integrity.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-03

## Unblocks when done
- E-03

## Context budget (max 5 — do not read outside)
- `trust-ledger/verify/index.html`
- `PRODUCT_TRUTH.md`

## Task
/trust-ledger/verify/ documents tamper FAIL path. Link from /trust/ and samples. No Ed25519 claim until shipped.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Claiming crypto not in PRODUCT_TRUTH

## Verify
```bash
grep -i 'tamper\|fail' trust-ledger/verify/index.html
```

## Done when
Verify page explains fail-closed export check.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `trust-ledger/verify/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-02`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-03 · TLE YAML samples trio

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Procurement |
| W3 signal | TLE samples + verify path credible |
| Requires | E-02 |
| Unblocks | E-04, L-04 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** TLE samples + verify path credible
- **Buyer persona:** Procurement
- **Effort:** M · **Mode:** cloud
- **Success reference:** Procurement-ready sample pack
- **Buyer proof:** Sample TLE + verify page prove fail-closed export integrity.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: TLE YAML samples trio. Buyer proof: Sample TLE + verify page prove fail-closed export integrity.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: E-02

## Unblocks when done
- E-04, L-04

## Context budget (max 5 — do not read outside)
- `trust-ledger/samples/`
- `docs/spec/examples/`

## Task
samples: go, conditional, rejected + README for procurement. Optional tampered fail example.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Inventing customer-specific TLE content

## Verify
```bash
ls samples/tle/*.yaml 2>/dev/null | wc -l | grep -qv '^0$' || ls trust-ledger/samples/ 2>/dev/null
```

## Done when
Three verdict samples + README exist for diligence.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `trust-ledger/samples/`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-03`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-04 · Export manifest JSON spec

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Engineering |
| W3 signal | Board PDF + procurement ZIP reachable in product |
| Requires | E-03 |
| Unblocks | E-05, E-06 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Board PDF + procurement ZIP reachable in product
- **Buyer persona:** Engineering
- **Effort:** S · **Mode:** cloud
- **Success reference:** Evidence manifest clarity
- **Buyer proof:** A GRC lead can download a board PDF or procurement ZIP from a real TLE path.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Export manifest JSON spec. Buyer proof: A GRC lead can download a board PDF or procurement ZIP from a real TLE path.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: E-03

## Unblocks when done
- E-05, E-06

## Context budget (max 5 — do not read outside)
- `docs/api/index.html`
- `docs/spec/`

## Task
Document sidecar manifest: tle_id, export_integrity, hashes — docs/api or trust-ledger.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- New API route without pilot need

## Verify
```bash
grep -i 'export_integrity' docs/api/index.html trust-ledger/index.html 2>/dev/null | head -1
```

## Done when
Manifest fields documented for integrators.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] Export path is real product/workspace — not a static fake link?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/api/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-04`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-05 · Board PDF path E2E

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | GRC |
| W3 signal | Board PDF + procurement ZIP reachable in product |
| Requires | E-01, E-04 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Board PDF + procurement ZIP reachable in product
- **Buyer persona:** GRC
- **Effort:** L · **Mode:** cloud
- **Success reference:** Board PDF in governance meeting — W3 bar
- **Buyer proof:** A GRC lead can download a board PDF or procurement ZIP from a real TLE path.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Board PDF path E2E. Buyer proof: A GRC lead can download a board PDF or procurement ZIP from a real TLE path.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: E-01, E-04

## Context budget (max 5 — do not read outside)
- `scripts/verify-ui-e2e.sh`
- `workspace/`
- `services/`

## Task
Workspace TLE detail exposes Board pack (PDF). verify-ui-e2e dashboard chunk asserts link.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- PDF generation requires founder-only prod keys
- Fake PDF without export pipeline

## Verify
```bash
./scripts/verify-ui-e2e.sh 2>&1 | grep -i 'board\|pdf' || echo 'run full e2e with dev stack'
```

## Done when
Board PDF export reachable from workspace TLE detail — **W3 critical path**.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] Export path is real product/workspace — not a static fake link?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/verify-ui-e2e.sh`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-05`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-06 · Procurement ZIP path E2E

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Procurement |
| W3 signal | Board PDF + procurement ZIP reachable in product |
| Requires | E-01, E-04 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Board PDF + procurement ZIP reachable in product
- **Buyer persona:** Procurement
- **Effort:** L · **Mode:** cloud
- **Success reference:** Diligence ZIP path
- **Buyer proof:** A GRC lead can download a board PDF or procurement ZIP from a real TLE path.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Procurement ZIP path E2E. Buyer proof: A GRC lead can download a board PDF or procurement ZIP from a real TLE path.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: E-01, E-04

## Context budget (max 5 — do not read outside)
- `scripts/verify-ui-e2e.sh`
- `Makefile`

## Task
Workspace TLE detail exposes Procurement pack (ZIP). Same e2e coverage as board PDF.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- ZIP contents not tied to real export service

## Verify
```bash
./scripts/verify-ui-e2e.sh 2>&1 | grep -i 'procurement\|zip' || make procurement-pack-e2e
```

## Done when
Procurement ZIP export reachable — **W3 critical path**.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?
- [ ] Export path is real product/workspace — not a static fake link?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/verify-ui-e2e.sh`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-06`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-07 · Confidence score on result page

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | CISO |
| W3 signal | Evaluate → result → workspace exports |
| Requires | E-01 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Evaluate → result → workspace exports
- **Buyer persona:** CISO
- **Effort:** S · **Mode:** cloud
- **Success reference:** Evaluate loop buyer clarity
- **Buyer proof:** Product loop shows confidence score and export links on TLE detail.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Confidence score on result page. Buyer proof: Product loop shows confidence score and export links on TLE detail.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: E-01

## Context budget (max 5 — do not read outside)
- `scripts/verify-ui-e2e.sh`
- `result/`

## Task
/evaluate → /result/{rid} shows Confidence score badge — fix if regressed.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Changing score algorithm without spec update

## Verify
```bash
grep -ri 'confidence' result/ evaluate/ workspace/ --include='*.html' 2>/dev/null | head -1
```

## Done when
Confidence visible on result flow.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/verify-ui-e2e.sh`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-07`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-08 · M365 connector mock OAuth

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | CIO |
| W3 signal | Evaluate → result → workspace exports |
| Requires | — |
| Unblocks | E-01 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Evaluate → result → workspace exports
- **Buyer persona:** CIO
- **Effort:** M · **Mode:** cloud
- **Success reference:** Metadata-only M365 path
- **Buyer proof:** Product loop shows confidence score and export links on TLE detail.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: M365 connector mock OAuth. Buyer proof: Product loop shows confidence score and export links on TLE detail.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- E-01

## Context budget (max 5 — do not read outside)
- `workspace/connectors/`
- `scripts/verify-ui-e2e.sh`

## Task
/workspace/connectors mock OAuth → workspace banner. e2e green.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Real Azure AD secrets in repo
- OAuth to production without customer

## Verify
```bash
./scripts/verify-ui-e2e.sh 2>&1 | grep -i connector || test -d workspace/connectors
```

## Done when
Mock connector flow completes without real tenant.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `workspace/connectors/`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-08`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-09 · API decision semantics

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Engineering |
| W3 signal | TLE samples + verify path credible |
| Requires | — |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** TLE samples + verify path credible
- **Buyer persona:** Engineering
- **Effort:** S · **Mode:** cloud
- **Success reference:** Clear API contract orientation
- **Buyer proof:** Sample TLE + verify page prove fail-closed export integrity.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: API decision semantics. Buyer proof: Sample TLE + verify page prove fail-closed export integrity.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Context budget (max 5 — do not read outside)
- `docs/api/index.html`

## Task
docs/api/index.html: allow≈201, review≈202, deny≈403 orientation paragraph.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- OpenAPI drift without implementation check

## Verify
```bash
grep -E '201|202|403' docs/api/index.html
```

## Done when
HTTP semantics documented for integrators.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/api/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-09`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-10 · Governance console deep link

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | CISO |
| W3 signal | Evaluate → result → workspace exports |
| Requires | — |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Evaluate → result → workspace exports
- **Buyer persona:** CISO
- **Effort:** S · **Mode:** cloud
- **Success reference:** Read-only governance console
- **Buyer proof:** Product loop shows confidence score and export links on TLE detail.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Governance console deep link. Buyer proof: Product loop shows confidence score and export links on TLE detail.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Context budget (max 5 — do not read outside)
- `console/index.html`

## Task
/console/ primary CTA resolves to pilot host; shadow mode copy correct.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Console claims execution rights Noetfield lacks

## Verify
```bash
grep -i 'shadow' console/index.html
```

## Done when
Console CTA and shadow copy accurate.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `console/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-10`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-11 · Copilot pilot success signals

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | CISO |
| W3 signal | Scarcity + investor honesty without fiction |
| Requires | L-05 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Scarcity + investor honesty without fiction
- **Buyer persona:** CISO
- **Effort:** S · **Mode:** cloud
- **Success reference:** 90-day design partner path
- **Buyer proof:** Investor/prospect sees honest scarcity — no fake logos or ARR.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Copilot pilot success signals. Buyer proof: Investor/prospect sees honest scarcity — no fake logos or ARR.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-05

## Context budget (max 5 — do not read outside)
- `copilot/pilot/index.html`
- `docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md §5`

## Task
/copilot/pilot/ lists Wk 0–12 path aligned with commercial SSOT §90-day.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Timeline promises without SOW alignment

## Verify
```bash
grep -i 'week' copilot/pilot/index.html
```

## Done when
Pilot timeline matches design partner program.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `copilot/pilot/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-11`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-12 · Trust Ledger hub

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | GRC |
| W3 signal | TLE samples + verify path credible |
| Requires | E-02 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** TLE samples + verify path credible
- **Buyer persona:** GRC
- **Effort:** S · **Mode:** cloud
- **Success reference:** TLE product hub
- **Buyer proof:** Sample TLE + verify page prove fail-closed export integrity.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Trust Ledger hub. Buyer proof: Sample TLE + verify page prove fail-closed export integrity.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: E-02

## Context budget (max 5 — do not read outside)
- `trust-ledger/index.html`

## Task
/trust-ledger/ links workspace + samples + verify.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- TLE SaaS checkout added

## Verify
```bash
grep -i 'verify\|sample' trust-ledger/index.html
```

## Done when
TLE hub is single spine for product + docs.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `trust-ledger/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-12`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-13 · Bank Pilot shadow scope

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | CISO |
| W3 signal | Trust Brief / gate intake path converts |
| Requires | — |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Trust Brief / gate intake path converts
- **Buyer persona:** CISO
- **Effort:** S · **Mode:** cloud
- **Success reference:** Shadow simulation positioning
- **Buyer proof:** Primary CTA routes to Trust Brief intake with traceable RID.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Bank Pilot shadow scope. Buyer proof: Primary CTA routes to Trust Brief intake with traceable RID.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Context budget (max 5 — do not read outside)
- `bank-pilot/index.html`
- `OFFERINGS_LOCKED.md`

## Task
/bank-pilot/ read-only, no custody — OFFERINGS_LOCKED alignment.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Payment/custody claims on Noetfield www

## Verify
```bash
grep -i 'read-only\|no custody' bank-pilot/index.html enterprise/index.html 2>/dev/null | head -1
```

## Done when
Bank pilot scope honest on www.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `bank-pilot/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-13`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-14 · SME pack lane

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | GRC |
| W3 signal | Trust Brief / gate intake path converts |
| Requires | — |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Trust Brief / gate intake path converts
- **Buyer persona:** GRC
- **Effort:** S · **Mode:** cloud
- **Success reference:** SME provider grade pack
- **Buyer proof:** Primary CTA routes to Trust Brief intake with traceable RID.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: SME pack lane. Buyer proof: Primary CTA routes to Trust Brief intake with traceable RID.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Context budget (max 5 — do not read outside)
- `copilot/sme/index.html`
- `docs/strategy/NOETFIELD_SME_PROVIDER_BLUEPRINT_LOCKED_v1.md`

## Task
/copilot/sme/ same TLE spine, SME pricing orientation — no enterprise platform claims.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Full GRC platform breadth claims

## Verify
```bash
test -f copilot/sme/index.html
```

## Done when
SME lane live with governance-first copy.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `copilot/sme/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-14`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-15 · Receipt mock consistency

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Design |
| W3 signal | Public www tells receipt-first wedge story |
| Requires | L-02 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Public www tells receipt-first wedge story
- **Buyer persona:** Design
- **Effort:** S · **Mode:** cloud
- **Success reference:** Receipt visual consistency
- **Buyer proof:** A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Receipt mock consistency. Buyer proof: A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-02

## Context budget (max 5 — do not read outside)
- `scripts/rebuild-www-v6.py`

## Task
All GTM hubs: nf-receipt-mock with export_integrity PASS via generator receipt() helper.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Hand-editing receipt HTML per page

## Verify
```bash
grep -r 'export_integrity' --include='*.html' copilot trust-brief federal msp 2>/dev/null | head -3
```

## Done when
Receipt mocks consistent across hubs.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/rebuild-www-v6.py`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-15`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-16 · Stat bar consistency

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Design |
| W3 signal | Public www tells receipt-first wedge story |
| Requires | — |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Public www tells receipt-first wedge story
- **Buyer persona:** Design
- **Effort:** S · **Mode:** cloud
- **Success reference:** Honest metrics bar
- **Buyer proof:** A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Stat bar consistency. Buyer proof: A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Context budget (max 5 — do not read outside)
- `scripts/rebuild-www-v6.py`
- `index.html`

## Task
Homepage stat bar: 4 · $10k · 90d · 3 SKUs — no fake analyst stats.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Third-party analyst stats without citation

## Verify
```bash
grep -F '90' index.html | head -1
```

## Done when
Stat bar matches commercial facts.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/rebuild-www-v6.py`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-16`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-17 · Mega CTA every hub

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Design |
| W3 signal | Trust Brief / gate intake path converts |
| Requires | — |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Trust Brief / gate intake path converts
- **Buyer persona:** Design
- **Effort:** S · **Mode:** cloud
- **Success reference:** Conversion spine
- **Buyer proof:** Primary CTA routes to Trust Brief intake with traceable RID.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Mega CTA every hub. Buyer proof: Primary CTA routes to Trust Brief intake with traceable RID.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Context budget (max 5 — do not read outside)
- `scripts/rebuild-www-v6.py`

## Task
Every hub ends nf-cta-mega — Request Governance Brief + secondary.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- CTA points off-domain without approval

## Verify
```bash
grep -r 'nf-cta-mega' --include='*.html' copilot federal msp enterprise trust-brief 2>/dev/null | wc -l
```

## Done when
Mega CTA on all primary hubs.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/rebuild-www-v6.py`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-17`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-18 · Shell v13 bump

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Ops |
| W3 signal | verify-gtm / e2e green after change |
| Requires | — |
| Unblocks | P-01 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** verify-gtm / e2e green after change
- **Buyer persona:** Ops
- **Effort:** S · **Mode:** cloud
- **Success reference:** Cache-coherent deploy
- **Buyer proof:** verify-gtm green — ship confidence for founder demo/outreach.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Shell v13 bump. Buyer proof: verify-gtm green — ship confidence for founder demo/outreach.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- P-01

## Context budget (max 5 — do not read outside)
- `assets/noetfield-shell.js`
- `scripts/rebuild-www-v6.py`

## Task
SHELL_VERSION and ?v=13 on all regenerated pages after www changes.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Partial bump leaving cache stale on key hubs

## Verify
```bash
grep 'SHELL_VERSION' assets/noetfield-shell.js && ./scripts/verify-static-www.sh
```

## Done when
Shell version bumped coherently.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `assets/noetfield-shell.js`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-18`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-19 · Honest scope badges every hub

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Procurement |
| W3 signal | Procurement can diligence without call |
| Requires | L-03 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Procurement can diligence without call
- **Buyer persona:** Procurement
- **Effort:** S · **Mode:** cloud
- **Success reference:** Honest scope tables
- **Buyer proof:** Procurement finds honest scope table + samples without a sales call.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Honest scope badges every hub. Buyer proof: Procurement finds honest scope table + samples without a sales call.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-03

## Context budget (max 5 — do not read outside)
- `scripts/rebuild-www-v6.py`
- `docs/DESIGN_REFERENCE_GOALS_LOCKED_v1.md`

## Task
scope_block() on hubs: Shipped/Orientation/Roadmap/N/A — no certifier rows as Shipped.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Marking roadmap items as shipped

## Verify
```bash
grep -r 'Shipped\|Orientation' --include='*.html' copilot federal msp 2>/dev/null | head -3
```

## Done when
Scope badges honest on hubs.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/rebuild-www-v6.py`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-19`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## E-20 · Buyer debrief after call

| Field | Value |
|-------|-------|
| Phase | EXPAND |
| Persona | Founder |
| W3 signal | Scarcity + investor honesty without fiction |
| Requires | L-15 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Scarcity + investor honesty without fiction
- **Buyer persona:** Founder
- **Effort:** S · **Mode:** hub
- **Success reference:** Pipeline intelligence capture
- **Buyer proof:** Investor/prospect sees honest scarcity — no fake logos or ARR.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Buyer debrief after call. Buyer proof: Investor/prospect sees honest scarcity — no fake logos or ARR.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-15

## Context budget (max 5 — do not read outside)
- `docs/copilot/DESIGN_PARTNER_PIPELINE_v1.md`

## Task
After CIO call: debrief YAML — pain, Copilot timeline, next step Trust Brief vs pilot. Cloud stores template only.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Customer PII in committed debrief without redaction

## Verify
```bash
mkdir -p docs/copilot/debriefs && test -d docs/copilot/debriefs
```

## Done when
Debrief template or one sanitized example on disk.

## Self-check (all must be yes)
- [ ] Hub-only: NF-CLOUD must NOT send email/calendar/PII.
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/copilot/DESIGN_PARTNER_PIPELINE_v1.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done E-20`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-01 · MSP READINESS→RECORD mapping UX

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | MSP |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | L-10 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** MSP
- **Effort:** S · **Mode:** cloud
- **Success reference:** Two-tier MSP attach
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: MSP READINESS→RECORD mapping UX. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-10

## Context budget (max 5 — do not read outside)
- `msp/index.html`
- `docs/msp/`

## Task
/msp/ links READINESS_TO_RECORD_MAPPING_v1.md; partner intake CTA.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- MSP page claims Phase 1 execution for Noetfield

## Verify
```bash
grep -i 'READINESS\|mapping' msp/index.html docs/msp/*.md 2>/dev/null | head -1
```

## Done when
MSP mapping doc linked from hub.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `msp/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-01`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-02 · Federal AIA mapping doc link

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | GRC |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | L-09 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** GRC
- **Effort:** S · **Mode:** cloud
- **Success reference:** GC AIA attach
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Federal AIA mapping doc link. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-09

## Context budget (max 5 — do not read outside)
- `federal/index.html`
- `docs/federal/`

## Task
Prominent AIA_TLE_MAPPING_v1.md link from federal proof grid.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Claiming AIA certification

## Verify
```bash
grep -i 'AIA' federal/index.html
```

## Done when
AIA mapping accessible from federal hub.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `federal/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-02`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-03 · Partner gateway

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | MSP |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | — |
| Unblocks | H-06 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** MSP
- **Effort:** S · **Mode:** cloud
- **Success reference:** Partner entry point
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Partner gateway. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- H-06

## Context budget (max 5 — do not read outside)
- `partners/index.html`

## Task
/partners/ API + MSP links; no MSB as primary hero.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- MSB hero on Noetfield partners page

## Verify
```bash
test -f partners/index.html && grep -vi 'MSB' partners/index.html | head -1
```

## Done when
Partner gateway orients MSP/API — not payments.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `partners/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-03`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-04 · GC Copilot PIN checklist

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | GRC |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | L-09 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** GRC
- **Effort:** S · **Mode:** cloud
- **Success reference:** GC Copilot readiness
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: GC Copilot PIN checklist. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-09

## Context budget (max 5 — do not read outside)
- `federal/index.html`
- `docs/federal/`

## Task
PIN checklist doc linked from federal; scope badges in hero.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Verify
```bash
grep -i 'PIN\|checklist' federal/index.html docs/federal/ 2>/dev/null | head -1
```

## Done when
PIN checklist discoverable from federal hub.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `federal/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-04`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-05 · NIST strip on procurement

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | Procurement |
| W3 signal | Procurement can diligence without call |
| Requires | L-04 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Procurement can diligence without call
- **Buyer persona:** Procurement
- **Effort:** S · **Mode:** cloud
- **Success reference:** Framework citation discipline
- **Buyer proof:** Procurement finds honest scope table + samples without a sales call.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: NIST strip on procurement. Buyer proof: Procurement finds honest scope table + samples without a sales call.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-04

## Context budget (max 5 — do not read outside)
- `docs/reference/GOVERNANCE_SOURCES_BOOK_v1.md`

## Task
Procurement ZIP citations mention NIST AI RMF — orientation only.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Claiming NIST certification

## Verify
```bash
grep -i 'NIST' copilot/procurement/index.html docs/copilot/PROCUREMENT_ONE_PAGER.md 2>/dev/null | head -1
```

## Done when
NIST orientation in procurement copy.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/reference/GOVERNANCE_SOURCES_BOOK_v1.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-05`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-06 · Partner LOI template

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | MSP |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | H-03 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** MSP
- **Effort:** S · **Mode:** cloud
- **Success reference:** Partner LOI orientation
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Partner LOI template. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: H-03

## Context budget (max 5 — do not read outside)
- `docs/msp/`
- `docs/partners/`

## Task
docs/msp/ or docs/partners/ LOI orientation — not legal advice.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Presenting template as legal counsel

## Verify
```bash
ls docs/msp/*LOI* docs/partners/*LOI* 2>/dev/null | head -1
```

## Done when
LOI orientation doc exists.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/msp/`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-06`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-07 · Wholesale pricing orientation

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | MSP |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | L-10 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** MSP
- **Effort:** S · **Mode:** cloud
- **Success reference:** MSP wholesale clarity
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Wholesale pricing orientation. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-10

## Context budget (max 5 — do not read outside)
- `msp/index.html`
- `OFFERINGS_LOCKED.md`

## Task
MSP Governance Pack $2k–10k via partner — one paragraph on /msp/.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Pricing outside OFFERINGS_LOCKED bands

## Verify
```bash
grep -E '2[, ]?000|10[, ]?000' msp/index.html
```

## Done when
Wholesale band visible on MSP hub.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `msp/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-07`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-08 · Phase 1 complement copy

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | MSP |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | L-10 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** MSP
- **Effort:** S · **Mode:** cloud
- **Success reference:** Generic Phase 1 complement
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Phase 1 complement copy. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-10

## Context budget (max 5 — do not read outside)
- `msp/index.html`

## Task
MSP page: Phase 1 examples generic — no third-party vendor names.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Named third-party vendor on public MSP page

## Verify
```bash
grep -i 'phase 1' msp/index.html
```

## Done when
Phase 1 complement copy without vendor teardown.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `msp/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-08`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-09 · Federal intake query param

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | GRC |
| W3 signal | Trust Brief / gate intake path converts |
| Requires | L-09, L-14 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** Trust Brief / gate intake path converts
- **Buyer persona:** GRC
- **Effort:** S · **Mode:** cloud
- **Success reference:** Federal intake vector
- **Buyer proof:** Primary CTA routes to Trust Brief intake with traceable RID.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Federal intake query param. Buyer proof: Primary CTA routes to Trust Brief intake with traceable RID.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-09, L-14

## Context budget (max 5 — do not read outside)
- `federal/index.html`
- `trust-brief/intake/index.html`

## Task
/trust-brief/intake/?interest=federal linked from federal hub.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Verify
```bash
grep -F 'interest=federal' federal/index.html trust-brief/intake/index.html 2>/dev/null | head -1
```

## Done when
Federal interest param wired.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `federal/index.html`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-09`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## H-10 · MSP partner conversation script

| Field | Value |
|-------|-------|
| Phase | CHANNEL |
| Persona | Founder |
| W3 signal | MSP or federal Phase 2 narrative |
| Requires | L-10 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** MSP or federal Phase 2 narrative
- **Buyer persona:** Founder
- **Effort:** S · **Mode:** hub
- **Success reference:** MSP channel playbook
- **Buyer proof:** MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: MSP partner conversation script. Buyer proof: MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-10

## Context budget (max 5 — do not read outside)
- `docs/MSP_GOVERNANCE_PACK_v1.md`

## Task
Hub: first MSP partner call script — Phase 2 attach after readiness vendor.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- NF-CLOUD places partner calls

## Verify
```bash
test -f docs/msp/ || mkdir -p docs/msp
```

## Done when
MSP call script on disk for Hub use.

## Self-check (all must be yes)
- [ ] Hub-only: NF-CLOUD must NOT send email/calendar/PII.
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `docs/MSP_GOVERNANCE_PACK_v1.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done H-10`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## P-01 · verify-ui-e2e www v12

| Field | Value |
|-------|-------|
| Phase | PROVE |
| Persona | Ops |
| W3 signal | verify-gtm / e2e green after change |
| Requires | L-02, E-18 |
| Unblocks | P-03 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** verify-gtm / e2e green after change
- **Buyer persona:** Ops
- **Effort:** M · **Mode:** cloud
- **Success reference:** Receipt-first www proof
- **Buyer proof:** verify-gtm green — ship confidence for founder demo/outreach.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: verify-ui-e2e www v12. Buyer proof: verify-gtm green — ship confidence for founder demo/outreach.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: L-02, E-18

## Unblocks when done
- P-03

## Context budget (max 5 — do not read outside)
- `scripts/verify-ui-e2e.sh`

## Task
Extend and run verify-ui-e2e.sh for §07–10, /trust/, federal, msp, copilot CCS rows.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Fixing e2e by weakening assertions

## Verify
```bash
./scripts/verify-ui-e2e.sh
```

## Done when
Static www v12 e2e rows green.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/verify-ui-e2e.sh`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done P-01`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## P-02 · rebuild-www-v6 single source

| Field | Value |
|-------|-------|
| Phase | PROVE |
| Persona | Ops |
| W3 signal | verify-gtm / e2e green after change |
| Requires | — |
| Unblocks | P-01 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** verify-gtm / e2e green after change
- **Buyer persona:** Ops
- **Effort:** S · **Mode:** cloud
- **Success reference:** Single www SSOT
- **Buyer proof:** verify-gtm green — ship confidence for founder demo/outreach.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: rebuild-www-v6 single source. Buyer proof: verify-gtm green — ship confidence for founder demo/outreach.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Unblocks when done
- P-01

## Context budget (max 5 — do not read outside)
- `scripts/rebuild-www-v6.py`

## Task
Hand-edited GTM HTML forbidden — generator only. Migrate stragglers into rebuild-www-v6.py.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Large unrelated refactor in generator

## Verify
```bash
python3 scripts/rebuild-www-v6.py && git diff --stat | head -5
```

## Done when
GTM pages regenerate cleanly from generator.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/rebuild-www-v6.py`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done P-02`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## P-03 · plan-with-no-asf-verify

| Field | Value |
|-------|-------|
| Phase | PROVE |
| Persona | Ops |
| W3 signal | verify-gtm / e2e green after change |
| Requires | P-01 |
| Unblocks | P-04 |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** verify-gtm / e2e green after change
- **Buyer persona:** Ops
- **Effort:** S · **Mode:** cloud
- **Success reference:** Ship gate green
- **Buyer proof:** verify-gtm green — ship confidence for founder demo/outreach.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: plan-with-no-asf-verify. Buyer proof: verify-gtm green — ship confidence for founder demo/outreach.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: P-01

## Unblocks when done
- P-04

## Context budget (max 5 — do not read outside)
- `scripts/plan-with-no-asf-verify.sh`

## Task
./scripts/plan-with-no-asf-verify.sh green after ship.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Skipping verify to ship faster

## Verify
```bash
./scripts/plan-with-no-asf-verify.sh
```

## Done when
Plan verify bundle passes.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/plan-with-no-asf-verify.sh`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done P-03`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## P-04 · sync-prompt-pack-status

| Field | Value |
|-------|-------|
| Phase | PROVE |
| Persona | Ops |
| W3 signal | verify-gtm / e2e green after change |
| Requires | — |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** verify-gtm / e2e green after change
- **Buyer persona:** Ops
- **Effort:** S · **Mode:** cloud
- **Success reference:** Ops hygiene
- **Buyer proof:** verify-gtm green — ship confidence for founder demo/outreach.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: sync-prompt-pack-status. Buyer proof: verify-gtm green — ship confidence for founder demo/outreach.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Context budget (max 5 — do not read outside)
- `scripts/sync-prompt-pack-status.py`
- `docs/ops/plans/tier1-status.json`

## Task
After done prompts: sync registry + QUICK_PICK + tier1-status.json.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Verify
```bash
python3 scripts/sync-tier1-status.py --dry-run 2>/dev/null || python3 scripts/sync-prompt-pack-status.py
```

## Done when
Status files reflect completed Tier 1 ids.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `scripts/sync-prompt-pack-status.py`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done P-04`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched

---

## P-05 · Staging smoke / demo URL

| Field | Value |
|-------|-------|
| Phase | PROVE |
| Persona | Ops |
| W3 signal | ≤5 min demo on dev or staging URL |
| Requires | E-01 |
| Unblocks | — |

## Role
NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.

## WISE frame
| Step | Rule |
|------|------|
| **W**itness | Repo state + deps before edits |
| **I**ntent | One buyer-visible outcome |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify command + self-check |

## Context
- **W3 signal:** ≤5 min demo on dev or staging URL
- **Buyer persona:** Ops
- **Effort:** M · **Mode:** cloud
- **Success reference:** Week 0–2 commercial SSOT milestone
- **Buyer proof:** A CISO completes evaluate → TLE → export in ≤5 minutes on demo URL.

## Reasoning (follow in order)
1. **Witness** — Read context budget only; check tier1-status.json for dependencies.
2. **Intent** — One artifact: Staging smoke / demo URL. Buyer proof: A CISO completes evaluate → TLE → export in ≤5 minutes on demo URL.…
3. **Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.
4. **Evidence** — Run verify command; if fail, recovery path below — do not widen scope.

## Preflight
- Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only
- Read `docs/ops/plans/tier1-status.json` — confirm dependencies done
- Confirm ≤3 tasks this session (GTM 60-day lock)

## Dependencies
- Requires **done** in tier1-status: E-01

## Context budget (max 5 — do not read outside)
- `os/SHIP_NOW.md`
- `Makefile`

## Task
Public demo URL documented in os/SHIP_NOW when staging live.

## Forbidden
- vendor comparison pages
- fourth SKU or Trust Ledger SaaS checkout
- fake certs, logos, ARR, or analyst firm stats
- MSB/payment/custody as Noetfield www lead
- TrustField/VIRLUX product build scope
- hand-editing GTM HTML outside rebuild-www-v6.py

## Stop and ask founder if
- Deploying prod without founder approval

## Verify
```bash
grep -i 'demo\|13081\|staging' os/SHIP_NOW.md | head -3
```

## Done when
Demo URL in SHIP_NOW for founder outreach.

## Self-check (all must be yes)
- [ ] Does this help W3 (board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Did I stay within 5-file context budget and three-SKU lock?
- [ ] Verify command passed without weakening assertions?

## Recovery if verify fails
If verify fails: (1) read error output, (2) fix smallest diff in `os/SHIP_NOW.md`, (3) re-run verify once. If still blocked → stop_if triggers → ask founder. Do NOT pick Tier 2 or archive prompts to 'work around' this task.

## Closeout
1. `python3 scripts/sync-tier1-status.py --done P-05`
2. `reports/cursor-reply-latest.txt` with verify output
3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched
