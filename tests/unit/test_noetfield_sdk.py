from unittest.mock import MagicMock, patch
from uuid import UUID

from noetfield_sdk import Governance, NoetfieldClient
from noetfield_sdk.governance import Governance as GovernanceClass


def test_sdk_client_constructor() -> None:
    client = NoetfieldClient("http://127.0.0.1:8001", api_key="test-key")
    assert client.base_url == "http://127.0.0.1:8001"
    assert client.api_key == "test-key"


def test_governance_check_requires_tenant() -> None:
    gov = Governance("https://platform.noetfield.com", api_key="test")
    try:
        gov.check(action="publish_report")
        raised = False
    except ValueError:
        raised = True
    assert raised


@patch.object(NoetfieldClient, "_request")
def test_governance_check_calls_evaluate(mock_request: MagicMock) -> None:
    mock_request.return_value = {"decision": "PROCEED", "allowed": True}
    tid = UUID("00000000-0000-4000-8000-000000000001")
    oid = UUID("00000000-0000-4000-8000-000000000002")
    gov = GovernanceClass(
        "https://platform.noetfield.com",
        api_key="test",
        tenant_id=tid,
        organization_id=oid,
    )
    result = gov.check(action="evaluate_copilot", confidence=0.9)
    assert result["decision"] == "PROCEED"
    mock_request.assert_called_once()
    call_args = mock_request.call_args
    assert call_args[0][0] == "POST"
    assert call_args[0][1] == "/api/v1/governance/evaluate"


@patch.object(NoetfieldClient, "_request")
def test_governance_audit_calls_export(mock_request: MagicMock) -> None:
    mock_request.return_value = {"export_type": "governance_audit", "entry_count": 1}
    tid = UUID("00000000-0000-4000-8000-000000000001")
    gov = GovernanceClass("https://platform.noetfield.com", tenant_id=tid)
    result = gov.audit(request_id="RID-TEST-1234")
    assert result["entry_count"] == 1
    mock_request.assert_called_once()
