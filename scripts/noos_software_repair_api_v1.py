#!/usr/bin/env python3
"""NOOS Software Repair — customer API + minimal UI (NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §9).

A narrow HTTP surface over the repair runner, on the Python standard library (no
third-party dependency). The customer submits a commission, watches deterministic
lifecycle states, and retrieves the verified patch, report, verification evidence,
cost, and audit receipt. API and UI share one backend, so CLI/automation has full
parity.

Pilot note: submission runs synchronously (jobs take seconds); a production build
would enqueue and stream progress. The UI never shows repair-writer freshness as
customer job success — job success and infra liveness are separate predicates.
"""

from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_motor_state_machine_v1 as fsm  # noqa: E402
import noos_software_repair_runner_v1 as runner  # noqa: E402

_LEDGER = fsm.MotorLedger()
_JOBS: dict[str, dict[str, Any]] = {}
_LOCK = threading.Lock()

_UI = """<!doctype html><html><head><meta charset=utf-8><title>NOOS Software Repair</title>
<style>body{font-family:system-ui,sans-serif;max-width:820px;margin:2rem auto;padding:0 1rem}
textarea{width:100%;height:160px;font-family:monospace}pre{background:#f4f4f5;padding:1rem;overflow:auto;border-radius:8px}
button{padding:.5rem 1rem;font-size:1rem;cursor:pointer}.state{font-weight:600}.ok{color:#15803d}.bad{color:#b91c1c}
.steps span{display:inline-block;padding:.15rem .5rem;margin:.1rem;border-radius:6px;background:#e4e4e7;font-size:.8rem}</style></head>
<body><h1>NOOS Software Repair Runway</h1>
<p>Submit a failing repository/test. NOOS reproduces, repairs (test-verified), and returns a patch + report.
A repaired job is a customer outcome, <em>not</em> infrastructure liveness.</p>
<h3>Commission</h3>
<textarea id=job>{
  "commission_id": "SR-UI-DEMO-1",
  "customer_id": "ui-customer",
  "recipe_id": "software_repair_ci_v1",
  "recipe_version": "1.0.0",
  "defect_class": "unit_test_regression",
  "repository": {"kind": "local_fixture", "path": "fixtures/repair/py-unit-regression"},
  "failure": {"test_command": ["python3","-m","pytest","tests","-q"], "allowed_files": ["src/mathutil.py"]}
}</textarea><br>
<button onclick=submit()>Submit repair commission</button>
<div id=out></div>
<script>
async function submit(){
  document.getElementById('out').innerHTML='<p>Analyzing &rarr; reproducing &rarr; planning &rarr; repairing &rarr; testing &hellip;</p>';
  const r=await fetch('/repair/commissions',{method:'POST',headers:{'Content-Type':'application/json'},body:document.getElementById('job').value});
  render(await r.json());
}
function render(d){
  const ok=d.job_status==='repaired';
  const steps=(d.lifecycle||[]).map(s=>`<span>${s}</span>`).join('');
  document.getElementById('out').innerHTML=
   `<h3>Result: <span class="state ${ok?'ok':'bad'}">${d.job_status}</span></h3>`+
   `<div class=steps>${steps}</div>`+
   `<p>Execution: <code>${d.job_id}</code> &middot; origin: <code>${d.receipt_origin}</code></p>`+
   `<p>Tests: before exit ${d.verification&&d.verification.tests_before_exit} &rarr; after ${d.verification&&d.verification.passed?'<b class=ok>PASSING</b>':'<b class=bad>failing</b>'}</p>`+
   (d.patch?`<h4>Verified patch</h4><pre>${d.patch.replace(/</g,'&lt;')}</pre>`:'')+
   `<p><a href="/repair/jobs/${d.job_id}/report">report</a> &middot; <a href="/repair/jobs/${d.job_id}">receipt</a> &middot; <a href="/repair/jobs/${d.job_id}/cost">cost</a></p>`;
}
</script></body></html>"""


def _view(res, receipt) -> dict[str, Any]:
    ex = receipt.get("execution", {})
    return {
        "job_id": res["execution_id"],
        "commission_id": receipt.get("commission_id"),
        "job_status": res["job_status"],
        "state": res["state"],
        "receipt_origin": receipt.get("receipt_origin"),
        "lifecycle": [h["state"] for h in ex.get("history", [])],
        "patch": (receipt.get("repaired") or {}).get("patch"),
        "verification": {
            "tests_before_exit": (receipt.get("tests_before") or {}).get("exit_code"),
            "passed": (receipt.get("tests_after") or {}).get("passed"),
        },
    }


def _run(job: dict[str, Any], *, ledger=None) -> dict[str, Any]:
    with _LOCK:
        res = runner.run_repair_job(job, ledger=ledger if ledger is not None else _LEDGER)
        receipt = json.loads(Path(res["receipt_path"]).read_text())
        _JOBS[res["execution_id"]] = {"job": job, "result": res, "receipt": receipt}
    return _view(res, receipt)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, default=str)
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            return self._send(200, _UI, "text/html")
        if path == "/health":
            return self._send(200, {"ok": True, "service": "noos-software-repair-api", "jobs": len(_JOBS)})
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[0] == "repair" and parts[1] == "jobs":
            jid = parts[2]
            j = _JOBS.get(jid)
            if not j:
                return self._send(404, {"error": "unknown job"})
            sub = parts[3] if len(parts) > 3 else None
            if sub is None:
                return self._send(200, j["receipt"])
            if sub == "events":
                return self._send(200, {"events": j["receipt"].get("execution", {}).get("history", [])})
            if sub == "artifacts":
                r = j["result"]
                return self._send(200, {"patch_path": r.get("patch_path"), "report_path": r.get("report_path"),
                                        "patch_hash": r.get("patch_hash"), "delivery": r.get("delivery")})
            if sub == "report":
                rp = j["result"].get("report_path")
                if not rp:
                    return self._send(404, {"error": "no report"})
                return self._send(200, Path(rp).read_text(), "text/markdown")
            if sub == "verification":
                rc = j["receipt"]
                return self._send(200, {"tests_before": rc.get("tests_before"), "tests_after": rc.get("tests_after")})
            if sub == "cost":
                mc = j["receipt"].get("model_calls", [])
                return self._send(200, {"model_calls": mc, "total_cost_usd": sum((c.get("cost_usd") or 0) for c in mc)})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        parts = path.strip("/").split("/")
        if path == "/repair/commissions":
            try:
                job = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                return self._send(400, {"error": "invalid json"})
            return self._send(200, _run(job))
        if len(parts) == 4 and parts[0] == "repair" and parts[1] == "jobs" and parts[3] in ("replay", "cancel"):
            jid = parts[2]
            j = _JOBS.get(jid)
            if not j:
                return self._send(404, {"error": "unknown job"})
            if parts[3] == "replay":
                new_job = dict(j["job"])
                new_job["commission_id"] = f"{new_job.get('commission_id')}-replay"
                return self._send(200, _run(new_job, ledger=fsm.MotorLedger()) | {"replay_of": jid})
            return self._send(200, {"job_id": jid, "note": "pilot jobs run synchronously to a terminal state; cancel applies to queued jobs in the production build", "state": j["result"]["state"]})
        return self._send(404, {"error": "not found"})


def serve(port: int = 8811):
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else 8811)
