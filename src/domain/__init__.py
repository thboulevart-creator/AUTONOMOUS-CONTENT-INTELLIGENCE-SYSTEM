"""Phase 3 — Domain Gates implementing INV-01 … INV-14 (application layer)."""
from .errors import DomainGateError
from .policy import PolicyConfig
from .gates import (
    EvidenceAdmissionGate,
    IndependenceClassifier,
    ReplicationChecker,
    OneShotGate,
    ExplorationClassifier,
    ExplorationFloorGate,
    ConfounderCheckGate,
    ContradictionHandler,
    ContextConditioningGate,
    ObservationInferenceGate,
    ExperimentClosureGate,
    PathDependenceGuard,
    NegativeInformationGuard,
)

__all__ = [
    "DomainGateError",
    "PolicyConfig",
    "EvidenceAdmissionGate",
    "IndependenceClassifier",
    "ReplicationChecker",
    "OneShotGate",
    "ExplorationClassifier",
    "ExplorationFloorGate",
    "ConfounderCheckGate",
    "ContradictionHandler",
    "ContextConditioningGate",
    "ObservationInferenceGate",
    "ExperimentClosureGate",
    "PathDependenceGuard",
    "NegativeInformationGuard",
]
