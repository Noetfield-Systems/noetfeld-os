"""Commercial agentic surfaces — demo, trial, Google-pattern reference."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DEMO = ROOT / "copilot" / "demo" / "index.html"
TRIAL = ROOT / "copilot" / "trial" / "index.html"
REF = ROOT / "docs" / "strategy" / "COMMERCIAL_AGENTIC_UI_REFERENCE_v1.md"
HEADER = ROOT / "assets" / "partials" / "header.html"


def test_commercial_agentic_reference_doc_exists() -> None:
    text = REF.read_text(encoding="utf-8")
    assert "ADK" in text
    assert "A2UI" in text
    assert "AG-UI" in text


def test_demo_page_has_interactive_agent_trace() -> None:
    text = DEMO.read_text(encoding="utf-8")
    assert "nf26-demoStepper" in text
    assert "nf26-eventTrace" in text
    assert "Human-in-the-loop" in text


def test_trial_page_positions_sandbox_not_fourth_sku() -> None:
    text = TRIAL.read_text(encoding="utf-8").lower()
    assert "sandbox" in text
    assert "three contract" in text
    assert "fourth sku" not in text
    assert "quickscan" not in text


def test_trial_page_links_start_sandbox() -> None:
    text = TRIAL.read_text(encoding="utf-8")
    assert 'href="/start/"' in text


def test_header_links_demo_and_trial() -> None:
    text = HEADER.read_text(encoding="utf-8")
    assert "/copilot/demo/" in text
    assert "/copilot/trial/" in text


def test_homepage_links_commercial_agentic_surfaces() -> None:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "/copilot/demo/" in text
    assert "/copilot/trial/" in text
