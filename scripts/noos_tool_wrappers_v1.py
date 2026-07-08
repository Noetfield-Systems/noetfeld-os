#!/usr/bin/env python3
"""NOOS tool wrappers (M2): allowlist-only named wrappers for git operations.

Wrappers enforce branch name patterns and forbid shell metacharacters. They route
actual git execution through the ToolBroker to centralize execution and receipts.

Functions:
- git_push_task_branch(branch, remote='origin', set_upstream=True): validate branch name, then push via broker.
- open_pr_task_branch(branch, title, body, base='main'): create a PR using gh CLI via broker (gh must be allowlisted in broker).

This module intentionally keeps behavior minimal: validation, no raw shell strings.
"""
from __future__ import annotations

import re
from typing import Dict, Any, List
from scripts.noos_tool_broker_v1 import ToolBroker

# Branch pattern: allow typical task/feature/fix/chore prefixes and kebab-case
BRANCH_RE = re.compile(r"^(?:task|feat|fix|chore|followup)\/[a-z0-9\-]+(?:\/[a-z0-9\-]+)*$")

broker = ToolBroker(allowlist=["git", "gh"], cost_cap_usd=1.0)


class WrapperError(Exception):
    pass


def _validate_branch(branch: str) -> None:
    if not branch or not isinstance(branch, str):
        raise WrapperError("invalid branch name: empty or not a string")
    if not BRANCH_RE.match(branch):
        raise WrapperError(f"branch name does not match allowed pattern: {branch}")


def git_push_task_branch(branch: str, remote: str = "origin", set_upstream: bool = True) -> Dict[str, Any]:
    """Push the local branch to remote enforcing branch name rules via the broker.

    Returns broker receipt dict.
    """
    _validate_branch(branch)
    cmd: List[str] = ["git", "push"]
    if set_upstream:
        cmd += [remote, f"{branch}:{branch}", "--set-upstream"]
    else:
        cmd += [remote, branch]
    return broker.execute(cmd)


def open_pr_task_branch(branch: str, title: str, body: str = "", base: str = "main") -> Dict[str, Any]:
    """Create a PR using gh CLI via the broker. gh must be allowed by broker.

    Note: this wrapper constructs a gh command array (no shell) and routes it through broker.
    """
    _validate_branch(branch)
    if not title:
        raise WrapperError("title required for PR")
    # gh pr create --title "..." --body "..." --base main --head branch
    cmd = ["gh", "pr", "create", "--title", title, "--body", body or "", "--base", base, "--head", branch]
    return broker.execute(cmd)


# CLI helper for manual testing (kept minimal)
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("usage: noos_tool_wrappers_v1.py push <branch> or pr <branch> <title>")
        raise SystemExit(2)
    action = sys.argv[1]
    if action == "push":
        r = git_push_task_branch(sys.argv[2])
        print(r)
    elif action == "pr":
        if len(sys.argv) < 4:
            print("pr requires branch and title")
            raise SystemExit(2)
        r = open_pr_task_branch(sys.argv[2], sys.argv[3], body="")
        print(r)
    else:
        print("unknown action")
        raise SystemExit(2)
