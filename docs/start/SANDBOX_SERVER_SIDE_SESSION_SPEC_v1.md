# Sandbox server-side session persistence (spec v1)

**Queue id:** `ship-sandbox-server-side-057`  
**Status:** Spec only — optional upgrade from `localStorage` (`nf_sandbox_v1`)

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
make ship-verify   # includes sandbox session API smoke
```

*Orientation spec · ship-057 pending implementation*
