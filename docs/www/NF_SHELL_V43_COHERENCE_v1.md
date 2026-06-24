# Shell v43 Coherence

**Version:** 1.0.0 · **Plan:** pf-0068 · **SKU:** — (platform) · **Phase:** 6  
**Law:** Homepage is canonical shell v43 — N-P6 key surfaces must match asset pins

---

## One line

Canonical www shell: `noetfield-www.css?v=43` · `noetfield-shell.js?v=43` · `noetfield-www.css` print `v=43` on platform front-door pages.

---

## Canonical pins (v43)

```html
<link rel="stylesheet" href="/assets/noetfield-www.css?v=43" />
<link rel="stylesheet" href="/assets/noetfield-print.css?v=43" media="print" />
<script src="/assets/noetfield-shell.js?v=43" defer></script>
<script src="/assets/noetfield-intake-core.js?v=43" defer></script>
<script src="/assets/noetfield-forms.js?v=43" defer></script>
```

---

## N-P6 aligned surfaces

| Surface | Path | v43 required |
|---------|------|--------------|
| Homepage | `/index.html` | Yes (canonical) |
| Investor diligence vault | `/investors/diligence/` | Yes |
| Investors hub | `/investors/` | Yes |
| Procurement pack | `/copilot/procurement/` | Yes (already v43) |

**Drift note:** Secondary lanes (`/start/`, `/templates/`, `/runtime/`) may remain v40 until next wave — N-P6 locks investor + homepage coherence.

---

## verify-static-www needles

- Homepage: `noetfield-www.css?v=43` · `nf-site-v14`
- Investor diligence: bump to v43 when aligned

---

## Not in scope

- Mass bump of all 30+ pages to v43 in one commit (incremental)
- TrustField or SourceA shell assets

---

## Verify

```bash
grep -q 'noetfield-www.css?v=43' index.html
grep -q 'noetfield-www.css?v=43' investors/diligence/index.html
grep -q 'noetfield-www.css?v=43' investors/index.html
```
