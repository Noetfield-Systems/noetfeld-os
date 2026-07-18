"""Fixture: a real lint failure — an unused import (ruff F401)."""

import os  # BUG: unused import; ruff F401 fails CI


def slugify(text):
    return "-".join(text.lower().split())
