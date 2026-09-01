"""Application service and technical provenance interfaces."""
from __future__ import annotations

from typing import Any, Protocol

from .ports import ProvenanceRepositoryPort


class ExecutionTrace(Protocol):
    def record(self, event: Any) -> Any: ...


class ProviderProvenance(Protocol):
    def record(self, execution_reference: Any, provider_metadata: Any) -> Any: ...


class ArtifactLineage(Protocol):
    def link(self, parent_reference: Any, child_reference: Any, relationship: str) -> Any: ...


class ProvenanceService:
    """Thin application facade over the technical provenance repository port.

    The service performs no domain validation, persistence work, provider
    selection, or provenance interpretation. All technical persistence is
    delegated to the injected ProvenanceRepositoryPort.
    """

    def __init__(self, *, repository: ProvenanceRepositoryPort) -> None:
        self._repository = repository

    def record_execution_trace(self, event: Any) -> Any:
        return self._repository.record_execution_trace(event)

    def record_provider_provenance(
        self,
        execution_reference: Any,
        provider_metadata: Any,
    ) -> Any:
        return self._repository.record_provider_provenance(
            execution_reference,
            provider_metadata,
        )

    def link_artifact_lineage(
        self,
        parent_reference: Any,
        child_reference: Any,
        relationship: str,
    ) -> Any:
        return self._repository.link_artifact_lineage(
            parent_reference,
            child_reference,
            relationship,
        )
