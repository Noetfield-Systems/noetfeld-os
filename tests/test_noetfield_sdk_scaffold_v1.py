"""Tests for the hardened noetfield SDK scaffold (issue #74).

Covers the four hardening workstreams — durable outbox, decision identity,
authenticated transport, payload minimization — plus the two carried-over
invariants: authorization comes ONLY from the /check Decision (fail closed),
and ledger/outbox delivery success never authorizes anything.

Network use is confined to a localhost fake Hub started per-test (explicit
dev opt-ins NOETFIELD_HUB_ALLOW_HTTP/ALLOW_ANON exercise the strict defaults).
"""

from __future__ import annotations

import json
import sys
import threading
from dataclasses import asdict
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
    """Localhost hub recording every request; failure mode is toggleable."""

    def __init__(self):
        self.requests: list[dict] = []
        self.fail_ledger = False
        self.fail_check = False
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

            def log_message(self, *a):  # silence
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
    assert d.policy_version.startswith("local:")
    assert d.decided_at.endswith("Z")


def test_receipt_mirrors_decision_id():
    gov = sdk.Governance()
    _, r = gov.execute("noop", lambda: 1, {})
    assert r.decision_id == r.decision.decision_id != ""


def test_hub_decision_identity_parsed(hub, devmode):
    gov = sdk.Governance(hub_url=hub.url)
    d = gov.check("transfer", {"amount": 1})
    assert d.allowed and d.decision_id == "dec-12345"
    assert d.policy_version == "hub-pol-v7"
    assert d.decided_at == "2026-07-17T10:00:00Z"


# ---- §1 durable outbox -----------------------------------------------------------

def test_outbox_written_before_delivery_and_pending_on_hub_failure(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    _, r = gov.execute("noop", lambda: 1, {})
    # the receipt is durably recorded even though delivery failed
    pending = gov.outbox.pending()
    assert [p["run_id"] for p in pending] == [r.run_id]
    assert (tmp_path / "ob" / "outbox.jsonl").is_file()


def test_restart_recovers_and_flush_redelivers(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov1 = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    _, r = gov1.execute("noop", lambda: 1, {})
    del gov1  # "process restart"

    hub.fail_ledger = False
    gov2 = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    assert gov2.ledger == []  # in-memory mirror is empty after restart
    found = gov2.audit(r.run_id)  # ...but the durable outbox still has it
    assert found is not None and found.run_id == r.run_id and found.verify(gov2._key)

    stats = gov2.flush_outbox(sleep_fn=lambda s: None)
    assert stats["delivered"] == 1 and stats["still_pending"] == 0
    ledger_posts = [q for q in hub.requests if q["path"] == "/ledger" and q["body"].get("run_id") == r.run_id]
    assert ledger_posts and ledger_posts[-1]["idempotency_key"] == r.run_id


def test_flush_is_idempotent_after_delivery(hub, devmode, tmp_path):
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    gov.execute("noop", lambda: 1, {})
    n_posts = len([q for q in hub.requests if q["path"] == "/ledger"])
    stats = gov.flush_outbox(sleep_fn=lambda s: None)
    assert stats == {"pending_before": 0, "delivered": 0, "still_pending": 0, "exhausted": 0}
    assert len([q for q in hub.requests if q["path"] == "/ledger"]) == n_posts  # no re-send


def test_exhausted_receipts_are_reported_never_dropped(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    _, r = gov.execute("noop", lambda: 1, {})
    for _ in range(6):
        gov.flush_outbox(max_attempts_per_receipt=3, sleep_fn=lambda s: None)
    stats = gov.flush_outbox(max_attempts_per_receipt=3, sleep_fn=lambda s: None)
    assert stats["exhausted"] == 1 and stats["delivered"] == 0
    assert [p["run_id"] for p in gov.outbox.pending()] == [r.run_id]  # still recorded


def test_flush_backoff_grows_between_consecutive_failures(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    for _ in range(3):
        gov.execute("noop", lambda: 1, {})
    sleeps: list[float] = []
    gov.flush_outbox(backoff_base_s=0.5, sleep_fn=sleeps.append)
    assert sleeps == [0.5, 1.0]  # backoff between the 2nd and 3rd failing receipts


def test_denied_runs_are_outboxed_too(tmp_path):
    gov = sdk.Governance(policy={"deny": ["rm"]}, outbox_dir=tmp_path / "ob")
    with pytest.raises(sdk.PolicyViolation):
        gov.execute("rm", lambda: 1, {})
    assert len(gov.outbox._read(gov.outbox.outbox_path)) == 1


def test_torn_final_line_is_tolerated(tmp_path):
    ob = sdk.FileOutbox(tmp_path / "ob")
    ob.append({"run_id": "aaa"})
    with open(ob.outbox_path, "a") as fh:
        fh.write('{"recorded_at": "2026-')  # simulated crash mid-write
    assert [p["run_id"] for p in ob.pending()] == ["aaa"]


# ---- §3 authenticated transport (fail closed) -----------------------------------

def test_http_hub_without_optin_denies_fail_closed(hub):
    gov = sdk.Governance(hub_url=hub.url, hub_token="tok")  # http, no ALLOW_HTTP
    d = gov.check("transfer", {"amount": 1})
    assert not d.allowed and d.policy == "hub.transport_policy"
    assert hub.requests == []  # nothing was sent


def test_missing_token_without_optin_denies_fail_closed(hub, monkeypatch):
    monkeypatch.setenv("NOETFIELD_HUB_ALLOW_HTTP", "1")
    gov = sdk.Governance(hub_url=hub.url)  # no token, no ALLOW_ANON
    d = gov.check("transfer", {"amount": 1})
    assert not d.allowed and d.policy == "hub.transport_policy"
    assert hub.requests == []


def test_bearer_token_and_idempotency_key_sent(hub, monkeypatch, tmp_path):
    monkeypatch.setenv("NOETFIELD_HUB_ALLOW_HTTP", "1")
    gov = sdk.Governance(hub_url=hub.url, hub_token="sekrit-token", outbox_dir=tmp_path / "ob")
    _, r = gov.execute("transfer", lambda: 1, {"amount": 1})
    check = next(q for q in hub.requests if q["path"] == "/check")
    ledger = next(q for q in hub.requests if q["path"] == "/ledger")
    assert check["auth"] == "Bearer sekrit-token"
    assert ledger["auth"] == "Bearer sekrit-token"
    assert ledger["idempotency_key"] == r.run_id


def test_signing_key_never_in_hub_payload(hub, devmode):
    gov = sdk.Governance(hub_url=hub.url, signing_key="super-secret-signing-key")
    # A caller mistake putting the key into context must not leak it: the
    # structural guard refuses the POST, and /check fails CLOSED.
    d = gov.check("transfer", {"note": "super-secret-signing-key"})
    assert not d.allowed and d.policy == "hub.error"
    assert "signing key" in d.reason
    assert hub.requests == []  # never left the process


def test_hub_contract_error_denies(hub, devmode):
    hub.fail_check = True
    gov = sdk.Governance(hub_url=hub.url)
    d = gov.check("transfer", {"amount": 1})
    assert not d.allowed and d.policy == "hub.error"


# ---- §4 payload minimization ------------------------------------------------------

def test_context_filter_strips_before_send_and_hash(hub, devmode):
    gov = sdk.Governance(hub_url=hub.url, context_filter=sdk.context_allowlist("amount"))
    _, r = gov.execute("transfer", lambda: 1, {"amount": 5, "customer_ssn": "123-45-6789"})
    check = next(q for q in hub.requests if q["path"] == "/check")
    assert check["body"]["context"] == {"amount": 5}
    assert "customer_ssn" not in json.dumps(hub.requests)
    # the hash covers exactly what was evaluated (the filtered context)
    assert r.input_hash == sdk._hash({"action": "transfer", "context": {"amount": 5}})


def test_ledger_receives_hashes_never_raw_io(hub, devmode, tmp_path):
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    secret_out = {"card_number": "4111111111111111"}
    gov.execute("charge", lambda: secret_out, {"amount": 2})
    ledger = next(q for q in hub.requests if q["path"] == "/ledger")
    body_text = json.dumps(ledger["body"])
    assert "4111111111111111" not in body_text
    assert ledger["body"]["output_hash"].startswith("sha256:")


def test_context_allowlist_helper():
    f = sdk.context_allowlist("a", "b")
    assert f({"a": 1, "b": 2, "c": 3}) == {"a": 1, "b": 2}


# ---- carried-over invariant: only /check authorizes ------------------------------

def test_ledger_delivery_success_never_authorizes(hub, devmode, tmp_path):
    hub.check_response = {"allowed": False, "reason": "hub says no", "policy": "hub.rule-2"}
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    with pytest.raises(sdk.PolicyViolation):
        gov.execute("transfer", lambda: 1, {"amount": 1})
    # the denial receipt was still delivered fine — and that changes nothing
    assert "/ledger" in hub.paths()


def test_ledger_failure_never_blocks_an_allowed_run(hub, devmode, tmp_path):
    hub.fail_ledger = True
    gov = sdk.Governance(hub_url=hub.url, outbox_dir=tmp_path / "ob")
    out, r = gov.execute("transfer", lambda: "done", {"amount": 1})
    assert out == "done" and r.decision.allowed
    assert gov.outbox.pending()  # undelivered, retained for flush


def test_env_outbox_dir_configures_outbox(monkeypatch, tmp_path):
    monkeypatch.setenv("NOETFIELD_OUTBOX_DIR", str(tmp_path / "envob"))
    gov = sdk.Governance()
    gov.execute("noop", lambda: 1, {})
    assert (tmp_path / "envob" / "outbox.jsonl").is_file()
