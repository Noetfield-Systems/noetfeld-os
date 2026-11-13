#!/usr/bin/env python3
"""NOOS keyless cloud coding worker: authorized WorkPacket -> code -> test -> PR.

Executed by GitHub Actions on a fresh isolated checkout. Reads the canonical
Railway PostgreSQL queue using GitHub-signed OIDC. Calls GitHub Models with
the job's built-in GITHUB_TOKEN (models:read); no external model secret.
A separate workflow job performs release verification/merge.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = Path(os.environ.get("NOOS_CODER_ROOT") or Path(__file__).resolve().parents[1])
API = "https://noos-loop-runner-production.up.railway.app"
MODEL_API = "https://models.github.ai/inference/chat/completions"
BASE = "deploy/noos-loop-runner-entrypoint"
REPO = "Noetfield-Systems/noetfeld-os"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
WORKFLOW_OUTPUT = os.environ.get("GITHUB_OUTPUT", "")
FORBIDDEN_MODULES = {"subprocess", "socket", "requests", "urllib", "http", "ftplib",
                     "ctypes", "pickle", "marshal", "shutil", "importlib"}
FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__"}
MAX_CONTENT = 14000


def output(**values):
    if not WORKFLOW_OUTPUT:
        return
    with open(WORKFLOW_OUTPUT, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            value = str(value)
            if "\n" in value or "\r" in value:
                raise ValueError("INVALID_WORKFLOW_OUTPUT")
            handle.write(key + "=" + value + "\n")


def request(url, *, method="GET", data=None, token=None, timeout=35):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data, separators=(",", ":")).encode()
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read(350).decode("utf-8", errors="replace")
        raise RuntimeError("HTTP_" + str(exc.code) + ":" + detail[:180]) from exc


def oidc():
    url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
    secret = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
    if not url.startswith("https://") or not secret:
        raise RuntimeError("GITHUB_OIDC_NOT_CONFIGURED")
    url += ("&" if "?" in url else "?") + "audience=noetfield-coding-workforce"
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + secret})
    with urllib.request.urlopen(req, timeout=15) as response:
        result = json.load(response)
    jwt_token = result.get("value", "")
    if len(jwt_token) < 250:
        raise RuntimeError("GITHUB_OIDC_INVALID")
    return jwt_token


def api(path, data, oidc_token):
    return request(API + path, method="POST", data=data, token=oidc_token)


def queue_issue(oidc_token):
    if os.environ.get("GITHUB_EVENT_NAME") != "issues":
        return
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    issue = event.get("issue") or {}
    author = (issue.get("user") or {}).get("login")
    if (event.get("action") != "opened" or author != "kazemnezhadsina144-dot"
            or not str(issue.get("title") or "").startswith("[NOOS-CODE] ")):
        print("NOOS_ISSUE_IGNORED")
        return
    try:
        payload = json.loads(issue.get("body") or "")
    except json.JSONDecodeError as exc:
        raise RuntimeError("FOUNDER_WORKPACKET_INVALID_JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("FOUNDER_WORKPACKET_NOT_OBJECT")
    expected_id = "noos-issue-" + str(issue["number"])
    if (payload.get("workpacket_id") != expected_id
            or payload.get("repo") != REPO or payload.get("founder_authorized") is not True):
        raise RuntimeError("FOUNDER_WORKPACKET_SCOPE_MISMATCH")
    answer = api("/v1/coding/queue", payload, oidc_token)
    if not answer.get("ok"):
        raise RuntimeError("WORKPACKET_PERSISTENCE_FAILED")
    print("NOOS_WORKPACKET_ENQUEUED " + expected_id)
    followups = payload.get("followups") or []
    if not isinstance(followups,list) or len(followups)>2:
        raise RuntimeError("WORKPACKET_FOLLOWUPS_OUT_OF_SCOPE")
    for index, next_job in enumerate(followups,1):
        if (not isinstance(next_job,dict)
            or next_job.get("workpacket_id")!=expected_id+"-next-"+str(index)
            or next_job.get("repo")!=REPO
            or next_job.get("founder_authorized") is not True):
            raise RuntimeError("WORKPACKET_FOLLOWUP_IDENTITY_DENIED")
        answer=api("/v1/coding/queue",next_job,oidc_token)
        if not answer.get("ok"):
            raise RuntimeError("WORKPACKET_FOLLOWUP_PERSISTENCE_FAILED")
        print("NOOS_FOLLOWUP_ENQUEUED "+next_job["workpacket_id"])


def shell(*argv, timeout=120, secretless=False):
    env = os.environ.copy()
    if secretless:
        for key in tuple(env):
            if ("TOKEN" in key or "SECRET" in key or "KEY" in key or
                    key.startswith(("ACTIONS_ID_", "GH_"))):
                env.pop(key, None)
    proc = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True,
                          text=True, timeout=timeout, check=False)
    if proc.returncode:
        raise RuntimeError("CODE_WORKER_COMMAND_FAILED:" + argv[0] + ":"
                           + ((proc.stderr or proc.stdout)[-320:]).replace("\n", " "))
    return proc.stdout.strip()


def model_generate(goal, name):
    if not TOKEN:
        raise RuntimeError("GITHUB_MODELS_TOKEN_MISSING")
    context = (ROOT / "AGENTS.md").read_text(encoding="utf-8")[:3400]
    system = (
        "You are a senior software engineer writing a focused, useful Python "
        "capability for a real production repository. Return ONLY JSON of "
        "the shape {\\\"module\\\":\\\"...Python source...\\\","
        "\\\"tests\\\":\\\"...Pytest source...\\\"}. No Markdown. "
        "Both files must be meaningful and testable, not mock examples. "
        "No network access, no secrets, no subprocess, no eval, no file-system "
        "writes in generated code. Keep dependencies to Python stdlib and pytest. "
        "Tests must import the module from scripts." 
    )
    user = (
        "Authorized engineering objective:\n" + goal[:8000] +
        "\n\nTarget Python module: scripts/" + name + ".py" +
        "\nTarget pytest file: tests/test_" + name + ".py" +
        "\nThe module import path is scripts." + name +
        "\nRepository constraints:\n" + context
    )
    body = {"model": "openai/gpt-4.1",
            "messages":[{"role":"system","content":system},
                        {"role":"user","content":user}],
            "max_tokens": 3500, "temperature": 0.1}
    answer = request(MODEL_API, method="POST", data=body, token=TOKEN, timeout=80)
    raw = (((answer.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
    raw = str(raw).strip()
    if raw.startswith("```"):
        raw = re.sub(r"^\x60{3}(?:json)?\s*", "", raw).removesuffix("```").strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("MODEL_NON_JSON_OUTPUT") from exc
    if set(parsed) != {"module","tests"}:
        raise RuntimeError("MODEL_OUTPUT_SCHEMA_INVALID")
    result = (parsed["module"],parsed["tests"])
    if any(not isinstance(x,str) or len(x)<80 or len(x)>MAX_CONTENT for x in result):
        raise RuntimeError("MODEL_CODE_SIZE_INVALID")
    return result


def check_ast(contents):
    parsed = ast.parse(contents)
    for node in ast.walk(parsed):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names = [n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or ""]
            if any(n.split(".")[0] in FORBIDDEN_MODULES for n in names):
                raise RuntimeError("MODEL_UNSAFE_IMPORT")
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in FORBIDDEN_CALLS:
            raise RuntimeError("MODEL_UNSAFE_DYNAMIC_CODE")
    return True


def write_and_test(goal, suffix):
    name = "noos_agent_feature_" + suffix
    module_path = "scripts/" + name + ".py"
    test_path = "tests/test_" + name + ".py"
    if (ROOT/module_path).exists() or (ROOT/test_path).exists():
        raise RuntimeError("REPOSITORY_TARGET_ALREADY_EXISTS")
    source,tests = model_generate(goal,name)
    check_ast(source)
    check_ast(tests)
    (ROOT/module_path).write_text(source,encoding="utf-8")
    (ROOT/test_path).write_text(tests,encoding="utf-8")
    shell(sys.executable, "-m", "compileall", "-q", module_path, test_path, timeout=25,secretless=True)
    shell(sys.executable, "-m", "pytest", "-q", test_path, timeout=150,secretless=True)
    shell("git", "diff", "--check", timeout=20,secretless=True)
    return module_path,test_path


def commit_and_open_pr(workpacket, paths):
    workpacket_slug = hashlib.sha256(workpacket.encode()).hexdigest()[:12]
    run_id = os.environ.get("GITHUB_RUN_ID", "0")
    branch = "sina/noos-coder-" + workpacket_slug + "-" + run_id
    shell("git","config","user.name","noetfield-cloud-coder[bot]")
    shell("git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com")
    shell("git","switch","-c",branch)
    shell("git","add","--",*paths)
    shell("git","commit","-m","feat(noos): scoped coding WorkPacket "+workpacket)
    head_sha = shell("git","rev-parse","HEAD")
    # Token was absent from git config while running model-generated code.
    shell("gh","auth","setup-git")
    shell("git","push","-u","origin",branch,timeout=90)
    title = "NOOS Cloud Coder: " + workpacket[:90]
    body = ("Founder-approved WorkPacket: " + workpacket +
            "\nSource: signed GitHub Actions + Railway PostgreSQL queue." +
            "\nBuilder SHA: " + head_sha +
            "\nGenerated files: " + ", ".join(paths) +
            "\nPassed: Python compilation + isolated targeted pytest." +
            "\nIndependent verifier/release is a separate workflow stage.")
    try:
        pr_url = shell("gh","pr","create","--base",BASE,"--head",branch,
                       "--title",title,"--body",body,timeout=60)
    except RuntimeError as exc:
        if "not permitted to create or approve pull requests" in str(exc):
            print("NOOS_GITHUB_POLICY_PR_DENIED_BRANCH_RETAINED")
            return head_sha, branch, None
        raise
    if not re.fullmatch(r"https://github\.com/Noetfield-Systems/noetfeld-os/pull/\d+",pr_url):
        raise RuntimeError("GITHUB_PR_RETURNED_UNEXPECTED_URL")
    return head_sha,branch,pr_url


def main():
    token=oidc()
    queue_issue(token)
    claim=api("/v1/coding/claim",{"repo":REPO,"lease_minutes":45},token)
    if not claim.get("ok"):
        raise RuntimeError("QUEUE_CLAIM_FAILED")
    if claim.get("state")=="IDLE":
        output(state="IDLE")
        print("NOOS_CODING_QUEUE_IDLE")
        return
    job=claim["job"]
    workpacket=job["workpacket_id"]
    suffix=hashlib.sha256(workpacket.encode()).hexdigest()[:12]
    print("NOOS_CODING_CLAIMED " + workpacket)
    try:
        paths=write_and_test(job["prompt"],suffix)
        head,branch,pr=commit_and_open_pr(workpacket,paths)
        evidence={"github_run_id":os.environ.get("GITHUB_RUN_ID"),
                  "commit_sha":head,"branch":branch,"pr_url":pr,
                  "paths":list(paths),"test_command":"pytest -q "+paths[1],
                  "tests_passed":True,"independently_verified":False}
        state="PR_OPENED" if pr else "BLOCKED"
        result=api("/v1/coding/report",{"job_id":job["job_id"],
                   "lease_token":job["lease_token"],"state":state,
                   "evidence":evidence},token)
        if not result.get("ok"):
            raise RuntimeError("QUEUE_RESULT_REPORT_FAILED")
        output(state=state,branch=branch,pr_url=pr or "",
               job_id=job["job_id"],test_path=paths[1])
        print("NOOS_CODE_RESULT "+state+" "+workpacket)
        if state == "PR_OPENED":
            # Restart on the next queued job without another Founder prompt.
            # GitHub cron remains the durable recovery path when dispatch is denied.
            try:
                stats=request(API+"/v1/coding/status",token=token)
                if int((stats.get("counts") or {}).get("QUEUED",0)) > 0:
                    shell("gh","workflow","run","noos-cloud-coder.yml","--ref","main",
                          timeout=25)
                    print("NOOS_CONTINUATION_DISPATCHED")
            except Exception:
                print("NOOS_CONTINUATION_SCHEDULE_FALLBACK")
    except Exception as exc:
        try:
            api("/v1/coding/report",{"job_id":job["job_id"],
                "lease_token":job["lease_token"],"state":"FAILED",
                "evidence":{"failure":type(exc).__name__,
                "github_run_id":os.environ.get("GITHUB_RUN_ID")}},token)
        except Exception:
            pass
        raise


if __name__=="__main__":
    main()
