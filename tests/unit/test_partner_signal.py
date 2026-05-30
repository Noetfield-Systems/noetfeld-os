import pytest
from uuid import uuid4

from noetfield_governance.partner_signal import (
    PartnerSignalIngestRequest,
    normalize_partner_signal,
    partner_evaluate_scenario_preset,
    validate_read_only_payload,
)


def test_validate_read_only_rejects_execution_keys() -> None:
    with pytest.raises(ValueError, match="forbidden"):
        validate_read_only_payload({"place_order": {"symbol": "BTC"}})


def test_normalize_partner_signal() -> None:
    tid, oid = uuid4(), uuid4()
    req = PartnerSignalIngestRequest(
        tenant_id=tid,
        organization_id=oid,
        partner_id="staging-vasp",
        signal_kind="balance_snapshot",
        payload={"currency": "CAD"},
    )
    cmd = normalize_partner_signal(req)
    assert cmd.signal_type == "partner_exchange_signal"
    assert cmd.provenance["ingestion"] == "partner_signal"
    assert cmd.payload["read_only"] is True


def test_exchange_preset_shadow() -> None:
    preset = partner_evaluate_scenario_preset("exchange")
    assert preset["mode"] == "shadow"
    assert preset["resource_type"] == "partner_exchange"


def test_msb_preset_shadow() -> None:
    preset = partner_evaluate_scenario_preset("msb")
    assert preset["mode"] == "shadow"
    assert preset["resource_type"] == "msb_payment"
    assert preset["action"] == "initiate_transfer_intent"
