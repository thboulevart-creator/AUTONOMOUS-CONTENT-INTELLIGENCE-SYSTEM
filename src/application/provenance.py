"""Technical/application provenance interfaces."""
from __future__ import annotations

from typing import Any, Protocol


class ExecutionTrace(Protocol):
    def record(self, event: Any) -> Any: ...


class ProviderProvenance(Protocol):
    def record(self, execution_reference: Any, provider_metadata: Any) -> Any: ...


class ArtifactLineage(Protocol):
    def link(self, parent_reference: Any, child_reference: Any, relationship: str) -> Any: ...
