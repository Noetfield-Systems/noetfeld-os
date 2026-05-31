# Noetfield SDK (Python)

Typed HTTP client for the **institutional** API surface documented in [`docs/api/`](/docs/api/).

## Install (development)

```bash
export PYTHONPATH="packages/sdk:packages/types:packages/config:services/governance:..."
```

Or import from the repo after `pip install -e .` with `PYTHONPATH` including `packages/sdk`.

## Usage

```python
from uuid import UUID
from noetfield_sdk import NoetfieldClient

client = NoetfieldClient(
    "https://platform.noetfield.com",
    api_key="your-pilot-key",  # required when GOVERNANCE_PILOT_AUTH_REQUIRED=true
)

result = client.evaluate(
    tenant_id=UUID("00000000-0000-4000-8000-000000000001"),
    organization_id=UUID("00000000-0000-4000-8000-000000000002"),
    action="publish_board_report",
    resource_type="governance_artifact",
    resource_id="demo-1",
    mode="shadow",
)
print(result["request_id"], result["decision"])

ledger = client.get_ledger(tenant_id=UUID("00000000-0000-4000-8000-000000000001"))
export = client.audit_export(request_id=result["request_id"])
```

Contracts align with `packages/types` and `docs/api/openapi.json`. **No payment or custody APIs** — pre-execution governance only.
