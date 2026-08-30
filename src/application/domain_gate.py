"""Application-facing domain gate boundary.

The application delegates to existing named domain gates. It does not
reimplement invariant logic.
"""
from __future__ import annotations

from typing import Any, Protocol


class DomainGatePort(Protocol):
    def check(self, context: Any) -> Any: ...
