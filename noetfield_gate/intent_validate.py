"""Intent validation against OpenAPI DecisionRequest (UPG-0156)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def validate_intent_file(path: Path) -> dict[str, Any]:
    from router import DecisionRequest

    raw = json.loads(path.read_text(encoding="utf-8"))
    model = DecisionRequest.model_validate(raw)
    return {
        "ok": True,
        "schema": "decision-request-v1",
        "path": str(path),
        "applicant_id": model.applicant_id,
        "fields": list(model.model_dump().keys()),
    }


__all__ = ["validate_intent_file"]
