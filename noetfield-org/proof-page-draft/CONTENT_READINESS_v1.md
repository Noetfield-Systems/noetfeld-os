# EXECUTION READINESS v1 (LOCKED)

**Status:** EXECUTION_READY — agent deploy via approved www path  
**Canonical path:** `noetfeld-OS/noetfield-org/proof-page-draft/CONTENT_READINESS_v1.md`  
**Lock receipt:** `../NOETFIELD_STRATEGY_LOCK_RECEIPT_v1.json`  
**Deploy plan:** `PUBLISH_PLAN.md`  
**Doc index:** `../DOC_INDEX_v1.md`

---

## Deploy authority (locked)

**Agents deploy** to production via the approved Noetfield www path: Cloudflare Pages `noetfield-www` (`Noetfield/scripts/deploy-www-cloudflare.sh`).  
See `PUBLISH_PLAN.md` for step-by-step execution.

---

## Package inventory (canonical — on disk)

| # | File | Purpose |
|---|------|---------|
| 1 | `../DOC_INDEX_v1.md` | What is current vs stale |
| 2 | `../NOETFIELD_COMPANY_STRATEGY_v1_BLUEPRINT.md` | Company strategy draft |
| 3 | `../NOETFIELD_STRATEGY_LOCK_RECEIPT_v1.json` | Lock receipt |
| 4 | `INVESTOR_CASE_STUDY_MODEL_v1.md` | Case study framework |
| 5 | `CASE_STUDY_TEMPLATE_v1.md` | Template for SourceA, SourceB, etc. |
| 6 | `noetfield.json` | Case Study #1 evidence bundle |
| 7 | `noetfield.html.md` | Case Study #1 page content |
| 8 | `noetfield_public_evidence_bundle_v1.schema.json` | Public JSON schema |
| 9 | `PUBLISH_PLAN.md` | **Agent deploy execution steps** |
| 10 | `CONTENT_READINESS_v1.md` | This checklist |

---

## Pre-deploy checklist (agent)

- [ ] Review Case Study #1 content (`noetfield.html.md`)
- [ ] Review JSON bundle (`noetfield.json`) — schema-valid
- [ ] Confirm public URLs in attachments resolve (200)
- [ ] Replace `#contact` with real audit request path or email (or document waiver in receipt)
- [ ] Compute `integrity.digest`
- [ ] Land assets in `Noetfield/proof/noetfield/` per `PUBLISH_PLAN.md`
- [ ] `make verify-static-www` PASS (Noetfield repo)
- [ ] Deploy: `bash scripts/deploy-www-cloudflare.sh` (Noetfield repo, clean main)
- [ ] Verify `https://www.noetfield.com/proof/noetfield` → 200
- [ ] Verify `https://www.noetfield.com/proof/noetfield.json` → valid JSON
- [ ] Emit `proof-page-live-receipt-v1`

---

## Agent scope

**Allowed:**
- Execute `PUBLISH_PLAN.md` end-to-end
- Edit `Noetfield/proof/` and related www static paths for this lane
- Run `deploy-www-cloudflare.sh`, `nf_post_deploy_verify.py`, live sync gate
- Update strategy docs in `noetfeld-OS/noetfield-org/` when deploy completes

**Forbidden:**
- Use tokens in `../FORBIDDEN_MARKERS.txt`
- Deploy from stale workspace-root `noetfield-org/`
- Deploy with dirty/unpushed `main` (deploy fence blocks this)
- Skip post-deploy verify or receipt

---

## After deploy (parallel lanes)

| Lane | Action |
|------|--------|
| B | Reconcile SG; push ahead repos; ratify strategy |
| C | Design corporate homepage; plan /enterprise migration |
| v0.2 | Case Study #2 — SourceA via `CASE_STUDY_TEMPLATE_v1.md` |

---

## Verdict

**EXECUTION_READY — agent deploys when checklist is green. See `PUBLISH_PLAN.md`.**
