# NF WWW Language Layers — LOCKED v1

**Scope:** Public www (`www.noetfield.com`) and generated marketing HTML.  
**Strategy:** Client-facing first. Internal factory (ASF, W3, portfolio, SourceA) stays in repo/docs/ops — shown only as **sample, sandbox, demo**.

**Mandatory UI gate:** [NF_UI_BUILD_CHECKLIST_LOCKED_v1.md](./NF_UI_BUILD_CHECKLIST_LOCKED_v1.md) — `make nf-ui-checklist` before any www/form/app UI ship.

## Four layers

| Layer | Audience | Where it belongs | Tone |
|-------|----------|------------------|------|
| **Founder / internal** | Agents, ops, portfolio | `docs/ops/`, `os/`, private workspace — **not** www hero copy | W3 economic signal, Lane SSOT, nurture SSOT, plan-with-no-asf, SourceA motor, REGISTRY.json, founder setup |
| **Client commercial** | SMB CIO, MSP, pilot buyer | Homepage, `/copilot/pilot/`, `/pricing/`, `/start/` lead | $2k–10k Copilot Pack, board PDF success, sandbox try-without-call |
| **Client institutional** | Federal, bank, investor diligence | `/federal/`, `/bank-pilot/`, `/investors/diligence/`, procurement | OSFI/AIA orientation, diligence vault, honest scope — not certifier claims |
| **Developer** | Sandbox + API integrators | `/start/`, `/docs/api/`, `/runtime/`, `/copilot/demo/` widget | OpenAPI, evaluate semantics, sample events — technical labels OK in demo widget only |

## Banned on public www (commercial + institutional surfaces)

- `W3 economic signal` → use **What success looks like**
- `Lane SSOT`, `commercial SSOT`, `nurture SSOT`, `SSOT:` doc links in sticky CTAs
- `SourceA`, `REGISTRY.json`, `OFFERINGS_LOCKED` in page body
- `docs/ops/` links on status, homepage, intake
- `(founder)` in form options
- **Invitation copy** — design partner, Become a…, Accepting design partners, You're invited
- Sales & demo runbooks listing `STAGING_DEMO`, `DEMO_REHEARSAL`, internal pipeline filenames

## Allowed samples (not process exposition)

- Interactive demo: policy update → evaluate → TLE (sandbox widget may emit technical event names)
- `/factory/` — **noindex** sandbox sample only
- `/runtime/`, `/templates/` — developer orientation; link to API/docs, not internal registry paths

## Rebuild SSOT

All generated marketing pages: `scripts/rebuild-www-v6.py`  
Gate: `scripts/verify-static-www.sh` + `tests/unit/test_public_simplification.py`

## Client replacements (reference)

| Internal | Client-facing |
|----------|---------------|
| W3 economic signal | What success looks like: signed pilot or deposit on Copilot Governance Pack |
| Lane SSOT | Program guide |
| commercial SSOT | commercial overview |
| nurture SSOT | sandbox guide (after signup path) |
| SSOT: /docs/... | Remove from sticky; use plain link text in diligence sections |

**Locked:** 2026-06-17 · Canada GTM client-view pass
