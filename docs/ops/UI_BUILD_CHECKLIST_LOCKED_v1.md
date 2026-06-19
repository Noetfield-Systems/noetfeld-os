# UI Build Checklist (LOCKED v1 — mandatory first read)

| Field | Value |
|-------|--------|
| **Status** | LOCKED — machine-enforced for all agents |
| **Authority** | Supersedes ad-hoc UI edits; read **before** any form, app, or www change |
| **Masterplan** | [WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md](../WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md) |
| **Packaging** | [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](../WWW_V16_PACKAGING_PLAN_LOCKED_v1.md) |
| **Freemium** | [FREEMIUM_POLICY_LOCKED_v1.md](../../governance/FREEMIUM_POLICY_LOCKED_v1.md) |
| **Verify** | `make verify-ui-build-checklist` |

---

## Rule: no UI work without this checklist

Every agent (cloud, local, hub) **must** complete steps 1–8 below before editing HTML, CSS, JS, React, or buyer-facing copy.  
Violation = scope fail → `verify-ui-build-checklist` + `verify-agent-scope` block merge.

**No invitation surfaces.** Public UI is self-serve only: sandbox, demo, async intake. No calendar booking, no “schedule a call”, no sales-invite CTAs.

---

## Step 1 — Read locked UI law (witness)

- [ ] `docs/WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md` (UI-01 … UI-10)
- [ ] `OFFERINGS_LOCKED.md` (3 contract SKUs + free sandbox)
- [ ] `governance/FREEMIUM_POLICY_LOCKED_v1.md` (observe vs enforce)
- [ ] `.cursor/agent-memory/MEMORY_LOCKED.yaml` → `tier1_ui_v18` + R-012

---

## Step 2 — Pick the UI upgrade ID (intent)

| ID | Surface | Done when |
|----|---------|-----------|
| UI-01 | Live Proof Hero (`/`) | `data-live-proof-hero` + `noetfield-live-proof.js` |
| UI-02 | Trial OS (`/start/`) | `data-trial-os-flow` + server sandbox v2 API |
| UI-03 | Command Center Shell | App shell v2 + usage meter |
| UI-04 | Design tokens | Single token source, no drift |
| UI-05 | Homepage compression | ≤8 sections, four-act journey |
| UI-06 | Receipt Studio | TLE export dock markers |
| UI-07 | Decision timeline | Audit timeline from evaluate |
| UI-08 | Agent Command Deck | `Investigate` deck on dashboard |
| UI-09 | Motion + a11y | `noetfield-v18-motion.css`, reduced-motion |
| UI-10 | Visual QA | `verify-ui-visual` + Playwright baselines |

Declare which UI-## you are shipping in commit/PR body.

---

## Step 3 — Shell + asset contract (scope)

**www institutional shell (default):**

```html
<link rel="stylesheet" href="/assets/noetfield-tokens.css" />
<link rel="stylesheet" href="/assets/noetfield-shell.css" />
<link rel="stylesheet" href="/assets/noetfield-www.css?v=40" />
<body class="nf-www nf-site-v14">
```

**nf26 agentic pages (`/copilot/demo/`, `/copilot/trial/`):**

```html
<link rel="stylesheet" href="/assets/noetfield-shell.css" />
<link rel="stylesheet" href="/assets/pages/institutional-2026.css" />
<body class="nf26-page">
```

Never hand-patch generated www without updating `scripts/rebuild-www-v6.py` when page is generator-owned.

---

## Step 4 — Commercial guard (no invitation)

- [ ] CTAs: `/start/`, `/copilot/demo/`, `/trust-brief/intake/`, `/pricing/` only
- [ ] **Forbidden on public pages:** `calendar`, `book a call`, `schedule a meeting`, `gate/sales` as primary CTA, `portal/login` for sandbox entry
- [ ] Three contract SKUs only — sandbox is product access, not SKU #4
- [ ] Observe mode in sandbox; enforce/HITL/production = paid pack only

---

## Step 5 — Forms + intake (stable system)

- [ ] Forms use `noetfield-intake-core.js` + `data-nf-intake-form` where applicable
- [ ] Async intake only — `operations@noetfield.com`; no mandatory sales call
- [ ] RID threading via `data-rid-link` / query `request_id`

---

## Step 6 — Sandbox v2 (if touching trial/start)

- [ ] Client: `assets/noetfield-sandbox.js` → `/api/sandbox/*`
- [ ] Server caps: 50 evaluates / 14 days / work email
- [ ] Export moment: watermarked PDF + intake upgrade with RID
- [ ] `make verify-freemium-policy`

---

## Step 7 — Navigation parity

Header/footer must link:

- `/copilot/demo/` · `/copilot/trial/` · `/start/` · pilot intake

Homepage journey must include demo + sandbox + trial paths.

---

## Step 8 — Evidence before ship

```bash
make verify-ui-build-checklist
make verify-static-www
make verify-freemium-policy
make verify-commercial-agentic
./scripts/verify-agent-scope.sh
# With dev stack:
make verify-ui-e2e
make verify-ui-visual
```

---

## Agent enforcement (machine)

| Gate | Enforces |
|------|----------|
| `scripts/verify-ui-build-checklist.sh` | This checklist + markers + no-invitation |
| `.cursor/skills/SKILL-009-ui-build-checklist-mandatory.md` | Agent read order |
| `MEMORY_LOCKED.yaml` R-012 | Session + pre-commit |
| `verify-agent-scope.sh` | SKILL-009 + checklist files exist |
| `verify-www` | Runs UI build checklist |

---

## Version

| Version | Date | Change |
|---------|------|--------|
| v1 | 2026-06-03 | Initial lock — Sandbox v2 + mandatory agent gate |
