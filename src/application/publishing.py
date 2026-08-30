"""Publishing application boundaries."""
from __future__ import annotations

from typing import Any, Protocol


class PublicationService(Protocol):
    def publish(self, publication_request: Any) -> Any: ...


class IdempotencyPort(Protocol):
    def resolve(self, intent_key: str) -> Any: ...
    def register(self, intent_key: str, publication_reference: Any) -> Any: ...


class PlatformAdapter(Protocol):
    def publish(self, request: Any) -> Any: ...
    def read_state(self, external_publication_id: str) -> Any: ...
