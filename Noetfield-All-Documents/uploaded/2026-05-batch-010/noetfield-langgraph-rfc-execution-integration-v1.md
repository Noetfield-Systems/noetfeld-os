# Noetfield LangGraph + RFC Integration v1.0

Document key: `noetfield-langgraph-rfc-execution-integration-v1`

Pipeline: RFC (GitHub) → CI → RFC Compiler → LangGraph DAG → Event Ledger.

## RFC output contract

Each RFC may include `execution_graph.json` with nodes: LLM_NODE, VALIDATION_NODE,
POLICY_NODE, STATE_NODE.

## Runtime binding rules

1. RFC immutable after compilation (change = new graph version)
2. Graph cannot bypass kernel — all outputs commit to ledger
3. LLM sandboxed — cannot mutate state directly
4. All edges are enforced transitions

## Replay

RFC + event log + graph → deterministic re-execution → hash compare → drift detection.
