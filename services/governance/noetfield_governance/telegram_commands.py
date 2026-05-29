"""Professional command copy and inline keyboards for Telegram."""

from __future__ import annotations

from noetfield_config import CANONICAL_INTAKE_EMAIL
from noetfield_governance.telegram_format import bold, escape_html, link

INTAKE_URL = "https://www.noetfield.com/trust-brief/intake/"
ENTERPRISE_URL = "https://www.noetfield.com/enterprise/"
FAQ_URL = "https://www.noetfield.com/faq/"
CONSOLE_URL = "https://www.noetfield.com/console/"


def welcome_message(first_name: str | None = None) -> str:
    name = escape_html(first_name) if first_name else "there"
    return (
        f"{bold('Noetfield')}\n"
        f"Governance execution infrastructure\n\n"
        f"Hello {name} — I am the institutional assistant for regulated organizations.\n\n"
        f"I can explain our three offerings, intake process, and Governance Console.\n"
        f"I do not execute payments or hold custody.\n\n"
        f"{bold('Quick commands')}\n"
        "/offerings — Trust Brief, Copilot, Bank Pilot\n"
        "/trustbrief — $10,000 diagnostic\n"
        "/intake — request a Governance Brief\n"
        "/human — contact operations\n\n"
        f"Or ask any question in plain language."
    )


def offerings_message() -> str:
    return (
        f"{bold('Three offerings (contract only)')}\n\n"
        f"1. {bold('Trust Brief')} — $10,000 · 6 weeks\n"
        "Governance audit, AI policy mapping, risk exposure analysis.\n\n"
        f"2. {bold('Copilot Governance Pack')}\n"
        "Enterprise AI compliance for Microsoft 365 Copilot rollouts.\n\n"
        f"3. {bold('Bank Pilot')}\n"
        "Read-only governance simulation · shadow mode · no execution rights.\n\n"
        f"{link(INTAKE_URL, 'Request Governance Brief')}"
    )


def trustbrief_message() -> str:
    return (
        f"{bold('Trust Brief')} — {bold('$10,000')}\n"
        "Fixed six-week engagement for boards and risk leaders.\n\n"
        "Deliverables: governance audit, AI policy map, risk exposure analysis, "
        "executive-ready outputs.\n\n"
        f"{link(INTAKE_URL, 'Start intake')} · {escape_html(CANONICAL_INTAKE_EMAIL)}"
    )


def intake_message() -> str:
    return (
        f"{bold('Request Governance Brief')}\n"
        "Non-confidential intake for scope confirmation.\n\n"
        f"{link(INTAKE_URL, 'Open intake form')}\n"
        f"Email: {escape_html(CANONICAL_INTAKE_EMAIL)}"
    )


def human_message() -> str:
    return (
        f"{bold('Operations intake')}\n"
        f"Email: {escape_html(CANONICAL_INTAKE_EMAIL)}\n"
        f"Web: {link(INTAKE_URL, 'trust-brief/intake')}\n\n"
        "Include your organization name and Request ID if you have one."
    )


def main_menu_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "Trust Brief ($10K)", "callback_data": "menu:trustbrief"},
                {"text": "Copilot Pack", "callback_data": "menu:copilot"},
            ],
            [
                {"text": "Bank Pilot", "callback_data": "menu:bankpilot"},
                {"text": "All offerings", "callback_data": "menu:offerings"},
            ],
            [
                {"text": "Request Brief", "url": INTAKE_URL},
                {"text": "FAQ on web", "url": FAQ_URL},
            ],
        ]
    }


def after_reply_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "Request Brief", "url": INTAKE_URL},
                {"text": "Talk to ops", "callback_data": "menu:human"},
            ],
        ]
    }


BOT_COMMANDS: list[dict[str, str]] = [
    {"command": "start", "description": "Welcome and main menu"},
    {"command": "help", "description": "How to use this assistant"},
    {"command": "offerings", "description": "Three contract offerings"},
    {"command": "trustbrief", "description": "Trust Brief — $10,000"},
    {"command": "copilot", "description": "Copilot Governance Pack"},
    {"command": "pilot", "description": "Bank Pilot (read-only)"},
    {"command": "intake", "description": "Request Governance Brief"},
    {"command": "human", "description": "Contact operations"},
    {"command": "reset", "description": "Clear conversation context"},
]
