# Mockup truth lock — Claude placeholders removed

**Status:** LOCKED  
**Date:** 2026-06-17  
**Authority:** OFFERINGS_LOCKED.md + packages/templates/REGISTRY.json + Governance Runtime 10-step

## What was invented (removed from truth-corrected mockups)

| Invented | Why wrong |
|----------|-----------|
| FINTRAC / AML / HIPAA / M&A / GDPR packs | Not shipped — only `copilot-governance-v1` and `bank-pilot-v1` exist |
| Cross-border KYB, Governed Exchange, Legal Review, Audit Factory, etc. | Not contract SKUs — factories retired as product language |
| "18 nodes", "24 nodes", "Most deployed" | No deployment metrics on disk |
| `sha256: 9f2c4e…a71b` receipt hash | Fabricated — use illustrative label or no hash |
| `transfer $48,000` / `max_transfer $10,000` | Payment rails out of scope for Noetfield |
| "Factory catalog" as product name | Locked term: **Templates** + **Policy packs** |

## Real product surface (use in mockups)

| Item | Truth source |
|------|----------------|
| Brand | Noetfield — AI governance runtime |
| Domain | https://www.noetfield.com |
| Platform API | https://platform.noetfield.com/api/v1/governance/evaluate |
| Templates (active) | Copilot Governance Template, OSFI E-23 Bank Shadow (stub) |
| Policy packs | `copilot-governance-v1`, `bank-pilot-v1` |
| Offerings | Trust Brief $10k · Copilot Pack $2k–10k · Bank Pilot shadow |
| Decisions | PROCEED · REQUIRE_HUMAN_REVIEW · REJECT |
| Receipt type | Trust Ledger Entry (TLE v1) — not "Certainty Report" in buyer docs |
| Sandbox | 14 days · 50 evaluate calls · `/start/` |
| Demo | `/copilot/demo/` (5-minute) |
| Intake | `operations@noetfield.com` |

## Illustrative receipt (allowed — matches real policy)

- **Action:** `publish_board_report`
- **Decision:** REQUIRE_HUMAN_REVIEW
- **Reason:** `copilot:review-required` (Phase 3.4 policy pack)
- **Label:** "Illustrative — sandbox evaluate output"

## Corrected mockup files

- `docs/mockups/truth/noetfield_landing_truth.html`
- `docs/mockups/truth/factory_catalog_truth.html` (renamed: template catalog)
- `docs/mockups/truth/product_banner_truth.html`
