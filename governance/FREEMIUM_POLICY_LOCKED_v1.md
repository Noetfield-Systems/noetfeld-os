# Freemium Policy (locked v1)

**Sandbox v2** — observe-only product access. Not a fourth contract SKU.

---

## Scope

| Surface | Route | Commercial status |
|---------|-------|-------------------|
| Developer sandbox | `/start/` | Free product access |
| Trial orientation | `/copilot/trial/` | Free product access |
| Contract SKUs | Trust Brief · Copilot Readiness Pack · Bank Pilot | Paid engagements only |

---

## Observe vs Enforce

| Capability | Free sandbox (`observe`) | Paid pack (`enforce`) |
|------------|--------------------------|------------------------|
| `POST /api/sandbox/evaluate` | Yes — capped (50 / 14 days) | Production `/api/v1/governance/evaluate` |
| Mock M365 connectors | Yes | Real metadata index |
| Board PDF export | Watermarked orientation PDF | Production board pack |
| Human approver / HITL | Preview only | Named approver chain |
| Factory catalog runs | 3 observe-mode demos | Full factory dispatch |
| Mode flag | `observe` | `enforce` or `shadow` (Bank Pilot) |

**Rule:** Free tier never enables enforce mode, production connectors, or uncapped evaluates.

---

## Server caps (Sandbox v2)

- `POST /api/sandbox/provision` — work email required; consumer domains blocked
- Redis-backed session (`nf:sbx:session:*`) with in-memory fallback
- Provision rate limit: 10 / hour / client IP (configurable)
- Evaluate cap: 50 per session (configurable via `SANDBOX_EVALUATE_LIMIT`)
- Session TTL: 14 days (configurable via `SANDBOX_TRIAL_DAYS`)
- Usage warning at 80% cap (40/50 evaluates)

---

## Export moment commerce

At Trial OS step 5 (`/start/#trial-os`):

1. Watermarked board PDF — `GET /api/sandbox/export/board.pdf`
2. Copilot Readiness upgrade CTA — intake URL with RID pre-filled
3. Factory demo buttons — observe-only orientation for 3 live factories

Stripe checkout (when wired) remains **commercial licensing only** — not a sandbox entitlement.

---

## Commercial ladder (public)

```
Demo → Sandbox → Copilot Readiness Pack → Trust Brief → Bank Pilot
```

**Removed from public ladder:** QuickScan as a standalone retail step. QuickScan remains a **sub-lane** of Copilot Readiness Pack per `OFFERINGS_LOCKED.md`, not a separate contract SKU on `/copilot/trial/`.

---

## Verification

```bash
make verify-freemium-policy
```

Checks: policy doc present, sandbox API routes wired, trial page ladder aligned, observe mode in client + server.

---

## Locked constraints (preserve)

- Three contract SKUs only on public surfaces
- Non-custodial — no payment execution / MSB
- Sandbox = product access, not retail SKU
- Factory catalog platform-only (no public self-serve factory billing)
