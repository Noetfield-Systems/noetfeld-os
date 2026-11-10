"""Real shared-queue continuation: Company observation -> Sina -> safe internal work.

Fixtures use a private temporary Company OS SQLite database and a fake HTTP
transport. No synthetic event is sent to a user, CRM, or real platform.
"""
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import core
import founder_signal_transport as bridge
import product_loops


class FounderFeedbackBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.observation_times = {}
        self.old_db = core.DB
        self.old_token = os.environ.get(bridge.TOKEN_ENV)
        self.old_autostart = os.environ.pop("COMPANY_OS_PORTFOLIO_AUTOSTART", None)
        core.DB = Path(self.tmp.name) / "company.sqlite"
        core.init()
        product_loops.register({
            "company_id": "noetfield-systems-inc",
            "project_id": "signal-forge",
            "name": "SignalForge",
            "vertical": "market-intelligence",
            "objective": "Improve the real SignalForge product using trustworthy operational data.",
            "priority": 4,
        })
        # Consume baseline product bootstrap to make isolated checks deterministic.
        while event := core.claim("events"):
            core.process_event(event)

    def tearDown(self):
        core.DB = self.old_db
        if self.old_token is None:
            os.environ.pop(bridge.TOKEN_ENV, None)
        else:
            os.environ[bridge.TOKEN_ENV] = self.old_token
        if self.old_autostart is not None:
            os.environ["COMPANY_OS_PORTFOLIO_AUTOSTART"] = self.old_autostart
        self.tmp.cleanup()

    def make(self, eid, kind="FIRST_PARTY_HTTP_HEALTH", signal="service_health", severity=3):
        payload = {
            "source_event_id": eid, "source_kind": kind,
            "source_ref": "https://signalforge-web-production.up.railway.app/api/health"
            if kind == "FIRST_PARTY_HTTP_HEALTH" else "company-os:real-reported-source",
            "signal": signal,
            "summary": "Observed genuine bounded operation without any external code or money changes.",
            "severity": severity,
            "observed_at": self.observation_times.setdefault(eid, datetime.now(timezone.utc).isoformat()),
        }
        if kind == "FIRST_PARTY_HTTP_HEALTH":
            # This is exactly the verified-health poll's existing transaction.
            with core.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                result = product_loops._insert_observation(
                    db, "noetfield-systems-inc", "signal-forge", payload, verified=True,
                )
                db.commit()
                return result
        return product_loops.observe("noetfield-systems-inc", "signal-forge", payload)

    def federation_rows(self):
        with core.connect() as db:
            return [dict(row) for row in db.execute(
                "SELECT * FROM events WHERE event_type=? ORDER BY id", (bridge.EVENT,))]

    def test_real_health_failure_enqueues_one_sina_event_no_parallel_queue(self):
        self.make("health-failure-00001")
        self.make("health-failure-00001")
        rows = self.federation_rows()
        self.assertEqual(len(rows), 1)
        body = json.loads(rows[0]["payload"])
        self.assertEqual(body["event_type"], "service_degraded")
        self.assertEqual(body["source_id"], "companyos")
        self.assertEqual(body["project_id"], "signal-forge")
        self.assertEqual(body["confidence"], 0.8)
        self.assertFalse(any("@" in str(value) for value in body.values()))
        self.assertEqual(rows[0]["status"], "queued")
        self.assertNotIn("token", json.dumps(rows[0]))
        with core.connect() as db:
            n = db.execute("SELECT count(*) n FROM sqlite_master WHERE name='founder_signal_queue'").fetchone()["n"]
        self.assertEqual(n, 0)

    def test_positive_health_and_synthetic_or_fake_paid_traction_never_become_signals(self):
        self.make("health-ok-00001", severity=0)
        self.make("qa-fake-events-1", kind="SYNTHETIC_AGENT_QA", signal="synthetic_qa", severity=4)
        self.make("fake-revenue-0001", kind="REPORTED_OPERATIONAL", signal="revenue", severity=4)
        self.assertEqual(self.federation_rows(), [])

    def test_market_source_generates_hypothesis_not_customer_claim(self):
        self.make("market-signal-00001", kind="REPORTED_PUBLIC_MARKET", signal="market_shift", severity=1)
        body = json.loads(self.federation_rows()[0]["payload"])
        self.assertEqual(body["event_type"], "market_signal")
        self.assertEqual(body["confidence"], 0.25)
        self.assertEqual(body["metrics"], {})
        self.assertNotIn("revenue", body["summary"].lower())

    def test_delivery_and_restart_idempotency_in_existing_event_states(self):
        self.make("service-event-00001")
        e = next(x for x in self.federation_rows() if x["event_type"] == bridge.EVENT)
        os.environ[bridge.TOKEN_ENV] = "x" * 60
        delivered = bridge.process(e, sender=lambda item: {
            "status": "DELIVERED_TO_SINA_INGRESS",
            "source_event_id": json.loads(item["payload"])["source_event_id"],
            "execution_permit_issued": False,
        })
        self.assertEqual(delivered["status"], "DELIVERED_TO_SINA_INGRESS")
        self.make("service-event-00001")
        self.assertEqual(len(self.federation_rows()), 1)
        self.assertEqual(self.federation_rows()[0]["status"], "processed")
        self.assertEqual(bridge.snapshot()["statuses"]["processed"], 1)

    def test_remote_failure_deferred_then_requeued_and_restarted(self):
        self.make("health-failure-retry1")
        event = self.federation_rows()[0]
        result = bridge.process(event, sender=lambda _: (_ for _ in ()).throw(RuntimeError("offline")))
        self.assertEqual(result["status"], "RETRY_DEFERRED")
        self.assertEqual(self.federation_rows()[0]["status"], "deferred")
        os.environ[bridge.TOKEN_ENV] = "r" * 60
        self.assertEqual(bridge.resume_deferred(now_epoch=0), 0)
        self.assertEqual(bridge.resume_deferred(now_epoch=4102444800), 1)
        self.assertEqual(self.federation_rows()[0]["status"], "queued")
        # restart simulation: reopen the same durable SQLite, no volatile global
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) n FROM events WHERE event_type=?",
                                        (bridge.EVENT,)).fetchone()["n"], 1)
        # Canonical product signal has precedence over feedback to Sina.
        claimed = core.claim("events")
        self.assertEqual(claimed["event_type"], "product.signal_observed")
        core.process_event(claimed)
        claimed = core.claim("events")
        self.assertEqual(claimed["event_type"], bridge.EVENT)
        bridge.process(claimed, sender=lambda _: {"status": "DELIVERED_TO_SINA_INGRESS"})
        self.assertEqual(self.federation_rows()[0]["status"], "processed")

    def test_sina_requires_scoped_config_and_exact_own_event(self):
        self.make("health-failure-scope1")
        event = self.federation_rows()[0]
        self.assertFalse(bridge.configured())
        with self.assertRaises(RuntimeError):
            bridge.deliver(event)
        os.environ[bridge.TOKEN_ENV] = "t" * 60
        with self.assertRaises(ValueError):
            bridge.deliver({**event, "source": "stranger"})
        with self.assertRaises(ValueError):
            bridge.deliver({**event, "payload": json.dumps({
                **json.loads(event["payload"]), "execution_permit_issued": True,
            })})


if __name__ == "__main__":
    unittest.main()
