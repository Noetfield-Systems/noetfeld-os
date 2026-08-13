"""Public operator tools on the noetfeld-os site."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from public_site.tools import PAGES, PUBLIC_ORIGIN, canonical

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "public_site" / "static" / "tools.js").read_text(encoding="utf-8")
LOAD = 1.3
WEEKS = 48
HOBBY = 3000


@pytest.fixture
def site_client():
    from run import app

    return TestClient(app)


def process_cost(touches: float, minutes: float, rate: float, people: float) -> float:
    return touches * (minutes / 60) * rate * LOAD * people * WEEKS


def test_engine_constants_match_the_operator_post() -> None:
    assert "var LOAD = 1.3;" in JS
    assert "var WEEKS = 48;" in JS
    assert "var HOBBY = 3000;" in JS
    assert "Nothing is posted" in JS
    assert "/copilot/readiness/" not in JS
    assert "/copilot/pilot/" in JS


def test_quiet_leak_hobby_line() -> None:
    small = process_cost(2, 5, 30, 1)
    large = process_cost(10, 12, 45, 3)
    assert small < HOBBY
    assert large > HOBBY
    assert round(large) == 16848


def test_tools_hub_and_each_check(site_client: TestClient) -> None:
    hub = site_client.get("/tools/")
    assert hub.status_code == 200
    assert "leave a process alone" in hub.text.lower() or "leave-it-alone" in hub.text.lower()
    assert 'href="/tools/quiet-leak/"' in hub.text
    assert "index,follow" in hub.text
    assert f'canonical" href="{PUBLIC_ORIGIN}/tools/"' in hub.text
    assert "/static/tools.js" in hub.text
    for slug in PAGES:
        response = site_client.get(f"/tools/{slug}/")
        assert response.status_code == 200, slug
        assert "Nothing stored" in response.text or "nothing stored" in response.text.lower() or "do not store" in response.text.lower() or "nf-tools-form" in response.text or "data-embed-src" in response.text
        assert canonical(slug) in response.text


def test_nav_and_trust_ledger_point_at_tools(site_client: TestClient) -> None:
    ledger = site_client.get("/trust-ledger/")
    assert ledger.status_code == 200
    assert 'href="/tools/"' in ledger.text
    assert "operator tools" in ledger.text


def test_unknown_tool_is_404(site_client: TestClient) -> None:
    response = site_client.get("/tools/not-a-real-check/")
    assert response.status_code == 404


def test_privacy_still_renders_after_nav_change(site_client: TestClient) -> None:
    response = site_client.get("/privacy/")
    assert response.status_code == 200
    assert "Privacy Notice" in response.text
    assert 'href="/tools/"' in response.text
