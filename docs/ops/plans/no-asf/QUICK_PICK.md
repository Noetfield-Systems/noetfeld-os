# PLAN WITH NO ASF — quick pick

When the founder says **PLAN WITH NO ASF**, start here. Pick the next **agent** item (not `asf_only`).

**Full registry:** [registry.json](./registry.json) (1000 plans) · **Update:** `python3 scripts/generate-plans-registry.py`

## Next 25 agent-ready plans

1. **NF-PLAN-0110** · P1/T1 · Pilot rate limits and auth scopes for workspace ui  
   Verify: `pytest and/or make ship-verify; area=workspace-ui; pattern=rate-limit`
1. **NF-PLAN-0111** · P1/T1 · Webhook emission on www gtm state transitions  
   Verify: `pytest and/or make ship-verify; area=www-gtm; pattern=webhook-event`
1. **NF-PLAN-0112** · P1/T1 · Audit-export field bundle for devex decisions  
   Verify: `pytest and/or make ship-verify; area=devex; pattern=audit-export`
1. **NF-PLAN-0113** · P1/T1 · Deterministic replay test for ci cd rule version  
   Verify: `pytest and/or make ship-verify; area=ci-cd; pattern=replay-test`
1. **NF-PLAN-0114** · P1/T1 · Cross-tenant negative tests for security  
   Verify: `pytest and/or make ship-verify; area=security; pattern=tenant-isolation`
1. **NF-PLAN-0115** · P1/T1 · Prometheus metrics and dashboards for data migrations  
   Verify: `pytest and/or make ship-verify; area=data-migrations; pattern=metrics`
1. **NF-PLAN-0117** · P1/T1 · Request validation against locked schema for docs diligence  
   Verify: `pytest and/or make ship-verify; area=docs-diligence; pattern=schema-validate`
1. **NF-PLAN-0118** · P1/T1 · YAML/JSON examples pack under docs/spec/examples  
   Verify: `pytest and/or make ship-verify; area=msb-partner; pattern=examples-pack`
1. **NF-PLAN-0119** · P1/T1 · Deprecation notice and version bump for legacy observability path  
   Verify: `pytest and/or make ship-verify; area=observability; pattern=deprecation`
1. **NF-PLAN-0120** · P1/T1 · Load test baseline and p95 budget for performance  
   Verify: `pytest and/or make ship-verify; area=performance; pattern=performance`
1. **NF-PLAN-0201** · P2/T1 · Add or extend API endpoint for www gtm  
   Verify: `pytest and/or make ship-verify; area=www-gtm; pattern=api-endpoint`
1. **NF-PLAN-0202** · P2/T1 · Integration tests covering devex happy path and 409 guards  
   Verify: `pytest and/or make ship-verify; area=devex; pattern=integration-test`
1. **NF-PLAN-0203** · P2/T1 · Align OpenAPI spec with implemented ci cd routes  
   Verify: `pytest and/or make ship-verify; area=ci-cd; pattern=openapi-sync`
1. **NF-PLAN-0204** · P2/T1 · Supabase migration for security tables and RLS  
   Verify: `pytest and/or make ship-verify; area=security; pattern=migration-schema`
1. **NF-PLAN-0205** · P2/T1 · Extend tle-smoke or ship-verify check for data migrations  
   Verify: `pytest and/or make ship-verify; area=data-migrations; pattern=smoke-script`
1. **NF-PLAN-0206** · P2/T1 · Governance console surface for testing read-only v0  
   Verify: `pytest and/or make ship-verify; area=testing; pattern=console-ui`
1. **NF-PLAN-0207** · P2/T1 · WWW / trust-ledger copy block for docs diligence buyer line  
   Verify: `pytest and/or make ship-verify; area=docs-diligence; pattern=www-copy`
1. **NF-PLAN-0209** · P2/T1 · Diligence one-pager evidence for observability controls  
   Verify: `pytest and/or make ship-verify; area=observability; pattern=diligence-doc`
1. **NF-PLAN-0210** · P2/T1 · Pilot rate limits and auth scopes for performance  
   Verify: `pytest and/or make ship-verify; area=performance; pattern=rate-limit`
1. **NF-PLAN-0211** · P2/T1 · Webhook emission on trust ledger state transitions  
   Verify: `pytest and/or make ship-verify; area=trust-ledger; pattern=webhook-event`
1. **NF-PLAN-0212** · P2/T1 · Audit-export field bundle for governance api decisions  
   Verify: `pytest and/or make ship-verify; area=governance-api; pattern=audit-export`

## Recently completed (update via `scripts/update-plan-status.py`)

- **NF-PLAN-0102** — docs diligence integration tests + 409 guards (`verify-docs-diligence.sh`)
- **NF-PLAN-0103** — msb partner OpenAPI sync + trust ledger routes (`verify-msb-partner-openapi.sh`)
- **NF-PLAN-0104** — observability tables migration + RLS (`verify-observability-migration.sh`)
