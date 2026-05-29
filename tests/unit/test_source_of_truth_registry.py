"""Source-of-truth registry consistency tests."""

from __future__ import annotations

from pathlib import Path

from scripts.ingest_source_inventory import build_payload, summarize_payload


def test_source_document_inventory_paths_exist_and_keys_unique() -> None:
    payload = build_payload()
    documents = payload.inventory["documents"]
    keys = [document["document_key"] for document in documents]

    assert len(keys) == len(set(keys))
    for document in documents:
        assert Path(document["source_path"]).exists(), document["source_path"]
        assert len(document["content_sha256"]) == 64


def test_source_of_truth_decisions_reference_documents() -> None:
    payload = build_payload()
    document_keys = {document["document_key"] for document in payload.inventory["documents"]}

    for decision in payload.sot_registry["decisions"]:
        assert decision["active_document_key"] in document_keys
        assert 0 <= decision["confidence"] <= 1


def test_active_rule_candidates_reference_documents() -> None:
    payload = build_payload()
    document_keys = {document["document_key"] for document in payload.inventory["documents"]}
    allowed_statuses = {
        "active_design_rule",
        "candidate_requires_formalization",
        "reference_only",
    }

    for rule in payload.rule_registry["active_rule_candidates"]:
        assert rule["source_document_key"] in document_keys
        assert rule["activation_status"] in allowed_statuses


def test_ingestion_payload_summary_counts() -> None:
    payload = build_payload()
    summary = summarize_payload(payload)

    assert summary["batch_id"] == "2026-05-combined"
    assert summary["batch_count"] == 7
    assert summary["document_count"] == 66
    assert summary["sot_decision_count"] == 34
    assert summary["active_rule_candidate_count"] == 47
    assert "wp03-npl-formal-grammar-2026-05-npl-1" in summary["active_documents"]
    assert "wp01-context-graph-runtime-edition-v2" in summary["active_documents"]


def test_second_batch_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["perplexity-ai-native-development-guidelines"]["classification"] == "active_reference"
    assert documents["grok-ai-native-dev-system-duplicate"]["classification"] == "duplicate"
    assert documents["posa-saas-first-100-users-launch-strategy-v1"]["classification"] == "external_product_gtm_reference"


def test_new_active_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "agents-must-not-act-on-stale-state" in rule_keys
    assert "trust-infrastructure-required-for-autonomy" in rule_keys
    assert "multi-agent-coordination-protocol-required" in rule_keys
    assert "hybrid-model-routing-policy-required" in rule_keys


def test_third_batch_posa_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["posa-v3-0-source-of-truth"]["classification"] == "active_source_of_truth"
    assert documents["posa-v3-1-autonomous-revenue-system"]["classification"] == "active_source_of_truth"
    assert documents["posa-digital-twin-training-memory-implementation-v1"]["classification"] == "active_source_of_truth"
    assert documents["shopify-price-intelligence-system-v1"]["classification"] == "separate_product_reference"


def test_posa_active_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "posa-continuous-loop-required" in rule_keys
    assert "posa-no-direct-execution-bypass" in rule_keys
    assert "posa-memory-event-log-immutable" in rule_keys
    assert "posa-digital-twin-gates-economic-actions" in rule_keys
    assert "posa-high-impact-actions-require-approval" in rule_keys


def test_fourth_batch_lineage_and_protocol_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["posa-v2-0-source-of-truth"]["classification"] == "superseded_posa_root_sot"
    assert documents["paas-v1-personal-autonomous-agent-system"]["classification"] == "historical_predecessor"
    assert documents["paes-v1-personal-ai-execution-system"]["classification"] == "historical_predecessor"
    assert documents["context-resonance-theory-paper"]["classification"] == "superseded_theory_reference"
    assert documents["aie-protocol-smart-contract-cosmos-architecture"]["classification"] == "active_protocol_module_reference"
    assert documents["context-resonance-theory-paper"]["classification"] == "superseded_theory_reference"
    assert documents["aie-protocol-smart-contract-cosmos-architecture-duplicate"]["classification"] == "duplicate"


def test_fourth_batch_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "crt-structured-constraints-reduce-entropy" in rule_keys
    assert "crt-intent-as-computational-primitive" in rule_keys
    assert "aie-dual-layer-execution-architecture" in rule_keys
    assert "aie-agent-stake-and-validation-required" in rule_keys


def test_fifth_batch_aie_and_aiis_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["aie-protocol-full-technical-whitepaper"]["classification"] == "active_source_of_truth"
    assert documents["aie-protocol-tokenomics-mathematical-model-v1"]["classification"] == "active_source_of_truth"
    assert documents["aie-protocol-tokenomics-adaptive-supply-model"]["classification"] == "superseded_tokenomics_reference"
    assert documents["aie-protocol-smart-contract-cosmos-architecture"]["classification"] == "active_protocol_module_reference"
    assert documents["context-resonance-theory-paper"]["classification"] == "superseded_theory_reference"
    assert documents["aiis-investor-whitepaper-agentic-intelligence-infrastructure"]["classification"] == "separate_product_lineage_reference"
    assert documents["architecture-of-meaning-book-proposal"]["classification"] == "superseded_knowledge_product_reference"


def test_fifth_batch_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "manifesto-intelligence-is-constraint-driven" in rule_keys
    assert "manifesto-agent-loop-fundamental-primitive" in rule_keys
    assert "aie-supply-equilibrium-nsp-target" in rule_keys

def test_sixth_batch_crt_architecture_and_slf_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["context-resonance-ieee-research-paper-crt"]["classification"] == "active_source_of_truth"
    assert documents["context-resonance-theory-paper"]["superseded_by"] == "context-resonance-ieee-research-paper-crt"
    assert documents["architecture-md-v2-event-driven-agentic-system"]["classification"] == "active_implementation_reference"
    assert documents["architecture-of-meaning-semantic-superconductivity-essay"]["classification"] == "active_source_of_truth"
    assert documents["slf-v5-frozen-canonical-spec"]["classification"] == "active_source_of_truth"
    assert documents["sot-engine-auto-running-architecture-v1"]["classification"] == "active_source_of_truth"


def test_sixth_batch_event_and_sot_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "no-action-without-canonical-event" in rule_keys
    assert "halt-protocol-max-two-retries" in rule_keys
    assert "memory-write-requires-state-validation-event" in rule_keys
    assert "sot-mined-from-repetition-not-theory" in rule_keys
    assert "semantic-superconductivity-constraint-density" in rule_keys

def test_seventh_batch_slf_paios_and_noetfield_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["slf-v3-system-logic-framework-epistemic"]["classification"] == "active_source_of_truth"
    assert documents["slf-v2-system-logic-framework"]["superseded_by"] == "slf-v3-system-logic-framework-epistemic"
    assert documents["sot-creation-guidelines-practical"]["classification"] == "active_source_of_truth"
    assert documents["paios-source-of-truth-blueprint-v1"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-ai-organization-runtime-sot-v1"]["classification"] == "active_strategic_reference"
    assert documents["slf-v5-logic-extension-layer-execution-state-control"]["classification"] == "active_execution_layer_reference"


def test_seventh_batch_epistemic_and_noetfield_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "slf-reality-dominance-law" in rule_keys
    assert "slf-invariant-only-repeatable-behavior" in rule_keys
    assert "noetfield-bounded-autonomy" in rule_keys
    assert "noetfield-runtime-event-mediation" in rule_keys
