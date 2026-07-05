# Cloudflare Static WWW Deploy Contract (v1)

**Updated:** 2026-07-05  
**Production:** Cloudflare static www (`server: cloudflare`)  
**Retired:** Vercel `noetfield` project (removed 2026-07-05)

## Surfaces

| URL | Owner repo | NOOS probe |
|-----|------------|------------|
| https://www.noetfield.com/ | Noetfield-Systems/Noetfield | `scripts/check_production_urls.sh` |
| https://www.noetfield.com/services/agentic-cost-governance | Noetfield static output | same |
| https://api.noetfield.com/health | Railway gel-api | same |

## NOOS role

- Probe only via surface loop + `make urls`
- Deploy execution lives in **Noetfield** repo (static generator `scripts/rebuild-www-v6.py`)
- `noetfield deploy --scope www` emits probe receipt; does not push assets

## ACG lane

- Publish commit: `096428e2`
- Service lane: `PUBLIC_PAGE_LIVE + PROSPECT_PACKET_READY`
