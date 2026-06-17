"""Factory execution exceptions."""

from __future__ import annotations


class FactoryError(Exception):
    """Base factory error."""


class FactoryValidationError(FactoryError):
    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class FactoryVetoError(FactoryError):
    def __init__(self, *, reason: str, reason_code: str, run_id: str) -> None:
        super().__init__(reason)
        self.reason = reason
        self.reason_code = reason_code
        self.run_id = run_id


class FactoryNotFoundError(FactoryError):
    def __init__(self, factory_id: str) -> None:
        super().__init__(f"Unknown factory: {factory_id}")
        self.factory_id = factory_id
