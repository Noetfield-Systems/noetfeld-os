# Routing map — clean paths

**Version:** 2026.06.03 · Anti-fragmentation: one canonical URL per public surface.

---

## Public www (`noetfield.com`)

| Route | Purpose | Law / SKU |
|-------|---------|-----------|
| `/` | Homepage | NORTH_STAR, three SKUs |
| `/trust-brief/` | Trust Brief SKU | OFFERINGS §1 |
| `/copilot/` | Copilot hub | OFFERINGS §2 |
| `/copilot/demo/` | 5-min agentic demo | COMMERCIAL_AGENTIC_UI_REFERENCE |
| `/copilot/trial/` | Free sandbox | Product access, not SKU |
| `/copilot/readiness/` | Readiness Pack | OFFERINGS §2 |
| `/gate/sales/` | Purchase hub | Stripe commercial license |
| `/gate/diligence/` | Investor buy-side lane | INVESTOR_GOVERNANCE_LANE_LOCKED |
| `/gate/procurement/` | Engagement intake | Bank pilot path |
| `/trust-ledger/` | Trust Ledger product | PLATFORM_BLUEPRINT §11 |
| `/gate/partners/investors/` | Noetfield capital raise | **noindex** — not portco diligence |

---

## Platform (planned / pilot)

| Route | Purpose |
|-------|---------|
| `platform.noetfield.com` | Runtime API + workspace |
| `GET /catalog/tiers` | Capability tier tree (not on www) |
| `GET /factories` | Factory registry with tier, status, SKU |
| `POST /factories/{id}/run` | Execute live factories only |
| `/platform/` | Static pilot hub (repo) |
| `/platform/dashboard/` | Governance console pilot |
| `/portal/login/` | Auth / sandbox entry |

---

## Repo routing

| Path | Role |
|------|------|
| `docs/LAWS/` | **Current law — start here** |
| `docs/SOURCE_OF_TRUTH/uploaded/` | Canonical document corpus |
| `docs/SOURCE_OF_TRUTH/registry/` | Machine SSOT decisions |
| `docs/SOURCE_OF_TRUTH/archive/` | Supersession index (old versions) |
| `docs/strategy/` | Operational locks (verified) |
| `docs/platform/CATALOG.md` | Tier + factory catalog hub |
| `governance/FACTORY_CATALOG.json` | Machine factory registry |
| `governance/CAPABILITY_TIER_CATALOG.json` | Machine tier capability tree |
| `L2-knowledge/strategy/noetfield/` | Derived — regenerate only |
| `Noetfield-All-Documents/` | Desktop mirror — regenerate only |
| `_archive/` | Cold storage / prohibited artifacts |

---

## Domain split (FINAL LOCK)

From [`DEPLOYMENT_ARCHITECTURE.md`](../../DEPLOYMENT_ARCHITECTURE.md):

- **www.noetfield.com** — institutional GTM, intake, artifacts
- **platform.noetfield.com** — demos, evaluate API, console (not payment rails)

---

## Intake vectors

| URL pattern | Lane |
|-------------|------|
| `?vector=investor-diligence` | Buy-side VC/PE → Trust Brief |
| `?rid=` | Request ID continuity (shell.js) |
| `/gate/intake/?need=*` | Gate routing wizard |
