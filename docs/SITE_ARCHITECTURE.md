# Noetfield public site architecture

**Product sentence:** [PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md)  
**Offerings:** [OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md) (three tiers only)

## Domain model

| Surface | Host | Role |
|---------|------|------|
| Institutional | `www.noetfield.com` | Sales, intake, reference, legal |
| Platform / pilot | `platform.noetfield.com` | Governance Simulation + Golden Edge API |

## Information architecture

### 1. Contract offerings (revenue)

| Path | Tier |
|------|------|
| `/trust-brief/` | Trust Brief — $10K / 6 weeks |
| `/copilot/` | Copilot Governance Pack |
| `/gate/` | Bank Pilot v6.1 |
| `/enterprise/` | Enterprise buyers |

### 2. Conversion (intake)

| Path | Use |
|------|-----|
| `/trust-brief/intake/` | **Request Governance Brief** (primary) |
| `/copilot/readiness/` | Copilot engagement |
| `/gate/procurement/` | Bank pilot engagement |
| `/gate/intake/` | Package / RID flow |
| `/contact/` | Direct contact |

### 3. Reference (diligence)

| Path | Use |
|------|-----|
| `/playbook/` | Governance modules & kits |
| `/trust-ledger/` | Reference telemetry (no public card checkout) |
| `/resources/` | Framework specifications & blueprint kits |
| `/gate/partners/` | Unified partner gateway |
| `/copilot/quickscan/` | Rapid Copilot snapshot |
| `/faq/` | Questions |

### 4. Company & legal

`/about/`, `/status/`, `/feedback/`, `/vendor/` · `/privacy/`, `/terms/`, `/cookies/`, `/accessibility/`, `/policies/`

### 5. Platform (pilot)

`/platform/`, `/platform/dashboard/` → simulation notes (runtime at `/console` on API host)

## Sitewide UI

- **Shell:** `assets/noetfield-shell.css` + `noetfield-shell.js` → header, offerings strip, footer
- **Sales layout:** `assets/noetfield-sales.css`
- **Hub / directory:** `assets/noetfield-institutional.css`
- **Directory page:** `/directory/` — master map of all major routes

## Page count

~86 `index.html` routes; tier landings and `/directory/` are GTM-aligned. Deep legacy routes retain shell + offerings strip via global injection.
