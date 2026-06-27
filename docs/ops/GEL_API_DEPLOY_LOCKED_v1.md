# GEL API DEPLOY — LOCKED v1

**Status:** LOCKED  
**Date:** 2026-06-26  
**Host:** https://api.noetfield.com  
**Railway:** project `noetfield-platform` · service `gel-api`

---

## Deploy

```bash
cd ~/Projects/noetfeld-os
bash scripts/deploy-gel-api-railway.sh
bash scripts/setup-gel-api-dns.sh
```

## Verify

```bash
curl -sS https://api.noetfield.com/health | python3 -m json.tool
curl -sS https://api.noetfield.com/readiness
noetfield gate  # set NOETFIELD_API_URL=https://api.noetfield.com
```

## CI

GitHub Actions: `.github/workflows/gel-ci.yml` — pytest + `noetfield gate` on push.

**Locked by:** noetfeld-os-cursor-chat
