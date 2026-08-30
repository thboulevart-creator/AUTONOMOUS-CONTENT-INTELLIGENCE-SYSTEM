"""Technical provider port interfaces."""
from __future__ import annotations

from typing import Any, Protocol


class LLMProvider(Protocol):
    def generate(self, request: Any) -> Any: ...


class ImageProvider(Protocol):
    def generate(self, request: Any) -> Any: ...


class VideoProvider(Protocol):
    def generate(self, request: Any) -> Any: ...


class VoiceProvider(Protocol):
    def generate(self, request: Any) -> Any: ...


class AvatarProvider(Protocol):
    def generate(self, request: Any) -> Any: ...
