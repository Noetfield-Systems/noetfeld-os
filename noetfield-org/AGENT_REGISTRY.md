# Noetfield-Systems Org Agent Registry

**Registry Version:** 1.0  
**Last Updated:** 2026-07-03T00:00:00Z  
**Status:** Active (Post-Migration)

## Core Agent Roles (5 Repos)

### SourceA Agent
- **Repo:** Noetfield-Systems/SourceA
- **Primary Agent:** Copilot (T1 executor)
- **Integrator:** noetfeld-OS loop dispatch
- **Role:** Gate logic worker · decision tree executor
- **Branch:** main
- **Must-Sync-With:** noetfeld-OS, sina-governance-SSOT
- **Forbidden Actions:** 
  - Force push
  - Direct main mutation without PR
  - Use old slug `Noetfield-Systems`
- **Workflows:** 
  - `trigger_noos_factory_dispatch_v1.py` (T0 dispatch)
  - `autorun_status_v1.py` (T1 status report)
  - `verify_noos_autonomous_24h_v1.py` (T3 verification)
- **Required Receipts:**
  - Gate execution receipt (JSON)
  - Autonomous verification receipt
  - Determinism verification receipt

### TrustField-Technologies Agent
- **Repo:** Noetfield-Systems/TrustField-Technologies
- **Primary Agent:** Copilot + Cursor local (T0/T1/T2)
- **Integrator:** GitHub Actions → Railway/Vercel
- **Role:** Platform enforcement · external verification · delivery
- **Branch:** main
- **Must-Sync-With:** SourceA, noetfeld-OS, sina-governance-SSOT
- **Forbidden Actions:**
  - Override external-verify workflow
  - Use old slug `Noetfield-Systems`
  - Deploy without passing external-verify
- **Workflows:**
  - `external-verify.yml` (T0 gate)
  - `vercel-deploy-hook.yml` (T1 deployment)
  - `railway-plan-worker-deploy.yml` (T0 worker)
- **Required Receipts:**
  - External verification receipt
  - Deployment receipt (Vercel/Railway)

### noetfeld-OS Agent
- **Repo:** Noetfield-Systems/noetfeld-OS
- **Primary Agent:** Copilot + Codex (T1/T3)
- **Integrator:** Loop orchestrator · receipt spine writer
- **Role:** Scheduled loop governance · dispatch · receipt lifecycle
- **Branch:** main (main business logic branch)
- **Must-Sync-With:** SourceA, TrustField-Technologies, sina-governance-SSOT
- **Forbidden Actions:**
  - Use old slug `Noetfield-Systems`
  - Wait indefinitely on receipt
  - Mutate receipt archive retroactively
- **Workflows:**
  - `noos-factory-autorun-tick-v1` (T0 factory executor)
  - `noos-loop-fleet-tick-v1` (T0 loop tick)
  - `verify_noos_autonomous_24h_v1.py` (T3 verification)
- **Required Receipts:**
  - Factory tick receipt
  - Loop fleet state receipt
  - Autonomous verification receipt
- **Org-Sync-Anchors:** `noetfield-org/LOOP_STATE.json`, `noetfield-org/SYNC_RECEIPTS.md`

### sina-governance-SSOT Agent
- **Repo:** Noetfield-Systems/sina-governance-SSOT
- **Primary Agent:** Codex (T3 reasoning)
- **Integrator:** Independent verifier · GitHub App advisor
- **Role:** Single source of truth · receipt validation · brain-config custody
- **Branch:** main
- **Must-Sync-With:** SourceA, TrustField-Technologies, noetfeld-OS
- **Forbidden Actions:**
  - Accept unverified receipt
  - Use old slug `Noetfield-Systems`
  - Override independent verifier decision
- **Workflows:**
  - `github-app-advisory/index.js` (T3 advisor)
  - `verifier/independent-verifier-birth-receipt` (T3 birth)
- **Required Receipts:**
  - Birth receipt
  - Independent verification receipt
  - Brain-config descriptor receipt

### Noetfield (Website) Agent
- **Repo:** Noetfield-Systems/Noetfield
- **Primary Agent:** Copilot (T1 builder)
- **Integrator:** Vercel deployer
- **Role:** Marketing surface · investor UX · trust ledger sample export
- **Branch:** main
- **Must-Sync-With:** sina-governance-SSOT (for TLE samples)
- **Forbidden Actions:**
  - Use old slug `Noetfield-Systems`
  - Deploy without passing buyer-audience-verify
- **Workflows:**
  - `vercel-www-deploy.yml` (T1 deployment)
  - `verify-www-buyer-audience.sh` (T1 verification)
- **Required Receipts:**
  - Web deployment receipt
  - Buyer audience verification receipt

## Mission Stack (M1–M6)

| Mission ID | Value Class | Spend Cap | Status | Integrator |
|-----------|-------------|-----------|--------|-----------|
| M1 | buyer_proof | T0–T1 | Active | SourceA + TrustField |
| M2 | loop_autonomy | T0–T2 | Active | noetfeld-OS |
| M3 | governance_spine | T1–T3 | Active | sina-governance-SSOT |
| M4 | platform_surface | T1–T2 | Active | Noetfield + noetfield-studio-ide |
| M5 | infrastructure | T0–T1 | Active | SinaaiMonoRepo + buildmatch |
| **M6** | **hygiene_to_proof_asset** | **T0–T2** | **Parked (AI Station)** | **Noetfield (investment docs)** |

**M6 Constraint:** Must not outcompete M1 buyer-proof spend or execution priority.

## Tool Routing (See ROUTING_MATRIX.md)

Tools are strictly routed per L17 executor classification. No agent may invoke a tool outside its T-level.

---

**Next:** Verify manifests exist in all 5 core repos (`.noetfield/agent_manifest.yml`).
