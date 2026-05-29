# Legal review checklist (NF-WWW-02, NF-WWW-05)

**Owner:** legal · **Scope:** Noetfield public surfaces only

Before scaling Trust Brief ($10k) or bank pilots, confirm:

## Positioning (three SKUs only)

- [ ] [OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md) — Trust Brief, Copilot Governance Pack, Bank Pilot only
- [ ] No custody, payment initiation, settlement, or FX on Noetfield product pages
- [ ] No MSB / PSP / “licensed money transmitter” claims unless actually registered ([STRATEGIC_LOCK.md](../STRATEGIC_LOCK.md))

## Pages to review

| Path | Focus |
|------|--------|
| [privacy/](../privacy/index.html) | Form processing (API intake, not Formspree); `operations@noetfield.com` |
| [terms/](../terms/index.html) | Engagement boundaries; limitation of liability |
| [trust-brief/intake/](../trust-brief/intake/index.html) | Non-confidential intake disclaimer; pricing guidance language |
| [enterprise/](../enterprise/index.html) | Bank Pilot read-only / shadow mode |
| [copilot/](../copilot/index.html) | Copilot pack scope |

## Intake

- [ ] Web intake uses `POST /api/intake` ([assets/noetfield-intake-api.js](../assets/noetfield-intake-api.js))
- [ ] All vectors route to `operations@noetfield.com`

## Sign-off

| Role | Name | Date |
|------|------|------|
| Legal | | |
| Founder | | |
