# PUBLIC WWW BRAND & E2E LAW (LOCKED v1)

**Layer:** L0-adjacent operational law (public deploy boundary)  
**Updated:** 2026-06-26  
**Owner:** Noetfield Systems Inc. (holding company · www.noetfield.com)  
**Enforcement:** `scripts/verify-static-www.sh` (offline disk) · `scripts/check_noetfield_com_e2e.py` (production smoke)

---

## 1. Purpose

www.noetfield.com is the **institutional buyer surface** for Noetfield Intelligence and Enterprise Copilot governance. It must read as a **credible holding-company-grade** vendor to regulated buyers, investors, and partners — never as an internal agent repo, founder ops log, or engineering catalog.

Repo copies of internal docs **stay on disk for agents** — they are **not www**.

---

## 2. Public brand posture (613 Intelligence + enterprise governance)

| Lane | Primary CTA | Enterprise sub-lane |
|------|-------------|---------------------|
| **Intelligence** | Book Diagnostic Sprint · from $2,500 | — |
| **Governance** | Apply for pilot ($2k–10k) · Copilot Governance Pack | Trust Brief · Bank Pilot · board PDF |

**Required homepage phrases (disk + live E2E):**

- Board-grade trust  
- tamper-evident decision records  
- Apply for pilot ($2k–10k)  
- Copilot Governance Pack · Trust Brief · Bank Pilot  
- Commercial path · Diagnostic Sprint · 01 · Diagnose → 04 · Govern  

**Forbidden on public HTML** (buyer-visible pages):

- Founder/agent ops: `founder never`, `Hub approve`, `613 GTM`, `AGENT_SELF_AUDIT`, `plan-with-no-asf`, `RESEND_API_KEY`, `docs/ops/`, `make nf-prove`, portfolio wave counts  
- Internal repo language: `OFFERINGS_LOCKED`, `SourceA`, `W3 economic signal`, `design partner`  
- Engineering surfaces linked from marketing: `/platform/factories/`, `services/governance/README`

---

## 3. Deploy boundary (vercel.json + .vercelignore)

### Must return 404 on www (redirect or exclude)

| Path | Reason |
|------|--------|
| `/docs/ops/*` | Agent runbooks |
| `/docs/platform/*` | Living system charter · internal platform SSOT |
| `/governance/*.json`, `/governance/*.md` (except public HTML hub) | OPS_LIVE · LAW_STACK · factory catalogs |
| `/OFFERINGS_LOCKED.md` | Internal SKU lock file |
| `/platform/*` | Engineering factory catalog · repo path leaks |
| `/.cursor/*`, `/scripts/*`, `/services/*`, `/os/*`, `/reports/*` | Engineering |

### Must remain public (200)

| Path | Reason |
|------|--------|
| `/governance/` | Enterprise buyer hub (HTML) |
| `/`, `/copilot/*`, `/trust/*`, `/investors/*`, `/pricing/*`, `/start/*` | GTM surfaces |
| `/docs/api/`, `/docs/diligence/*`, `/docs/copilot/*` | Procurement diligence (buyer-facing) |

---

## 4. Production E2E contract

Run: `python3 scripts/check_noetfield_com_e2e.py`  
Optional base override: `NOETFIELD_E2E_BASE=https://www.noetfield.com`

### HTTP 200 required

`/`, `/start/`, `/pricing/`, `/copilot/`, `/copilot/pilot/`, `/copilot/demo/`, `/copilot/proof-case/`, `/trust/`, `/trust-brief/intake/`, `/trust-ledger/sample-report/`, `/investors/`, `/work-with-us/`, `/health` (or `/api/health`), `/governance/`

### HTTP 404 required (internal leak regression)

`/docs/platform/NF_LIVING_SYSTEM_CHARTER_DRAFT_v3.md`, `/governance/OPS_LIVE_STATUS_LOCKED.json`, `/OFFERINGS_LOCKED.md`, `/platform/factories/`

### API smoke

- `/api/intake/health` — `www_email_configured: true`, `delivery_mode: resend`  
- POST `/evaluate` — returns `rid`  

### Copy smoke (homepage + pilot)

- Homepage: Apply for pilot, Copilot Governance Pack, Trust Brief, **Board-grade trust**, operations@noetfield.com  
- Pilot: nfPilotApplyForm, Copilot Governance Pack, tamper-evident  

---

## 5. Offline disk mirror

Before every www deploy merge: **`make verify-static-www`** must PASS.

Disk HTML, partials, `vercel.json`, and `.vercelignore` are the **source of truth** for what may ship. Production E2E confirms live deploy matches this law.

---

## 6. Amendment

Changes to this law require updating **both** enforcement scripts in the same PR. Do not weaken block lists without founder approval.
