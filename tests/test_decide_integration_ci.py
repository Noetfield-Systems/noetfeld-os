"""UPG-0160 — integration: noetfield decide against live local test server."""

from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn

from noetfield_gate.cli import main


def _free_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@pytest.fixture()
def live_api_url(temp_runtime):
    app, raw_key = temp_runtime
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 10
    while not server.started and time.time() < deadline:
        time.sleep(0.05)
    if not server.started:
        pytest.fail("uvicorn test server did not start")
    yield f"http://127.0.0.1:{port}", raw_key
    server.should_exit = True


def test_decide_cli_against_live_local_server(live_api_url, tmp_path):
    api_url, api_key = live_api_url
    receipt = tmp_path / "decision-receipt.json"
    code = main(
        [
            "decide",
            "--sample",
            "--api-url",
            api_url,
            "--api-key",
            api_key,
            "--out",
            str(receipt),
        ]
    )
    assert code == 0
    assert receipt.is_file()
    body = receipt.read_text(encoding="utf-8")
    assert "APPROVE" in body or "REVIEW" in body or "DECLINE" in body
