# Noetfield-Systems Org Repository Registry

**Org:** Noetfield-Systems  
**Registry Version:** 1.0  
**Last Updated:** 2026-07-05T15:44:00Z  
**Status:** Active (Post-Migration + Service Lane Coordination)

## Core Execution Repos

### 1. SourceA
- **Slug:** `Noetfield-Systems/SourceA`
- **URL:** https://github.com/Noetfield-Systems/SourceA.git
- **Branch:** main
- **Purpose:** Core execution engine · gate logic · decision trees
- **Agent Role:** T1 worker · primary decision executor
- **Must-Sync-With:** noetfeld-OS, sina-governance-SSOT
- **Workflows:** trigger dispatch · verify autonomous · replay determinism
- **Owner:** Noetfield-Systems

### 2. TrustField-Technologies
- **Slug:** `Noetfield-Systems/TrustField-Technologies`
- **URL:** https://github.com/Noetfield-Systems/TrustField-Technologies.git
- **Branch:** main
- **Purpose:** Platform enforcement · external verification · delivery
- **Agent Role:** T0/T1 executor · workflow routing · platform hooks
- **Must-Sync-With:** noetfeld-OS, sina-governance-SSOT, SourceA
- **Workflows:** external-verify · vercel-deploy · railway-worker-deploy
- **Owner:** Noetfield-Systems

### 3. noetfeld-OS
- **Slug:** `Noetfield-Systems/noetfeld-OS`
- **URL:** https://github.com/Noetfield-Systems/noetfeld-OS.git
- **Branch:** main
- **Purpose:** Loop governance · factory dispatch · autonomous tick · receipt spine
- **Agent Role:** T1/T3 orchestrator · loop state machine · receipt writer
- **Must-Sync-With:** SourceA, TrustField-Technologies, sina-governance-SSOT
- **Workflows:** noos-factory-autorun · noos-loop-fleet-tick · noos-deadman-v1 · verify-autonomous-24h
- **Cloud Workers:** `noos-loop-fleet-tick-v1` (loop motor, */5) · `noos-deadman-v1` (liveness watchdog, */30)
- **Cloud ops runbook:** `scripts/phase_a_wire_cloud_motor_v1.sh` · `make cloud-motor-resync` · `docs/ops/NOOS_MOTOR_RESTART_RECIPES_v1.md`
- **Owner:** Noetfield-Systems

### 4. sina-governance-SSOT
- **Slug:** `Noetfield-Systems/sina-governance-SSOT`
- **URL:** https://github.com/Noetfield-Systems/sina-governance-SSOT.git
- **Branch:** main
- **Purpose:** Single source of truth · independent verifier · brain-config · receipts
- **Agent Role:** T3 reasoning · receipt validation · independent verification
- **Must-Sync-With:** SourceA, TrustField-Technologies, noetfeld-OS
- **Workflows:** github-app-advisory · verifier-birth · independent-verify
- **Owner:** Noetfield-Systems

## Surface & Tooling Repos

### 5. Noetfield
- **Slug:** `Noetfield-Systems/Noetfield`
- **URL:** https://github.com/Noetfield-Systems/Noetfield.git
- **Branch:** main
- **Purpose:** Marketing website · investor relations · trust ledger UX
- **Agent Role:** T1 builder · asset deployment · web frontend
- **Must-Sync-With:** sina-governance-SSOT (for trust ledger samples)
- **Workflows:** static-www deploy · CF www-proxy denylist worker · buyer-audience-verify (Vercel retired 2026-07-05)
- **Production:** Cloudflare Pages `noetfield-www` + edge worker `noetfield-www-proxy` (denylist → Pages origin)
- **Interface commit:** `573069c1` — `infra/cf-www-proxy/` + `scripts/generate_cf_www_denylist_v1.py`
- **Owner:** Noetfield-Systems

### 6. noetfield-studio-ide
- **Slug:** `Noetfield-Systems/noetfield-studio-ide`
- **URL:** https://github.com/Noetfield-Systems/noetfield-studio-ide.git
- **Branch:** main
- **Purpose:** Local development IDE · gate receipt editor · visual export
- **Agent Role:** T2 builder · local heavy compute · IDE tooling
- **Must-Sync-With:** SourceA, noetfeld-OS
- **Workflows:** export-png-svg
- **Owner:** Noetfield-Systems

## Platform Infrastructure

### 7. SinaaiMonoRepo
- **Slug:** `Noetfield-Systems/SinaaiMonoRepo`
- **URL:** https://github.com/Noetfield-Systems/SinaaiMonoRepo.git
- **Branch:** main
- **Purpose:** Platform utilities · registry · data models
- **Agent Role:** T0/T1 utility · platform config · data spine
- **Must-Sync-With:** SourceA, TrustField-Technologies
- **Workflows:** registry-validate
- **Owner:** Noetfield-Systems

### 8. buildmatch
- **Slug:** `Noetfield-Systems/buildmatch`
- **URL:** https://github.com/Noetfield-Systems/buildmatch.git
- **Branch:** main
- **Purpose:** Static site deployment · build matching · CI verification
- **Agent Role:** T0 executor · deployment validator
- **Must-Sync-With:** TrustField-Technologies
- **Workflows:** build-and-deploy
- **Owner:** Noetfield-Systems

## Migration Status

**Old Org Slug:** `Noetfield-Systems` (FORBIDDEN — see SLUG_SWEEP_RECEIPTS.md)

**Org Slug Cleanup:** ✓ Complete (all active config/workflow/script refs updated to `Noetfield-Systems`)

**Historical References Preserved:** ✓ Yes (marked `HISTORICAL_REFERENCE` where not in active execution paths)

**Verified Windows Invalidated:** ✓ Tracked in SYNC_RECEIPTS.md

## Service Lanes

**Registry File:** SERVICE_LANES.md

Service lanes are buyer-facing or operational services delivered via mission execution. NOOS tracks service status, gates, and current blockers without becoming the product owner.

### Active Service Lanes

#### AI Spend Leak Audit + Premium Model Firewall
- **Service ID:** `svc-cost-audit-firewall-001`
- **Category:** Agentic Cost Governance
- **Product Owner (Buyer-Facing):** Noetfield.com
- **Delivery Owner:** SourceA
- **Control Layer:** NOOS
- **Canon/Ledger:** SG
- **Status:** PUBLIC_PAGE_LIVE + PROSPECT_PACKET_READY
- **Live URL:** https://www.noetfield.com/services/agentic-cost-governance
- **Publish Commit:** 096428e2 (origin/main)
- **Prospect Packet:** docs/commercial/ACG_FIRST_PROSPECT_PACKET_v1.md (SourceA bfc05dbb, preserve/acg-2026-07-05)
- **Current Gate:** Public page live ✓ → prospect packet ready ✓ → founder send ⏳
- **NOOS Blocking:** None
- **See:** SERVICE_LANES.md for owner planes, receipts, and next actions

---

## Sync Verification Checklist

- [ ] All repos on `main` branch
- [ ] All remotes point to `Noetfield-Systems` org
- [ ] No active references to `Noetfield-Systems` in workflows/configs
- [ ] Agent manifests present in all 5 core repos
- [ ] Copilot instructions present in all 5 core repos
- [ ] LOOP_STATE.json reflects current mission stack
- [ ] SYNC_RECEIPTS.md has post-migration restart windows
- [x] SERVICE_LANES.md created and service lanes registered
- [x] SG service registration confirmed for active lanes (svc-cost-audit-firewall-001)
- [x] Noetfield.com ACG page live (096428e2, PUBLIC_PAGE_LIVE)
- [x] SourceA first prospect packet ready (bfc05dbb, PROSPECT_PACKET_READY)
- [ ] Founder review + first prospect send (FT-COMMERCIAL-SEND)
- [ ] Factory lift + full revenue motion LIVE
