"""Tests for TLE HMAC signer."""

from noetfield_governance.tle_signer import sign_tle_body, verify_tle_signature


def test_sign_and_verify_roundtrip() -> None:
    body = {"tle_id": "TLE-TEST", "decision": "Go", "status": "Draft"}
    sig = sign_tle_body(body, key_id="nf-governance-v1-1.0.0")
    assert sig["algorithm"] == "HMAC-SHA256"
    assert verify_tle_signature(body, sig) is True


def test_tamper_fails_verify() -> None:
    body = {"tle_id": "TLE-TEST", "decision": "Go"}
    sig = sign_tle_body(body, key_id="nf-governance-v1-1.0.0")
    body["decision"] = "No-Go"
    assert verify_tle_signature(body, sig) is False
