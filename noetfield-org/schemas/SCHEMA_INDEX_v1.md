# Motor Schema Index v1

**Status:** OPERATIONAL (NOOS)  
**Authority:** Implements P7 §11–§12, P8 continuation, P8 commissioning  
**Custody pins:** `../CUSTODY_AUTHORITY_PINS_v1.json`  

| Schema | File | Use |
|---|---|---|
| Founder reasoning packet | `founder_reasoning_packet.v1.schema.json` | `ESCALATION_PACKET_BUILDER` output |
| Founder reasoning result | `founder_reasoning_result.v1.schema.json` | `REASONING_RESULT_INGESTOR` input |
| Motor job contract | `motor_job_contract.v1.schema.json` | scheduler dispatch unit |
| Private worker binding | `private_worker_binding.v1.schema.json` | runtime deployment config (non-canonical providers) |

**Terminology:** Receipts and job state use P7 canonical names (`WAITING_FOR_FOUNDER_REASONING`, `COST-T*`). Advisor aliases (`C0`, `REASONING_WAIT`) map via P7 §12.

**Examples (non-canonical):** `../config/examples/cost_policy.example.yaml`, `deployment_bindings.private.example.yaml`

**Absorbed from:** `FOUNDER_CONTINUATION_MOTOR_LOCKED_PACKAGE_v1/schemas/` — harmonized 2026-07-10.
