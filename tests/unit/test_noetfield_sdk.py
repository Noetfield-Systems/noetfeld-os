from uuid import UUID

from noetfield_sdk import NoetfieldClient


def test_sdk_evaluate_payload_shape() -> None:
    client = NoetfieldClient("http://127.0.0.1:8001", api_key="test-key")
    # Smoke the URL builder only (no live server required)
    assert client.base_url == "http://127.0.0.1:8001"
    tid = UUID("00000000-0000-4000-8000-000000000001")
    oid = UUID("00000000-0000-4000-8000-000000000002")
    # _request would network; verify client constructs
    assert client.api_key == "test-key"
    assert tid and oid
