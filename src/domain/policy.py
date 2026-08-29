"""Policy configuration. Production parameters remain UNSPECIFIED by default."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolicyConfig:
    min_independent_corroborations: int | None = None
    high_confidence_threshold: float | None = None
    exploration_floor_ratio: float | None = None
    materiality_threshold: float | None = None
    materiality_method: str | None = None
    syndication_temporal_window: Any = None
    confounder_categories: tuple[str, ...] | None = None
    confounder_min_sources: int | None = None
    decision_window: Any = None
    replication_min_dimensions: int | None = None

    def require(self, name: str) -> Any:
        val = getattr(self, name)
        if val is None:
            raise ValueError(
                f"Policy parameter '{name}' is UNSPECIFIED. "
                "Supply an explicit value (test fixture or operator configuration)."
            )
        return val
