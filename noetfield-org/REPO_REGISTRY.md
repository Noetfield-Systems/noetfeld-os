# Noetfield Org Repo Registry

Status: active
Plane: L17 org sync

This registry defines the core repos participating in the org sync plane. It is a coordination layer only; it does not replace repo-local SSOTs or lane-specific vaults.

## Core repos

| Repo | Canonical GitHub repo | Local role | Required registry files |
|---|---|---|---|
| SourceA | `noetfield-systems/sourcea` | design + spine + brain foundation | `.noetfield/agent_manifest.yml`, `.github/copilot-instructions.md` |
| TrustField-Technologies | `Noetfield-Systems/TrustField-Technologies` | peer delivery plane | `.noetfield/agent_manifest.yml`, `.github/copilot-instructions.md` |
| noetfeld-os | `Noetfield-Systems/noetfeld-os` | GEL runtime + control process | `.noetfield/agent_manifest.yml`, `.github/copilot-instructions.md` |
| sina-governance-SSOT | `kazemnezhadsina144[-]dot/sina-governance-SSOT` | governance registry / SSOT lane | `.noetfield/agent_manifest.yml`, `.github/copilot-instructions.md` |
| Noetfield | `Noetfield-Systems/Noetfield` | public brand + commercial surface | `.noetfield/agent_manifest.yml`, `.github/copilot-instructions.md` |

## Slug migration law

The legacy slug `kazemnezhadsina144[-]dot` is a **forbidden active-config marker**.

- Allowed: historical docs, receipts, archaeology notes.
- Forbidden: active repo URLs, active dispatch defaults, active owner handles, active manifest defaults, active agent-routing config.

## Coordination notes

- The integrator protocol is support-only for task arbitration.
- Repo-local truth remains local to each repo.
- Cross-repo synchronization should land as receipts and registry rows, not as a new parallel doctrine.
