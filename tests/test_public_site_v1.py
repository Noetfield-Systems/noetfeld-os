"""Tests for public institutional site routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def site_client():
    from run import app

    return TestClient(app)


def test_privacy_page(site_client: TestClient) -> None:
    response = site_client.get("/privacy/")
    assert response.status_code == 200
    assert "Privacy Notice" in response.text
    assert "cookie-banner" in response.text


def test_cookies_page(site_client: TestClient) -> None:
    response = site_client.get("/cookies/")
    assert response.status_code == 200
    assert "Cookie Policy" in response.text
    assert "noos_cookie_consent_v1" in response.text


def test_static_cookie_script(site_client: TestClient) -> None:
    response = site_client.get("/static/cookies.js")
    assert response.status_code == 200
    assert "noos_cookie_consent_v1" in response.text
