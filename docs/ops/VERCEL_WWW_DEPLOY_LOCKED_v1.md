# VERCEL WWW DEPLOY — LOCKED v1

**Status:** LOCKED  
**Date:** 2026-06-26  
**Audience:** Founder + agents — where www lives on Vercel

---

## Where to find it in Vercel

| Field | Value |
|-------|--------|
| **Team / scope** | `the-777-foundation` (The 777 Foundation) |
| **Project name** | `noetfield` ← **not** `www`, **not** `project-gc7lm` |
| **Production URL** | https://www.noetfield.com |
| **Dashboard** | https://vercel.com/the-777-foundation/noetfield |
| **GitHub repo** | https://github.com/Noetfield-Systems/Noetfield (connected) |
| **Production branch** | `main` |

---

## Deploy from Mac (CLI)

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
bash scripts/deploy-www-vercel.sh
```

Or manually:

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
npx vercel link --project noetfield --scope the-777-foundation --yes
npx vercel deploy --prod --scope the-777-foundation --yes
```

---

## Verify

```bash
curl -sS https://www.noetfield.com/health
curl -sS https://www.noetfield.com/api/intake/health | python3 -m json.tool
python3 ~/Projects/noetfeld-os/scripts/check_noetfield_com_e2e.py
```

Pass: `www_email_configured: true`, `delivery_mode: resend`.

---

## Common confusion

| Wrong | Right |
|-------|-------|
| Scope `noetfield-systems` | Scope **`the-777-foundation`** |
| Project `www` | Project **`noetfield`** |
| `project-gc7lm.vercel.app` | **Dead** — use `www.noetfield.com` |

---

## Latest production deploy (2026-06-26)

| Field | Value |
|-------|--------|
| Deployment ID | `dpl_4mWNMRWceW9ag4co5S6fsAPqJjj7` |
| Inspector | https://vercel.com/the-777-foundation/noetfield/4mWNMRWceW9ag4co5S6fsAPqJjj7 |
| Aliases | www.noetfield.com, noetfield.com, noetfield.vercel.app |

**Locked by:** noetfeld-os-cursor-chat
