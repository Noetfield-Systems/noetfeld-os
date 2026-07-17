"""Tests for the hardened noetfield SDK scaffold (issue #74).

Covers the four hardening workstreams — durable outbox, decision identity,
authenticated transport, payload minimization — plus the two carried-over
invariants (only /check authorizes; delivery/outbox errors never change
execution) AND regression tests for every finding confirmed by the adversarial
review of the first cut.

Network use is confined to a localhost fake Hub started per-test.
"""

from __future__ import annotations

import http.client
import json
import os
import stat
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import noetfield_sdk_scaffold as sdk  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in (
        "NOETFIELD_HUB_URL", "NOETFIELD_SIGNING_KEY", "NOETFIELD_HUB_TOKEN",
        "NOETFIELD_OUTBOX_DIR", "NOETFIELD_HUB_ALLOW_HTTP", "NOETFIELD_HUB_ALLOW_ANON",
        "NOETFIELD_HUB_CA_FILE", "NOETFIELD_HUB_CLIENT_CERT", "NOETFIELD_HUB_CLIENT_KEY",
    ):
        monkeypatch.delenv(var, raising=False)
    yield


class FakeHub:
    """Localhost hub recording every request; behavior is toggleable."""

    def __init__(self):
        self.requests: list[dict] = []
        self.fail_ledger = False
        self.fail_check = False
        self.redirect_check_to = None  # e.g. "/evil" -> 302 on /check
        self.check_response = {
            "allowed": True, "reason": "hub says yes", "policy": "hub.rule-1",
            "decision_id": "dec-12345", "policy_version": "hub-pol-v7",
            "decided_at": "2026-07-17T10:00:00Z",
        }
        hub = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                hub.requests.append({
                    "path": self.path,
                    "auth": self.headers.get("Authorization"),
                    "idempotency_key": self.headers.get("Idempotency-Key"),
                    "body": json.loads(body or b"null"),
                })
                if self.path == "/check" and hub.redirect_check_to:
                    self.send_response(302)
                    self.send_header("Location", hub.redirect_check_to)
                    self.end_headers()
                    return
                fail = (self.path == "/ledger" and hub.fail_ledger) or (
                    self.path == "/check" and hub.fail_check
                )
                if fail:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"{}")
                    return
                payload = hub.check_response if self.path == "/check" else {"ok": True}
                data = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *a):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def paths(self):
        return [r["path"] for r in self.requests]


@pytest.fixture
def hub():
    h = FakeHub()
    yield h
    h.stop()


@pytest.fixture
def devmode(monkeypatch):
    """Explicit dev opt-ins so the localhost http hub is reachable."""
    monkeypatch.setenv("NOETFIELD_HUB_ALLOW_HTTP", "1")
    monkeypatch.setenv("NOETFIELD_HUB_ALLOW_ANON", "1")


# ---- core behavior preserved -------------------------------------------------

def test_local_allow_and_deny_with_signed_receipts():
    gov = sdk.Governance(policy={"transfer": {"max_amount": 10_000}})
    out, r = gov.execute("transfer", lambda: {"status": "sent"}, {"amount": 4_000})
    assert out == {"status": "sent"} and r.verify(gov._key)
    with pytest.raises(sdk.PolicyViolation):
        gov.execute("transfer", lambda: {"status": "sent"}, {"amount": 48_000})
    assert len(gov.ledger) == 2  # denied runs are receipted too


def test_receipt_tamper_detection():
    gov = sdk.Governance()
    _, r = gov.execute("noop", lambda: 1, {})
    r.action = "tampered"
    assert not r.verify(gov._key)


# ---- §2 decision identity ------------------------------------------------------

def test_local_decision_carries_identity():
    gov = sdk.Governance(policy={})
    d = gov.check("anything", {})
    assert d.decision_id.startswith("local-") and len(d.decision_id) > 8
    assert d.policy_version.startswith("local:") and d.decided_at.endswith("Z")


def test_receipt_mirrors_decision_id():
    gov = sdk.Governance()
    _, r = gov.execute("noop", lambda: 1, {})
    assert r.decision_id == r.decision.decision_id != ""


def test_hub_decision_identity_parsed(hub, devmode):
    gov = sdk.Governance(hub_url=hub.url)
    d = gov.check("transfer", {"amount": 1})
    assert d.allowed and d.decision_id == "dec-12345"
    assert d.policy_version == "hub-pol-v7" and d.decided_at == "2026-07-17T10:00:00Z"


def test_denial_decisions_carry_identity(hub):
    # regression #26: fail-closed denials (transport-policy, hub.error) still
    # get a decision_id so the receipt->authorization link survives on denials.
    gov = sdk.Governance(hub_url=hub.url)  # http, no opt-in -> transport-policy deny
    d = gov.check("x", {})
    assert not d.allowed and d.decision_id.startswith("deny-") and d.decided_at.endswith("Z")


# ---- §1 durable outbox -----------------------------------------------------------

def test_outbox_written_before_delivery_and_pending_on_hub_failure(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    _, r = gov.execute("noop", lambda: 1, {})
    assert [p["run_id"] for p in gov.outbox.pending()] == [r.run_id]
    assert (tmp_path / "ob" / "outbox.jsonl").is_file()


def test_restart_recovers_and_flush_redelivers(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov1 = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    _, r = gov1.execute("noop", lambda: 1, {})
    del gov1  # "process restart"

    hub.fail_ledger = False
    gov2 = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    assert gov2.ledger == []
    found = gov2.audit(r.run_id)
    assert found is not None and found.run_id == r.run_id and found.verify(gov2._key)

    stats = gov2.flush_outbox(sleep_fn=lambda s: None)
    assert stats["delivered"] == 1 and stats["still_pending"] == 0
    posts = [q for q in hub.requests if q["path"] == "/ledger" and q["body"].get("run_id") == r.run_id]
    assert posts and posts[-1]["idempotency_key"] == r.run_id


def test_flush_is_idempotent_after_delivery(hub, devmode, tmp_path):
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    gov.execute("noop", lambda: 1, {})
    n = len([q for q in hub.requests if q["path"] == "/ledger"])
    stats = gov.flush_outbox(sleep_fn=lambda s: None)
    assert stats == {"pending_before": 0, "delivered": 0, "still_pending": 0, "exhausted": 0}
    assert len([q for q in hub.requests if q["path"] == "/ledger"]) == n


def test_exhausted_receipts_are_reported_never_dropped(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    _, r = gov.execute("noop", lambda: 1, {})
    for _ in range(6):
        gov.flush_outbox(max_attempts_per_receipt=3, sleep_fn=lambda s: None)
    stats = gov.flush_outbox(max_attempts_per_receipt=3, sleep_fn=lambda s: None)
    assert stats["exhausted"] == 1 and stats["delivered"] == 0
    assert [p["run_id"] for p in gov.outbox.pending()] == [r.run_id]


def test_flush_backoff_grows_between_consecutive_failures(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    for _ in range(3):
        gov.execute("noop", lambda: 1, {})
    sleeps: list[float] = []
    gov.flush_outbox(backoff_base_s=0.5, sleep_fn=sleeps.append)
    assert sleeps == [0.5, 1.0]


def test_denied_runs_are_outboxed_too(tmp_path):
    gov = sdk.Governance(policy={"deny": ["rm"]}, outbox_dir=tmp_path / "ob")
    with pytest.raises(sdk.PolicyViolation):
        gov.execute("rm", lambda: 1, {})
    assert len(gov.outbox._read(gov.outbox.outbox_path)) == 1


def test_torn_final_line_is_tolerated(tmp_path):
    ob = sdk.FileOutbox(tmp_path / "ob")
    ob.append({"run_id": "aaa"}, hub_required=True)
    with open(ob.outbox_path, "a") as fh:
        fh.write('{"recorded_at": "2026-')  # simulated crash mid-write
    assert [p["run_id"] for p in ob.pending()] == ["aaa"]


def test_next_append_after_torn_line_survives(tmp_path):
    # regression #3: an append after a torn (newline-less) line must not be
    # glued onto the fragment and lost.
    ob = sdk.FileOutbox(tmp_path / "ob")
    ob.append({"run_id": "good1"}, hub_required=True)
    with open(ob.outbox_path, "a") as fh:
        fh.write('{"recorded_at": "torn-fragment-no-newline"')  # crash: no \n
    ob.append({"run_id": "good2"}, hub_required=True)  # must be isolated + survive
    ids = [p["run_id"] for p in ob.pending()]
    assert ids == ["good1", "good2"]


def test_flush_without_hub_does_not_false_ack(hub, devmode, tmp_path):
    # regression #5: a receipt that needs hub delivery must NOT be marked
    # delivered by a flush that runs with the hub config dropped.
    hub.fail_ledger = True
    gov1 = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    _, r = gov1.execute("noop", lambda: 1, {})
    del gov1
    gov2 = sdk.Governance(outbox_dir=tmp_path / "ob")  # hub_url dropped (drift)
    stats = gov2.flush_outbox(sleep_fn=lambda s: None)
    assert stats["delivered"] == 0 and stats["still_pending"] == 1
    assert [p["run_id"] for p in gov2.outbox.pending()] == [r.run_id]


def test_audit_tolerates_extra_decision_keys(tmp_path):
    # regression #6: a future/old Decision shape must not crash audit().
    ob = sdk.FileOutbox(tmp_path / "ob")
    ob.append({
        "run_id": "future1", "action": "x", "input_hash": "sha256:0", "output_hash": None,
        "ts": "2026-07-17T10:00:00Z", "decision_id": "d1", "sig": "hmac:0",
        "decision": {"allowed": True, "reason": "ok", "policy": "p", "decision_id": "d1",
                     "policy_version": "v", "decided_at": "2026-07-17T10:00:00Z",
                     "risk_score": 0.9},  # unknown future field
    }, hub_required=False)
    gov = sdk.Governance(outbox_dir=tmp_path / "ob")
    found = gov.audit("future1")
    assert found is not None and found.decision.allowed and found.run_id == "future1"


def test_local_transport_failures_do_not_burn_network_cap(hub, devmode, tmp_path, monkeypatch):
    # regression #7: after a real network failure, restarting with the token
    # missing (local transport-policy failures) must not exhaust the cap.
    hub.fail_ledger = True
    gov1 = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    _, r = gov1.execute("noop", lambda: 1, {})  # 1 real network failure
    del gov1
    monkeypatch.delenv("NOETFIELD_HUB_ALLOW_HTTP", raising=False)  # now non-https -> local deny
    gov2 = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    for _ in range(10):
        gov2.flush_outbox(max_attempts_per_receipt=3, sleep_fn=lambda s: None)
    assert gov2.outbox.network_attempt_counts().get(r.run_id, 0) == 1  # unchanged
    assert [p["run_id"] for p in gov2.outbox.pending()] == [r.run_id]  # still pending, not exhausted-dropped


def test_run_id_is_128_bit():
    gov = sdk.Governance()
    _, r = gov.execute("noop", lambda: 1, {})
    assert len(r.run_id) == 32  # regression #19: full uuid4 hex, not 12 chars


def test_env_outbox_dir_configures_outbox(monkeypatch, tmp_path):
    monkeypatch.setenv("NOETFIELD_OUTBOX_DIR", str(tmp_path / "envob"))
    gov = sdk.Governance()
    gov.execute("noop", lambda: 1, {})
    assert (tmp_path / "envob" / "outbox.jsonl").is_file()


# ---- §3 authenticated transport (fail closed) -----------------------------------

def test_http_hub_without_optin_denies_fail_closed(hub):
    gov = sdk.Governance(hub_url=hub.url, hub_token="tok")
    d = gov.check("transfer", {"amount": 1})
    assert not d.allowed and d.policy == "hub.transport_policy" and hub.requests == []


def test_missing_token_without_optin_denies_fail_closed(hub, monkeypatch):
    monkeypatch.setenv("NOETFIELD_HUB_ALLOW_HTTP", "1")
    gov = sdk.Governance(hub_url=hub.url)
    d = gov.check("transfer", {"amount": 1})
    assert not d.allowed and d.policy == "hub.transport_policy" and hub.requests == []


def test_bearer_token_and_idempotency_key_sent(hub, monkeypatch, tmp_path):
    monkeypatch.setenv("NOETFIELD_HUB_ALLOW_HTTP", "1")
    gov = sdk.Governance(hub_url=hub.url, hub_token="sekrit-token", outbox_dir=tmp_path / "ob")
    _, r = gov.execute("transfer", lambda: 1, {"amount": 1})
    check = next(q for q in hub.requests if q["path"] == "/check")
    ledger = next(q for q in hub.requests if q["path"] == "/ledger")
    assert check["auth"] == "Bearer sekrit-token" and ledger["auth"] == "Bearer sekrit-token"
    assert ledger["idempotency_key"] == r.run_id


def test_redirect_is_not_followed_and_denies(hub, devmode):
    # regression #2: a 3xx must not be followed (no token leak / TLS downgrade);
    # it fails closed to a denial.
    hub.redirect_check_to = "/evil"
    gov = sdk.Governance(hub_url=hub.url, hub_token="leak-me")
    d = gov.check("transfer", {"amount": 1})
    assert not d.allowed and d.policy == "hub.error"
    assert "/evil" not in hub.paths()  # the redirect target was never requested


def test_non_boolean_allowed_denies(hub, devmode):
    # regression #1: allowed is honored only when JSON true — never truthy-coerced.
    for bad in ["false", "denied", 1, [1], {"x": 1}]:
        hub.check_response = {"allowed": bad, "reason": "r", "policy": "p"}
        gov = sdk.Governance(hub_url=hub.url)
        assert not gov.check("transfer", {"amount": 1}).allowed, bad


def test_signing_key_never_in_hub_payload(hub, devmode):
    gov = sdk.Governance(hub_url=hub.url, signing_key="super-secret-signing-key")
    d = gov.check("transfer", {"note": "super-secret-signing-key"})
    assert not d.allowed and d.policy == "hub.error" and "signing key" in d.reason
    assert hub.requests == []


def test_short_signing_key_guard(hub, devmode):
    # regression #15: keys under 8 bytes must still be guarded.
    gov = sdk.Governance(hub_url=hub.url, signing_key="short")
    d = gov.check("transfer", {"note": "short"})
    assert not d.allowed and "signing key" in d.reason and hub.requests == []


def test_escaped_signing_key_guard(hub, devmode):
    # regression #16: a key whose bytes get JSON-escaped must still be caught.
    key = 'key"with"quotes'
    gov = sdk.Governance(hub_url=hub.url, signing_key=key)
    d = gov.check("transfer", {"note": key})
    assert not d.allowed and "signing key" in d.reason and hub.requests == []


def test_hub_contract_error_denies(hub, devmode):
    hub.fail_check = True
    gov = sdk.Governance(hub_url=hub.url)
    d = gov.check("transfer", {"amount": 1})
    assert not d.allowed and d.policy == "hub.error"


def test_http_exception_on_check_denies_not_raises(hub, devmode, monkeypatch):
    # regression #13: http.client.HTTPException (not an OSError) must be caught.
    def boom(*a, **k):
        raise http.client.IncompleteRead(b"")
    gov = sdk.Governance(hub_url=hub.url)
    monkeypatch.setattr(gov, "_hub_post", boom)
    d = gov.check("transfer", {"amount": 1})
    assert not d.allowed and d.policy == "hub.error"


# ---- §4 payload minimization ------------------------------------------------------

def test_context_filter_strips_before_send_and_hash(hub, devmode):
    gov = sdk.Governance(hub_url=hub.url, context_filter=sdk.context_allowlist("amount"))
    _, r = gov.execute("transfer", lambda: 1, {"amount": 5, "customer_ssn": "123-45-6789"})
    check = next(q for q in hub.requests if q["path"] == "/check")
    assert check["body"]["context"] == {"amount": 5}
    assert "customer_ssn" not in json.dumps(hub.requests)
    assert r.input_hash == sdk._hash({"action": "transfer", "context": {"amount": 5}})


def test_context_filter_applied_exactly_once(hub, devmode):
    # regression #12: a non-idempotent filter must be applied once, not twice —
    # double application here would flip allow -> deny.
    calls = {"n": 0}

    def add100(ctx):
        calls["n"] += 1
        return {"amount": ctx.get("amount", 0) + 100}

    gov = sdk.Governance(policy={"transfer": {"max_amount": 300}}, context_filter=add100)
    out, r = gov.execute("transfer", lambda: "ok", {"amount": 150})  # once: 250 <= 300 allow
    assert out == "ok"
    assert calls["n"] == 1
    assert r.input_hash == sdk._hash({"action": "transfer", "context": {"amount": 250}})


def test_ledger_receives_hashes_never_raw_io(hub, devmode, tmp_path):
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    gov.execute("charge", lambda: {"card_number": "4111111111111111"}, {"amount": 2})
    ledger = next(q for q in hub.requests if q["path"] == "/ledger")
    assert "4111111111111111" not in json.dumps(ledger["body"])
    assert ledger["body"]["output_hash"].startswith("sha256:")


def test_context_allowlist_helper():
    assert sdk.context_allowlist("a", "b")({"a": 1, "b": 2, "c": 3}) == {"a": 1, "b": 2}


# ---- carried-over invariant: only /check authorizes ------------------------------

def test_ledger_delivery_success_never_authorizes(hub, devmode, tmp_path):
    hub.check_response = {"allowed": False, "reason": "hub says no", "policy": "hub.rule-2"}
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    with pytest.raises(sdk.PolicyViolation):
        gov.execute("transfer", lambda: 1, {"amount": 1})
    assert "/ledger" in hub.paths()  # denial receipt delivered fine — changes nothing


def test_ledger_failure_never_blocks_an_allowed_run(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    out, r = gov.execute("transfer", lambda: "done", {"amount": 1})
    assert out == "done" and r.decision.allowed
    assert gov.outbox.pending()


def test_outbox_io_error_never_masks_denial(tmp_path):
    # regression #14: an outbox OSError (disk full / permission) must not mask
    # the PolicyViolation on a denied run, nor destroy an allowed run's result.
    gov = sdk.Governance(policy={"deny": ["rm"], "transfer": {"max_amount": 10}}, outbox_dir=tmp_path / "ob")
    gov.execute("noop", lambda: 1, {})  # create the files
    for f in ("outbox.jsonl", "delivery.jsonl"):
        p = tmp_path / "ob" / f
        if p.exists():
            os.chmod(p, stat.S_IRUSR)  # read-only -> append raises PermissionError
    try:
        with pytest.raises(sdk.PolicyViolation):  # NOT PermissionError
            gov.execute("rm", lambda: 1, {})
        out, _ = gov.execute("transfer", lambda: "done", {"amount": 1})  # allowed still returns
        assert out == "done" and gov.last_outbox_error
    finally:
        for f in ("outbox.jsonl", "delivery.jsonl"):
            p = tmp_path / "ob" / f
            if p.exists():
                os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)
