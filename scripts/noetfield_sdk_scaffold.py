"""
noetfield — minimal governance SDK (scaffold, hardened per issue #74)

Deterministic control-plane client. The contract:

    check policy  ->  execute under that decision  ->  sign a receipt

The model never makes the rules. It runs a contract you own. Policy is
evaluated deterministically from a plain dict (or your Hub), and every run
produces a tamper-evident, signed receipt.

Pure stdlib. Works fully offline against a local policy dict. Set
NOETFIELD_HUB_URL to enforce centrally instead, and NOETFIELD_SIGNING_KEY
to seal receipts with your own key.

Hardening (issue #74) on top of the PR #69 scaffold:

1. **Durable receipt outbox** — when an outbox directory is configured
   (``NOETFIELD_OUTBOX_DIR`` or ``outbox_dir=``), every receipt is appended to
   an append-only JSONL outbox **before** any Hub POST, delivery acks are
   appended to a separate append-only delivery log, and ``flush_outbox()``
   redelivers anything undelivered (idempotent: ``run_id`` is the idempotency
   key, also sent as an ``Idempotency-Key`` header). A process restart loses
   nothing: pending = outbox − acked.
2. **Decision identity** — ``Decision`` carries ``decision_id`` /
   ``policy_version`` / ``decided_at`` (parsed from the Hub ``/check``
   response; synthesized for local decisions), and ``Receipt.decision_id``
   mirrors it so the receipt→authorization link is auditable.
3. **Authenticated Hub transport** — fail-closed transport policy: the Hub URL
   must be https (opt out for dev with ``NOETFIELD_HUB_ALLOW_HTTP=1``) and a
   bearer credential must be present (``NOETFIELD_HUB_TOKEN``; opt out with
   ``NOETFIELD_HUB_ALLOW_ANON=1``). Optional CA pinning
   (``NOETFIELD_HUB_CA_FILE``) and mTLS client identity
   (``NOETFIELD_HUB_CLIENT_CERT`` / ``NOETFIELD_HUB_CLIENT_KEY``). The signing
   key never enters any Hub payload — a structural guard refuses to POST a
   body containing it.
4. **Payload minimization** — pass ``context_filter=`` (see
   ``context_allowlist``) to strip the execution context down to exactly the
   fields policy evaluation needs before it is hashed or sent to ``/check``.
   ``/ledger`` continues to receive only hashes, never raw inputs/outputs.

Constraint carried over from PR #69 (unchanged, tested): authorization comes
ONLY from the ``/check`` Decision — any transport or contract error denies —
and ledger/outbox delivery success never authorizes anything.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import ssl
import time
import urllib.request
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Optional


def _canonical(obj: Any) -> bytes:
    """Deterministic bytes for any JSON-able object: sorted keys, no spaces."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def _hash(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(obj)).hexdigest()


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class PolicyViolation(Exception):
    """Raised when an action is denied pre-execution."""


@dataclass
class Decision:
    allowed: bool
    reason: str
    policy: str  # which rule decided
    # --- identity (issue #74 §2); defaults keep old callers working -------
    decision_id: str = ""
    policy_version: str = ""
    decided_at: str = ""


@dataclass
class Receipt:
    run_id: str
    action: str
    decision: Decision
    input_hash: str
    output_hash: Optional[str]
    ts: str
    decision_id: str = ""  # mirror of decision.decision_id for direct audit joins
    sig: str = ""

    def verify(self, key: bytes) -> bool:
        body = {k: v for k, v in asdict(self).items() if k != "sig"}
        return hmac.compare_digest(self.sig, _seal(body, key))


def _seal(payload: dict, key: bytes) -> str:
    return "hmac:" + hmac.new(key, _canonical(payload), hashlib.sha256).hexdigest()


def context_allowlist(*keys: str) -> Callable[[dict], dict]:
    """Payload-minimization helper: a context_filter that keeps only ``keys``.

    Policy evaluation should see the fields it needs — nothing else. Secrets
    and raw business payloads do not belong in ``context``.
    """

    def _filter(ctx: dict) -> dict:
        return {k: ctx[k] for k in keys if k in ctx}

    return _filter


_HUB_TIMEOUT_S = 10


# ---------------------------------------------------------------------------
# Durable outbox (issue #74 §1) — append-only JSONL, write-before-POST
# ---------------------------------------------------------------------------
class FileOutbox:
    """Append-only receipt outbox with a separate append-only delivery log.

    ``outbox.jsonl``    one line per receipt, written BEFORE any delivery
    ``delivery.jsonl``  one line per delivery attempt ({run_id, ok, at, attempt})

    Pending = receipts whose run_id has no ok:true delivery line. Both files
    are only ever appended (fsync'd), so a crash between "receipt recorded"
    and "receipt delivered" is always recovered by ``pending()`` after
    restart. Redelivery is safe: run_id is the idempotency key.
    """

    def __init__(self, directory: str | os.PathLike):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.outbox_path = self.dir / "outbox.jsonl"
        self.delivery_path = self.dir / "delivery.jsonl"

    @staticmethod
    def _append(path: Path, obj: dict) -> None:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, sort_keys=True, default=str) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    @staticmethod
    def _read(path: Path) -> list[dict]:
        if not path.is_file():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # a torn final line from a crash is recoverable noise
        return rows

    def append(self, receipt_dict: dict) -> None:
        """Record a receipt durably. MUST be called before any delivery attempt."""
        self._append(self.outbox_path, {"recorded_at": _utc_now(), "receipt": receipt_dict})

    def record_attempt(self, run_id: str, ok: bool, attempt: int, detail: str = "") -> None:
        self._append(
            self.delivery_path,
            {"run_id": run_id, "ok": ok, "attempt": attempt, "at": _utc_now(), "detail": detail[:200]},
        )

    def delivered_ids(self) -> set[str]:
        return {row["run_id"] for row in self._read(self.delivery_path) if row.get("ok")}

    def attempt_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in self._read(self.delivery_path):
            rid = row.get("run_id", "")
            counts[rid] = max(counts.get(rid, 0), int(row.get("attempt") or 0))
        return counts

    def pending(self) -> list[dict]:
        """Undelivered receipts, oldest first (outbox order)."""
        done = self.delivered_ids()
        out = []
        for row in self._read(self.outbox_path):
            receipt = row.get("receipt") or {}
            if receipt.get("run_id") and receipt["run_id"] not in done:
                out.append(receipt)
        return out


# ---------------------------------------------------------------------------
# Governance client
# ---------------------------------------------------------------------------
class Governance:
    def __init__(
        self,
        policy: Optional[dict] = None,
        hub_url: Optional[str] = None,
        signing_key: Optional[str] = None,
        hub_token: Optional[str] = None,
        outbox_dir: Optional[str] = None,
        context_filter: Optional[Callable[[dict], dict]] = None,
    ):
        self.policy = policy or {}
        self.hub_url = hub_url or os.getenv("NOETFIELD_HUB_URL")
        self._key = (signing_key or os.getenv("NOETFIELD_SIGNING_KEY") or "dev-unsafe-key").encode()
        self._hub_token = hub_token or os.getenv("NOETFIELD_HUB_TOKEN") or ""
        self._context_filter = context_filter
        self.ledger: list[Receipt] = []  # in-memory mirror; the outbox is the durable copy
        outdir = outbox_dir or os.getenv("NOETFIELD_OUTBOX_DIR")
        self.outbox: Optional[FileOutbox] = FileOutbox(outdir) if outdir else None
        self._policy_version = "local:" + _hash(self.policy)[7:19]

    # --- transport policy (issue #74 §3) ---------------------------------
    def _transport_problem(self) -> str:
        """Fail-closed transport preconditions for ANY Hub call.

        Returns '' when the transport is acceptable, else the reason. https is
        required unless NOETFIELD_HUB_ALLOW_HTTP=1; a bearer credential is
        required unless NOETFIELD_HUB_ALLOW_ANON=1. Both opt-outs are explicit
        dev-only switches — production keeps the strict defaults.
        """
        url = self.hub_url or ""
        if not url.startswith("https://") and os.getenv("NOETFIELD_HUB_ALLOW_HTTP") != "1":
            return "hub url is not https and NOETFIELD_HUB_ALLOW_HTTP != 1"
        if not self._hub_token and os.getenv("NOETFIELD_HUB_ALLOW_ANON") != "1":
            return "no hub credential (NOETFIELD_HUB_TOKEN) and NOETFIELD_HUB_ALLOW_ANON != 1"
        return ""

    def _ssl_context(self) -> Optional[ssl.SSLContext]:
        ca = os.getenv("NOETFIELD_HUB_CA_FILE")
        cert = os.getenv("NOETFIELD_HUB_CLIENT_CERT")
        key = os.getenv("NOETFIELD_HUB_CLIENT_KEY")
        if not (ca or cert):
            return None
        ctx = ssl.create_default_context(cafile=ca or None)
        if cert:
            ctx.load_cert_chain(certfile=cert, keyfile=key or None)
        return ctx

    def _hub_post(self, url: str, payload: Any, idempotency_key: str = "") -> Any:
        body = _canonical(payload)
        # Structural guard: the signing key must never enter a Hub payload.
        if len(self._key) >= 8 and self._key in body:
            raise ValueError("refusing hub POST: payload contains the signing key")
        headers = {"Content-Type": "application/json"}
        if self._hub_token:
            headers["Authorization"] = f"Bearer {self._hub_token}"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=_HUB_TIMEOUT_S, context=self._ssl_context()) as resp:
            return json.loads(resp.read() or b"null")

    # --- policy -----------------------------------------------------------
    def check(self, action: str, context: dict | None = None) -> Decision:
        ctx = context or {}
        if self._context_filter:
            ctx = self._context_filter(ctx)  # minimize BEFORE eval, hash, or send
        if self.hub_url:
            return self._hub_check(action, ctx)
        return self._local_check(action, ctx)

    def _local_check(self, action: str, ctx: dict) -> Decision:
        def decide(allowed: bool, reason: str, rule: str) -> Decision:
            return Decision(
                allowed,
                reason,
                rule,
                decision_id="local-" + uuid.uuid4().hex[:12],
                policy_version=self._policy_version,
                decided_at=_utc_now(),
            )

        p = self.policy
        if action in p.get("deny", []):
            return decide(False, f"action '{action}' is on the deny list", "deny")
        if action in p.get("approval", {}).get("human_required", []) and not ctx.get("approved_by"):
            return decide(False, "human approval required, none present", "approval")
        amt = ctx.get("amount")
        cap = p.get("transfer", {}).get("max_amount")
        if amt is not None and cap is not None and amt > cap:
            return decide(False, f"amount {amt} exceeds max_amount {cap}", "transfer.max_amount")
        cost = ctx.get("cost")
        budget = p.get("budget", {}).get("max_cost")
        if cost is not None and budget is not None and cost > budget:
            return decide(False, f"cost {cost} exceeds max_cost {budget}", "budget.max_cost")
        return decide(True, "no policy matched; allowed", "default-allow")

    def _hub_check(self, action: str, ctx: dict) -> Decision:
        # Fail closed: any transport-policy, transport, or contract error denies.
        problem = self._transport_problem()
        if problem:
            return Decision(False, f"hub transport policy: {problem}", "hub.transport_policy")
        try:
            body = self._hub_post(f"{self.hub_url}/check", {"action": action, "context": ctx})
            return Decision(
                allowed=bool(body["allowed"]),
                reason=str(body.get("reason", "")),
                policy=str(body.get("policy", "hub")),
                decision_id=str(body.get("decision_id", "")),
                policy_version=str(body.get("policy_version", "")),
                decided_at=str(body.get("decided_at", "")),
            )
        except (OSError, ValueError, KeyError, TypeError) as e:
            return Decision(False, f"hub check failed: {e}", "hub.error")

    # --- execution ----------------------------------------------------------
    def execute(self, action: str, fn: Callable[[], Any], context: dict | None = None) -> tuple[Any, Receipt]:
        ctx = context or {}
        if self._context_filter:
            ctx = self._context_filter(ctx)
        run_id = uuid.uuid4().hex[:12]
        decision = self.check(action, ctx)
        in_hash = _hash({"action": action, "context": ctx})

        if not decision.allowed:
            receipt = self._receipt(run_id, action, decision, in_hash, None)
            raise PolicyViolation(f"{decision.reason}  [{receipt.sig}]")

        result = fn()
        receipt = self._receipt(run_id, action, decision, in_hash, _hash(result))
        return result, receipt

    def _receipt(self, run_id, action, decision, in_hash, out_hash) -> Receipt:
        r = Receipt(
            run_id=run_id,
            action=action,
            decision=decision,
            input_hash=in_hash,
            output_hash=out_hash,
            ts=_utc_now(),
            decision_id=decision.decision_id,
        )
        body = {k: v for k, v in asdict(r).items() if k != "sig"}
        r.sig = _seal(body, self._key)
        self.log(r)
        return r

    # --- ledger / outbox ------------------------------------------------------
    def log(self, receipt: Receipt) -> None:
        """Record the receipt. Durable outbox write happens BEFORE any delivery
        attempt; delivery success/failure NEVER changes what was authorized."""
        self.ledger.append(receipt)
        if self.outbox is not None:
            self.outbox.append(asdict(receipt))
            self._deliver(asdict(receipt))
        elif self.hub_url:
            self._hub_log_best_effort(asdict(receipt))

    def _ledger_payload(self, receipt_dict: dict) -> dict:
        # /ledger receives the signed receipt: hashes + decision identity only,
        # never raw inputs/outputs (Receipt never holds them at all).
        return receipt_dict

    def _deliver(self, receipt_dict: dict) -> bool:
        """One delivery attempt for one receipt; append-only attempt audit."""
        run_id = receipt_dict.get("run_id", "")
        attempt = self.outbox.attempt_counts().get(run_id, 0) + 1 if self.outbox else 1
        if self.hub_url:
            problem = self._transport_problem()
            if problem:
                if self.outbox:
                    self.outbox.record_attempt(run_id, False, attempt, f"transport policy: {problem}")
                return False
            try:
                self._hub_post(f"{self.hub_url}/ledger", self._ledger_payload(receipt_dict), idempotency_key=run_id)
                if self.outbox:
                    self.outbox.record_attempt(run_id, True, attempt)
                return True
            except (OSError, ValueError) as e:
                if self.outbox:
                    self.outbox.record_attempt(run_id, False, attempt, str(e))
                return False
        # No hub configured: the durable outbox itself is the ledger sink.
        if self.outbox:
            self.outbox.record_attempt(run_id, True, attempt, "no hub configured; outbox is the sink")
        return True

    def _hub_log_best_effort(self, receipt_dict: dict) -> None:
        # Legacy no-outbox path: best-effort, never masks the PolicyViolation
        # raised for denied runs and never authorizes anything.
        if self._transport_problem():
            return
        try:
            self._hub_post(f"{self.hub_url}/ledger", self._ledger_payload(receipt_dict),
                           idempotency_key=receipt_dict.get("run_id", ""))
        except (OSError, ValueError):
            pass

    def flush_outbox(
        self,
        max_attempts_per_receipt: int = 5,
        backoff_base_s: float = 0.5,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> dict:
        """Redeliver undelivered receipts (restart-safe, idempotent by run_id).

        Retries each pending receipt once per call with exponential backoff
        BETWEEN receipts that keep failing; receipts that have already burned
        ``max_attempts_per_receipt`` attempts are left pending and reported —
        they are never dropped (append-only outbox; give up != delete).
        """
        if self.outbox is None:
            return {"pending_before": 0, "delivered": 0, "still_pending": 0, "exhausted": 0}
        pending = self.outbox.pending()
        attempts = self.outbox.attempt_counts()
        delivered = exhausted = 0
        consecutive_failures = 0
        for receipt_dict in pending:
            run_id = receipt_dict.get("run_id", "")
            if attempts.get(run_id, 0) >= max_attempts_per_receipt:
                exhausted += 1
                continue
            if consecutive_failures:
                sleep_fn(backoff_base_s * (2 ** (consecutive_failures - 1)))
            if self._deliver(receipt_dict):
                delivered += 1
                consecutive_failures = 0
            else:
                consecutive_failures += 1
        still = len(self.outbox.pending())
        return {
            "pending_before": len(pending),
            "delivered": delivered,
            "still_pending": still,
            "exhausted": exhausted,
        }

    def audit(self, run_id: str) -> Optional[Receipt]:
        hit = next((r for r in self.ledger if r.run_id == run_id), None)
        if hit is not None or self.outbox is None:
            return hit
        # Restart case: the in-memory mirror is empty but the outbox is durable.
        for row in self.outbox._read(self.outbox.outbox_path):
            rec = row.get("receipt") or {}
            if rec.get("run_id") == run_id:
                dec = rec.get("decision") or {}
                return Receipt(
                    run_id=rec["run_id"],
                    action=rec.get("action", ""),
                    decision=Decision(**dec) if isinstance(dec, dict) else dec,
                    input_hash=rec.get("input_hash", ""),
                    output_hash=rec.get("output_hash"),
                    ts=rec.get("ts", ""),
                    decision_id=rec.get("decision_id", ""),
                    sig=rec.get("sig", ""),
                )
        return None


if __name__ == "__main__":
    gov = Governance(policy={"transfer": {"max_amount": 10_000}})

    # allowed
    out, ok = gov.execute("transfer", lambda: {"status": "sent"}, {"amount": 4_000})
    print("ALLOWED ", ok.run_id, ok.decision.decision_id, ok.decision.reason, ok.sig[:24], "...")
    print("verify  ", ok.verify(gov._key))

    # blocked pre-execution (the banner's $48k case, as real logic)
    try:
        gov.execute("transfer", lambda: {"status": "sent"}, {"amount": 48_000})
    except PolicyViolation as e:
        print("BLOCKED ", e)
