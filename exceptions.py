"""
Structured API errors for the decision gate.
"""

from __future__ import annotations


class GateError(Exception):
    code: str = "GATE_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class PolicyGateError(GateError):
    code = "POLICY_NOT_READY"


class DuplicateRequestError(GateError):
    code = "REQUEST_ID_CONFLICT"


__all__ = ["DuplicateRequestError", "GateError", "PolicyGateError"]
