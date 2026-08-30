"""Evidence admission application service.

This is the first concrete Application workflow. It orchestrates the existing
EvidenceAdmissionGate and the application-facing persistence port without
reimplementing domain rules or owning persistence policy.
"""
from __future__ import annotations

from typing import Any

from .ports import EvidenceRepositoryPort
from ..domain.gates import EvidenceAdmissionGate


class EvidenceAdmissionService:
    """Admit a candidate Evidence record through the domain gate, then persist it."""

    def __init__(
        self,
        *,
        gate: EvidenceAdmissionGate,
        repository: EvidenceRepositoryPort,
    ) -> None:
        self._gate = gate
        self._repository = repository

    def admit(self, candidate: dict[str, Any]) -> Any:
        """Validate an Evidence candidate through the domain authority and persist it.

        The candidate is passed unchanged to the persistence port after the gate
        succeeds. A gate failure propagates and persistence is not attempted.
        """
        admitted = self._gate.admit(candidate)
        return self._repository.create(admitted)
