"""Sina → canonical Company OS event, dependency, idempotency, restart tests."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import founder_portfolio_bridge as bridge


def projection(status="partially_implemented"):
    projects = [
        {
            "project_id": "noetfield-company-workforce",
            "name": "Noetfield Company Workforce",
            "company_id": "noetfield-systems-inc",
            "owner_scope": "company",
            "type": "internal-infrastructure",
            "status": status,
            "source_repository": "Noetfield-Systems/noetfeld-os",
            "product_id": "",
        },
        {
            "project_id": "trustfield-msb-workflow",
            "name": "TrustField",
            "company_id": None,
            "owner_scope": "founder-portfolio",
            "type": "venture-candidate",
            "status": "entity_unverified",
            "source_repository": "Noetfield-Systems/TrustField-Technologies",
            "product_id": "",
        },
    ]
    return {
        "schema": bridge.SCHEMA,
        "owner": "sina_founder_os",
        "source_of_truth": "portfolio/PROJECT-AND-ASSET-REGISTRY.json",
        "source_version": "1.3.1",
        "projection_sha256": hashlib.sha256(bridge.canonical(projects).encode("utf-8")).hexdigest(),
        "projects": projects,
        "company_entity_provisioning_authorized": False,
        "runtime_states_verified": False,
        "customer_metrics_included": False,
        "execution_permit_issued": False,
    }


class SinaPortfolioCompanyEventTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.prev_db = core.DB
        core.DB = Path(self.temp.name) / "company.sqlite"
        self.prev_autostart = os.environ.pop("COMPANY_OS_PORTFOLIO_AUTOSTART", None)
        self.prev_token = os.environ.pop(bridge.TOKEN_ENV, None)
        core.init()
        with core.connect() as db:
            db.execute("""INSERT INTO product_programs
              (company_id,project_id,name,vertical,objective,status,priority,
               health_url,max_tasks_per_cycle,created_at,updated_at)
              VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              ("noetfield-systems-inc", "noetfield-company-workforce",
               "Noetfield Company Workforce", "company-operation",
               "Operate the existing Company OS execution workforce",
               "INTERNAL_ACTIVE", 3, None, 4, core.now(), core.now()))

    def tearDown(self):
        core.DB = self.prev_db
        if self.prev_autostart is not None:
            os.environ["COMPANY_OS_PORTFOLIO_AUTOSTART"] = self.prev_autostart
        if self.prev_token is not None:
            os.environ[bridge.TOKEN_ENV] = self.prev_token
        self.temp.cleanup()

    def test_real_canonical_queue_event_generates_two_dependent_internal_tasks(self):
        document = projection()
        checked = bridge.verify_projection(document)
        first = bridge.reconcile_once(lambda: checked)
        self.assertEqual(first["canonical_queue"], "EXISTING_COMPANY_OS_EVENTS")
        self.assertEqual(first["matched_programs"], 1)
        self.assertEqual(first["unmapped_projects"], 1)
        with core.connect() as db:
            e = dict(db.execute("SELECT * FROM events WHERE id=?", (first["event_id"],)).fetchone())
        self.assertFalse(json.loads(e["payload"])["external_execution_authorized"])
        core.process_event(e)
        with core.connect() as db:
            rows = db.execute("SELECT * FROM tasks WHERE event_id=?", (e["id"],)).fetchall()
            self.assertEqual(len(rows), 2)
            dep = db.execute("SELECT count(*) n FROM task_dependencies").fetchone()["n"]
            self.assertEqual(dep, 1)
        specialist = core.claim("tasks")
        self.assertEqual(specialist["role"], "risk_governance")
        core.process_task(specialist)
        executive = core.claim("tasks")
        self.assertEqual(executive["role"], "chief_of_staff")
        core.process_task(executive)
        self.assertIsNone(core.claim("tasks"))
        with core.connect() as db:
            records = db.execute("SELECT status,result FROM tasks WHERE event_id=?", (e["id"],)).fetchall()
        self.assertEqual([x["status"] for x in records], ["drafted", "drafted"])
        self.assertTrue(all(json.loads(x["result"])["external_action"] == "not_executed" for x in records))

    def test_same_source_after_restart_is_idempotent_and_modified_source_is_new_event(self):
        first = bridge.reconcile_once(lambda: bridge.verify_projection(projection()))
        bridge._last_poll = 0.0  # simulate process restart: no volatile cache remains
        again = bridge.reconcile_once(lambda: bridge.verify_projection(projection()))
        self.assertEqual(first["event_id"], again["event_id"])
        altered = bridge.reconcile_once(lambda: bridge.verify_projection(projection("new_candidate_status")))
        self.assertNotEqual(first["event_id"], altered["event_id"])
        with core.connect() as db:
            n = db.execute("SELECT count(*) n FROM events WHERE event_type=?", (bridge.EVENT,)).fetchone()["n"]
        self.assertEqual(n, 2)

    def test_tampered_hash_missing_flags_fake_entity_and_unknown_fields_fail_closed(self):
        valid = projection()
        for changed in (
            {**valid, "projection_sha256": "0" * 64},
            {**valid, "execution_permit_issued": True},
            {**valid, "customer_metrics_included": True},
            {**valid, "other_company_secret": "raw"},
            {**valid, "projects": [{**valid["projects"][0], "company_id": "faked"},
                                      valid["projects"][1]]},
        ):
            with self.assertRaises(ValueError):
                bridge.verify_projection(changed)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) n FROM events").fetchone()["n"], 0)

    def test_production_image_includes_the_bridge_and_compiles_before_start(self):
        dockerfile = Path(__file__).with_name("Dockerfile").read_text(encoding="utf-8")
        self.assertIn("COPY app.py core.py product_loops.py founder_portfolio_bridge.py", dockerfile)
        self.assertIn("python -m py_compile app.py core.py paperclip_bridge.py product_loops.py founder_portfolio_bridge.py",
                      dockerfile)

    def test_disabled_without_private_token_and_no_extra_scheduler(self):
        self.assertEqual(bridge.tick()["state"], "NOT_CONFIGURED")
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) n FROM events").fetchone()["n"], 0)


if __name__ == "__main__":
    unittest.main()
