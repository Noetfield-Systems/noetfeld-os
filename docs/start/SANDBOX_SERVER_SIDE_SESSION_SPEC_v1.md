# Sandbox server-side session persistence (spec v1)

**Queue id:** `ship-sandbox-server-side-057`  
**Status:** Shipped — server-first when `NF_SANDBOX_API=1`; `localStorage` fallback

## Goal

Persist sandbox trial sessions server-side so founders can resume across devices without inventing a fourth contract SKU.

## Non-goals

- Production tenant provisioning (Copilot Governance Pack SOW)
- Payment or custody rails

## API sketch (governance-console backend)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/sandbox/sessions` | Create session · returns `session_id` + limits |
| GET | `/api/v1/sandbox/sessions/{id}` | Resume · evaluates_used · expires_at |
| PATCH | `/api/v1/sandbox/sessions/{id}` | Increment evaluate count · trial_step |

## Client

- `assets/noetfield-sandbox.js`: try server POST when `NF_SANDBOX_API=1`; fallback to `localStorage`
- Workspace UsageMeter reads same session id

## Verify (when implemented)

```bash
cd governance-console/backend && python3 -m pytest tests/test_sandbox_sessions.py -q
make ship-verify   # includes sandbox session API smoke when dev stack up
```

*Orientation spec · ship-057 shipped 2026-06-18*
