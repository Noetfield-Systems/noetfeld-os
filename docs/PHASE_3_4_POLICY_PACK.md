# Phase 3.4 Governance Policy Pack

Phase 3.4 turns the backend runtime from auditable infrastructure into a
policy-enforced governed intelligence runtime.

## Scope

This phase adds a deterministic governance policy pack that can later be
mirrored into OPA. The Python evaluator is the authoritative fallback for local
runtime, tests, and early deployments.

## Policy rules

Runtime packs load from `packages/policy-packs/*.json` via `policy_loader.py`.
The Python evaluator remains the authoritative fallback when a pack file is missing.

| Rule | Behavior |
| --- | --- |
| `confidence:min-threshold` | Low-confidence actions require human review. |
| `human-review:high-impact` | High-impact governance actions require review. |
| `autonomy:no-silent-publication` | AI, service, and inspector actors cannot silently publish, export, or approve governed artifacts. |
| `inspectors:bounded-execution` | Inspector collaborations are bounded by a configured limit. |
| `copilot:review-required` | Copilot Governance outputs require human review before publication. |

## Reason codes

- `ALLOW`
- `REQUIRE_HUMAN_REVIEW`
- `VETO_BLOCKED_ACTION`
- `VETO_LOW_CONFIDENCE`
- `VETO_AUTONOMOUS_PUBLICATION`
- `VETO_INSPECTOR_LIMIT`

## Obligations

Every policy decision returns obligations such as:

- `emit_governance_event`
- `retain_audit_trace`
- `preserve_actor_attribution`
- `queue_human_review`
- `capture_reviewer_rationale`

## Copilot Governance demo path

The Copilot Governance use-case now executes through policy:

1. Manual or webhook signal is ingested.
2. Graph relationship is mutated.
3. Graph reflection runs.
4. Workflow enters `pending_review`.
5. Governance runtime evaluates the Copilot use-case action.
6. Policy requires human review.
7. Human approval request event is emitted.
8. Audit/event replay can reconstruct the path.

## Non-goals

- No autonomous publishing.
- No UI-first workflow.
- No replacement of core runtime with Copilot-specific abstractions.
- No OPA dependency requirement before the deterministic policy pack is stable.
