# /proof/noetfield — Publish Execution Plan v0.1 (LOCKED)

**Status:** SHIPPED v0.1 — `/proof/noetfield/` + JSON live; see `WWW_IMPLEMENTATION_STATUS_v1.md` for ongoing www truth  
**Canonical path:** `noetfeld-OS/noetfield-org/proof-page-draft/PUBLISH_PLAN.md`  
**Production path:** Cloudflare Pages `noetfield-www` via `Noetfield/scripts/deploy-www-cloudflare.sh`

---

## Deploy authority (locked)

**Agents deploy** Case Study #1 via the **approved Noetfield www production path** (Cloudflare static www).  
Drafts live in `noetfeld-OS/noetfield-org/proof-page-draft/`; **live assets live in `Noetfield/` repo**.

Do not use forbidden tokens in `../FORBIDDEN_MARKERS.txt`. Do not publish from stale workspace-root `noetfield-org/`.

---

## Artifacts

**Source (NOOS drafts):**

```
noetfeld-OS/noetfield-org/proof-page-draft/
  noetfield.html.md          → convert to HTML
  noetfield.json             → copy + finalize digest
  noetfield_public_evidence_bundle_v1.schema.json
```

**Target (Noetfield repo — live www):**

```
Noetfield/proof/noetfield/index.html
Noetfield/proof/noetfield.json
```

**Live URLs (after deploy + verify):**

```
https://www.noetfield.com/proof/noetfield
https://www.noetfield.com/proof/noetfield.json
```

---

## Agent execution order

### Step 1 — Finalize drafts (NOOS)

1. Review `noetfield.html.md` + `noetfield.json`
2. Replace `#contact` with real audit request path or email (if available; else keep `#contact` and note in receipt)
3. Verify attachment URLs in JSON return 200
4. Compute `integrity.digest` — sha256 of canonical JSON **excluding** `integrity.digest`
5. Set `generated_at` to publish timestamp (ISO-8601 UTC)

### Step 2 — Land assets in Noetfield repo

```bash
cd /Users/sinakazemnezhad/Desktop/Noetfield-Systems/Noetfield
mkdir -p proof/noetfield
```

1. Convert `noetfield.html.md` → `proof/noetfield/index.html` (match existing static www shell/CSS patterns; see `services/agentic-cost-governance/index.html` for reference)
2. Copy finalized `noetfield.json` → `proof/noetfield.json`
3. Ensure `governance/PUBLIC_OUTPUT_DENYLIST.json` does **not** block `/proof/noetfield` (add allow if needed)
4. Run local static verify:

```bash
make verify-static-www
python3 scripts/rebuild-www-v6.py   # if route must appear in nav/generator
```

### Step 3 — Commit + deploy (Noetfield repo)

Deploy fence requires **clean `main` synced with `origin/main`** (see `scripts/deploy-www-cloudflare.sh`).

```bash
git status --short          # must be clean except staged proof files
git add proof/noetfield/
git commit -m "publish: Case Study #1 /proof/noetfield v0.1"
git push origin main
bash scripts/deploy-www-cloudflare.sh
```

Optional canonical-domain verify (when DNS ready):

```bash
CF_PAGES_DNS_READY=1 bash scripts/deploy-www-cloudflare.sh
```

### Step 4 — Post-deploy verify

```bash
python3 scripts/nf_post_deploy_verify.py --surface www --www-base https://www.noetfield.com
curl -sS -o /dev/null -w '%{http_code}\n' https://www.noetfield.com/proof/noetfield
curl -sS -o /dev/null -w '%{http_code}\n' https://www.noetfield.com/proof/noetfield.json
```

### Step 5 — Receipts

1. Emit `proof-page-live-receipt-v1` in `noetfeld-OS/noetfield-org/receipts/`
2. Append entry to `noetfeld-OS/noetfield-org/SYNC_RECEIPTS.md`
3. Run NOOS live sync gate:

```bash
cd /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
NOOS_LIVE_SYNC_SCOPE=public bash scripts/check_noos_live_sync_gate.sh
```

### Step 6 — LinkedIn (optional, after live verify)

Post follow-up with live proof URL after Step 4 passes.

---

## Pre-deploy checklist

- [ ] `noetfield.html.md` reviewed
- [ ] `noetfield.json` reviewed + schema-valid
- [ ] `integrity.digest` computed (not `COMPUTE_AT_PUBLISH`)
- [ ] Assets in `Noetfield/proof/noetfield/`
- [ ] `make verify-static-www` PASS
- [ ] `main` clean + pushed
- [ ] `deploy-www-cloudflare.sh` PASS
- [ ] Live URLs 200
- [ ] `proof-page-live-receipt-v1` emitted

---

## Verdict

**EXECUTION_READY — agent deploys via approved Cloudflare www path when checklist is green.**
