# Receipt Schemas v2

## Cycle receipt (every tick)

```json
{
  "schema": "autorun-cycle-receipt-v2",
  "workflow_id": "", "sandbox_id": "", "lane": "",
  "trigger_source": "schedule",
  "started_at": "", "finished_at": "",
  "state_before": "", "state_after": "",
  "transition_log_tail": [],
  "command": "", "exit_code": 0,
  "stdout_tail": "", "stderr_tail": "",
  "queue_head_before": "", "queue_head_after": "",
  "dirty_before": 0, "dirty_after": 0,
  "cost": {
    "provider": "", "model": "",
    "tokens_in": 0, "tokens_out": 0,
    "unit_cost_usd": 0, "total_usd": 0
  },
  "value_class": "revenue_path|proof_asset|risk_reduction|hygiene|none",
  "sink_invariant": {
    "law": "sum(origin_counts) == sink_count",
    "counts": {}, "provenance_tags": {},
    "verdict": "PASS|BLOCKED_WITH_REASON"
  },
  "founder_blocked": { "count": 0, "oldest_id": "", "priority": "", "age_seconds": 0, "escalated": false },
  "blocker_reason": null,
  "evidence": [{ "command": "", "exit_code": 0, "output": "" }],
  "next_action": ""
}
```

## Gate receipt (any YES/NO decision)

```json
{
  "schema": "gate-receipt-v1",
  "decision": "YES|NO",
  "reason": "",
  "evidence": [{ "command": "", "exit_code": 0, "output": "" }]
}
```

## External-verify receipt (only valid ship proof)

```json
{
  "schema": "external-verify-receipt-v1",
  "runner": "github-action|separate-worker",
  "run_url": "",
  "checks": [{
    "url": "", "fetched_at": "",
    "follow_redirects": false,
    "http_status": 0,
    "body_sha256": "",
    "required_markers_present": [],
    "forbidden_markers_absent": [],
    "verdict": "PASS|FAIL"
  }],
  "seconds_after_deploy": 0
}
```

## Improvement receipt (Kaizen)

```json
{
  "schema": "improvement-receipt-v2",
  "class": "machine_safe|founder_gated",
  "source": "failed_check|drift|throttle_roi|audit_finding",
  "diff_summary": "", "expected_effect": "",
  "expected_roi": { "cost_saved_usd": 0, "risk_reduced": "", "revenue_unblocked": "", "build_cost_usd": 0 },
  "rollback_command": "",
  "external_verify_before": "", "external_verify_after": "",
  "auto_rolled_back": false
}
```

## Drift receipt (L12)

```json
{
  "schema": "drift-receipt-v1",
  "detected_at": "",
  "surface": "config|worker_version|cron_schedule|route_binding|content",
  "committed_truth": "", "deployed_truth": "",
  "diff": "",
  "auto_filed_improvement_id": ""
}
```

## Heartbeat (daily per system)

```json
{
  "schema": "autorun-heartbeat-v2",
  "date": "YYYY-MM-DD",
  "loops": [{
    "workflow_id": "", "lane": "", "last_run_at": "", "state": "",
    "sink_invariant_ok": true,
    "cost_window_usd": 0,
    "cost_per_complete_usd": 0,
    "spend_by_value_class": { "revenue_path": 0, "proof_asset": 0, "risk_reduction": 0, "hygiene": 0, "none": 0 },
    "throttled_roi": false
  }],
  "drift": { "checked": true, "mismatches": [] },
  "founder_blocked_total": 0,
  "founder_gated_improvements": [{ "id": "", "expected_roi": {}, "age_days": 0 }],
  "escalations": []
}
```

## Throttle rule (L11)

```
window = trailing 7 days per workflow
if spend[value_class=none] / spend[total] > 0.30:
    state -> THROTTLED_ROI
    frequency -> half
    heartbeat.escalations += workflow_id
Recovery: founder review OR two consecutive windows under threshold.
```

Forbidden marker starter set (extend per project): local user paths (`/Users/`), personal repo IDs where an org is canonical, `— skipped` fake-green lines, bare `—` placeholder counters, internal hostnames, secret patterns.
