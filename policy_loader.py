"""
Governance layer for NOETFELD OS.

This module is responsible for loading JSON policy definitions that
constrain and shape how the decision engine behaves.

The design keeps policy I/O separate from the core engine so that:
* product/ops can evolve JSON safely,
* the engine can depend on stable, typed structures.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from config import BASE_DIR


POLICY_DIR: Path = BASE_DIR


@dataclass(frozen=True)
class CorridorRule:
    """
    A single corridor rule defines allowed ranges for a metric and the
    decision that should be enforced when the corridor is violated.
    """

    name: str
    metric: str
    min_value: float | None
    max_value: float | None
    on_breach_decision: str  # e.g. "REVIEW" or "DECLINE"


@dataclass(frozen=True)
class BasePolicy:
    """
    Base policy defines the default behaviour of the decision engine:

    * score thresholds for APPROVE / REVIEW / DECLINE
    * whether manual overrides are allowed
    """

    approve_threshold: float
    review_threshold: float
    allow_manual_override: bool = True


@dataclass(frozen=True)
class CorridorPolicy:
    """
    Corridor policy is a collection of corridor rules.
    """

    corridors: list[CorridorRule]

    def find_breaches(self, metrics: dict[str, float]) -> list[CorridorRule]:
        """
        Given a dict of metric -> value, return all corridor rules that
        are breached.
        """
        breaches: list[CorridorRule] = []
        for rule in self.corridors:
            value = metrics.get(rule.metric)
            if value is None:
                continue
            if rule.min_value is not None and value < rule.min_value:
                breaches.append(rule)
                continue
            if rule.max_value is not None and value > rule.max_value:
                breaches.append(rule)
        return breaches


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_base_policy(path: Path | None = None) -> BasePolicy:
    """
    Load the base policy JSON and return a typed object.
    """
    if path is None:
        path = POLICY_DIR / "base_policy.json"
    raw = _load_json(path)
    return BasePolicy(
        approve_threshold=float(raw["approve_threshold"]),
        review_threshold=float(raw["review_threshold"]),
        allow_manual_override=bool(raw.get("allow_manual_override", True)),
    )


def load_corridor_policy(path: Path | None = None) -> CorridorPolicy:
    """
    Load the corridor policy JSON and return a typed object.
    """
    if path is None:
        path = POLICY_DIR / "corridor_policy.json"
    raw = _load_json(path)
    corridors: list[CorridorRule] = []
    for item in raw.get("corridors", []):
        corridors.append(
            CorridorRule(
                name=str(item["name"]),
                metric=str(item["metric"]),
                min_value=float(item["min_value"]) if item.get("min_value") is not None else None,
                max_value=float(item["max_value"]) if item.get("max_value") is not None else None,
                on_breach_decision=str(item.get("on_breach_decision", "REVIEW")),
            )
        )
    return CorridorPolicy(corridors=corridors)


__all__ = [
    "BasePolicy",
    "CorridorRule",
    "CorridorPolicy",
    "load_base_policy",
    "load_corridor_policy",
]

