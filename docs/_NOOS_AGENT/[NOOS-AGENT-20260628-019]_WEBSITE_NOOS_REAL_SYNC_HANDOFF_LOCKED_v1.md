<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260628-019
doc_type: CROSS_REPO_SYNC_HANDOFF_LOCKED
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL
related_code: docs/_NOOS_AGENT/PRODUCT_TRUTH.md, docs/_NOOS_AGENT/NOETFIELD_OS_SSOT_v1_LOCKED.md
-->

# Website + NOOS Real Sync Handoff - LOCKED v1

## Purpose

This is the NOOS vault mirror of the website/NOOS sync handoff. It prevents drift between the public Noetfield website agent and the Noetfield OS agent.

## One-Line Model

```text
noetfield.com = story, buyer path, public proof, conversion
noetfeld-os  = GEL runtime, gate, log, audit/TLE implementation truth
SourceA      = parent engine pattern, not Noetfield implementation storage
```

## Authority Split

| Lane | Canonical owner | Owns | Must not own |
|------|-----------------|------|--------------|
| Website | `~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/` | `www.noetfield.com`, public routes, nav, copy, chatbot behavior, public chatbot knowledge, Vercel deploy, website E2E | GEL runtime implementation |
| Platform spine | `~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/` | `platform.noetfield.com`, governance service wrapper, public chat/intake integration, website-facing APIs | SourceA internal runtime |
| Noetfield OS / GEL | `~/Projects/noetfeld-os/` | `api.noetfield.com`, FastAPI GEL runtime, decision endpoint, idempotency, API auth, health/readiness, noetfield-gate, TLE/audit evidence | Website source, Vercel deploy, public nav |
| SourceA | SourceA workspace | Engine patterns, receipt/gate invariants, foundational governance laws | Default Noetfield implementation docs |

## Agreement

The NOOS agent is correct on the main relationship:

- `noetfield.com` is the brand, story, evidence, and buyer conversion surface.
- `noetfeld-os` is the runtime and delivery repo for GEL gate/log/audit/TLE work.
- SourceA can inform engine law, but Noetfield implementation truth must not be saved into SourceA unless ASF explicitly names SourceA.
- NOOS docs belong in `~/Projects/noetfeld-os/docs/_NOOS_AGENT/` with `NOOS-AGENT-DOC`, trace id, and `MANIFEST.json` row.

## Correction

Noetfield OS should not own website implementation plans broadly.

Correct split:

- NOOS may own GEL/runtime-facing website requirements, for example `/runtime/`, `/gel/`, `api.noetfield.com` truth, SDK/gate copy, and TLE proof requirements.
- Website repo owns public-site implementation, route files, nav, public chatbot behavior, public copy, Vercel deploy truth, static verification, and live website E2E.
- If NOOS proposes website strategy, it is an input. It becomes website truth only when implemented or locked in the website repo.

## Sync Rule

Before editing, each agent states one lane:

```text
website | platform-spine | gel-runtime | studio-ide | foundation-pattern
```

Then read the lane authority:

- Website/platform-spine: website repo `governance/NOETFIELD_LIVE_NERVE_RECEIPT.json`, `ROUTING_CARD.md`, `reports/agent-auto/LIVE-STATUS.md`, `docs/ops/NOETFIELD_OWNERSHIP_SYNC_CHARTER_LOCKED_v1.md`, and the relevant verify target.
- GEL runtime: `docs/_NOOS_AGENT/PRODUCT_TRUTH.md` and `docs/_NOOS_AGENT/NOETFIELD_OS_SSOT_v1_LOCKED.md`.
- Cross-lane work: read both authority stacks and write the result into both places only when both agents need the same operational truth.

## Live Nerve Rule

Before claiming the whole Noetfield ecosystem is green, website/platform and NOOS agents must check:

```bash
cd /Users/sinakazemnezhad/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
make verify-live-nerve
```

The receipt proves local public-output, chatbot manifest truth, live www output, live www chat semantics, live platform chat semantics, and `api.noetfield.com` readiness.

## Write Rule

Website-side handoffs and website implementation docs go in:

```text
~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/docs/ops/
```

NOOS-side handoffs and runtime implementation docs go in:

```text
~/Projects/noetfeld-os/docs/_NOOS_AGENT/
```

Do not save Noetfield implementation docs into SourceA unless ASF explicitly asks for SourceA.

## Public Chatbot Rule

The public chatbot is not a hardcoded FAQ machine.

Correct behavior:

- Model/retrieval-first.
- Server-side provider keys only.
- Public knowledge/pinned context allowed.
- Intent classification is telemetry and alignment, not a canned answer switchboard.
- Local website fallback is routing-only during outages.
- Do not introduce weird negative framing unless the user asks directly.
- E2E should protect natural, contextual behavior and fail static local rule engines.

## Intelligence/Nav Decision

ASF and both agents agree that a top-nav item must have a distinct job.

Current issue:

- `Intelligence` in website primary nav points to `/`.
- If it only means home, it should be called `Home`.
- If it means proof/research/insights, it needs a real `/intelligence/` hub before it deserves top-nav weight.

Recommended website nav direction:

```text
Home · Governance · Copilot · AI Factories · Trust Ledger · Pricing · Demo
```

Secondary/footer:

```text
Federal · MSP · Templates · Trust · About · Contact · Legal
```

NOOS should not directly edit website nav unless ASF explicitly assigns website implementation to this agent. NOOS may provide GEL/runtime truth for website copy.

## Locked Offerings Constraint

Website nav and chatbot must respect the website repo's `OFFERINGS_LOCKED.md`:

- Trust Brief — $10,000.
- Copilot Governance Pack — $2k-10k lead wedge.
- Bank Pilot.
- Developer sandbox is free access, not a fourth contract SKU.

Names like `AI Operations Audit`, `Automation Sprint`, or `Managed AI Ops` can be copy/lane language only if mapped to locked offerings. They must not become new contract SKUs without a new lock.

## Verification Matrix

| Change type | Required verification |
|-------------|-----------------------|
| Website HTML/nav/copy/chatbot | `make verify-static-www`, `bash scripts/verify-ui-build-checklist.sh`, `make verify-www-e2e` when live behavior matters |
| Platform public chat/intake | affected unit tests plus `make verify-www-e2e` after deploy |
| GEL runtime | noetfeld-os tests plus `api.noetfield.com` health/readiness |
| Cross-lane docs | website doc index plus NOOS `MANIFEST.json` when mirrored |

## Next Three Sync Tasks

1. Decide whether primary nav says `Home` or whether `/intelligence/` becomes a real proof/insight hub.
2. Keep chatbot model/retrieval-first and remove any remaining static answer incentives from tests, docs, or fallback copy.
3. When runtime/GEL copy changes, NOOS updates `PRODUCT_TRUTH.md`; website agent updates public pages only after mapping the runtime truth to buyer-safe language.

## Live Check — 2026-06-28

### Noetfield OS / GEL local

- `bash scripts/check_noos_agent_docs.sh` — PASS.
- `bash scripts/check_noetfield_business_strategy.sh` — PASS.
- `bash scripts/check_upgrade_plan_300.sh` — PASS.
- `.venv/bin/python -m pytest -q` — PASS, `26 passed`.
- Local uvicorn on `127.0.0.1:8001`:
  - `/health` — 200.
  - `/readiness` — 200, `ready=true`, `policy_loaded=true`, `db_ok=true`.
  - `/docs` — 200.

### Online Noetfield

- `https://www.noetfield.com/` — 200.
- `https://www.noetfield.com/gate/` — 200.
- `https://www.noetfield.com/trust-ledger/` — 200.
- `https://www.noetfield.com/status/` — 200.
- `https://platform.noetfield.com/health` — 200, service `noetfield-platform`, runtime `phase-3.1-backend-core`.
- `https://api.noetfield.com/health` — 200, service `noetfeld-os`, version `0.3.0`.
- `https://api.noetfield.com/readiness` — 200, `ready=true`.

### Website Intelligence/nav state

- Live homepage title is `Noetfield Intelligence — AI consulting for Canadian SMEs`.
- Live homepage uses `/intelligence/intake/` as Diagnostic Sprint CTA.
- `https://www.noetfield.com/intelligence/` returns 404.
- Therefore `Intelligence` is currently a homepage positioning word / intake lane, not a real top-level hub page.
- Decision remains: either rename nav to `Home`, or build a real `/intelligence/` proof/insight hub. Do not keep a primary tab that is functionally the homepage.

### Validator/nerves state

- SourceA live surfaces show:
  - `sascip_safety_line`: ADMIT, probes PASS.
  - `nerve_system_line`: aligned, drift=86, `ui_fc=BLOCK`, `maclaw=PASS`, `worker=BLOCK`.
  - `ui_upgrade_first_check_line`: wired YES but validator FAIL.
- SourceA session gate receipt is not green:
  - `mirror_poison_validate` fails with 2 poison hits.
  - `entry_gate_worker` fails.
- `bash scripts/validate-agent-filing-registry-v1.sh` — PASS.
- `bash scripts/validate-pipeline-node-graph-v1.sh` — FAIL because graph/catalog/directory-map are out of sync for multiple nodes.

### Practical meaning

Noetfield runtime and online service are healthy. The broader SourceA nerve system is wired but not fully healthy; its safety posture is ADMIT, but proof spine still has drift in mirror poison, worker entry gate, UI first-check, and node graph/catalog alignment. Website implementation truth must stay in the website repo; NOOS should keep runtime truth and cross-lane handoff truth current.

## Success Definition

The website agent sells the evidence and buyer path. The NOOS agent proves the gate and log. Both agents coordinate through disk truth, not chat memory, and neither creates a duplicate source of truth for the other's lane.
