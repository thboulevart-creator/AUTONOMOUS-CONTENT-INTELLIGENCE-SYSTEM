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

        The gate remains authoritative. After it succeeds, the application maps
        the admitted candidate to the exact persistence-port contract; it does not
        reinterpret or reimplement the domain admission rules.
        """
        admitted = self._gate.admit(candidate)
        return self._repository.create(
            source_type=admitted["source_type"],
            raw_payload=admitted["raw_payload"],
            observed_at=admitted["observed_at"],
            source_ref=admitted["source_ref"],
            collected_at=admitted.get("collected_at"),
            collection_context=admitted.get("collection_context"),
            evidence_id=admitted.get("id"),
        )
