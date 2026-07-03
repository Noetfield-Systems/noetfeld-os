# NOOS Self-Healing Ecosystem v1

**Purpose:** Autonomous continuous audit, fix, research, and proposal generation running 24/7 across all org repos.

---

## Architecture

The self-healing system operates in 4 layers, forming a continuous cycle:

```
┌─────────────────────────────────────────────────────────────┐
│                    AUDIT LAYER (15 min)                      │
│   Scan for failures, masking, drift, SLO misses             │
│   Output: audit-findings-v1.json                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├─→ Safe findings (low-risk) → Auto-fix
                   │
                   └─→ High-risk findings → Escalate for research
                   
┌──────────────────┴──────────────────────────────────────────┐
│                    HEAL LAYER (30 min)                       │
│   Auto-fix safe issues: cache, retries, config resets       │
│   Output: healing-handoff-v1.json, heal-report              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   └─→ Escalated findings → Researcher
                   
┌──────────────────┴──────────────────────────────────────────┐
│                  RESEARCHER LAYER (1 hour)                   │
│   Deep-dive investigation of escalated findings             │
│   Analyze: history, integrations, drift, cross-deps         │
│   Output: research-findings-v1.json                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   └─→ Research reports → Specialist
                   
┌──────────────────┴──────────────────────────────────────────┐
│                 SPECIALIST LAYER (2 hours)                   │
│   Propose high-confidence fixes based on research           │
│   Classify: auto-ready vs manual review needed              │
│   Output: specialist-proposals-v1.json + GitHub issue       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   └─→ Proposals → Next heal cycle
                   
┌──────────────────┴──────────────────────────────────────────┐
│           ORCHESTRATOR LAYER (3 hours)                       │
│   Aggregate health across all org repos                      │
│   Consolidate findings, create org dashboard                │
│   Coordinate next audit cycle                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Workflows

| Workflow | Schedule | Role | Input | Output |
|----------|----------|------|-------|--------|
| **noos-workflow-audit.yml** | Every 15 min | Audit | Workflow states, logs | `noos-audit-findings-v1.json` |
| **noos-self-heal.yml** | Every 30 min | Heal | Audit findings | `noos-healing-handoff-v1.json` |
| **noos-researcher.yml** | Hourly | Research | Escalated findings | `noos-research-findings-v1.json` |
| **noos-specialist.yml** | Every 2 hours | Propose | Research findings | `noos-specialist-proposals-v1.json` |
| **noos-cross-repo-orchestrator.yml** | Every 3 hours | Coordinate | All repos' health | Org dashboard |

---

## Scripts

### `scripts/noos_self_heal_v1.py`
Auto-fixes safe issues only:
- **Cache invalidation** — Stale GitHub action caches, Docker layer caches
- **Retry logic** — Retry flaky/transient test failures
- **Config reset** — Unlock stuck workflow state, courtesy signals
- **Dependency updates** — Patch-only updates within version constraints

**No approval required.** Returns exit code 1 only if escalations exist.

### `scripts/noos_researcher_v1.py`
Deep-dives into escalated findings:
- **Workflow history** — Last 10 runs, failure rate, flakiness detection
- **Integration health** — Check Supabase, GitHub, Slack endpoints
- **Configuration drift** — Git history of recent changes
- **Cross-repo dependencies** — Which repos consume the failing component

**Investigation depths:** quick (30s), standard (120s), deep (300s)

### `scripts/noos_specialist_v1.py`
Proposes fixes from research:
- **Systematic flakiness** → Add retry logic, adjust timeouts
- **Integration issues** → Add fallback, circuit breaker, increase timeouts
- **Config drift** → Audit gate, snapshot baseline

**Confidence scoring:** Returns only proposals with >75% confidence for automation.

---

## State Transfer (noos-healing-handoff-v1.json)

Persists state across cycles so each layer knows what prior layers did:

```json
{
  "version": "1.0",
  "last_run": "2026-07-03T23:50:00Z",
  "cycle_count": 42,
  "fixed_issues": ["cache_stale_gel_ci", "retry_transient_test_42"],
  "escalated_issues": ["slo_miss_schedule_canary", "integration_supabase_timeout"],
  "research_findings": [...],
  "specialist_proposals": [...],
  "metrics": {
    "total_fixes_attempted": 156,
    "total_fixes_succeeded": 142,
    "success_rate": 0.91
  },
  "cross_repo_status": {
    "noetfeld-os": {...},
    "Noetfield": {...},
    "TrustField": {...}
  }
}
```

---

## Safe Fixes Classification

### Low-Risk (Auto-Apply, No Approval)
- ✓ Cache invalidation (expires automatically)
- ✓ Retry logic (bounded attempts, exponential backoff)
- ✓ Dependency patch updates (within semver constraints)
- ✓ Config resets (return to baseline state)

### Medium-Risk (Researcher Reviews, Specialist Proposes)
- ⚠ Increase timeout thresholds (may hide real issues)
- ⚠ Add fallback logic (may mask integration problems)
- ⚠ Update deployment config (could affect live services)

### High-Risk (Escalate to Human)
- ✗ Disable failing tests or lints
- ✗ Remove monitoring or assertions
- ✗ Change authentication/authorization
- ✗ Modify payment/billing logic

---

## Escalation & Review Flow

1. **Audit finds issue** → Classify as safe or high-risk
2. **Safe fixes** → Execute immediately, update handoff
3. **High-risk findings** → Escalate to researcher
4. **Researcher investigates** → Build diagnosis with confidence score
5. **Specialist proposes** → Generate fix proposal for next cycle
6. **Manual review** → Create GitHub issue for human approval
7. **Next heal cycle** → Execute approved proposals

---

## Cross-Repo Coordination

Orchestrator runs every 3 hours and:
- Fetches health status from all org repos (noetfeld-os, Noetfield, TrustField)
- Consolidates findings into org-wide dashboard
- Identifies repo interdependencies
- Alerts on org-level SLO misses

**Repos monitored:**
- `Noetfield-Systems/noetfeld-os` (primary, this repo)
- `Noetfield-Systems/Noetfield` (product runtime)
- `Noetfield-Systems/TrustField` (compliance/governance)

---

## Metrics & Dashboards

### Per-Cycle Metrics
```json
{
  "findings": {
    "total": 25,
    "blocking": 3,
    "dependencies": 22
  },
  "healing": {
    "fixed": 8,
    "escalated": 3,
    "failed": 0,
    "success_rate": 1.0
  },
  "research": {
    "investigated": 3,
    "systematic_issues": 1,
    "integration_issues": 1,
    "unknown": 1
  },
  "proposals": {
    "generated": 3,
    "high_confidence": 2,
    "ready_for_automation": 1,
    "require_review": 2
  }
}
```

### Archive
All reports stored in `receipts/proof/`:
- `noos-kaizen-self-heal-report-v1.json`
- `noos-kaizen-researcher-report-v1.json`
- `noos-kaizen-specialist-proposals-v1.json`

---

## Monitoring & Alerts

### Logging
Each workflow step outputs JSON critique blocks:
```json
{
  "overall_ok": true,
  "findings": [
    "Fixed 8 safe issues",
    "Escalated 3 high-risk findings to researcher"
  ]
}
```

### Alerts
- **High escalation count** → Warning if >5 escalations per cycle
- **Success rate <95%** → Review failures
- **Research consensus low** → Surface uncertain diagnoses
- **Org SLO miss** → Create org-wide ticket

---

## Manual Overrides

Users can manually trigger workflows:
```bash
# Trigger heal cycle immediately
gh workflow run noos-self-heal.yml --ref main

# Trigger deep-dive research
gh workflow run noos-researcher.yml --ref main -f depth=deep

# Manual specialist review
gh workflow run noos-specialist.yml --ref main
```

---

## Future Enhancements

**Phase 2:** Auto-file Kaizen proofs on SLO miss/drift (requires audit approval gate)

**Phase 3:** ML-based fix confidence scoring (train on past proposals + outcomes)

**Phase 4:** Self-updating workflow constraints (learn optimal timeouts, retry counts from data)

---

## Running Locally

Test scripts without side effects:

```bash
# Test self-heal (dry-run)
python3 scripts/noos_self_heal_v1.py --dry-run

# Test researcher (no escalations = no work)
python3 scripts/noos_researcher_v1.py --depth quick

# Test specialist (no research = no proposals)
python3 scripts/noos_specialist_v1.py
```

All scripts are stateless and can be run in any order for testing.

---

**Status:** ✓ Phase 1 complete (audit + heal + research + specialist running 24/7)

**Next:** Deploy orchestrator to aggregate org health; monitor first week of production runs.
