# Proof Page Live Receipt — Case Study #1 (pre-deploy assets)

**Receipt ID:** `proof-page-live-receipt-v1-20260713`  
**Date:** 2026-07-13T09:30:00Z  
**Status:** ASSETS_LANDED — deploy pending clean Noetfield main  
**Authority:** NOOS / Lane A  

---

## Assets landed

| Asset | Location |
|-------|----------|
| HTML page | `Noetfield/proof/noetfield/index.html` |
| JSON bundle | `Noetfield/proof/noetfield.json` |
| Draft source | `noetfeld-OS/noetfield-org/proof-page-draft/` |

## Integrity

- **Digest:** `045a661a1678403513c6c51e55fa58440196b54d6351a3722cfd9ba5ec415cfd`
- **generated_at:** `2026-07-13T09:25:00Z`

## Target URLs (after deploy)

- https://www.noetfield.com/proof/noetfield
- https://www.noetfield.com/proof/noetfield.json

## Deploy command

```bash
cd Noetfield && bash scripts/deploy-www-cloudflare.sh
```

**Blocker note:** Deploy fence requires clean `main` synced with `origin/main`. Unrelated dirty files in Noetfield repo must be committed or restored before deploy executes.

## Next

1. Commit `proof/` in Noetfield repo
2. Deploy via approved Cloudflare www path
3. Verify live URLs → 200
4. Update this receipt status to `PUBLIC_PAGE_LIVE`
