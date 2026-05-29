"""Public HTML must not contain prohibited financial product language."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_IN_HOME = (
    "Cross-Border Payments",
    "Payment Intent",
    "FX Calculator",
    "Active Corridors",
    "Submit Payment",
)

ALLOWED_PUBLIC = (
    ROOT / "index.html",
    ROOT / "platform" / "index.html",
    ROOT / "platform" / "dashboard" / "index.html",
)


def test_homepage_has_no_prohibited_payment_language() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    for phrase in FORBIDDEN_IN_HOME:
        assert phrase not in text, f"index.html still contains: {phrase}"


def test_homepage_states_governance_positioning() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    assert "governance" in text
    assert "request governance brief" in text


def test_product_truth_single_sentence() -> None:
    text = (ROOT / "PRODUCT_TRUTH.md").read_text(encoding="utf-8")
    assert "Governance Execution & AI Policy Enforcement Infrastructure" in text


def test_offerings_locked_three_tiers() -> None:
    text = (ROOT / "OFFERINGS_LOCKED.md").read_text(encoding="utf-8")
    assert "Trust Brief" in text
    assert "$10,000" in text or "$10K" in text
    assert "Copilot Governance Pack" in text
    assert "Bank Pilot v6.1" in text


def test_enterprise_page_exists() -> None:
    text = (ROOT / "enterprise" / "index.html").read_text(encoding="utf-8")
    assert "book governance assessment" in text.lower()
    assert "10,000" in text


def test_platform_dashboard_has_no_treasury_corridor_ui() -> None:
    text = (ROOT / "platform" / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "Treasury Routing" not in text
    assert "In-Flight Settlements" not in text
    assert "Active Corridors" not in text


def test_north_star_exists() -> None:
    assert (ROOT / "NORTH_STAR.md").is_file()
    assert (ROOT / "OFFERINGS.md").is_file()
