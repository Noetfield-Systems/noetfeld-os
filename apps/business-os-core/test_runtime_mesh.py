"""The unified control UI reports evidence without granting execution authority."""
import io
import json
import unittest
from unittest.mock import patch

import runtime_mesh


class Response:
    status = 200

    def __init__(self, payload, content_type="application/json"):
        self.data = io.BytesIO(payload)
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size):
        return self.data.read(size)


class PinnedOpener:
    def __init__(self, override=None):
        self.override = override or {}
        self.seen = []

    def open(self, request, timeout):
        self.seen.append(request.full_url)
        assert request.full_url in {p[2] for p in runtime_mesh.PROBES}
        assert request.get_method() == "GET"
        assert timeout <= 3
        assert not request.has_header("Authorization")
        if request.full_url in self.override:
            return self.override[request.full_url]
        if request.full_url.endswith("/v1/goals/health"):
            return Response(b'{"goal_runtime":true}')
        if "agent-fabric" in request.full_url:
            return Response(b'{"service":"noetfield-agent-fabric","status":"ok"}')
        if request.full_url.endswith("/healthz"):
            return Response(b'{"status":"ok"}')
        return Response(b"<html>login</html>", "text/html")


class RuntimeMeshTests(unittest.TestCase):
    def test_source_reports_never_infer_motor_execution_or_verifier_proof(self):
        client = PinnedOpener()
        result = runtime_mesh.snapshot(opener=client, founder_bridge_status={
            "connection": "LIVE", "work_packets_claimed": 7, "pending_ack": 1,
            "verified_outcomes": 0, "external_effects": 0,
            "last_cycle_rejection_reasons": {"project_not_allowed": 1},
            "last_cycle_rejected_projects":[{"reason_code":"project_not_allowed",
                "project_id":"noetfield-earnloop","company_id":"noetfield-systems-inc"}],
        })
        self.assertEqual(result["schema"], runtime_mesh.SCHEMA)
        self.assertEqual(len(client.seen), len(runtime_mesh.PROBES))
        self.assertEqual(result["summary"]["healthy_reports"], len(runtime_mesh.PROBES))
        self.assertEqual(result["founder_handoff"]["work_packets_claimed"], 7)
        self.assertEqual(result["founder_handoff"]["last_cycle_rejection_reasons"], {"project_not_allowed": 1})
        self.assertEqual(result["founder_handoff"]["last_cycle_rejected_projects"][0]["project_id"],"noetfield-earnloop")
        self.assertFalse(result["summary"]["runway_e2e_commissioned"])
        self.assertEqual(result["summary"]["verified_edges"], 0)
        self.assertTrue(all(not e["e2e_verified"] for e in result["edges"]))
        self.assertTrue(all(not n["e2e_verified"] for n in result["nodes"]))
        self.assertTrue(all(not n["authenticated"] for n in result["nodes"]))

    def test_wrong_runway_response_does_not_prove_goal_runtime(self):
        url = next(p[2] for p in runtime_mesh.PROBES if p[0] == "runway_goal")
        item = next(p for p in runtime_mesh.PROBES if p[0] == "runway_goal")
        result = runtime_mesh._probe(item, PinnedOpener({url: Response(b'{"ok":true}')}))
        self.assertEqual(result["state"], "SCHEMA_UNCONFIRMED")

    def test_invalid_json_redirect_or_large_body_cannot_be_green(self):
        item = next(p for p in runtime_mesh.PROBES if p[0] == "runway_goal")
        url = item[2]
        for response in [Response(b"{invalid"), Response(b"x" * (runtime_mesh.MAX_BODY + 1))]:
            self.assertEqual(runtime_mesh._probe(item, PinnedOpener({url: response}))["state"], "UNREACHABLE" if response.data.getvalue().startswith(b"{invalid") else "INVALID_RESPONSE")
        self.assertIsNone(runtime_mesh.NoRedirect().redirect_request(None, None, 302, "", None, "https://invalid.example/"))

    def test_no_untrusted_urls_or_caller_chosen_dispatch(self):
        self.assertTrue(all(p[2].startswith("https://") for p in runtime_mesh.PROBES))
        self.assertTrue(all("?" not in p[2] for p in runtime_mesh.PROBES))
        self.assertNotIn("external_effects", runtime_mesh.snapshot(opener=PinnedOpener())["summary"])


if __name__ == "__main__":
    unittest.main()
