# Noetfield — public site (www)

**Noetfield only** — not VIRLUX (separate product; see [external/virlux/](../external/virlux/)).

Host: `www.noetfield.com` · Source: repo root HTML + `assets/`

## Launch blockers

| ID | Item | Status | Owner | Type | Notes |
|----|------|--------|-------|------|-------|
| NF-WWW-01 | Deploy static site + CDN on every `main` push | todo | ops | launch_blocker | See `docs/GO_LIVE_CHECKLIST.md` |
| NF-WWW-02 | Legal review: `privacy/`, `terms/` aligned to 3 SKUs only | todo | legal | launch_blocker | `docs/LEGAL_REVIEW_CHECKLIST.md` |
| NF-WWW-03 | Trust Brief intake API-only | done | engineering | code | `noetfield-intake-api.js` |
| NF-WWW-04 | Regenerate `sitemap.xml` from live routes only | done | engineering | code | `scripts/generate_sitemap.py` + www CI |
| NF-WWW-05 | MSB / regulatory claims — only if actually registered | blocked | legal | launch_blocker | Do not imply licenses not held |

## GTM / content — done or in progress

| ID | Item | Status | Notes |
|----|------|--------|-------|
| NF-GTM-01 | Five-surface nav + enterprise consolidation | done | `docs/FINAL_PUBLIC_SITE.md` |
| NF-GTM-02 | Single intake email `operations@noetfield.com` | done | `OFFERINGS_LOCKED.md` |
| NF-GTM-03 | Trust Brief $10K aligned on intake estimator | done | Planning disclaimer on form |
| NF-GTM-04 | FAQ + assistant channels section | done | `/faq/#assistant` |
| NF-GTM-05 | Chat widget → platform API | done | `noetfield-chat.js` + ecosystem JSON |

## Future improvements

| ID | Item | Status | Owner | Type | Notes |
|----|------|--------|-------|------|-------|
| NF-WWW-10 | Dedicated `/pricing` for paid ads | todo | engineering | nice_to_have | |
| NF-WWW-11 | Light-mode variant | todo | engineering | nice_to_have | |
| NF-WWW-12 | Restore or replace `/contact/`, `/feedback/`, `/status/` | done | Redirects to intake/FAQ |
| NF-WWW-13 | Static www canonical | done | engineering | code | `docs/CANONICAL_WWW.md` |
| NF-WWW-14 | Copilot + Bank Pilot on `/gate/intake/` | done | engineering | code | Gate intake cards |
| NF-WWW-15 | CDN 301 rules for collapsed redirect stubs | todo | ops | ops | ~80 stub paths |

## TrustField boundary

| ID | Item | Status | Notes |
|----|------|--------|-------|
| NF-TF-01 | No TrustField execution/custody on public HTML | done | FINAL LOCK audits |
| NF-TF-02 | Strategic docs stay in SOT archive only | todo | ops | `Noetfield-All-Documents/` not buyer-facing |
