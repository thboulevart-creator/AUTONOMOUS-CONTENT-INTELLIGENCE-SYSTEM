"""Composition-root boundary.

Concrete domain, persistence, provider and platform implementations are wired
here in the implementation phase. No runtime composition is performed yet.
"""
from __future__ import annotations

from typing import Any


def build_application(*, dependencies: Any) -> Any:
    """Composition entry point reserved for implementation.

    Intentionally raises until concrete application services are implemented.
    """
    raise NotImplementedError("Application composition is not implemented yet")
