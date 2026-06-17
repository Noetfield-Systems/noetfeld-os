# Start Page — Template Deploy CTA

**Version:** 1.0.0 · **Plan:** pf-0063 · **SKU:** NF-QS (platform) · **Phase:** 5  
**Law:** Sandbox is product access — Copilot Governance Pack is the lead program

---

## One line

When `/start/?template=copilot-governance-v1` is in the URL, show a template-deploy callout with canonical CTAs before the Trial OS wizard.

---

## Query param law

| Param | Value | Behavior |
|-------|-------|----------|
| `template` | `copilot-governance-v1` | Show `#nf-template-deploy-callout` banner |
| (other) | — | No callout · default sandbox flow |

**Canonical deploy URL:** `/start/?template=copilot-governance-v1`

---

## CTA map

| Action | URL |
|--------|-----|
| Deploy template (primary) | `/start/?template=copilot-governance-v1` |
| Apply for pilot | `/trust-brief/intake/?interest=pilot&vector=copilot-governance` |
| Template catalog | `/templates/` |
| Governance API | `/docs/api/` |

---

## Callout copy (locked)

> **Copilot Governance Template** — policy pack `copilot-governance-v1` pre-wired. Complete sandbox signup, then run your first evaluate against shipped rules.

---

## Implementation

- `/start/index.html` — inline script or `assets/noetfield-forms.js` extension
- Element id: `nf-template-deploy-callout` (hidden unless param matches)
- Links reuse `.nf-template-deploy` class for analytics consistency

---

## Upgrade path

```text
/templates/ → Deploy CTA → /start/?template=copilot-governance-v1 → Trial OS → Copilot Governance Pack
```

---

## Not in scope

- Auto-provision production tenant from query param alone
- Payment or custody flows
- TrustField RPAA intake on same form

---

## Verify

```bash
grep -q 'copilot-governance-v1' docs/start/NF_START_TEMPLATE_DEPLOY_CTA_v1.md
grep -q 'nf-template-deploy-callout' start/index.html
```
