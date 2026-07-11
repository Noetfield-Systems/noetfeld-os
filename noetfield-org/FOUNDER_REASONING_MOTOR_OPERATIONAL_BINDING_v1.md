# Founder Reasoning Motor — OPERATIONAL BINDING v1

**Document class:** OPERATIONAL_BINDING (not Library SSOT)  
**Status:** LOCKED  
**Language:** English  
**Locked:** 2026-07-10  
**Owner layer:** NOOS / noetfeld-OS integrator  
**Implements:** SG Master SSOT §0.7 + D5 motor plane  

## Authority pins (commit-pinned custody chain)

See `CUSTODY_AUTHORITY_PINS_v1.json` in this directory for current commit SHAs.  
Wiring receipt: `sina-governance-SSOT/receipts/custody/CUSTODY_WIRING_FOUNDER_REASONING_v1.json`

| Upstream (defines) | Path |
|---|---|
| Master SSOT anchor | `sina-governance-SSOT/ssot/strategy-ssot-v6-split.md` §0.7 |
| Custody matrix | `…/P2-SSOT/LIBRARY_CUSTODY_MATRIX_LOCKED_v1.md` |
| Authority graph | `…/P2-SSOT/AUTHORITY_GRAPH_FOUNDER_REASONING_LOCKED_v1.md` |
| Terminology | `…/P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md` §11–§12 |
| Continuation doctrine | `…/P8-MACHINE-LOOPS/founder-reasoning-continuation-doctrine-LOCKED_v1.md` |
| Commissioning standard | `…/P8-MACHINE-LOOPS/MOTOR_COMMISSIONING_AND_ACCEPTANCE_STANDARD_LOCKED_v1.md` |
| Cost execution doctrine | `…/P10-PRODUCT-LAYERS/COST_EXECUTION_DOCTRINE_LOCKED_v1.md` |
| Motor schemas | `noetfield-org/schemas/` (this repo) |

**Rule:** If upstream pins drift, refresh pins + wiring receipt before claiming custody compliance.

---

## Correction (previous error)

The wrong pattern was:

```text
cheap → HANDOFF_REQUIRED → stop
```

The correct architecture is:

```text
99% low-cost automatic execution
→ 1% Reasoning queue for Founder
→ fast resolution inside existing subscription apps
→ result returns to motor
→ automatic continuation
```

---

## 1. Low-cost automatic path

The motor always starts from the cheapest capable route:

```text
COST-T0 — no model
Python / workflows / tests / rules / schemas / search / CI

COST-T1 — free or very low cost
Small models and low-cost APIs for:
- classification
- extraction
- initial decomposition
- skeleton generation
- draft patch
- summarization
- initial diagnosis

COST-T2 — stronger API models, still budgeted
Only when COST-T0/COST-T1 have failed with real receipts of insufficiency
```

Current practical bindings may be selected from founder deployment sources in **product private bindings** (not listed here).

**Binding rule:** provider names belong in private deployment bindings, not in canonical motor law.

---

## 2. Expensive reasoning path is not automatic

When work truly requires high-level reasoning, the motor must **not** turn on an expensive API by itself.

It must build a complete `FOUNDER_REASONING_PACKET` (see P8 minimum fields) and enqueue to `FOUNDER_REASONING_QUEUE`.

---

## 3. Founder Reasoning Cockpit

Founder enters subscription surfaces (Custom GPT / ChatGPT / Claude / etc.), resolves packet, returns via `REASONING_RESULT_INGESTOR`.

```text
Premium API automation ❌
Subscription-based founder reasoning ✅
```

---

## 4. System does not sleep during reasoning

Park: `WAITING_FOR_FOUNDER_REASONING` on dependent jobs only. Independent branches continue.

---

## 5. Result re-entry

Validate against `schemas/founder_reasoning_result.v1.schema.json`.

```yaml
reasoning_result:
  packet_id:
  heading_id:
  job_id:
  diagnosis:
  chosen_action:
  proposed_change:
  constraints:
  rejected_options:
  confidence:
  verification_requirements:
  founder_authority_statement:
```

Ingress: Custom GPT Action, endpoint, repository dispatch, inbox file, Mobile Cockpit approve/send.

Motor: `result received → schema validation → authority validation → repair/build job → execute → verify → continue`

---

## 6. Cost policy (operational)

```text
cheapest capable → next cheap capable → bounded medium-cost API → FOUNDER_REASONING_QUEUE
```

Degradation codes: `PARTIAL`, `SKIPPED_LLM`, `LLM_PROVIDER_NOT_CONFIGURED` — deterministic loops must not hard-fail on missing LLM.

---

## 7. Lane sequence (architecture v2 fix)

```text
W-DET → W-INTEL-LOW → W-INTEL-BOUNDED → FOUNDER_REASONING_QUEUE → RESULT_INGESTION → continue
```

---

## 8. Required integrator components

1. `ESCALATION_PACKET_BUILDER`
2. `FOUNDER_REASONING_QUEUE`
3. `MOBILE_REASONING_COCKPIT` / action interface
4. `REASONING_RESULT_INGESTOR`

---

## 9. Motor schemas (NOOS operational)

| Schema | Path |
|---|---|
| Packet | `schemas/founder_reasoning_packet.v1.schema.json` |
| Result | `schemas/founder_reasoning_result.v1.schema.json` |
| Job contract | `schemas/motor_job_contract.v1.schema.json` |
| Private binding | `schemas/private_worker_binding.v1.schema.json` |

Index: `schemas/SCHEMA_INDEX_v1.md`. Terminology aliases: SG P7 §12.

Config examples (non-canonical): `config/examples/cost_policy.example.yaml`, `deployment_bindings.private.example.yaml`.

---

## Enforcement (runtime)

- Receipts: use `WAITING_FOR_FOUNDER_REASONING` + `packet_id`; reject bare terminal `HANDOFF_REQUIRED`.
- Use prefixed tiers: `COST-T*`, `MERGE-T*`, `EXEC-T*` per P7 §11–§12.
- ROUTING_MATRIX executor tiers remain `EXEC-T*` namespace.
- Runtime status: `DESIGN_LOCKED` until P8 commissioning cold proofs pass.

---

*Operational binding v1 — implements SG custody chain; not a substitute for Master SSOT or Library doctrine.*
