# Noetfield Dual-Layer Documentation Standard v1.0

Document key: `noetfield-dual-layer-documentation-standard-v1`

Industry-grade spec separating Vision (WHY/WHAT/OUTCOME) from Engineering (HOW/TRUTH).

## Canonical structure

Every document: A Vision Layer, B Engineering Layer, C Traceability Map, D Governance Metadata.

## Vision rules

No implementation details, schemas, DB, or APIs. Readable by non-engineers.

## Engineering rules

Fully technical, deterministic, testable. No narrative language.

## Traceability rule

If any Vision element lacks Engineering mapping → document is INVALID.

## Layer priority

Engineering overrides Vision on execution conflicts. Authoritative layer: Engineering only.
