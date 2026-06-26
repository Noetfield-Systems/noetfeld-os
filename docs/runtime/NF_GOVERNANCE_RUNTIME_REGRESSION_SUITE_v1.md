# Governance Runtime Regression Suite

**Version:** 1.0.0 · **Plan:** pf-0075 · **SKU:** NF-RD (platform) · **Phase:** 8  
**Law:** `make verify-final-lock` green on every ship — Governance Runtime 10-step regression gate

---

## One line

Maps Governance Runtime 10-step LOCK to `verify-final-lock` — final-lock audit · deploy-copilot-template · intake email · unit pytest.

---

## Regression chain (`make verify-final-lock`)

| Step | Command | Gate |
|------|---------|------|
| 1 | `python3 scripts/audit_final_system_lock.py` | `violations: 0` |
| 2 | `bash scripts/deploy-copilot-template.sh` | Policy pack · governance YAML · phase35 demo · REGISTRY |
| 3 | `python3 scripts/audit_intake_email.py` | `operations@noetfield.com` canonical |
| 4 | `python3 -m pytest tests/unit -q` | All unit tests pass (229+ at LOCK) |
| 5 | `bash scripts/wait-dev-www-ready.sh` | Static www needles before UI e2e (cold-boot safe) |

**Pre-demo bundle:** `make verify-gtm` chains static-www · wait-dev-www-ready · verify-ui-e2e · copilot-pilot-e2e · procurement-pack-e2e.

---

## Governance Runtime 10-step mapping

| GR step | Regression check |
|---------|------------------|
| Policy packs on disk | deploy-copilot-template step 1 |
| Governance-as-code sample | deploy-copilot-template step 2 |
| Phase 3.5 demo | `make phase35-demo` in deploy script |
| Template registry | REGISTRY.json assert |
| Public API contract | pytest `test_public_gtm_alignment` etc. |
| Intake spine | audit_intake_email.py |
| Final system lock | audit_final_system_lock.py |

**Private LOCK:** `~/.sina/agent-workspaces/noetfield_cloud/commercial-goal/GOVERNANCE_RUNTIME_10_STEP_LOCKED_v1.md`

---

## When to run

- Before every merge to main
- After portfolio waves touching product (`pf-0075 acceptance`)
- CI equivalent: `make verify-final-lock`

```bash
cd Noetfield-All-Documents/Noetfield
make verify-final-lock
```

---

## Not in scope

- Production Cloudflare deploy
- TrustField regression suite (see `verify-portfolio-300-phase9.sh`)
- E2E browser automation (separate `verify-ui-e2e` · use `wait-dev-www-ready.sh` first)

---

## Verify

```bash
grep -q 'verify-final-lock' Makefile
bash scripts/deploy-copilot-template.sh
make verify-final-lock
```
