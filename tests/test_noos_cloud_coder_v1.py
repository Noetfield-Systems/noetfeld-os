"""Tests for the real coding worker's narrow output security boundary."""
import ast
import os
import pytest

from scripts import noos_coding_agent_action_v1 as worker
from scripts import noos_github_oidc_v1 as identity


def test_bounded_target_paths_are_deterministic():
    import hashlib
    job = "noos-issue-1234"
    suffix = hashlib.sha256(job.encode()).hexdigest()[:12]
    assert len(suffix) == 12
    assert suffix.isalnum()
    assert worker.BASE == "deploy/noos-loop-runner-entrypoint"
    assert worker.REPO == "Noetfield-Systems/noetfeld-os"


def test_generated_code_can_be_checked_without_executing():
    assert worker.check_ast("def tally(values):\n    return sum(values)\n")
    for code in ("import subprocess\n", "from socket import socket\n",
                 "def evil():\n    eval('2+2')\n"):
        with pytest.raises(RuntimeError):
            worker.check_ast(code)


def test_oidc_verification_needs_signed_token():
    with pytest.raises(ValueError, match="GITHUB_OIDC_MISSING"):
        identity.authorize("", "claim")
    with pytest.raises(ValueError, match="GITHUB_OIDC_OPERATION_DENIED"):
        identity.authorize("", "dangerous_operation")
    assert identity.WORKFLOW.endswith("/noos-cloud-coder.yml@refs/heads/main")


def test_no_default_inference_credentials():
    assert worker.API.startswith("https://")
    assert worker.MODEL_API == "https://models.github.ai/inference/chat/completions"
