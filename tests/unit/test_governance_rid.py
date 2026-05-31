from noetfield_governance.governance_rid import generate_rid, normalize_rid
import pytest


def test_generate_rid_format() -> None:
    rid = generate_rid()
    assert rid.startswith("RID-")


def test_normalize_rid_valid() -> None:
    assert normalize_rid("rid-abc-123") == "RID-ABC-123"


def test_normalize_rid_invalid() -> None:
    with pytest.raises(ValueError):
        normalize_rid("not-a-rid")
