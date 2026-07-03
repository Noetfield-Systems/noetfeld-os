# L17 Tool Routing Matrix

**Last Updated:** 2026-07-03T00:00:00Z  
**Status:** Active Enforcement  
**Canonical Source:** This file (ROUTING_MATRIX.md)

## L17 Executor Tiers & Tool Access

Tool routing is **L17-exclusive**. No agent may invoke tools outside its tier. This matrix is the source of truth; do not create separate tool doctrine.

### T0: GitHub Actions (Primary Orchestrator)
**Execution Layer:** CI/CD workflows · automated dispatch · system orchestration  
**Authority:** Platform enforcement level

| Tool | Access | Purpose | Workflows |
|------|--------|---------|-----------|
| GitHub Dispatch | Full | Trigger factory/loop ticks | `noos-factory-autorun`, `noos-loop-fleet-tick` |
| GitHub API (repo ops) | Full | Create/merge PRs, manage refs | Deploy hooks, verification gates |
| Vercel Deploy Hook | Full | Trigger web deployment | `vercel-deploy-hook.yml` |
| Railway Deploy | Full | Platform services deployment | `railway-plan-worker-deploy.yml` |
| Cloudflare Workers | Full | Serverless execution | External-verify workers |
| Receipt Writing (filesystem) | Full | Write gate/state receipts | Factory tick, loop fleet tick |
| Secret/Token Access | Full (scoped) | OAuth, API tokens, SSH keys | GitHub App, deployment creds |

**Forbidden for T0:**
- Direct database mutation (use T1)
- Interactive debugging loops
- Unscoped credential exposure
- Manual approval bypass

---

### T1: Copilot (GitHub-Native Repo Worker)
**Execution Layer:** Repository code modification · PR automation · inline verification  
**Authority:** Code-level executor

| Tool | Access | Purpose | Scope |
|------|--------|---------|-------|
| GitHub Issues API | Read/Write | Create/update issues | Within repo only |
| GitHub PR API | Read/Write | Open/review/merge PRs | Within repo + cross-repo on approval |
| File Edit (via VS Code) | Full (on branch) | Code changes, config updates | Within workspace branch |
| Git Commit/Push | Full (on branch) | Commit changes | Working branch only (never main) |
| Local Terminal | Limited | Build validation, test runs | Sandbox environment |
| Copilot Chat | Full | Reasoning & suggestions | Interactive within scope |
| External APIs (SDK) | Read-only | Call service APIs | SourceA gate, TrustField verify endpoints |

**Forbidden for T1:**
- Force push
- Direct main branch mutation
- Secret credential handling (use T0 secrets)
- Out-of-scope file system access
- Background waiting (report and hand off to T0/T3)

**Required for T1:**
- Read repo state before acting
- Do not treat stale June status files as live truth
- Work on branch, open PR for review
- Report SHA, dirty state, test results, files changed

---

### T2: Cursor Local (Heavy Local Builder)
**Execution Layer:** Local development · sandboxed builds · interactive experimentation  
**Authority:** Machine-local execution

| Tool | Access | Purpose | Context |
|------|--------|---------|---------|
| Local Terminal (full) | Full | Build, test, run locally | Workspace-scoped |
| Local File System | Full | Read/write all files | Workspace directory only |
| Package Managers | Full | npm, pip, cargo, etc. | Local dependencies |
| Docker / Containers | Full | Local image build/run | Dev environment only |
| IDEs & Debuggers | Full | VS Code, interactive debug | Local workflow |
| Git (local) | Full | Commit, branch, rebase locally | Before pushing to T1 |
| Sandbox/Interpreter | Full | Execute code locally | No network access unless explicit |

**Forbidden for T2:**
- No push to remote (use T1 to open PR)
- No credential embedding in local code
- No production environment access
- No cross-repo mutations

**Use Cases:**
- Heavy refactoring / feature prototyping
- Local test runs & debug
- Build & dependency resolution
- Prepare clean commits for T1 PR

---

### T3: Codex / Reasoning (Advanced Orchestration)
**Execution Layer:** Cross-repo reasoning · receipt validation · strategy synthesis  
**Authority:** Multi-layered verification & policy

| Tool | Access | Purpose | Authority |
|------|--------|---------|-----------|
| Receipt Reading (all repos) | Full | Audit receipt cascade | Verification state inspection |
| Receipt Validation | Full | Verify signatures, integrity | Receipt authenticity checks |
| Cross-Repo Analysis | Read-only | Compare states across repos | Sync plane validation |
| Brain Config (SSOT) | Full | Read sina-governance-SSOT configs | Policy & constraint definitions |
| Mission Registry | Read-only | Inspect M1–M6 mission state | Mission stack verification |
| GitHub App API | Full | Advisory comments, review decisions | Independent verification comments |
| Codex (Claude reasoning) | Full | Strategic analysis, multi-step planning | Complex scenarios |

**Forbidden for T3:**
- Direct code mutation (suggest to T1)
- Execution without approval from T0/T1
- Unilateral mission override
- Receipt tampering (only validation)

**Required for T3:**
- Publish decisions via GitHub issues/PRs (not direct commits)
- Sign all advisory receipts
- Maintain independent verification audit trail
- No background waiting (report blocking conditions)

---

### T3 Cloud Integrator (Integration Merge Layer)
**Execution Layer:** External system orchestration · merge layer  
**Authority:** Cross-platform coordination

| Tool | Access | Purpose | Systems |
|------|--------|---------|---------|
| Cloud Platforms (Railway, Vercel, Cloudflare) | Full | Deploy, configure, monitor | Infrastructure as code |
| External APIs (Supabase, GitHub Enterprise, etc.) | Scoped | OAuth, data sync, webhooks | Third-party services |
| Merge Conflict Resolution | Full | Resolve deployment conflicts | Deploy → verify cycle |
| Cross-Platform State Sync | Full | Reconcile state across services | Railway ↔ GitHub ↔ Vercel |
| Incident Response | Full | Rollback, emergency fix deploy | Production incidents only |

**Forbidden:**
- Production data mutation without receipt
- Secret exposure in logs
- Rollback without receipt

---

## Enforcement & Audit

**T0 Verification:** GitHub Actions workflow logs (encrypted, retention: 90 days)

**T1 Verification:** Copilot Chat session logs + PR history (retention: 1 year)

**T2 Verification:** Local git history (user-retained)

**T3 Verification:** Receipt cascade + GitHub App advisory log (retention: indefinite)

**Escalation Path:**
1. T0 blocks execution → report to incident channel
2. T1 reports blocker → T0 or T3 must unblock
3. T2 discovers issue → prepare PR for T1, notify T3
4. T3 identifies policy violation → advisory + receipt + blocking label

---

## Migration Note

**Old Tool Doctrine:** Scattered across multiple repos (DEPRECATED)  
**New Doctrine:** This file (ROUTING_MATRIX.md) is canonical  
**Sync Rule:** Any tool routing outside this matrix is **not enforced** and must be documented as historical anomaly or deprecated pattern.

---

## Test & Validation

- [ ] T0 workflows respect their tier
- [ ] T1 Copilot never force-pushes or mutates main
- [ ] T2 Cursor output goes through T1 PR review
- [ ] T3 Codex publishes via issues, not commits
- [ ] Cross-tier handoffs documented in receipts
