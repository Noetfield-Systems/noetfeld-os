"""Regression: one Company OS operates many products in concurrent departments.

All tests use temporary databases and injected read-only observations. Synthetic
fixtures are NEVER counted as real users, signups, sales or production effects.
"""
from __future__ import annotations
import hashlib
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import core
import portfolio_studio as studio


def feed():
    projects = [
        ("atelier-community", "Atelier Community", "private-adult-community-product", "Noetfield-Systems/Atelier", None),
        ("venture-formation-lab", "Venture Formation Lab", "startup-community-and-founder-matching", "Noetfield-Systems/venture-formation-lab", None),
        ("buildmatch-platform", "BuildMatch", "construction-professional-matching", "Noetfield-Systems/buildmatch", None),
        ("trade-radar-platform", "Trade Radar", "trade-intelligence-free-data-tools", "Noetfield-Systems/TRADE-RADAR", None),
        ("noetfield-verification-layer", "Verification Layer", "governed-verification-saas", "Noetfield-Systems/Verification_Layer", "noetfield-systems-inc"),
        ("room-private-messaging", "Room", "private-founder-messaging-product", "Noetfield-Systems/Room", None),
    ]
    items=[{"project_id": pid, "name": name, "type": typ, "source_repository": repo,
            "company_id": company_id, "owner_scope": "company" if company_id else "founder-portfolio",
            "status": "REPOSITORY_PRESENT_RUNTIME_NOT_VERIFIED", "product_id": ""}
           for pid,name,typ,repo,company_id in projects]
    body = json.dumps(items, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {"schema": studio.SCHEMA, "owner": "sina_founder_os",
            "projection_sha256": hashlib.sha256(body.encode()).hexdigest(),
            "source_of_truth": "portfolio/PROJECT-AND-ASSET-REGISTRY.json",
            "projects": items}


def repo_signal(project):
    return {"status": "PUBLIC_REPO_OBSERVED", "source": "https://api.github.com/repos/"+project["source_repository"],
            "observed_at": "2026-11-09T00:00:00+00:00",
            "pushed_at": "2026-11-08T22:00:00Z",
            "user_traction": "UNKNOWN", "revenue": "UNKNOWN",
            "stargazers_not_users": 2}


class ParallelStudioTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.old = core.DB
        core.DB = Path(self.directory.name) / "company.sqlite"
        core.init()

    def tearDown(self):
        core.DB = self.old
        self.directory.cleanup()

    def test_four_products_receive_nine_roles_and_actual_result_ledger(self):
        base = time.time()
        first = studio.tick(fetcher=feed,probe=repo_signal,timestamp=base)
        self.assertEqual(first, {"state":"QUEUED","queued":4})
        with core.connect() as db:
            events=db.execute("SELECT * FROM events WHERE event_type='portfolio.studio.cycle'").fetchall()
            self.assertEqual(len(events), 4)
            self.assertEqual(len({e["brand"] for e in events}),4)
        for _ in range(4):
            event=core.claim("events")
            self.assertIsNotNone(event)
            core.process_event(event)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) n FROM tasks").fetchone()["n"],36)
            deps=db.execute("SELECT COUNT(*) n FROM task_dependencies").fetchone()["n"]
            self.assertEqual(deps,32)
        processed=0
        for _ in range(45):
            task=core.claim("tasks")
            if not task: break
            core.process_task(task)
            processed+=1
        self.assertEqual(processed,36)
        state=studio.overview()
        self.assertEqual(len(state["project_cycles"]),4)
        self.assertTrue(all(x["internal_drafts"]==9 for x in state["project_cycles"]))
        self.assertFalse(state["autonomous_product_build_verified"])
        self.assertFalse(state["automatic_public_distribution_enabled"])
        with core.connect() as db:
            item=db.execute("SELECT result FROM tasks WHERE role='roi_analyst' LIMIT 1").fetchone()
            result=json.loads(item["result"])["recommendation"]
            self.assertIsNone(result["verified_human_users"])
            self.assertIsNone(result["revenue_collected"])
            self.assertFalse(result["actual_product_mutation"])
            self.assertFalse(result["score_is_market_validation"])
            self.assertEqual(result["source_evidence"]["repo_status"],"PUBLIC_REPO_OBSERVED")

    def test_daily_round_robin_no_duplicates_after_restart(self):
        base=1762704000
        self.assertEqual(studio.tick(fetcher=feed,probe=repo_signal,timestamp=base)["queued"],4)
        self.assertEqual(studio.tick(fetcher=feed,probe=repo_signal,timestamp=base+10)["queued"],0)
        self.assertEqual(studio.tick(fetcher=feed,probe=repo_signal,timestamp=base+studio.CADENCE_SECONDS+1)["queued"],2)
        self.assertEqual(studio.tick(fetcher=feed,probe=repo_signal,timestamp=base+2*studio.CADENCE_SECONDS+2)["queued"],0)
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) n FROM events WHERE event_type='portfolio.studio.cycle'").fetchone()["n"],6)

    def test_wrong_registry_digest_never_creates_jobs(self):
        wrong=feed()
        wrong["projection_sha256"]="0"*64
        result=studio.tick(fetcher=lambda:wrong,probe=repo_signal,timestamp=1762704000)
        self.assertEqual(result["state"],"BLOCKED")
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) n FROM events").fetchone()["n"],0)

    def test_no_bridge_credentials_fails_closed(self):
        with patch.dict(os.environ,{"SINA_PORTFOLIO_FEED_URL":"","SINA_COMPANY_PORTFOLIO_TOKEN":""}):
            self.assertFalse(studio.configured())
            self.assertEqual(studio.tick()["state"],"NOT_CONFIGURED")
        with core.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) n FROM events").fetchone()["n"],0)

    def test_project_priority_prefers_network_effect_hypotheses_not_fake_users(self):
        data=feed()["projects"]
        consumer=next(p for p in data if p["project_id"]=="atelier-community")
        infra=next(p for p in data if p["project_id"]=="noetfield-verification-layer")
        score_a=studio.score_hypothesis(consumer,{"status":"NO_REPOSITORY_REFERENCE"})
        score_b=studio.score_hypothesis(infra,{"status":"NO_REPOSITORY_REFERENCE"})
        self.assertGreater(score_a,score_b)
        self.assertLessEqual(score_a,100)


if __name__=="__main__":
    unittest.main()
