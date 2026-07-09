# Noetfield-Systems Org Repository Registry

**Org:** Noetfield-Systems  
**Registry Version:** 1.0  
**Last Updated:** 2026-07-04T06:10:00Z  
**Status:** Active (Post-Migration)

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
- **Workflows:** noos-factory-autorun · noos-loop-fleet-tick · verify-autonomous-24h
- **Org-Sync-Anchors:** noetfield-org/* (this directory)
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
- **Workflows:** vercel-www-deploy · buyer-audience-verify
- **Owner:** Noetfield-Systems

### 6. noetfield-studio-ide
- **Slug:** `Noetfield-Systems/noetfield-studio-ide`
- **URL:** https://github.com/Noetfield-Systems/noetfield-studio-ide.git
- **Branch:** main
- **Canonical local path:** `~/Desktop/Noetfield/noetfield-studio-ide/` (product truth — not in `noetfeld-os`)
- **Founder mirror remote:** `https://github.com/kazemnezhadsina144-dot/noetfield-studio-ide.git` (storage only)
- **Drift-risk duplicate:** `~/Desktop/Noetfield-Systems/noetfield-studio-ide/` — do not delete until reconciliation confirms no unique work
- **Purpose:** Local-first Agentic IDE · cheap-worker runtime · model-agnostic agent workbench
- **Agent Role:** **Studio IDE Owner v1** (T2) · local heavy compute · product implementation
- **NOOS role:** Observe/govern boundary, kernel handoff, live sync (`NOOS_LIVE_SYNC_SCOPE=studio`) — does not host Studio code
- **GitHub doctrine:** Mirror/storage only — not worker runtime
- **Must-Sync-With:** noetfeld-OS (boundary + sync), SourceA (registry authority)
- **Workflows:** export-png-svg · boundary:check · vitest · playwright (local)
- **Owner:** Noetfield-Systems · charter `NOOS-AGENT-20260703-008`

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

## Sync Verification Checklist

- [ ] All repos on `main` branch
- [ ] All remotes point to `Noetfield-Systems` org
- [ ] No active references to `Noetfield-Systems` in workflows/configs
- [ ] Agent manifests present in all 5 core repos
- [ ] Copilot instructions present in all 5 core repos
- [ ] LOOP_STATE.json reflects current mission stack
- [ ] SYNC_RECEIPTS.md has post-migration restart windows
