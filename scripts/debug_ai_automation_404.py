#!/usr/bin/env python3
"""Debug 404 for /ai-automation/ — writes NDJSON to session log."""
from __future__ import annotations

import json
import subprocess
import time
import urllib.request
from pathlib import Path

LOG = Path("/Users/sinakazemnezhad/Desktop/Noetfield-All-Documents/.cursor/debug-816a74.log")
ROOT = Path(__file__).resolve().parents[1]
SESSION = "816a74"


def log(hypothesis_id: str, message: str, data: dict, run_id: str = "pre-fix") -> None:
    entry = {
        "sessionId": SESSION,
        "hypothesisId": hypothesis_id,
        "location": "scripts/debug_ai_automation_404.py",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
        "runId": run_id,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def http_status(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return -1


def main() -> None:
    import sys
    run_id = sys.argv[1] if len(sys.argv) > 1 else "pre-fix"
    local_file = ROOT / "ai-automation" / "index.html"
    tracked = subprocess.run(
        ["git", "ls-files", "ai-automation/index.html"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout.strip()
    on_origin = subprocess.run(
        ["git", "ls-tree", "-r", "origin/cursor/bank-grade-fullstack-37f0", "--name-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout.strip()

    on_main = ""
    if subprocess.run(["git", "fetch", "origin", "main"], cwd=ROOT, capture_output=True).returncode == 0:
        on_main = subprocess.run(
            ["git", "ls-tree", "-r", "origin/main", "--name-only"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        ).stdout

    log("H1", "local file + git track state", {
        "local_exists": local_file.is_file(),
        "git_tracked": bool(tracked),
        "current_branch": branch,
        "on_origin_bank_grade": "ai-automation/index.html" in on_origin,
        "on_origin_main": "ai-automation/index.html" in on_main,
    }, run_id)
    log("H2", "production HTTP status", {
        "ai_automation_status": http_status("https://www.noetfield.com/ai-automation/"),
        "copilot_control_status": http_status("https://www.noetfield.com/copilot/"),
    }, run_id)


if __name__ == "__main__":
    main()
