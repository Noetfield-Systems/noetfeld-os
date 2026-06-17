# Deploy Copilot Template — CI Gate

**Version:** 1.0.0 · **Plan:** pf-0064 · **SKU:** NF-QS (platform) · **Phase:** 5  
**Law:** CI gate validates shipped template only — no invented packs

---

## One line

`scripts/deploy-copilot-template.sh` is wired into `make verify-final-lock` — validates policy pack load, governance-as-code sample, phase35 demo, and `REGISTRY.json`.

---

## Gate script

**Path:** `scripts/deploy-copilot-template.sh`

| Step | Check |
|------|-------|
| 1 | `load_policy_pack('copilot-governance-v1')` |
| 2 | `load_governance_config(docs/spec/samples/governance-copilot-v1.yaml)` |
| 3 | `make phase35-demo` |
| 4 | `packages/templates/REGISTRY.json` contains `copilot-governance` |

---

## Makefile wire

```makefile
verify-final-lock: final-lock-audit
	bash scripts/deploy-copilot-template.sh
	python3 scripts/audit_intake_email.py
	PYTHONPATH=... python3 -m pytest tests/unit -q
```

**Order:** after `final-lock-audit` · before `audit_intake_email` · before pytest

---

## When it runs

- `make verify-final-lock` (local + CI)
- Portfolio verify when product code touched (pf-0064 acceptance)

---

## Failure modes

| Failure | Fix |
|---------|-----|
| Policy pack missing | Restore `packages/policy-packs/copilot-governance-v1.json` |
| Governance YAML drift | Align `docs/spec/samples/governance-copilot-v1.yaml` |
| phase35-demo fail | Fix governance service / demo fixtures |
| Registry missing template | Update `packages/templates/REGISTRY.json` |

---

## Not in scope

- Bank Pilot template full deploy (stub only)
- Production Cloudflare deploy
- TrustField artifacts

---

## Verify

```bash
grep -q 'deploy-copilot-template' Makefile
bash scripts/deploy-copilot-template.sh
```
