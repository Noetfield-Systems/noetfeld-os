"""Tests for RID lineage binding."""

from noetfield_governance.governance_rid import bind_rid_lineage, generate_rid, normalize_rid


def test_bind_rid_lineage() -> None:
    rid = generate_rid()
    lineage = bind_rid_lineage(
        rid=rid,
        policy_refs=["copilot-governance-v1@1.0.0"],
        config_policy_version_hash="sha256:abc123",
    )
    assert lineage["request_id"] == rid
    assert lineage["policy_version_hash"].startswith("sha256:")
    assert lineage["config_policy_version_hash"] == "sha256:abc123"


def test_normalize_rid_valid() -> None:
    assert normalize_rid("RID-ABC123-DEF456") == "RID-ABC123-DEF456"
