"""
Risk model for NOETFELD OS.

This module converts raw applicant + deal inputs into:
* engineered risk features
* a composite score on a 0–100 scale
* a per-factor score breakdown compatible with SCORING_WEIGHTS.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from config import (
    CREDIT_SCORE_MIN,
    CREDIT_SCORE_MAX,
    DTI_MAX_APPROVE,
    LTV_MAX_STANDARD,
    SCORING_WEIGHTS,
)


@dataclass(frozen=True)
class RiskFeatures:
    credit_score: float
    dti_ratio: float
    employment_history_years: float
    ltv_ratio: float
    liquid_reserves_months: float


@dataclass(frozen=True)
class RiskResult:
    composite_score: float
    scores: dict[str, float]
    features: RiskFeatures


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _scale_unit_to_100(x: float) -> float:
    return _clamp(x, 0.0, 1.0) * 100.0


def engineer_features(payload: Mapping[str, Any]) -> RiskFeatures:
    """
    Extract and normalise the core risk features from an input payload.

    Expected keys in `payload` (caller validated in the API layer):
    * credit_score (int/float)
    * monthly_debt (float)
    * monthly_income (float)
    * loan_amount (float)
    * collateral_value (float)
    * employment_history_years (float)
    * liquid_reserves_months (float)
    """
    credit_score = float(payload.get("credit_score", CREDIT_SCORE_MIN))
    monthly_debt = float(payload.get("monthly_debt", 0.0))
    monthly_income = float(payload.get("monthly_income", 1.0))
    loan_amount = float(payload.get("loan_amount", 0.0))
    collateral_value = float(payload.get("collateral_value", max(loan_amount, 1.0)))
    employment_years = float(payload.get("employment_history_years", 0.0))
    reserves_months = float(payload.get("liquid_reserves_months", 0.0))

    dti_ratio = monthly_debt / monthly_income if monthly_income > 0 else 1.0
    ltv_ratio = loan_amount / collateral_value if collateral_value > 0 else 1.0

    return RiskFeatures(
        credit_score=credit_score,
        dti_ratio=dti_ratio,
        employment_history_years=employment_years,
        ltv_ratio=ltv_ratio,
        liquid_reserves_months=reserves_months,
    )


def score(features: RiskFeatures) -> RiskResult:
    """
    Perform a simple, explainable scoring based on engineered features.
    """
    # Credit score normalised to [0, 1]
    credit_unit = _clamp(
        (features.credit_score - CREDIT_SCORE_MIN)
        / (CREDIT_SCORE_MAX - CREDIT_SCORE_MIN),
        0.0,
        1.0,
    )

    # Lower DTI is better; 0 at DTI_MAX_APPROVE and 1 at 0
    dti_unit = 1.0 - _clamp(features.dti_ratio / max(DTI_MAX_APPROVE, 1e-6), 0.0, 1.0)

    # Employment: 0 at 0 years, saturate at 10 years
    employment_unit = _clamp(features.employment_history_years / 10.0, 0.0, 1.0)

    # LTV: lower better; 0 at 1.0+, 1 at 0
    ltv_unit = 1.0 - _clamp(features.ltv_ratio / max(LTV_MAX_STANDARD, 1e-6), 0.0, 1.0)

    # Liquid reserves: 0 at 0 months, saturate at 12 months
    reserves_unit = _clamp(features.liquid_reserves_months / 12.0, 0.0, 1.0)

    factor_units: dict[str, float] = {
        "credit_score": credit_unit,
        "dti_ratio": dti_unit,
        "employment_history_years": employment_unit,
        "ltv_ratio": ltv_unit,
        "liquid_reserves_months": reserves_unit,
    }

    scores: dict[str, float] = {
        name: _scale_unit_to_100(unit) for name, unit in factor_units.items()
    }

    composite_score = sum(
        scores[name] * SCORING_WEIGHTS.get(name, 0.0)
        for name in scores.keys()
    )

    return RiskResult(
        composite_score=composite_score,
        scores=scores,
        features=features,
    )


__all__ = [
    "RiskFeatures",
    "RiskResult",
    "engineer_features",
    "score",
]

