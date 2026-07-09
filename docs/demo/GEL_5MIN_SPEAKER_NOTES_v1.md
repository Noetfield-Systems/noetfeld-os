# GEL 5-Minute Demo — Speaker Notes v1

**Script:** `scripts/demo-gel-5min-v1.sh`  
**UPG:** 0021–0025, 0026  
**Audience:** Enterprise buyer, design partner, investor room

---

## Setup (before room)

```bash
cd ~/Desktop/Noetfield-Systems/noetfeld-OS
pip install -e .
export NOETFIELD_API_URL=https://api.noetfield.com
export NOETFIELD_API_KEY=<design-partner-key>
bash scripts/demo-gel-5min-v1.sh
```

Dry-run once locally. Total target **under 300 seconds**.

---

## Beat map

| Time | Beat | Say | Show |
|------|------|-----|------|
| 0:30 | Gate | "Before any agent runs, we gate the environment." | `noetfield gate` → PASS |
| 1:15 | Approve | "Intent hits policy + corridors; decision lands on disk." | `--sample` → APPROVE receipt |
| 2:00 | Decline | "Extreme DTI breaches corridor — fail-closed DECLINE." | `--sample-block` → DECLINE |
| 2:45 | Export | "Audit bundle maps to Trust Ledger v1 for procurement." | portal export JSON + `audit_digest` |
| 3:30 | Tamper | "Mutate the record — digest verification fails." | verify script FAIL |
| 4:15 | Replay | "Same request_id — deterministic idempotent outcome." | two receipts match |

---

## Honest scope lines

- GEL is **pre-execution only** — no custody, no execution authority.
- Hosted API is live at `api.noetfield.com`; PyPI packages are live (org migration pending).
- Synthetic demo intents — not a real customer case.

---

## If blocked

| Blocker | Fallback |
|---------|----------|
| No API key | Mint dev key: `python3 scripts/mint_api_key.py` + local `python3 run.py` on `:8001` |
| Portal export 404 | Script builds TLE bundle locally from receipt (already wired) |
| Gate BLOCK | Run from repo root or set `NOETFIELD_ROOT` |

---

## Close

"Policy before execution. Receipt after. Evaluate in five minutes — `pip install noetfield-gate`."

Point to `/gel/` and `/ai-value-governance-os/` for enterprise depth.
