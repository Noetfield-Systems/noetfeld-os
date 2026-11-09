"""Multi-product Company OS loops exercise real core events and specialist tasks.

No mock company tenants are represented as customers; test fixtures stay in
temporary SQLite. Every queued product task remains an internal draft.
"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import product_loops


class CompanyProductLoops(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.prev = core.DB
        core.DB = Path(self.tmp.name) / "company-os.sqlite"
        core.init()

    def tearDown(self):
        core.DB = self.prev
        self.tmp.cleanup()

    def register(self, name="atelier", company="noetfield-systems-inc", **kwargs):
        return product_loops.register({
            "company_id": company, "project_id": name, "name": name.title(),
            "vertical": "social-community",
            "objective": "Grow useful product activation and community participation from genuine audience signals.",
            "priority": 4, **kwargs,
        })

    def observe(self, name, source_id, kind="REPORTED_OPERATIONAL", signal="acquisition", **kwargs):
        return product_loops.observe("noetfield-systems-inc", name, {
            "source_event_id": source_id, "source_kind": kind,
            "source_ref": "company-os:trusted-operator-evidence",
            "signal": signal, "summary": "Measured product evidence requires a cross-department operating response.",
            "severity": 2, **kwargs,
        })

    def drain_events(self, count=20):
        for _ in range(count):
            e = core.claim("events")
            if e is None:
                break
            core.process_event(e)

    def test_register_internal_projects_and_bootstrap_parallel_department_cycles(self):
        a = self.register("atelier")
        b = self.register("venture-formation-lab")
        self.assertTrue(a["operating"])
        self.assertTrue(b["operating"])
        self.assertEqual(product_loops.portfolio()["program_count"], 2)
        with core.connect() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) n FROM events WHERE event_type='product.signal_observed'"
            ).fetchone()["n"], 2)
        self.drain_events()
        with core.connect() as db:
            for project in ("atelier", "venture-formation-lab"):
                roles = {r["role"] for r in db.execute(
                    "SELECT role FROM tasks WHERE project_id=?", (project,)).fetchall()}
                self.assertTrue({
                    "market_intelligence", "product_strategy", "marketing_content",
                    "customer_success", "engineering_operator", "roi_analyst",
                    "risk_governance", "chief_of_staff"}.issubset(roles))
                ceo = db.execute(
                    "SELECT id FROM tasks WHERE project_id=? AND role='chief_of_staff'",(project,)
                ).fetchone()
                self.assertEqual(db.execute(
                    "SELECT COUNT(*) n FROM task_dependencies WHERE task_id=?",
                    (ceo["id"],)).fetchone()["n"], 7)
            self.assertEqual(db.execute("SELECT COUNT(*) n FROM tasks").fetchone()["n"], 16)

    def test_market_and_product_signals_change_department_selection(self):
        self.register("social-game")
        self.drain_events()
        a = self.observe("social-game", "market-signal-0001", signal="market_shift")
        b = self.observe("social-game", "error-signal-0001", signal="app_error", severity=4)
        self.assertGreater(b["priority_score"], a["priority_score"])
        first = core.claim("events")
        self.assertEqual(json.loads(first["payload"])["observation_id"], b["observation_id"])
        core.process_event(first)
        self.drain_events()
        with core.connect() as db:
            m = {r["role"] for r in db.execute(
                "SELECT role FROM tasks WHERE observation_id=?", (a["observation_id"],))}
            err = {r["role"] for r in db.execute(
                "SELECT role FROM tasks WHERE observation_id=?", (b["observation_id"],))}
        self.assertIn("partnerships", m)
        self.assertIn("marketing_content", m)
        self.assertIn("engineering_operator", err)
        self.assertIn("risk_governance", err)

    def test_reported_real_and_synthetic_qa_are_never_mixed_into_traction(self):
        self.register("community-app")
        real = self.observe("community-app", "real-analytics-0001",
            kind="REPORTED_REAL_USER_ANALYTICS", signal="activation",
            metric_name="activation", metric_value=12, sample_count=30)
        fake = self.observe("community-app", "synthetic-persona-0001",
            kind="SYNTHETIC_AGENT_QA", signal="synthetic_qa",
            metric_name="scenarios", metric_value=42, sample_count=42)
        self.assertEqual(real["verification"], "SOURCE_REPORTED_UNVERIFIED")
        self.assertEqual(fake["verification"], "SYNTHETIC_TEST_ONLY")
        scope = product_loops.portfolio("noetfield-systems-inc")["programs"][0]
        self.assertEqual(scope["reported_real_user_observations_unverified"], 1)
        self.assertEqual(scope["synthetic_qa_observations"], 1)
        self.assertIsNone(scope["verified_real_users"])
        self.assertIsNone(scope["verified_revenue"])
        self.assertLess(fake["priority_score"], real["priority_score"])
        self.drain_events()
        with core.connect() as db:
            roles = {r["role"] for r in db.execute(
                "SELECT role FROM tasks WHERE observation_id=?", (fake["observation_id"],))}
        self.assertNotIn("sales_qualification", roles)
        self.assertNotIn("roi_analyst", roles)

    def test_directional_forecasting_uses_real_reported_metrics_not_synthetic(self):
        self.register("social-learning-app")
        for i,metric in enumerate((5,12,23),1):
            self.observe("social-learning-app","real-usage-000"+str(i),
                kind="REPORTED_REAL_USER_ANALYTICS",signal="activation",
                metric_name="activation_rate",metric_value=metric,sample_count=100)
        self.observe("social-learning-app","synthetic-usage-0001",
            kind="SYNTHETIC_AGENT_QA",signal="synthetic_qa",
            metric_name="activation_rate",metric_value=100000,sample_count=100000)
        forecast=product_loops.portfolio()["programs"][0]["directional_signal_forecasts"]
        self.assertEqual(len(forecast),1)
        self.assertEqual(forecast[0]["metric"],"activation_rate")
        self.assertEqual(forecast[0]["direction"],"INCREASING")
        self.assertLess(forecast[0]["one_next_sample_heuristic"],40)
        self.assertFalse(forecast[0]["business_forecast_verified"])
        self.assertEqual(forecast[0]["confidence"],"LOW")

    def test_duplicate_exact_event_is_idempotent_conflicting_source_id_denied(self):
        self.register("matcher")
        a = self.observe("matcher", "event-000001")
        b = self.observe("matcher", "event-000001")
        self.assertEqual(a["observation_id"], b["observation_id"])
        self.assertTrue(b["idempotent"])
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.observe("matcher", "event-000001", severity=4)
        with core.connect() as db:
            count = db.execute(
                "SELECT COUNT(*) n FROM product_observations WHERE project_id='matcher'"
            ).fetchone()["n"]
        self.assertEqual(count, 2)  # registered baseline + one unique real event

    def test_client_provisioning_requires_owner_proof_and_cannot_run(self):
        p = self.register("external-client-app",company="unverified-client")
        self.assertEqual(p["program"]["status"], "CLIENT_OWNER_VERIFICATION_REQUIRED")
        self.assertFalse(p["operating"])
        with self.assertRaisesRegex(ValueError,"not_operational"):
            product_loops.observe("unverified-client","external-client-app",{
                "source_event_id":"signal-0001","source_kind":"REPORTED_PUBLIC_MARKET",
                "source_ref":"company-os:market-report-0001","signal":"opportunity",
                "summary":"Published market report suggests a measurable user need."})
        with core.connect() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) n FROM events WHERE event_type='product.signal_observed'"
            ).fetchone()["n"],0)

    def test_specialist_work_is_real_existing_queue_and_memory_is_scoped(self):
        self.register("atelier")
        self.register("business-match")
        self.drain_events()
        first = core.claim("tasks")
        self.assertIsNotNone(first)
        self.assertIn(first["project_id"], ("atelier","business-match"))
        core.process_task(first)
        with core.connect() as db:
            item = db.execute(
                "SELECT status,result,company_id,project_id FROM tasks WHERE id=?",
                (first["id"],)).fetchone()
            self.assertEqual(item["status"], "drafted")
            output = json.loads(item["result"])
            self.assertEqual(output["external_action"], "not_executed")
            self.assertIn(output["provider"], ("deterministic","provider_error"))
        scope = first["company_id"]+":"+first["project_id"]
        other = "business-match" if first["project_id"] == "atelier" else "atelier"
        self.assertTrue(core.retrieve(scope, first["id"]))
        self.assertFalse(core.retrieve("noetfield-systems-inc:"+other, first["id"]))

    def test_live_poll_fails_closed_without_explicit_allowlist(self):
        self.register("signalforge",health_url="https://signalforge-ai-production.up.railway.app/health")
        with patch.dict(os.environ,{"COMPANY_OS_APPROVED_OBSERVATION_HOSTS":""}):
            with patch.object(product_loops,"_probe") as probe:
                result=product_loops.tick_due()
                self.assertEqual(result["new_health_signals"],0)
                probe.assert_not_called()
        state=product_loops.portfolio()["programs"][0]
        self.assertFalse(state["health_monitoring_authorized"])

    def test_allowed_health_read_creates_real_transport_signal_not_fake_users(self):
        host = "some-product-staging.up.railway.app"
        self.register("social-product",health_url="https://"+host+"/healthz")
        with patch.dict(os.environ,{"COMPANY_OS_APPROVED_OBSERVATION_HOSTS":host}):
            with patch.object(product_loops,"_probe",return_value=(200,"HTTP_OK")) as probe:
                out=product_loops.tick_due()
                self.assertEqual(out["new_health_signals"],1)
                probe.assert_called_once()
            report=product_loops.portfolio()["programs"][0]
            self.assertTrue(report["health_monitoring_authorized"])
            self.assertIsNone(report["verified_real_users"])
            self.assertIn("FIRST_PARTY_HTTP_TRANSPORT_OBSERVED",
                          [x["verification"] for x in report["last_signals"]])
        with core.connect() as db:
            row=db.execute("SELECT COUNT(*) n FROM product_observations WHERE source_kind='FIRST_PARTY_HTTP_HEALTH'").fetchone()
            self.assertEqual(row["n"],1)

    def test_ssot_project_projection_bootstraps_all_internal_lanes_once(self):
        # The Founder-owned portfolio scope is an operating workspace,
        # explicitly NOT a claim about legal entity formation or customers.
        with patch.dict(os.environ, {"COMPANY_OS_PORTFOLIO_AUTOSTART":"true"}):
            core.init()
            reread=product_loops.bootstrap_internal()
        self.assertEqual(reread["created"],0)
        self.assertEqual(reread["drift_blocked"],0)
        self.assertGreaterEqual(reread["unchanged"],12)
        portfolio=product_loops.portfolio()
        self.assertGreaterEqual(portfolio["program_count"],12)
        by_id={p["project_id"]:p for p in portfolio["programs"]}
        for project in ("atelier","venture-formation-lab","signalforge",
                        "misenorth","interior-match","social-games-lab",
                        "trading-exchange-lab","buildworkflow-field-change-handoff"):
            self.assertIn(project,by_id)
            self.assertIn(by_id[project]["status"],
                          ("INTERNAL_ACTIVE","FOUNDER_PROJECT_ACTIVE_NOT_LEGAL_TENANT"))
            self.assertIsNone(by_id[project]["verified_real_users"])
            self.assertIsNone(by_id[project]["verified_revenue"])
        self.assertEqual(by_id["atelier"]["company_id"],"founder-portfolio")
        self.assertFalse(by_id["atelier"]["customer_tenant_verified"])
        with core.connect() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) n FROM events WHERE event_type='product.signal_observed'"
            ).fetchone()["n"],portfolio["program_count"])

    def test_reject_untrusted_source_urls_private_network_and_malformed_metrics(self):
        self.register("example-app")
        for url in ("http://127.0.0.1/health","https://localhost/health",
                    "https://app.invalid/some-internal",
                    "https://user:pass@app.invalid/health"):
            with self.subTest(url=url):
                if url == "https://localhost/health":
                    self.assertFalse(product_loops._approved_health_host(url))
                else:
                    with self.assertRaises(ValueError):
                        product_loops.validate_health_url(url)
        with self.assertRaises(ValueError):
            self.observe("example-app","bad-signal-0001",
                         kind="FIRST_PARTY_HTTP_HEALTH")
        with self.assertRaises(ValueError):
            self.observe("example-app","bad-signal-0001",metric_value=float("inf"))
        with self.assertRaises(ValueError):
            self.observe("example-app","bad-signal-0001",summary="Contact a@b.test for the password")


if __name__ == "__main__":
    unittest.main()
