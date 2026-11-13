"""Noetfield PostgreSQL backend: authorization and idempotency contract."""
import os

import pytest

from scripts import noos_postgres_store_v1 as store


def test_postgres_is_opt_in(monkeypatch):
    monkeypatch.delenv("NOOS_STORAGE_BACKEND", raising=False)
    assert store.configured() is False
    monkeypatch.setenv("NOOS_STORAGE_BACKEND", "railway_postgres")
    assert store.configured() is True


def test_repository_allowlist_does_not_admit_arbitrary_orgs(monkeypatch):
    monkeypatch.setenv("NOOS_CODING_ALLOWED_REPOS", "Noetfield-Systems/noetfeld-os")
    assert store.allowed_repo("Noetfield-Systems/noetfeld-os")
    assert not store.allowed_repo("SomeOtherOrg/noetfeld-os")
    assert not store.allowed_repo("Noetfield-Systems/other")
    assert not store.allowed_repo("Noetfield-Systems/../../secrets")


def test_unauthorized_workpacket_is_rejected_before_database(monkeypatch):
    monkeypatch.setenv("NOOS_CODING_ALLOWED_REPOS", "Noetfield-Systems/noetfeld-os")
    base = {
        "workpacket_id": "workpacket-test-0001",
        "project_id": "project-noetfield",
        "repo": "Noetfield-Systems/noetfeld-os",
        "prompt": "Implement a bounded code improvement and tests.",
    }
    with pytest.raises(ValueError, match="INVALID_OR_UNAUTHORIZED_WORKPACKET"):
        store.enqueue_job(base)
    with pytest.raises(ValueError, match="INVALID_OR_UNAUTHORIZED_WORKPACKET"):
        store.enqueue_job({**base, "founder_authorized":True,"repo":"SomeOtherOrg/noetfeld-os"})
    with pytest.raises(ValueError, match="INVALID_OR_UNAUTHORIZED_WORKPACKET"):
        store.enqueue_job({**base, "founder_authorized":True,"prompt":"x"})


def test_invalid_reporting_cannot_finalize_job(monkeypatch):
    with pytest.raises(ValueError, match="INVALID_JOB_ID_OR_LEASE"):
        store.report_job({"job_id":"bad","lease_token":"bad","state":"VERIFIED","evidence":{}})


def test_queue_schema_prevents_duplicate_claims_and_lease_free_completion():
    assert "FOR UPDATE SKIP LOCKED" in store.claim_job.__code__.co_consts.__str__()
    assert "lease_until>now()" in store.report_job.__code__.co_consts.__str__()
    assert "ON CONFLICT(workpacket_id)" in store.enqueue_job.__code__.co_consts.__str__()
