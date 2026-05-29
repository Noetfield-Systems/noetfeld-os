# Noetfield roadmap (public)

**Product strategy (detail):** [strategy/noetfield-future-path.md](strategy/noetfield-future-path.md)

This page is safe for a **public** repository. Detailed `NF-*` checklists and founder-only ops notes live in **GitHub Issues** and a **local gitignored** folder ([ops/README.md](../ops/README.md)) — not in the repo root.

---

## Horizons

| When | Focus |
|------|--------|
| **Now** | Production www + platform, public chat, API intake, optional Telegram |
| **Next** | Staging, CI validation, legal alignment, pilot-ready console |
| **Later** | RAG, pilot auth hardening, multi-tenant scale |

---

## Shipped on `main` (engineering)

- Public chat (OpenRouter / Gemini + fallback)
- `POST /api/intake` + Postgres persistence
- API-primary web intake (`noetfield-intake-api.js`)
- Telegram webhook + structured `INTAKE:` messages
- Gate intake paths (Trust Brief, Copilot, Bank Pilot)
- Platform/www CI workflows, sitemap generator
- Docs: RUNBOOK, PRACTICAL_PLAYBOOK, STAGING, Bank Pilot demo script

---

## How we track work

| Audience | Where |
|----------|--------|
| **Public / partners** | This file + strategy doc + GitHub Releases |
| **Team + agents** | [GitHub Issues](https://github.com/kazemnezhadsina144-dot/Noetfield/issues) with labels `launch`, `legal`, `engineering` |
| **Founder private** | `ops/private/` (gitignored on your machine) |

**Boundaries:** [PROJECT_BOUNDARIES_LOCKED.md](../PROJECT_BOUNDARIES_LOCKED.md) — Noetfield only in this repo; TrustField and VIRLUX are separate entities.
