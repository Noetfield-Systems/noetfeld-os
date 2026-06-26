# SDK — Local Governance Scaffold

**Version:** 1.0.0 · **Plan:** pf-0065 · **SKU:** NF-QS (platform) · **Phase:** 5  
**Law:** Offline scaffold only — production path is `POST /api/v1/governance/evaluate`

---

## One line

Documents `packages/sdk/examples/local_governance_scaffold.py` — offline Copilot governance demo using shipped policy vocabulary, HMAC-sealed receipts, and human-review routing.

---

## Example path

```
packages/sdk/examples/local_governance_scaffold.py
```

---

## What it demonstrates

| Feature | Detail |
|---------|--------|
| Policy vocabulary | `COPILOT_HIGH_IMPACT` actions from `copilot-governance-v1` |
| Decisions | allow · require human review · deny |
| Receipts | HMAC-SHA256 sealed `Receipt` dataclass |
| Mode | Offline / local only |

---

## Production path

```python
from noetfield_sdk import NoetfieldClient

client = NoetfieldClient("https://platform.noetfield.com", api_key="...")
result = client.evaluate(
    tenant_id=...,
    organization_id=...,
    action="publish_board_report",
    resource_type="governance_artifact",
    resource_id="demo-1",
    mode="shadow",
)
```

See `/docs/api/` and `packages/sdk/README.md`.

---

## Run locally

```bash
export PYTHONPATH="packages/sdk:packages/types:packages/config:services/governance:..."
python3 packages/sdk/examples/local_governance_scaffold.py
```

---

## Not in scope

- Payment transfer limits or custody simulation
- TrustField RPAA client
- MSB execution APIs

---

## Verify

```bash
test -f packages/sdk/examples/local_governance_scaffold.py
test -f docs/sdk/NF_SDK_LOCAL_GOVERNANCE_SCAFFOLD_v1.md
grep -q 'NF_SDK_LOCAL_GOVERNANCE_SCAFFOLD' packages/sdk/README.md
```
