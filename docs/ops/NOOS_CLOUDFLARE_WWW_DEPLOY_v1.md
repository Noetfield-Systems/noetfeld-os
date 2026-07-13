# Cloudflare Static WWW Deploy Contract (v1)

**Updated:** 2026-07-05  
**Production:** Cloudflare Pages `noetfield-www` + edge worker `noetfield-www-proxy` (denylist → Pages origin)

## Surfaces

| URL | Owner repo | NOOS probe |
|-----|------------|------------|
| https://www.noetfield.com/ | Noetfield-Systems/Noetfield | `scripts/check_production_urls.sh` |
| https://www.noetfield.com/services/agentic-cost-governance | Noetfield static output | same |
| https://api.noetfield.com/health | Railway gel-api | same |

## NOOS role

- Probe only via surface loop + `make urls`
- Deploy execution lives in **Noetfield** repo (`infra/cf-www-proxy/` denylist worker → Pages origin)
- Denylist generator: `scripts/generate_cf_www_denylist_v1.py` (Noetfield repo)
- `noetfield deploy --scope www` emits probe receipt; does not push assets

## Edge worker contract

| Component | Value |
|-----------|-------|
| Worker | `noetfield-www-proxy` |
| Origin | `https://noetfield-www.pages.dev` |
| Denylist | `governance/PUBLIC_OUTPUT_DENYLIST.json` → generated `denylist.generated.js` |
| Route | `www.noetfield.com/*` (proxied) |
| NOOS commit (interface) | Noetfield `573069c1` — CF denylist worker lane |

## ACG lane

- Publish commit: `096428e2`
- Service lane: `PUBLIC_PAGE_LIVE + PROSPECT_PACKET_READY`
