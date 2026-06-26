# Governance-as-Code (LOCKED v1)

**Status:** LOCKED  
**Date:** 2026-06-17  
**Schema:** `packages/schemas/governance.schema.json`  
**Loader:** `services/governance/noetfield_governance/governance_config.py`

---

## Purpose

Declarative governance config that versions with every Trust Ledger Entry. Like Terraform for agent policy — one file controls budget, approval, PII, audit, and policy pack binding.

## Reference instance

`docs/spec/samples/governance-copilot-v1.yaml`

```yaml
governance:
  policy_pack: copilot-governance-v1
  budget:
    max_cost_usd: 5.00
  approval:
    human_required: true
  pii:
    deny: true
  audit:
    enabled: true
    retain_days: 365
  memory:
    encrypted: true
  legal:
    strict: true
```

## Runtime binding

1. Evaluate request may pass `governance_config_path` in payload.
2. Default path used when omitted: `governance-copilot-v1.yaml`.
3. `config_policy_version_hash` returned on evaluate response.
4. Hash bound to RID lineage via audit export.

## Validation

```bash
./scripts/validate-compliance-schemas.sh
```

## Non-goals (v1)

- OPA/Rego deployment
- Multi-file governance modules
- Remote config pull from marketplace
