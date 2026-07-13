# Proof Page Live Receipt — Case Study #1

**Receipt ID:** `proof-page-live-receipt-v1-20260713`  
**Date:** 2026-07-13T09:35:00Z  
**Status:** PUBLIC_PAGE_LIVE  
**Authority:** NOOS / Lane A  

---

## Deploy record

| Field | Value |
|-------|-------|
| Noetfield commit | `f7da5c4f` (rebased onto origin/main) |
| Deploy script | `Noetfield/scripts/deploy-www-cloudflare.sh` |
| Pages preview | `https://e899a824.noetfield-www.pages.dev` |
| Production verify | `https://www.noetfield.com/proof/noetfield` → **200** |
| JSON verify | `https://www.noetfield.com/proof/noetfield.json` → **200** |

## Integrity

- **Digest:** `045a661a1678403513c6c51e55fa58440196b54d6351a3722cfd9ba5ec415cfd`
- **generated_at:** `2026-07-13T09:25:00Z`
- **schema:** `noetfield_public_evidence_bundle_v1`

## Live URLs

- https://www.noetfield.com/proof/noetfield
- https://www.noetfield.com/proof/noetfield.json

## Notes

- Preview post-deploy verify failed on `/health` path (404 on preview hostname); production www proof routes verified 200.
- Noetfield local WIP stashed as `wip-pre-proof-deploy-20260713` — restore with `git stash pop` when ready.

## Service lane

**Case Study #1:** PUBLIC_PAGE_LIVE · Milestone M-001 IN_COMMISSIONING → proof surface live
