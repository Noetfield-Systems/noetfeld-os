# GEL — Governance Execution Layer

## What GEL means

**GEL** stands for **Governance Execution Layer**. It is Noetfield's deterministic control plane for agent and automation workflows — **not** a generic acronym we avoid. Public page: **https://www.noetfield.com/gel/**

Tagline: **Policy before execution. Receipt after.**

## What GEL does

- Evaluates operational intent against your **policy pack** before any downstream system runs
- Returns **APPROVE / REVIEW / DECLINE** (or allow/deny in compliance language)
- Emits **Trust Ledger Entries (TLEs)** — tamper-evident decision records for audit and board use

## GEL vs www homepage

| Surface | URL | Audience | Purpose |
|---------|-----|----------|---------|
| **Homepage / Intelligence** | `www.noetfield.com` | Buyers, SMEs, pilots | Consulting, Diagnostic Sprint, Copilot Pack, Trust Brief, intake |
| **GEL product page** | `www.noetfield.com/gel/` | Developers, integrators | Runtime, CLI, hosted API, chain tools |
| **Governance Console** | `platform.noetfield.com/console` | Authorized pilot users | Submit intent, view decisions and compliance log |

The homepage sells **programs and engagements**. GEL is the **execution engine** behind pre-execution governance.

## What ships today (GEL lane)

- **Hosted API:** `https://api.noetfield.com` — health at `/health`, readiness at `/readiness`, decisions at `POST /v1/decision`
- **Chain tools:** `noetfield gate` (local PASS/BLOCK) and `noetfield decide` (remote receipt)
- **PyPI package:** `noetfield-gate` — install with `pip install noetfield-gate`
- **Local dev:** FastAPI + SQLite prototype in `noetfeld-os` repo (port 8001)

## GEL tier ladder (runtime commercial — separate from consulting SKUs)

Documented on `/runtime/` — Starter (~$10K sandbox tier), Standard (~$50K multi-tenant), Trust Ledger tier (~$120K quarterly export). These are **runtime product tiers**, not the same as Trust Brief consulting SKU.
