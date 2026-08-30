"""Experiment application service.

This service deliberately does not implement an Experiment lifecycle. V0.1
has no normative Experiment status machine. It coordinates only the frozen
persistence operations exposed by ExperimentRepositoryPort.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from .ports import ExperimentRepositoryPort


class ExperimentRunner:
    """Minimal V0.1 Experiment coordinator."""

    def __init__(self, *, repository: ExperimentRepositoryPort) -> None:
        self._repository = repository

    def create(
        self,
        *,
        experiment_type: str,
        status: str = "draft",
        design: Any = None,
        experiment_id: UUID | None = None,
    ) -> Any:
        """Create an Experiment through the persistence port.

        ``status`` is preserved as supplied; the application does not assign
        lifecycle meaning to it.
        """
        return self._repository.create(
            experiment_type=experiment_type,
            status=status,
            design=design,
            experiment_id=experiment_id,
        )

    def get(self, experiment_id: UUID | str) -> Any:
        """Load an Experiment through the persistence port."""
        return self._repository.get_by_id(experiment_id)

    def add_arm(
        self,
        *,
        experiment_id: UUID | str,
        arm_type: str,
        content_id: UUID | str | None = None,
        variant_id: UUID | str | None = None,
        label: str | None = None,
        arm_id: UUID | None = None,
    ) -> Any:
        """Add an Experiment Arm through the existing repository boundary."""
        return self._repository.add_arm(
            experiment_id=experiment_id,
            arm_type=arm_type,
            content_id=content_id,
            variant_id=variant_id,
            label=label,
            arm_id=arm_id,
        )

    def get_arms(self, experiment_id: UUID | str) -> Any:
        """Return Experiment Arms through the persistence port."""
        return self._repository.get_arms(experiment_id)
