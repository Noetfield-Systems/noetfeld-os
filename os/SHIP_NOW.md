# SHIP NOW — Noetfield

**Ship rule:** Bounded founder `implement` + [GTM_NEXT.md](docs/ops/plans/no-asf/GTM_NEXT.md) queue — see `os/plan.json` `ship_rule`. Ingest required after VERIFY. No self-start (R-007/R-011).

## Active queue (`next_tasks`)

**Next iter 17:** see [GTM_NEXT.md](docs/ops/plans/no-asf/GTM_NEXT.md) (services bridge, procurement checkpoint copy, merged PR window 5).

**Shipped iter 16 (2026-06-10):** blueprint governance-console bridge, rehearsal parity loop, rolling merged PR window.

**Shipped seventh audit (PR #45 @ 80ad8a7):** iter 15 on main.

**Shipped sixth audit (PR #44 @ c2543b5):** iter 14 on main.

**Shipped iter 15 (2026-06-10):** trust-brief parity loop, merged PR gate, demo rehearsal in script ol.

**Shipped iter 14 (2026-06-10):** demo trust-brief CTA, pilot checklist rehearsal, OPEN_PRS autocheck.

**Shipped fifth audit (PR #43 @ 9f0e3f7):** iter 13 on main.

**Shipped iter 13 (2026-06-10):** pilot trust-brief CTA, homepage procurement verify guard, cursor-reply coherence FAIL gate.

**Shipped fourth audit (PR #42 @ 43715a4):** third-audit workflow + iter 12 on main.

**Shipped iter 12 (2026-06-10):** trust-brief on procurement, drift blueprints index on procurement, demo-url verify guard.

**Shipped iter 11 (2026-06-10):** trust-brief hub CTA verify, drift sources on procurement, demo rehearsal on hub.

**Shipped post-audit + 10-phase audit:** R-011 agentic law, workflow reconcile, www 030–032, coherence verify.

**Shipped iter 9 (2026-06-06):** procurement one-pager www wire, governance sources href, homepage demo CTA verify.

**Prior iter 8:** GTM_NEXT queue + QUICK_PICK fallback, staging demo www wire, security-buyer TLE copy.

**Prior iter 7:** registry pattern propagation + QUICK_PICK dedup, diligence procurement wire, design-partner BC AI channel.

**Prior iter 6:** registry sync + QUICK_PICK refresh, BC AI www wire, dual-brand boundary matrix.

**Queue:** Registry is fully synced — pick from [GTM_NEXT.md](docs/ops/plans/no-asf/GTM_NEXT.md) or `next_tasks` below. [QUICK_PICK.md](docs/ops/plans/no-asf/QUICK_PICK.md) inlines GTM_NEXT when registry backlog is empty.

## Active commercial P0 (agentic — Hub only)

| ID | Owner | Handoff |
|----|-------|---------|
| **ship-design-partner-outreach-026** | Agentic layer | [AGENTIC_COMMERCIAL_HANDOFF_v1.md](docs/ops/AGENTIC_COMMERCIAL_HANDOFF_v1.md) |

NF-CLOUD ships pipeline **copy** on disk; founder Hub approves send. See R-011 + `os/plan.json` `agentic_queue`.

## NO ASF closeout cadence

1. Merge ship PR to `main` (if open)
2. Founder **`implement`** → bounded ≤3 tasks
3. `./scripts/plan-with-no-asf-verify.sh` (includes `verify-no-asf-coherence.sh`)
4. `python3 scripts/sync-prompt-pack-status.py`
5. `reports/cursor-reply-latest.txt`
6. **ASK** founder next move (Hub ingest = agentic layer)

## Shipped waves

| Wave | IDs | Highlights |
|------|-----|------------|
| 040–042 | Customer acquisition | design partner SOW, copilot hub, homepage CTA |
| 037–039 | GTM demo polish | buyer pack, workspace confidence UX, `make verify-gtm` |
| 034–036 | GTM Tier A | procurement zip, 5-min demo page, `make demo-url` |
| 023–033 | pilot → alembic | Trust Ledger product waves |
| **Locks** | GTM + sources book | `docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md`, `docs/references/GOVERNANCE_SOURCES_BOOK_v1.md` |

## Agent references

| Doc | Path |
|-----|------|
| Governance Sources Book | `docs/references/GOVERNANCE_SOURCES_BOOK_v1.md` |
| Governance Sources Handbook | `docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md` |
| Governance Drift Detection | `docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md` |
| GTM 60-day (CEO) | `docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md` |
| Agentic commercial law | `docs/ops/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` |

## Verify

```bash
./scripts/plan-with-no-asf-verify.sh
```

Or step-by-step:

```bash
make verify-gtm
make dev-local && make verify-local-dev && make tle-smoke && make copilot-pilot-e2e
pytest governance-console/backend/tests/test_tle_flow.py -q
```
