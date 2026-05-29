# Noetfield Bank-Grade Implementation Design v1.0

Document key: `noetfield-bank-grade-implementation-design-v1`

Production multi-service topology:

- Edge: API Gateway, identity, policy pre-check
- Core: L1 normalization → CDA/PHO → MECR (L2) stateless cluster
- L3 EGS: enforcement + append-only audit (no financial logic persistence)
- L4: SoT graph (reference/trace only — Neo4j-style index, no decision logic)

Sequence: intake → auth → L1 → CDA → MECR → EGS → L4 trace → external handoff.

Failure modes: L2 mismatch → REWRITE; SoT orphan → REJECT; boundary violation → HARD BLOCK.
