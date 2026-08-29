"""Structured domain-gate rejection errors."""
from __future__ import annotations


class DomainGateError(Exception):
    def __init__(self, *, gate: str, invariant: str, reason: str, entity_id: str | None = None):
        self.gate = gate
        self.invariant = invariant
        self.reason = reason
        self.entity_id = entity_id
        super().__init__(f"[{invariant}/{gate}] {reason}" + (f" entity={entity_id}" if entity_id else ""))
