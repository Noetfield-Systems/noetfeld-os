# Sandbox Nurture Sequence

**Version:** 1.0.0 · **Plan:** pf-0073 · **SKU:** — (platform funnel) · **Phase:** 7  
**Law:** Self-serve sandbox — 14-day trial · 50 evaluate calls · no mandatory sales call

---

## One line

14-day nurture law for `/start/` Trial OS — stages S0–S4 from sandbox activation to pilot CTA — metrics in [SANDBOX_FUNNEL_METRICS_SPEC_v1.md](../copilot/SANDBOX_FUNNEL_METRICS_SPEC_v1.md).

---

## Trial limits (locked)

| Field | Value |
|-------|-------|
| Trial duration | 14 days |
| Evaluate budget | 50 calls |
| M365 connectors | Mock only in sandbox |
| Sales call | Not required for sandbox |

---

## Nurture stages

| Stage | Day window | Action | CTA |
|-------|------------|--------|-----|
| S0 | Day 0 | Account + environment | Continue in sandbox |
| S1 | Day 1–3 | Mock M365 connect | First evaluate |
| S2 | Day 4–7 | Run evaluates (target ≥5) | View TLE sample |
| S3 | Day 8–12 | Export orientation | Open workspace |
| S4 | Day 13–14 | Pilot CTA | Apply for Governance Pack |

---

## Upgrade path

```text
/start/ sandbox → evaluate → export sample → /trust-brief/intake/?vector=copilot-governance → Copilot Governance Pack ($2k–10k)
```

---

## www alignment

- `/start/index.html` — `#nf-sandbox-nurture-callout` in Trial OS section
- Usage chip: `0/50 evaluates · 14 days left`
- SSOT link in callout footer

---

## Not in scope

- Automated email sends (founder never sends — Hub approves nurture templates)
- Production tenant auto-provision from sandbox alone
- TrustField RPAA intake on same form

---

## Verify

```bash
test -f docs/start/NF_SANDBOX_NURTURE_SEQUENCE_v1.md
grep -q 'NF_SANDBOX_NURTURE_SEQUENCE' start/index.html
grep -q '14-day' docs/start/NF_SANDBOX_NURTURE_SEQUENCE_v1.md
```
