"""
NOETFELD OS — Central configuration.
All domain constants, thresholds, weights, and paths live here.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR: Path = Path(__file__).parent.resolve()
DB_PATH: Path = BASE_DIR / "noetfeld.db"
BASE_POLICY_PATH: Path = BASE_DIR / "base_policy.json"
CORRIDOR_POLICY_PATH: Path = BASE_DIR / "corridor_policy.json"
API_KEYS_PATH: Path = BASE_DIR / "api_keys.local.json"

# ---------------------------------------------------------------------------
# Credit / risk scoring thresholds
# ---------------------------------------------------------------------------

CREDIT_SCORE_MIN: int = 300
CREDIT_SCORE_MAX: int = 850

# Decision bands
CREDIT_BAND_EXCELLENT: int = 750
CREDIT_BAND_GOOD: int = 670
CREDIT_BAND_FAIR: int = 580
CREDIT_BAND_POOR: int = 300  # anything below FAIR is "poor"

# Debt-to-income ratio (0.0–1.0)
DTI_MAX_APPROVE: float = 0.43   # conventional max for approval
DTI_CAUTION_THRESHOLD: float = 0.36  # flag for manual review above this

# Loan-to-value ratio
LTV_MAX_STANDARD: float = 0.80   # above this → PMI / stricter terms
LTV_MAX_JUMBO: float = 0.75

# ---------------------------------------------------------------------------
# Decision engine weights (must sum to 1.0)
# ---------------------------------------------------------------------------

SCORING_WEIGHTS: dict[str, float] = {
    "credit_score": 0.35,
    "dti_ratio": 0.25,
    "employment_history_years": 0.15,
    "ltv_ratio": 0.15,
    "liquid_reserves_months": 0.10,
}

assert abs(sum(SCORING_WEIGHTS.values()) - 1.0) < 1e-9, (
    "SCORING_WEIGHTS must sum to 1.0"
)

# ---------------------------------------------------------------------------
# Decision labels
# ---------------------------------------------------------------------------

DECISION_APPROVE: str = "APPROVE"
DECISION_REVIEW: str = "REVIEW"
DECISION_DECLINE: str = "DECLINE"

# Composite score cutoffs (0–100 internal scale)
DECISION_APPROVE_THRESHOLD: float = 70.0
DECISION_REVIEW_THRESHOLD: float = 45.0
# Below REVIEW_THRESHOLD → DECLINE

# ---------------------------------------------------------------------------
# Audit / retention
# ---------------------------------------------------------------------------

AUDIT_MAX_ROWS: int = 100_000   # soft cap before archiving
AUDIT_TABLE_NAME: str = "audit_log"
