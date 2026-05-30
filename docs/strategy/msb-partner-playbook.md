# MSB partner channel playbook (90 days)

**Canonical strategy:** [canada-partner-gtm-2026.md](./canada-partner-gtm-2026.md)  
**Deploy:** [MSB_DEPLOY_AND_PILOT.md](../MSB_DEPLOY_AND_PILOT.md)  
**Staging:** [MSB_STAGING_INTEGRATION.md](../MSB_STAGING_INTEGRATION.md)

## Positioning (MSB BD)

> Noetfield is the control layer your MSB calls before payment APIs run — policy, RID, and Trust Ledger export; you keep FINTRAC/RPAA execution.

## Fast revenue ladder

1. **Trust Brief $10k** — MSB referral or MSB’s enterprise client  
2. **Shadow Pack** — ~$12k–$18k CAD (private SOW in `ops/private/msb/`) — 30-day shadow + workshops  
3. **Copilot pack** — MSB distribution to corporate clients  
4. **Annual API license** — after shadow success  

## 90-day execution tracker

Copy to `ops/private/msb/OUTREACH_TRACKER.md` via `./scripts/seed-msb-partner-pack.sh` and update weekly.

| Week | Goal | Done |
|------|------|------|
| 1–2 | Merge/deploy; MSB target list (10 names) | ☐ |
| 3–4 | 5 outreaches; 1 Shadow Week demo | ☐ |
| 5–6 | 5 outreaches; 2 Shadow Week demos | ☐ |
| 7–8 | Close 1 Trust Brief or Shadow Pack | ☐ |
| 9–10 | Close 2nd Trust Brief or start staging | ☐ |
| 11–13 | MSB staging evaluate + shared RID | ☐ |

### Outreach targets (fill in private tracker)

| MSB / PSP | Contact (compliance/CTO) | Intro source | Demo date | Deal |
|-----------|------------------------|--------------|-----------|------|
| | | | | |

## Email hook (template)

Subject: Pre-execution governance for [MSB name] APIs (RPAA-safe software vendor)

Body bullets:

- Shadow evaluate before your payment APIs — no custody in Noetfield  
- Trust Ledger export + RID for FINTRAC/OSFI evidence  
- 30-minute Shadow Week demo — no payment execution through us  

CTA: `/trust-brief/intake/?vector=partner-msb` or operations@noetfield.com

## Demo script

[SHADOW_WEEK_DEMO.md](../SHADOW_WEEK_DEMO.md) — use `scenario-presets/msb` for MSB meetings.

## Say / don’t say

| Say | Don’t say |
|-----|-----------|
| Pre-execution governance for licensed MSBs | We are an MSB |
| Trust Ledger compliance log | Payment orchestration |
| Software vendor outside RPAA | Noetfield transmits funds |

## Success metrics (90 days)

- ≥10 MSB meetings  
- ≥2 Trust Brief and/or ≥1 Shadow Pack closed  
- ≥1 MSB staging integration with shared RID  
- `make verify-final-lock` clean on `main`
