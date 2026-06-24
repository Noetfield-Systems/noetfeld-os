# Pilot Apply Sticky CTA

**Version:** 1.0.0 · **Plan:** pf-0074 · **SKU:** NF-RD · **Phase:** 8  
**Law:** Mobile-tested sticky bar on intake surfaces — ≥44px touch targets

---

## One line

`#intakeStickyCta` on engagement intake pages — persistent pilot apply bar on mobile scroll · SSOT for Copilot Governance Pack funnel.

---

## Surfaces (locked)

| Page | Path | Sticky id |
|------|------|-----------|
| Trust Brief intake | `/trust-brief/intake/` | `#intakeStickyCta` |
| Engagement gateway | `/gate/intake/` | `#intakeStickyCta` |

---

## DOM contract

```html
<section class="stickyCta" id="intakeStickyCta" aria-label="Sticky CTA">
  <div class="stickyInner">
    <div class="stickyText">…</div>
    <div class="actions">
      <a class="btn primary" href="…">Apply for pilot</a>
    </div>
  </div>
</section>
```

**CSS:** `/assets/noetfield-intake.css` — `body` padding-bottom for sticky clearance · buttons ≥44px min-height.

**JS (trust-brief):** `noetfield-intake-pilot-mode.js` toggles pilot vs Trust Brief sticky copy when `?interest=pilot`.

---

## Copy law (gateway)

> **Copilot Governance Pack** — $2k–10k · 90 days · board PDF in governance meeting. Async intake · operations@noetfield.com.

Primary CTA: `/trust-brief/intake/?interest=pilot&vector=copilot-governance`

---

## Mobile test checklist

- [x] Sticky visible after scroll on viewport ≤390px
- [x] Primary button tappable without overlap with footer
- [x] No horizontal scroll from sticky bar
- [x] `verify-static-www.sh` needles on both intake pages

---

## Not in scope

- TrustField RPAA intake on same sticky
- Auto-submit forms from sticky bar alone
- Founder email sends — Hub approves nurture

---

## Verify

```bash
grep -q 'intakeStickyCta' gate/intake/index.html
grep -q 'intakeStickyCta' trust-brief/intake/index.html
bash scripts/verify-static-www.sh
```
