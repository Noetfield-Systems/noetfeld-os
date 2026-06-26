# Commercial inbox & packaging routing (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED — operations@ routing after v16 self-serve packaging |
| **Updated** | 2026-06-18 |
| **Inbox** | `operations@noetfield.com` only (public surfaces) |
| **Google Workspace** | **ACTIVE** (2026-06-18) — direct email + Reply works now |
| **Form auto-send (Resend)** | **DEFERRED post-factory** — not P0; factory spine + portfolio waves first |
| **Packaging SSOT** | [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](../WWW_V16_PACKAGING_PLAN_LOCKED_v1.md) |

---

## Sequencing law (founder 2026-06-18)

1. **Factory + portfolio waves** — gates, verify, disk closeout (`make nf-prove-factory-spine`, Phase 16+)
2. **Google Workspace inbox** — **done** · `operations@noetfield.com` receives direct email now
3. **Resend / Vercel form auto-notify** — **deferred until after factory** · not session boot · not queue head

Intake until Resend ships: **mailto:** links · direct email · optional platform persistence — never mandatory sales call.

---

## 1. Inbox principles

1. **Google Workspace inbox is live** — `operations@noetfield.com` receives direct email today (2026-06-03). Reply-from-inbox works.
2. **Form auto-notify deferred post-factory** — `RESEND_API_KEY` on Vercel www wires every form → inbox + auto-ack. Intentionally after factory build wave. Until then: `mailto:` fallbacks + direct email.
3. **Self-serve first** — sandbox users do not need a thread unless they hit limits or request production keys.
3. **RID on every human thread** — footer `data-rid` or evaluate `rid` when escalating.
4. **No sales call for sandbox** — agentic layer may nurture; founder Hub approves outbound only (R-011).
5. **Three contract SKUs** — intake vectors map to Trust Brief · Copilot Pack · Bank Pilot — never invent a fourth product line.

---

## 2. Routing table

| Trigger | Source | Auto? | Route | Subject template |
|---------|--------|-------|-------|------------------|
| Sandbox signup | `/start/` form | Yes — product only | No email required | — |
| Sandbox limit hit | 50 evaluates / 14d expiry | Optional nurture | Agentic queue | `Noetfield — Sandbox upgrade (RID-…)` |
| Production keys | `/docs/api/` · `/pricing/` | No | Trust Brief or pilot intake | `Noetfield — Production API keys (RID-…)` |
| Copilot Governance Pack apply | `/copilot/pilot/` | No | `?interest=pilot` intake | `Noetfield — Governance Pack apply (RID-…)` |
| Trust Brief purchase | `/trust-brief/intake/` | No | SOW kickoff | `Noetfield — Trust Brief Intake (RID-…)` |
| Bank Pilot | `/bank-pilot/` · gate | No | `?vector=bank-pilot` | `Noetfield — Bank Pilot inquiry (RID-…)` |
| Federal / MSP | Lane hubs | No | Lane-specific intake | `Noetfield — Federal Brief (RID-…)` |
| Investor | `/investors/` | No | Agentic → founder | `Noetfield — Investor brief (RID-…)` |

---

## 3. Agentic autonomous workflows (inbox context)

When agentic layer triages inbound:

| Workflow | Agent may | Agent must not |
|----------|-----------|----------------|
| Sandbox nurture | Send async demo link · `/start/` · `/copilot/demo/` | Claim production keys issued |
| Pilot qualify | Book debrief · attach board PDF sample | Sign SOW without founder |
| Trust Brief | Confirm $10k scope · schedule kickoff | Discount or SKU creep |
| Production upgrade | Route to Copilot Governance Pack intake | Bypass M365 readiness story |

**Handoff:** [AGENTIC_COMMERCIAL_HANDOFF_v1.md](./AGENTIC_COMMERCIAL_HANDOFF_v1.md)

---

## 4. Email body minimum (human threads)

```
RID: RID-…
Path: /start/ | /copilot/pilot/ | /trust-brief/intake/ | …
Mode: sandbox | production
Tenant: sandbox-xxxxxxxx (if known)
Ask: [upgrade | Trust Brief | Bank Pilot | federal | MSP]
```

---

## 5. Anti-patterns

- Routing sandbox signups to mandatory sales calls
- Creating `sales@` / `contact@` aliases on public www
- Promising freemium **production** M365 connectors
- Fourth SKU in intake templates
- Agentic send without founder Hub approve (R-011)

---

## 6. Verify

- `make verify-ops-live` — OPS witness SSOT (R-013)
- Public pages link to `operations@noetfield.com` only for **contract** paths
- `/start/` does not require email to operations@ — local session only
- `make verify-ui-e2e` — start · pricing · api sandbox CTAs green
