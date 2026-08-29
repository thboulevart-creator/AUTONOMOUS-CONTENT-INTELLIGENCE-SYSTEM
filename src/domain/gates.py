"""Domain Gates implementing Operational Specification INV-01 … INV-14."""
from __future__ import annotations
from typing import Any, Sequence
from .errors import DomainGateError
from .policy import PolicyConfig

class EvidenceAdmissionGate:
    REQUIRED = ("source_type", "observed_at", "raw_payload")
    def admit(self, candidate: dict) -> dict:
        missing = [f for f in self.REQUIRED if candidate.get(f) in (None, "", {})]
        if not candidate.get("source_ref"):
            missing.append("source_ref")
        if missing:
            raise DomainGateError(gate="EvidenceAdmissionGate", invariant="INV-01", reason=f"Incomplete Evidence: missing {missing}")
        payload = candidate.get("raw_payload")
        if payload is None or payload == {} or payload == "":
            raise DomainGateError(gate="EvidenceAdmissionGate", invariant="INV-01", reason="raw_payload must be non-empty")
        return candidate

class IndependenceClassifier:
    VALID = ("independent", "dependent", "unknown")
    def classify(self, *, primary_event_identity: str | None = None, upstream_identity: str | None = None, other_primary_event_identity: str | None = None, other_upstream_identity: str | None = None, derivation_link: bool = False, republication: bool = False) -> str:
        if derivation_link or republication:
            return "dependent"
        if primary_event_identity and other_primary_event_identity and primary_event_identity == other_primary_event_identity:
            return "dependent"
        if upstream_identity and other_upstream_identity and upstream_identity == other_upstream_identity:
            return "dependent"
        if (primary_event_identity and other_primary_event_identity and upstream_identity and other_upstream_identity and primary_event_identity != other_primary_event_identity and upstream_identity != other_upstream_identity):
            return "independent"
        return "unknown"
    def count_independent(self, states: Sequence[str]) -> int:
        return sum(1 for s in states if s == "independent")

class ReplicationChecker:
    DIMENSIONS = ("audience", "platform", "account", "temporal_window", "intervention")
    def __init__(self, policy: PolicyConfig):
        self.policy = policy
    def is_independent_replication(self, *, dims_a: dict, dims_b: dict) -> bool:
        min_dims = self.policy.require("replication_min_dimensions")
        differing = sum(1 for d in self.DIMENSIONS if dims_a.get(d) is not None and dims_b.get(d) is not None and dims_a.get(d) != dims_b.get(d))
        return differing >= min_dims

class OneShotGate:
    def __init__(self, policy: PolicyConfig, independence: IndependenceClassifier | None = None):
        self.policy = policy
        self.independence = independence or IndependenceClassifier()
    def allow_promotion(self, *, proposed_status: str, proposed_confidence: float, independence_states: Sequence[str]) -> None:
        min_c = self.policy.require("min_independent_corroborations")
        high = self.policy.require("high_confidence_threshold")
        if proposed_status != "active" or proposed_confidence < high:
            return
        independent_count = self.independence.count_independent(independence_states)
        if independent_count < min_c:
            raise DomainGateError(gate="OneShotGate", invariant="INV-04", reason=f"independent corroborations={independent_count} < min={min_c}")

class ExplorationClassifier:
    def __init__(self, policy: PolicyConfig):
        self.policy = policy
    def classify(self, *, difference_description: str | None, difference_magnitude: float | None, label: str | None = None) -> dict:
        method = self.policy.require("materiality_method")
        threshold = self.policy.require("materiality_threshold")
        if label and label.lower() in ("exploration", "explore") and not difference_description:
            return {"is_substantive_exploration": False, "reason": "label_only", "materiality_method": method, "materiality_threshold": threshold}
        if not difference_description:
            return {"is_substantive_exploration": False, "reason": "no_identifiable_difference", "materiality_method": method, "materiality_threshold": threshold}
        if difference_magnitude is None or difference_magnitude < threshold:
            return {"is_substantive_exploration": False, "reason": "below_materiality_threshold", "materiality_method": method, "materiality_threshold": threshold, "difference_magnitude": difference_magnitude}
        return {"is_substantive_exploration": True, "reason": "material_difference", "materiality_method": method, "materiality_threshold": threshold, "difference_description": difference_description, "difference_magnitude": difference_magnitude}

class ExplorationFloorGate:
    def __init__(self, policy: PolicyConfig):
        self.policy = policy
    def evaluate(self, *, decisions: Sequence[dict]) -> None:
        floor = self.policy.require("exploration_floor_ratio")
        if floor <= 0:
            raise DomainGateError(gate="ExplorationFloorGate", invariant="INV-06", reason="exploration_floor_ratio must be > 0")
        if not decisions:
            raise DomainGateError(gate="ExplorationFloorGate", invariant="INV-06", reason="empty decision window")
        genuine = sum(1 for d in decisions if d.get("is_substantive_exploration") is True)
        ratio = genuine / len(decisions)
        if ratio < floor:
            raise DomainGateError(gate="ExplorationFloorGate", invariant="INV-06", reason=f"exploration ratio {ratio:.3f} < floor {floor}")

REQUIRED_CONFOUNDER_KEYS = ("search_performed", "categories_considered", "sources_consulted", "result_status", "recorded_at")

class ConfounderCheckGate:
    VALID_STATUS = ("confounder_detected", "confounder_not_detected", "confounder_unknown", "search_insufficient")
    def validate(self, record: dict | None) -> None:
        if not record:
            raise DomainGateError(gate="ConfounderCheckGate", invariant="INV-07", reason="confounder check record absent")
        missing = [k for k in REQUIRED_CONFOUNDER_KEYS if k not in record or record[k] in (None, "", [], {})]
        if missing:
            raise DomainGateError(gate="ConfounderCheckGate", invariant="INV-07", reason=f"incomplete: missing {missing}")
        if record["result_status"] not in self.VALID_STATUS:
            raise DomainGateError(gate="ConfounderCheckGate", invariant="INV-07", reason=f"invalid result_status: {record['result_status']}")
        if record["search_performed"] is not True:
            raise DomainGateError(gate="ConfounderCheckGate", invariant="INV-07", reason="search_performed must be true")

class ContradictionHandler:
    def react(self, *, current_status: str, current_confidence: float, has_contradiction: bool, high_threshold: float) -> dict:
        if not has_contradiction:
            return {"action": "none", "status": current_status, "confidence": current_confidence}
        if current_status == "active" and current_confidence >= high_threshold:
            return {"action": "contest_or_reduce", "status": "contested", "confidence": min(current_confidence, high_threshold - 0.01), "reason": "contradictory_evidence"}
        if current_status == "active":
            return {"action": "reduce_confidence", "status": current_status, "confidence": max(0.0, current_confidence * 0.5), "reason": "contradictory_evidence"}
        return {"action": "record", "status": current_status, "confidence": current_confidence}

class ContextConditioningGate:
    def validate_scope(self, *, conditions: dict | None, claimed_universal: bool = False) -> None:
        if claimed_universal and not conditions:
            raise DomainGateError(gate="ContextConditioningGate", invariant="INV-09", reason="cannot universalise without supporting conditions")
        if claimed_universal:
            dims = ("platform", "account", "audience", "temporal")
            if not any(conditions.get(d) for d in dims if conditions):
                raise DomainGateError(gate="ContextConditioningGate", invariant="INV-09", reason="universal claim lacks supporting dimensions")

class ObservationInferenceGate:
    VALID_RELATION = ("observed", "inferred")
    def classify(self, *, relation_type: str, has_evidence_trace: bool) -> str:
        if relation_type not in self.VALID_RELATION:
            raise DomainGateError(gate="ObservationInferenceGate", invariant="INV-10", reason=f"relation_type must be observed|inferred, got {relation_type}")
        if relation_type == "observed" and not has_evidence_trace:
            raise DomainGateError(gate="ObservationInferenceGate", invariant="INV-10", reason="observed claim requires Evidence/Content traceability")
        return relation_type

class ExperimentClosureGate:
    def validate_mutation(self, *, design_locked: bool, performance_exists: bool, design_changed: bool) -> None:
        if performance_exists and design_changed:
            raise DomainGateError(gate="ExperimentClosureGate", invariant="INV-11", reason="cannot mutate design after Performance exists")
        if design_changed and design_locked:
            raise DomainGateError(gate="ExperimentClosureGate", invariant="INV-11", reason="design is locked; post-hoc modification forbidden")

class PathDependenceGuard:
    def allow_direct_path(self, *, from_entity: str, to_entity: str, intermediates_present: bool) -> bool:
        return True

class NegativeInformationGuard:
    def hard_delete_allowed(self) -> bool:
        return False
