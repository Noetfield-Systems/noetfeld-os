# @noetfield/auth-core

Shared Supabase SSR auth helpers per SG `auth_core_interface_spec_v1.json`.

## Exports

- `createBrowserClient` / `createServerClient` — `@supabase/ssr` adapters
- `evaluateAuthGuard` — middleware redirect logic (`getClaims()` session flag required)
- `REQUIRED_AUTH_ROUTES` — `/auth/sign-in`, `/auth/sign-up`, `/auth/callback`, `/auth/sign-out`
- Types: `Venture`, `Role`, `AppMetadata`

## Server law

Pass `hasSession` from `supabase.auth.getClaims()` — not `getSession()` alone.

## Build

```bash
cd packages/auth-core && npm install && npm run build
```
