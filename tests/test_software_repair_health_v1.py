"""NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §1/§2 — health separation + product organic gate."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_software_repair_health_v1 as h  # noqa: E402


def _full_evidence(**over):
    ev = {"producer": h.PRODUCT_PRODUCER, "execution_plane": h.PRODUCT_EXECUTION_PLANE}
    for c in h.ORGANIC_CONDITIONS:
        ev[c] = True
    ev.update(over)
    return ev


# ---- §2: all 15 conditions + canonical producer/plane required --------------
def test_full_evidence_is_organic():
    r = h.product_organic_confirmed(_full_evidence())
    assert r["product_organic_confirmed"] is True
    assert r["receipt_origin"] == "organic"
    assert r["failed_conditions"] == []


def test_missing_commission_is_not_organic_but_manual():
    # A github_actions run WITHOUT an authoritative commission is a diagnostic.
    r = h.product_organic_confirmed(_full_evidence(commission_persisted=False))
    assert r["product_organic_confirmed"] is False
    assert r["receipt_origin"] == "manual"
    assert "commission_persisted" in r["failed_conditions"]


def test_github_event_name_alone_is_not_organic():
    # Only producer+plane set, no conditions -> NOT organic (event name != provenance).
    r = h.product_organic_confirmed({"producer": h.PRODUCT_PRODUCER, "execution_plane": h.PRODUCT_EXECUTION_PLANE})
    assert r["product_organic_confirmed"] is False
    assert r["receipt_origin"] != "organic"


def test_non_canonical_producer_never_organic():
    r = h.product_organic_confirmed(_full_evidence(producer="gha:noos-factory-autorun"))
    assert r["product_organic_confirmed"] is False
    assert r["producer_canonical"] is False
    assert "producer_not_canonical" in r["failed_conditions"]


def test_non_canonical_plane_never_organic():
    r = h.product_organic_confirmed(_full_evidence(execution_plane="railway"))
    assert r["product_organic_confirmed"] is False
    assert r["plane_canonical"] is False


def test_declared_origins_pass_through():
    for o in ("test", "local_reference", "repair", "replay"):
        r = h.product_organic_confirmed({"producer": "x", "execution_plane": "y", "declared_origin": o})
        assert r["receipt_origin"] == o
        assert r["product_organic_confirmed"] is False


# ---- §1: three independent health domains -----------------------------------
def test_health_domains_are_independent():
    d = h.health_domains(
        platform_loop={"state": "SEPARATE_OPERATIONS_INCIDENT", "last_organic_completion_at": "2026-07-12T13:50:49Z"},
        product={"last_product_organic": _full_evidence(), "authoritative_persistence": "supabase"},
        customer_job={"commission_id": "SR-1", "state": "completed", "job_id": "exe_x"},
    )
    dom = d["domains"]
    # platform degraded, product healthy — independent
    assert dom["A_platform_loop"]["state"] == "SEPARATE_OPERATIONS_INCIDENT"
    assert dom["B_product"]["state"] == "RUNNING_CONFIRMED"
    assert dom["B_product"]["last_product_organic_confirmed"] is True
    assert dom["C_customer_job"]["state"] == "completed"


def test_healthy_product_does_not_mark_platform_healthy():
    d = h.health_domains(
        platform_loop={"state": "DEGRADED"},
        product={"last_product_organic": _full_evidence()},
    )
    assert d["domains"]["B_product"]["state"] == "RUNNING_CONFIRMED"
    assert d["domains"]["A_platform_loop"]["state"] == "DEGRADED"  # unchanged


def test_platform_degraded_does_not_invalidate_product():
    d = h.health_domains(
        platform_loop={"state": "SEPARATE_OPERATIONS_INCIDENT"},
        product={"last_product_organic": _full_evidence(), "state": "NOT_YET_PROVEN"},
    )
    # product state derives ONLY from product-organic evidence, not platform
    assert d["domains"]["B_product"]["state"] == "RUNNING_CONFIRMED"


def test_customer_job_invalid_state_normalized():
    d = h.health_domains(customer_job={"commission_id": "x", "state": "weird"})
    assert d["domains"]["C_customer_job"]["state"] == "unknown"
