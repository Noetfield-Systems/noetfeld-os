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

PILOT_CTA = "Apply for pilot"


def test_homepage_has_no_prohibited_payment_language() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    for phrase in FORBIDDEN_IN_HOME:
        assert phrase not in text, f"index.html still contains: {phrase}"


def test_homepage_states_governance_positioning() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    assert "governance" in text
    assert "the audit trail your copilot deployment will be asked for later" in text
    assert "apply for pilot" in text
    assert "eu ai act art. 12" in text
    assert "tamper-evident" in text


def test_public_www_has_no_design_partner_language() -> None:
    paths = (
        "index.html",
        "copilot/pilot/index.html",
        "assets/partials/header.html",
        "assets/partials/footer.html",
        "investors/index.html",
    )
    for rel in paths:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "design-partner" not in text, rel
        assert "design partner" not in text, rel


def test_public_www_has_no_legacy_comparison_headlines() -> None:
    text = (ROOT / "investors/index.html").read_text(encoding="utf-8")
    assert "Available now vs what capital accelerates" not in text


def test_homepage_section_count_at_most_eight() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    count = text.count("<section")
    assert count <= 8, f"homepage has {count} sections; expected ≤8 (U5 v17 compression)"


def test_homepage_has_export_assurance_inner() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "Export assurance" in text
    assert "Full buyer depth" in text


def test_pilot_page_has_lane_depth_blocks() -> None:
    text = (ROOT / "copilot" / "pilot" / "index.html").read_text(encoding="utf-8")
    for needle in ("Digital trust lane", "Governance gaps", "Buyer voices", "Policy-bound workflows"):
        assert needle in text, needle


def test_pilot_intake_hides_legacy_sticky_and_prepare() -> None:
    js = (ROOT / "assets" / "noetfield-intake-pilot-mode.js").read_text(encoding="utf-8")
    assert "intakeStickyCta" in js
    assert "tbPrepareTrustBrief" in js
    assert "sticky.hidden = true" in js or "sticky) sticky.hidden = true" in js


def test_pilot_intake_page_has_governance_pack_mode() -> None:
    text = (ROOT / "trust-brief" / "intake" / "index.html").read_text(encoding="utf-8")
    assert "noetfield-intake-pilot-mode.js" in text
    assert "intakeHeroPilot" in text
    assert "Copilot Governance Pack" in text
    assert "Submit pilot application" in text
    assert "tb_pilot_band" in text


def test_positioning_locked_sentence() -> None:
    text = (ROOT / "POSITIONING.md").read_text(encoding="utf-8")
    assert (
        "Governance Execution Infrastructure that evaluates AI-driven operational intent before execution in regulated environments."
        in text
    )


def test_offerings_locked_three_tiers() -> None:
    text = (ROOT / "OFFERINGS_LOCKED.md").read_text(encoding="utf-8")
    assert "Trust Brief" in text
    assert "$10,000" in text or "$10k" in text.lower()
    assert "Copilot Governance Pack" in text
    assert "Bank Pilot" in text
    assert "interest=pilot" in text.lower()
    assert "v6.1" not in text


def test_enterprise_page_structure() -> None:
    text = (ROOT / "enterprise" / "index.html").read_text(encoding="utf-8")
    assert PILOT_CTA in text
    assert "10,000" in text or "$10k" in text.lower()
    assert "regulated" in text.lower()
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
    assert "tamper-evident" in text.lower() or "evaluate" in text.lower()
    assert "stripe-buy-button" not in text.lower()
    assert 'http-equiv="refresh"' not in text


def test_offerings_strip_partial_exists() -> None:
    text = (ROOT / "assets" / "partials" / "offerings-strip.html").read_text(encoding="utf-8")
    assert PILOT_CTA in text
    assert "Pilot · $2k–10k" in text


def test_footer_partial_pilot_first() -> None:
    text = (ROOT / "assets" / "partials" / "footer.html").read_text(encoding="utf-8")
    assert "Apply for pilot ($2k–10k)" in text
    assert "Copilot Governance Pack" in text


def test_tier_pages_have_shell_and_cta() -> None:
    for rel in TIER_PAGES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "nfHeader" in text, rel
        assert PILOT_CTA in text, rel
        assert 'name="viewport"' in text, rel


def test_pilot_page_full_landing() -> None:
    text = (ROOT / "copilot" / "pilot" / "index.html").read_text(encoding="utf-8")
    assert "GTM-locked pilot success signals" in text
    assert "Pilot deliverables" in text
    assert "interest=pilot" in text
    assert "QuickScan" in text


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
