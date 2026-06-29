---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-28"
doc_id: noetfield-website-noos-real-sync-handoff-locked-v1
status: LOCKED
---

# Noetfield Website + Noetfield OS Real Sync Handoff - LOCKED v1

## Purpose

This handoff prevents drift between the public Noetfield website agent and the Noetfield OS agent.

Noetfield succeeds when the buyer surface, platform spine, and GEL runtime tell one story without duplicating each other's source of truth.

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

## Agreement With NOOS Agent

The NOOS agent is correct on the main relationship:

- `noetfield.com` is the brand, story, evidence, and buyer conversion surface.
- `noetfeld-os` is the runtime and delivery repo for GEL gate/log/audit/TLE work.
- SourceA can inform engine law, but Noetfield implementation truth must not be saved into SourceA unless ASF explicitly names SourceA.
- NOOS docs belong in `~/Projects/noetfeld-os/docs/_NOOS_AGENT/` with `NOOS-AGENT-DOC`, trace id, and `MANIFEST.json` row.

## Correction To Avoid Drift

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

- Website/platform-spine: `ROUTING_CARD.md`, `reports/agent-auto/LIVE-STATUS.md`, `docs/ops/NOETFIELD_OWNERSHIP_SYNC_CHARTER_LOCKED_v1.md`, and the relevant verify target.
- GEL runtime: `~/Projects/noetfeld-os/docs/_NOOS_AGENT/PRODUCT_TRUTH.md` and `~/Projects/noetfeld-os/docs/_NOOS_AGENT/NOETFIELD_OS_SSOT_v1_LOCKED.md`.
- Cross-lane work: read both authority stacks and write the result into both places only when both agents need the same operational truth.

## Live Nerve Rule

Before trusting website docs, generated output, chatbot knowledge, or prior chat summaries, read the live nerve receipt:

```bash
make verify-live-nerve
```

```text
governance/NOETFIELD_LIVE_NERVE_RECEIPT.json
```

If the receipt is missing or `gate=FAIL`, the next safe action is to repair the live nerve. Do not use stale docs as implementation truth while the live nerve is failing.

Current live nerve nodes:

```text
N1_PUBLIC_OUTPUT
N2_CHAT_TRUTH
N3_DOC_FRESHNESS
N4_WWW_LIVE_OUTPUT
N5_WWW_CHAT_SEMANTIC
N6_PLATFORM_CHAT_SEMANTIC
N7_GEL_LIVE_RUNTIME
N8_ROUTE_NAV_TRUTH
N9_VALIDATOR_NODE_REGISTRY
```

This means website, platform public chat, and GEL readiness are checked together before claiming the ecosystem is green.

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

## Public Chat Truth Spine

The public chatbot has a stricter rule after the 2026-06-28 stale executive overview incident:

```text
public truth source -> public chat validator -> chat tests -> static www verify -> deploy -> live curl smoke
```

Required gate:

```bash
bash scripts/verify-public-chat-truth.sh
make verify-static-www
```

The validator must fail if public chatbot truth returns to stale "governance execution infrastructure / compliance log / allow or deny" positioning. The accepted executive overview is buyer-facing:

- Copilot governance evidence.
- Trust Ledger Entry.
- Metadata-only M365 evidence index.
- Board PDF.
- Procurement ZIP.
- Copilot Governance Pack ($2k-10k, 90 days).

Future agents must not fix chatbot incidents by changing only page HTML or a single markdown file. The website response path includes the widget, Vercel proxy, public chatbot knowledge, platform retrieval, tests, deploy, and live endpoint.

## Intelligence/Nav Decision

ASF and both agents agree that a top-nav item must have a distinct job.

Current issue:

- `Intelligence` in the primary nav points to `/`.
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

Do not adopt a nav that creates unshipped products or conflicts with `OFFERINGS_LOCKED.md`.

## Locked Offerings Constraint

Website nav and chatbot must respect `OFFERINGS_LOCKED.md`:

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

## Success Definition

The website agent sells the evidence and buyer path. The NOOS agent proves the gate and log. Both agents coordinate through disk truth, not chat memory, and neither creates a duplicate source of truth for the other's lane.
