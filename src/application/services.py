"""Application service interfaces.

Only method signatures are defined. Implementations are intentionally absent.
"""
from __future__ import annotations

from typing import Any, Protocol


class DecisionRouter(Protocol):
    def route(self, decision_id: str) -> Any: ...


class ProductionPlanner(Protocol):
    def plan(self, request: Any) -> Any: ...


class CostController(Protocol):
    def authorize(self, request: Any) -> Any: ...


class AutonomyController(Protocol):
    def evaluate(self, command: Any) -> Any: ...


class ExperimentRunner(Protocol):
    def start(self, experiment_id: str) -> Any: ...
    def execute(self, experiment_id: str) -> Any: ...
    def evaluate(self, experiment_id: str) -> Any: ...
    def close(self, experiment_id: str) -> Any: ...


class ExperimentAssignment(Protocol):
    def assign(self, experiment_id: str, variant_or_content_reference: Any) -> Any: ...


class ConfounderControl(Protocol):
    def assess(self, experiment_context: Any) -> Any: ...


class ExperimentIntegrity(Protocol):
    def validate(self, experiment_id: str, transition: Any) -> Any: ...


class StrategySelector(Protocol):
    def select(self, execution_context: Any) -> Any: ...


class AvatarStrategy(Protocol):
    def execute(self, assigned_treatment: Any) -> Any: ...


class NoAvatarStrategy(Protocol):
    def execute(self, assigned_control: Any) -> Any: ...


class PerformanceIngestion(Protocol):
    def append(self, observation: Any) -> Any: ...


class QualityControl(Protocol):
    def validate_or_transform(self, artifact: Any) -> Any: ...
