# Homepage IA Section Guard (≤8)

**Version:** 1.0.0 · **Plan:** pf-0067 · **SKU:** — (platform) · **Phase:** 6  
**Law:** U5 v17 IA compression — homepage keeps ≤8 top-level `<section>` elements

---

## One line

`index.html` must contain **≤8** `<section>` tags — enforced by `scripts/verify-static-www.sh`.

---

## Rule

| Field | Value |
|-------|-------|
| Max sections | 8 |
| Count method | `grep -c '<section' index.html` |
| Gate script | `scripts/verify-static-www.sh` |
| Make target | `make verify-static-www` |

---

## Current IA map (locked orientation)

| # | Section id / role |
|---|-------------------|
| 01 | Pilot · live-proof hero |
| 02 | Prove · journey |
| 03 | Try · sandbox CTA |
| 04 | Trust · procurement |
| 05+ | Compressed blocks inside sections — not new top-level sections |

**Compression tactic:** nest callouts, stat bars, and journey strips inside section 01 — do not add sibling `<section>` for each micro-block.

---

## www alignment

- `/index.html` — sole homepage surface under guard
- Portfolio verify: `verify-np6-wave.sh` spot-checks section count
- Product verify: `make verify-static-www`

---

## Not in scope

- Redesigning homepage narrative
- Adding ninth section for GEL/runtime (use `/runtime/`)

---

## Verify

```bash
section_count=$(grep -c '<section' index.html)
test "$section_count" -le 8
bash scripts/verify-static-www.sh
```
