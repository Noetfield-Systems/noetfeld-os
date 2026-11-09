"""Noetfield Company OS ↔ Paperclip v2026 contract and failure-path tests."""
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
import app
import core
import paperclip_bridge as pc


CFG = pc.Config(
    enabled=True, board_key="pcp_board_"+"x"*40,
    company_id="7a9a9cf2-231c-4edc-a9a7-1f00ba36056a",
    project_id="a7a27ab0-1d76-4e15-9b1e-d5cd9abcf012",
    base_url=pc.CANONICAL_BASE,
)
ITEM = dict(
    title="Prepare a scoped company operating review",
    objective="Assess a single redacted workflow and propose internal non-privileged tasks.",
    source_ref="https://github.com/Noetfield-Systems/sina_founder_os/issues/42",
    idempotency_key="company-os-paperclip-0001",
)


class PaperclipBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.execute("CREATE TABLE ignored(x TEXT)")
        self.calls = []
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def fetch(self, method, path, *, cfg=None, body=None):
        self.calls.append((method,path,body))
        if method == "GET":
            return []
        return {
            "id":"paperclip-issue-1",
            "companyId":CFG.company_id,
            "projectId":CFG.project_id,
            "status":"backlog",
        }

    def test_status_is_uncommissioned_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            status = pc.status()
        self.assertFalse(status["configured"])
        self.assertFalse(status["agent_wakeup_authorized"])
        self.assertFalse(status["production_mutations_authorized"])
        self.assertFalse(status["workspace_authenticated"])

    def test_no_token_or_wrong_host_denied_before_http(self):
        for bad in (
            pc.Config(True, "", CFG.company_id, CFG.project_id, pc.CANONICAL_BASE),
            pc.Config(True, CFG.board_key, CFG.company_id, CFG.project_id, "https://evil.test"),
            pc.Config(True, CFG.board_key, "", CFG.project_id, pc.CANONICAL_BASE),
        ):
            with self.assertRaises(pc.PaperclipError):
                pc.api_call("GET", "/api/companies/"+CFG.company_id, cfg=bad)

    def test_get_is_company_scoped_and_restricts_methods(self):
        with patch.object(pc.urllib.request, "build_opener") as opener:
            with self.assertRaises(pc.PaperclipError) as err:
                pc.api_call("POST", "/api/agents/a/wakeup", cfg=CFG, body={})
        self.assertEqual(err.exception.code, "PAPERCLIP_ACTION_NOT_ALLOWED")
        opener.assert_not_called()

    def test_snapshot_fetches_one_company_and_sanitizes(self):
        def fetch(method,path,*,cfg=None,body=None):
            if path.endswith("/agents"):
                return [{"id":"a", "name":"Builder","status":"idle",
                         "token":"SHOULD_NOT_LEAK","companyId":CFG.company_id},
                        {"id":"evil","name":"Other","companyId":"other"}]
            if path.endswith("/projects"):
                return [{"id":CFG.project_id,"name":"Founder Intake"}]
            if path.endswith("/issues"):
                return [{"id":"i","title":"Paperclip backlog",
                         "projectId":CFG.project_id,"description":"raw content"},
                        {"id":"other-project","projectId":"another-project"}]
            if path.endswith("/approvals"):
                return [{"id":"approval-1","status":"pending","payload":{"secret":"no"}}]
            return {"id":CFG.company_id,"name":"Noetfield Systems Inc.",
                    "privateInternal":"not-for-client"}
        result = pc.snapshot(cfg=CFG,fetch=fetch)
        self.assertEqual(result["counts"]["agents"],1)
        self.assertEqual(result["counts"]["issues"],1)
        self.assertEqual(result["counts"]["approvals"],1)
        self.assertNotIn("token",result["records"]["agents"][0])
        self.assertNotIn("payload",result["records"]["approvals"][0])
        self.assertFalse(result["execution_permit"])

    def test_snapshot_rejects_company_scope_mismatch(self):
        with self.assertRaises(pc.PaperclipError) as ex:
            pc.snapshot(cfg=CFG,fetch=lambda *args,**kwargs: {"id":"other"})
        self.assertEqual(ex.exception.code,"PAPERCLIP_COMPANY_SCOPE_MISMATCH")

    def test_backlog_created_once_without_agent_assignment(self):
        first = pc.submit_backlog(self.db, cfg=CFG, fetch=self.fetch, **ITEM)
        again = pc.submit_backlog(self.db, cfg=CFG, fetch=self.fetch, **ITEM)
        self.assertEqual(first["state"],"BACKLOG_CREATED")
        self.assertTrue(again["idempotent"])
        writes = [v for v in self.calls if v[0]=="POST"]
        self.assertEqual(len(writes),1)
        body = writes[0][2]
        self.assertEqual(body["status"],"backlog")
        self.assertEqual(body["projectId"],CFG.project_id)
        self.assertNotIn("assigneeAgentId",body)
        self.assertNotIn("executionPolicy",body)
        self.assertIn("not an execution permit",body["description"])

    def test_changed_key_payload_conflicts(self):
        pc.submit_backlog(self.db, cfg=CFG,fetch=self.fetch,**ITEM)
        with self.assertRaises(pc.PaperclipError) as ex:
            pc.submit_backlog(self.db,cfg=CFG,fetch=self.fetch,
                **{**ITEM,"objective":"A totally different redacted business requirement."})
        self.assertEqual(ex.exception.code,"BACKLOG_IDEMPOTENCY_CONFLICT")

    def test_remote_timeout_fails_closed_and_never_duplicate_posts(self):
        def timeout_after_write(method,path,*,cfg=None,body=None):
            self.calls.append((method,path,body))
            if method == "POST":
                raise pc.PaperclipError("PAPERCLIP_NETWORK_OR_TIMEOUT",502)
            return []
        with self.assertRaises(pc.PaperclipError):
            pc.submit_backlog(self.db,cfg=CFG,fetch=timeout_after_write,**ITEM)
        with self.assertRaises(pc.PaperclipError) as ex:
            pc.submit_backlog(self.db,cfg=CFG,fetch=timeout_after_write,**ITEM)
        self.assertEqual(ex.exception.code,"PAPERCLIP_UNCERTAIN_WRITE_REQUIRES_REVIEW")
        self.assertEqual(len([x for x in self.calls if x[0]=="POST"]),1)

    def test_sensitive_input_rejected(self):
        for change in (
            {"objective":"Send details to alice@example.com before approval, thanks."},
            {"objective":"Use bearer ghp_abcdabcdabcdabcdabcdsecret to run unapproved writes."},
        ):
            with self.assertRaises(pc.PaperclipError):
                pc.submit_backlog(self.db,cfg=CFG,fetch=self.fetch,**{**ITEM,**change})
        self.assertFalse(self.calls)


class CompanyOSPaperclipAPITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_db = core.DB
        core.DB = Path(self.tmp.name) / "paperclip-api-test.sqlite"
        self.token=app.TOKEN
        app.TOKEN="test-founder-token-not-public"
        self.client=TestClient(app.app)
        self.client.__enter__()
    def tearDown(self):
        self.client.__exit__(None,None,None)
        core.DB=self.old_db
        app.TOKEN=self.token
        self.tmp.cleanup()

    def test_configuration_surface_does_not_leak_board_key(self):
        with patch.dict(os.environ,{"PAPERCLIP_COMPANY_OS_BOARD_API_KEY":"pcp_board_"+"x"*40}):
            unauthorized=self.client.get("/api/control/paperclip/status")
            authorized=self.client.get("/api/control/paperclip/status",
                headers={"Authorization":"Bearer test-founder-token-not-public"})
        self.assertEqual(unauthorized.status_code,401)
        self.assertEqual(authorized.status_code,200)
        self.assertNotIn("pcp_board_",authorized.text)
        self.assertIn("NOT_COMMISSIONED",authorized.text)

    def test_backlog_requires_commissioned_identity(self):
        r=self.client.post("/api/control/paperclip/backlog",
            headers={"Authorization":"Bearer test-founder-token-not-public"},
            json=ITEM)
        self.assertEqual(r.status_code,503)
        self.assertEqual(r.json()["detail"],"PAPERCLIP_NOT_COMMISSIONED")


if __name__=="__main__":
    unittest.main()
