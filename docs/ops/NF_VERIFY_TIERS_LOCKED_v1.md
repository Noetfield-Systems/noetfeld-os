# NF Verify Tiers — LOCKED v1

```yaml
agent_tag: nf-local-repo-agent
status: LOCKED
authored_at: "2026-06-17"
schema_version: nf-verify-tiers-v1
```

## One sentence

> **T0 → T1 → T2 → T3 — green each tier before ship; machines win.**

## Tier map

| Tier | Make target | When |
|------|-------------|------|
| **T0** | `make verify-tier0` | Session boot · NF-GAOS W0/W1 gate |
| **T1** | `make verify-tier1` | Merge readiness · ship-verify bundle |
| **T2** | `make verify-tier2` | GTM live · dev stack + buyer pages |
| **T3** | `make verify-tier3` | Release bundle · plan-with-no-asf-verify |

## Commands (canonical)

```bash
make verify-tier0   # nf-gaos-w1
make verify-tier1   # ship-verify
make verify-tier2   # verify-gtm
make verify-tier3   # plan-with-no-asf-verify
make verify-all-tiers   # T0 → T1 → T2 → T3 sequential
```

## Governance runtime (post-T3 optional)

```bash
make verify-final-lock   # deploy-copilot-template + unit pytest
bash scripts/deploy-copilot-template.sh
```

## Notes

- **T2** auto-boots dev stack when `:13080` health fails (`verify-gtm.sh`).
- **T3** requires dev stack for UI e2e, gtm-ops link parity, copilot pilot/procurement e2e.
- **Procurement page** is a buyer diligence surface — ops doc hrefs allowed; excluded from static-www P0 leak scan.
- **Staging smoke** runs only when `NF_STAGING_URL` is set.

*NF Verify Tiers · locked 2026-06-17*
