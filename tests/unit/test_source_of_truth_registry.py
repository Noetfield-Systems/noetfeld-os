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
    assert summary["batch_count"] == 13
    assert summary["document_count"] == 135
    assert summary["sot_decision_count"] == 66
    assert summary["active_rule_candidate_count"] == 97
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
    assert documents["noetfield-ai-organization-runtime-sot-v1"]["classification"] == "superseded_strategic_reference"
    assert documents["slf-v5-logic-extension-layer-execution-state-control"]["classification"] == "active_execution_layer_reference"


def test_seventh_batch_epistemic_and_noetfield_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "slf-reality-dominance-law" in rule_keys
    assert "slf-invariant-only-repeatable-behavior" in rule_keys
    assert "noetfield-bounded-autonomy" in rule_keys
    assert "noetfield-runtime-event-mediation" in rule_keys

def test_eighth_batch_noetfield_v31_and_gie_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["noetfield-ambient-intelligence-nervous-system-sot-v31"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-gie-specification-supplement-v31"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-ambient-intelligence-sot-v30"]["superseded_by"] == "noetfield-ambient-intelligence-nervous-system-sot-v31"
    assert documents["noetfield-ai-organization-runtime-sot-v1"]["classification"] == "superseded_strategic_reference"
    assert documents["governed-execution-system-mvp-blueprint-v1"]["classification"] == "active_commercial_wedge_reference"
    assert documents["noetfield-execution-consensus-vm-v40-blueprint"]["classification"] == "active_source_of_truth"


def test_eighth_batch_gie_and_governance_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "gie-min-confidence-threshold-055" in rule_keys
    assert "governed-execution-deterministic-pipeline" in rule_keys
    assert "noetfield-living-knowledge-graph-central" in rule_keys

def test_ninth_batch_prompt_os_and_gtm_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["noetfield-prompt-system-constitution-v02-mvp"]["classification"] == "active_source_of_truth"
    assert documents["master-strategic-context-engine-v37-efficient"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-strategic-structuring-reasoning-engine-stage2-v20"]["classification"] == "active_source_of_truth"
    assert documents["linkedin-profile-hyper-commercial-v4"]["classification"] == "active_source_of_truth"
    assert documents["trustfield-noetfield-strategic-architecture-locked-fa"]["classification"] == "active_source_of_truth"


def test_ninth_batch_prompt_pipeline_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "prompt-pipeline-strict-stage-sequencing" in rule_keys
    assert "prompt-stage3-golden-execution-command" in rule_keys
    assert "prompt-mvp-action-first-two-step" in rule_keys

def test_tenth_batch_documentation_and_kernel_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["noetfield-dual-layer-documentation-standard-v1"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-rfc-standard-v1-github-ci"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-stack-blueprint-v1-refined-final"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-data-stack-kafka-qdrant-alternative"]["classification"] == "superseded_architecture_draft"
    assert documents["noetfield-data-stack-kafka-qdrant-alternative"]["superseded_by"] == "noetfield-stack-blueprint-v1-refined-final"
    assert documents["noetfield-execution-kernel-full-stack-blueprint-v1"]["superseded_by"] == "noetfield-stack-blueprint-v1-refined-final"
    assert documents["noetfield-conversation-kernel-maturity-report"]["classification"] == "reference_only"


def test_tenth_batch_execution_kernel_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "postgres-single-source-of-truth" in rule_keys
    assert "langgraph-cannot-bypass-event-ledger" in rule_keys
    assert "vision-engineering-traceability-required" in rule_keys
    assert "semantic-layer-advisory-only" in rule_keys


def test_tenth_batch_sot_domains_are_registered() -> None:
    payload = build_payload()
    domains = {decision["domain"]: decision for decision in payload.sot_registry["decisions"]}

    assert domains["noetfield_documentation_standard"]["active_document_key"] == "noetfield-dual-layer-documentation-standard-v1"
    assert domains["noetfield_rfc_governance"]["active_document_key"] == "noetfield-rfc-standard-v1-github-ci"
    assert domains["noetfield_execution_kernel_architecture"]["active_document_key"] == "noetfield-stack-blueprint-v1-refined-final"
    assert domains["noetfield_execution_roadmap"]["active_document_key"] == "noetfield-5-year-vision-enterprise-ai-os"

def test_eleventh_batch_kernel_and_governance_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["noetfield-execution-kernel-temporal-v1-canonical"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-v2-temporal-governance-os-bank-grade"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-v2-agentic-architecture-summary-duplicate"]["classification"] == "duplicate"
    assert documents["noetfield-evidence-pack-json-schema-v1"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-directory-enforced-consistency-spec-fa"]["classification"] == "active_source_of_truth"


def test_eleventh_batch_governance_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "no-autonomous-production-execution" in rule_keys
    assert "state-derived-from-event-log-only" in rule_keys
    assert "directory-sot-consult-before-response" in rule_keys
    assert "evidence-pack-hsm-signed-manifest" in rule_keys


def test_eleventh_batch_sot_domains_are_registered() -> None:
    payload = build_payload()
    domains = {decision["domain"]: decision for decision in payload.sot_registry["decisions"]}

    assert domains["noetfield_execution_kernel_spec"]["active_document_key"] == "noetfield-execution-kernel-temporal-v1-canonical"
    assert domains["noetfield_temporal_governance_v2"]["active_document_key"] == "noetfield-v2-temporal-governance-os-bank-grade"
    assert domains["noetfield_evidence_pack_schema"]["active_document_key"] == "noetfield-evidence-pack-json-schema-v1"
    assert domains["noetfield_operating_discipline"]["active_document_key"] == "noetfield-directory-enforced-consistency-spec-fa"

def test_twelfth_batch_bank_governance_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["noetfield-bank-integration-pack-v2"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-cross-layer-integration-spec-v1"]["superseded_by"] == "noetfield-bank-integration-pack-v2"
    assert documents["noetfield-master-document-directory-l0-l5-v1"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-agent-governance-executive-bundle-duplicate"]["classification"] == "duplicate"


def test_twelfth_batch_bank_governance_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "noetfield-never-executes-payments" in rule_keys
    assert "ghp-no-execution-instructions" in rule_keys
    assert "bank-pack-overrides-conflicting-execution-specs" in rule_keys
    assert "sot-registry-reference-only" in rule_keys


def test_twelfth_batch_bank_sot_domains_are_registered() -> None:
    payload = build_payload()
    domains = {decision["domain"]: decision for decision in payload.sot_registry["decisions"]}

    assert domains["noetfield_bank_governance_integration"]["active_document_key"] == "noetfield-bank-integration-pack-v2"
    assert domains["noetfield_gcip_document_hierarchy"]["active_document_key"] == "noetfield-master-document-directory-l0-l5-v1"
    assert domains["noetfield_l3_egs_runtime"]["active_document_key"] == "noetfield-l3-execution-engine-egs-v2"

def test_thirteenth_batch_legal_and_product_kernel_resources_are_classified() -> None:
    payload = build_payload()
    documents = {document["document_key"]: document for document in payload.inventory["documents"]}

    assert documents["noetfield-rpaa-legal-opinion-letter-v1"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-constitutional-annex-product-kernel-v4-en"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-bank-procurement-one-pager-rbc-td-v1"]["classification"] == "active_source_of_truth"
    assert documents["noetfield-product-kernel-schedule-v4-duplicate"]["classification"] == "duplicate"
    assert documents["noetfield-legal-counsel-memorandum-rpaa-draft"]["superseded_by"] == "noetfield-rpaa-legal-opinion-letter-v1"


def test_thirteenth_batch_legal_and_kernel_rule_candidates_are_present() -> None:
    payload = build_payload()
    rule_keys = {rule["rule_key"] for rule in payload.rule_registry["active_rule_candidates"]}

    assert "constitution-v32-supremacy-over-annex" in rule_keys
    assert "cda-non-actionable-governance-only" in rule_keys
    assert "pho-zero-instruction-construction" in rule_keys
    assert "no-transaction-based-revenue-model" in rule_keys


def test_thirteenth_batch_legal_sot_domains_are_registered() -> None:
    payload = build_payload()
    domains = {decision["domain"]: decision for decision in payload.sot_registry["decisions"]}

    assert domains["noetfield_legal_regulatory_positioning"]["active_document_key"] == "noetfield-rpaa-legal-opinion-letter-v1"
    assert domains["noetfield_product_kernel_l1"]["active_document_key"] == "noetfield-constitutional-annex-product-kernel-v4-en"
    assert domains["noetfield_bank_procurement"]["active_document_key"] == "noetfield-bank-procurement-one-pager-rbc-td-v1"
