# NF-GAOS W1 — Governed Agent OS (LOCKED v1)

```yaml
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-17"
status: LOCKED
schema_version: nf-gaos-w1-v1
supersedes_waves: "W0 waves-after table — W1–W2 delivered"
```

## One sentence

> **Gate → orient → voyage → BAVT → panel visibility — four rules · machines win · chat never SSOT.**

## W1 machines (delivered)

| Machine | Command |
|---------|---------|
| Session gate | `make nf-session-gate` |
| Live orient | `make nf-live-orient` |
| Voyage integrity | `make nf-voyage-integrity` |
| Stale guard | `python3 scripts/nf_stale_guard_v1.py --json` |
| Orient cascade | `make nf-orient` (manual only) |
| BAVT | `make nf-bavt` |
| Anti-fragmentation | `make verify-nf-anti-frag` |
| Governance unify scan | `python3 scripts/nf_governance_unify_v1.py --scan --json` |
| Panel export | `bash scripts/nf-panel-export-v1.sh` |
| Full verify | `make verify-nf-gaos-w1` |

## Cursor rules (4 alwaysApply)

- `nf-authority-stack.mdc`
- `nf-routing-card.mdc`
- `noetfield-ask-before-edit.mdc`
- `nf-ship-bundle.mdc`

Retired alwaysApply → MOVED stubs in `noetfield-*.mdc`.

## Routing Panel

- URL: http://127.0.0.1:8780/ → **Noetfield** tab
- API: http://127.0.0.1:8780/api/panel/noetfield

## Founder Action (document only)

Hub one-tap **NF Onboard** → `make nf-onboard` (SourceA Worker `sa-*` implements hub card).

## W3 deferred

Founder-word pipelines: orientation · hospital · maze (Noetfield-scoped) — not on session boot.

*NF-GAOS W1 · locked 2026-06-17*
