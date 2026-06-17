"""Final public simplification: no internal architecture names on marketing surfaces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PUBLIC_PAGES = (
    ROOT / "index.html",
    ROOT / "enterprise" / "index.html",
    ROOT / "trust-brief" / "index.html",
    ROOT / "copilot" / "index.html",
    ROOT / "console" / "index.html",
)

FORBIDDEN_PHRASES = (
    "Golden Edge",
    "GCIP",
    "STRATEGIC_LOCK",
    "PRODUCT_TRUTH",
    "pre-execution",
    "audit ledger",
    "Golden Edge v3",
    "PostgreSQL",
    "FastAPI",
)

PRIMARY_NAV = ("/copilot/", "/templates/", "/trust/", "/enterprise/", "/pricing/", "/partners/")


def test_positioning_exact_sentence() -> None:
    text = (ROOT / "POSITIONING.md").read_text(encoding="utf-8").strip()
    assert text.endswith(
        "Governance Execution Infrastructure that evaluates AI-driven operational intent before execution in regulated environments."
    )


def test_product_brief_no_internal_names() -> None:
    text = (ROOT / "PRODUCT_BRIEF.md").read_text(encoding="utf-8")
    for phrase in ("Golden Edge", "GCIP", "STRATEGIC_LOCK", "NOS", "NPL"):
        assert phrase not in text


def test_public_pages_no_internal_architecture_terms() -> None:
    for path in PUBLIC_PAGES:
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, f"{path.name}: {phrase}"


def test_header_primary_nav_items() -> None:
    header = (ROOT / "assets" / "partials" / "header.html").read_text(encoding="utf-8")
    primary = header.split('class="menuPrimary"', 1)[1].split("</div>", 1)[0]
    for href in PRIMARY_NAV:
        assert href in primary, href
    assert primary.count("<a ") == 6
    assert "/directory/" not in header
    assert 'href="/gate/' not in header
    assert "Work with us" not in primary
    assert "Next steps" not in primary


def test_gate_index_redirects_enterprise() -> None:
    text = (ROOT / "gate" / "index.html").read_text(encoding="utf-8")
    assert "/enterprise/" in text


def test_directory_redirects_home() -> None:
    text = (ROOT / "directory" / "index.html").read_text(encoding="utf-8")
    assert 'url="/"' in text or 'url=/' in text


def test_console_ui_product_language() -> None:
    text = (ROOT / "services" / "governance" / "noetfield_governance" / "static" / "governance-console-v1.html").read_text(
        encoding="utf-8"
    )
    assert "Governance Evaluation Interface" in text
    assert "Compliance log" in text or "compliance log" in text
    assert "Golden Edge" not in text
    assert "PostgreSQL" not in text
    assert "Submit Intent" in text
    assert "View Decision + Compliance Log" in text
