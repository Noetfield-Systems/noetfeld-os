"""Public HTML must align with final GTM simplification (no legacy surfaces)."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_IN_HOME = (
    "Cross-Border Payments",
    "Payment Intent",
    "FX Calculator",
    "Active Corridors",
    "Submit Payment",
)

TIER_PAGES = (
    "index.html",
    "enterprise/index.html",
    "trust-brief/index.html",
    "copilot/index.html",
    "console/index.html",
)


def test_homepage_has_no_prohibited_payment_language() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    for phrase in FORBIDDEN_IN_HOME:
        assert phrase not in text, f"index.html still contains: {phrase}"


def test_homepage_states_governance_positioning() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    assert "governance" in text
    assert "request governance brief" in text


def test_positioning_locked_sentence() -> None:
    text = (ROOT / "POSITIONING.md").read_text(encoding="utf-8")
    assert (
        "Governance Execution Infrastructure that evaluates AI-driven operational intent before execution in regulated environments."
        in text
    )


def test_offerings_locked_three_tiers() -> None:
    text = (ROOT / "OFFERINGS_LOCKED.md").read_text(encoding="utf-8")
    assert "Trust Brief" in text
    assert "$10,000" in text
    assert "Copilot Governance Pack" in text
    assert "Bank Pilot" in text
    assert "v6.1" not in text


def test_enterprise_page_structure() -> None:
    text = (ROOT / "enterprise" / "index.html").read_text(encoding="utf-8")
    assert "Request Governance Brief" in text
    assert "10,000" in text
    for heading in ("Problem", "Risk", "Solution"):
        assert heading in text
    assert "Golden Edge" not in text


def test_directory_redirects_home() -> None:
    text = (ROOT / "directory" / "index.html").read_text(encoding="utf-8")
    assert 'url="/"' in text or 'url=/' in text


def test_resources_redirects_enterprise() -> None:
    text = (ROOT / "resources" / "index.html").read_text(encoding="utf-8")
    assert "/enterprise/" in text


def test_gate_index_redirects_enterprise() -> None:
    text = (ROOT / "gate" / "index.html").read_text(encoding="utf-8")
    assert "/enterprise/" in text


def test_trust_ledger_explainer_not_subscription() -> None:
    text = (ROOT / "trust-ledger" / "index.html").read_text(encoding="utf-8")
    assert "Trust Ledger" in text
    assert "audit-export" in text or "audit export" in text.lower()
    assert "stripe-buy-button" not in text.lower()
    assert 'http-equiv="refresh"' not in text


def test_offerings_strip_partial_exists() -> None:
    text = (ROOT / "assets" / "partials" / "offerings-strip.html").read_text(encoding="utf-8")
    assert "Request Governance Brief" in text


def test_tier_pages_have_shell_and_cta() -> None:
    for rel in TIER_PAGES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "nfHeader" in text, rel
        assert "Request Governance Brief" in text, rel
        assert 'name="viewport"' in text, rel


def test_bank_grade_p0_pages_have_responsive_shell() -> None:
    for rel in ("bank-pilot/index.html", "enterprise/index.html", "trust-brief/intake/index.html"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert 'name="viewport"' in text, rel
        assert "noetfield-tokens.css" in text, rel
        assert "nfHeader" in text or "nf-page" in text or "wrap" in text, rel


def test_bank_grade_html_smoke_script() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "smoke_bank_grade_html.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_public_site_health_script() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_public_site_health.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_product_brief_external_only() -> None:
    text = (ROOT / "PRODUCT_BRIEF.md").read_text(encoding="utf-8")
    assert "Golden Edge" not in text
    assert "GCIP" not in text


def test_internal_docs_still_present_for_repo() -> None:
    assert (ROOT / "NORTH_STAR.md").is_file()
    assert (ROOT / "PRODUCT_TRUTH.md").is_file()
