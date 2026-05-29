# Evidence Pack JSON Schema v1

Document key: `noetfield-evidence-pack-json-schema-v1`

Portable, signed, auditor-verifiable package reconstructing governance state for a scope/time window.

## Required fields

`pack_id`, `scope`, `timestamp`, `manifest_sha256`, `snapshots[]`, `events_url`, `lineage_graph`,
`drift_summary`, `decision_logs`, `signatures[]`

## Transport

`pack.json` + `data.tar.gz` + `manifest.sha256` + `manifest.sig` (detached HSM signature).

## Verification

`verify.sh` rehashes files and validates detached signature with public key.

## Signatures

Minimum: snapshot_agent, audit_agent, steward. Aligns with Copilot Governance / Trust Ledger wedge.
