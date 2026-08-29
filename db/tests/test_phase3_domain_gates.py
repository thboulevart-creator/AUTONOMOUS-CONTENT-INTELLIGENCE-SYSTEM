"""Phase 3 Domain Gates tests INV-01..INV-14. Real PostgreSQL where needed."""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.domain import (
    DomainGateError, PolicyConfig, EvidenceAdmissionGate, IndependenceClassifier,
    ReplicationChecker, OneShotGate, ExplorationClassifier, ExplorationFloorGate,
    ConfounderCheckGate, ContradictionHandler, ContextConditioningGate,
    ObservationInferenceGate, ExperimentClosureGate, PathDependenceGuard,
    NegativeInformationGuard,
)
from src.persistence.repositories import EvidenceRepository

TEST_POLICY = PolicyConfig(
    min_independent_corroborations=2, high_confidence_threshold=0.8,
    exploration_floor_ratio=0.2, materiality_threshold=0.1, materiality_method="test_delta",
    replication_min_dimensions=1, confounder_categories=("amplification",), confounder_min_sources=1,
)

def test_app_adm_01_valid_evidence_accepted():
    assert EvidenceAdmissionGate().admit({"source_type": "api", "source_ref": "r", "observed_at": datetime.now(timezone.utc), "raw_payload": {"t": 1}})["source_type"] == "api"

def test_app_adm_02_incomplete_evidence_rejected():
    with pytest.raises(DomainGateError) as e:
        EvidenceAdmissionGate().admit({"source_type": "api", "raw_payload": {}})
    assert e.value.invariant == "INV-01"

def test_app_ind_01_truly_independent():
    assert IndependenceClassifier().classify(primary_event_identity="A", upstream_identity="1", other_primary_event_identity="B", other_upstream_identity="2") == "independent"

def test_app_ind_02_republication_dependent():
    assert IndependenceClassifier().classify(republication=True) == "dependent"

def test_app_ind_03_insufficient_unknown():
    assert IndependenceClassifier().classify(primary_event_identity="A") == "unknown"

def test_adv_ind_01_payload_diff_not_independent():
    clf = IndependenceClassifier()
    assert clf.classify(primary_event_identity="X", upstream_identity="u", other_primary_event_identity="X", other_upstream_identity="u") == "dependent"
    assert clf.count_independent(["unknown", "dependent", "independent"]) == 1

def test_app_rep_01_material_dimension_diff():
    assert ReplicationChecker(TEST_POLICY).is_independent_replication(dims_a={"platform": "t"}, dims_b={"platform": "l"})

def test_adv_rep_01_same_context_different_id_not_independent():
    d = {"platform": "x", "audience": "y", "account": "z", "temporal_window": "w", "intervention": "i"}
    assert not ReplicationChecker(TEST_POLICY).is_independent_replication(dims_a=d, dims_b=d)

def test_app_one_01_single_source_rejected():
    with pytest.raises(DomainGateError) as e:
        OneShotGate(TEST_POLICY).allow_promotion(proposed_status="active", proposed_confidence=0.95, independence_states=["independent"])
    assert e.value.invariant == "INV-04"

def test_app_one_02_two_independent_allowed():
    OneShotGate(TEST_POLICY).allow_promotion(proposed_status="active", proposed_confidence=0.95, independence_states=["independent", "independent"])

def test_adv_one_01_unknown_and_dependent_excluded():
    with pytest.raises(DomainGateError):
        OneShotGate(TEST_POLICY).allow_promotion(proposed_status="active", proposed_confidence=0.99, independence_states=["independent", "unknown", "dependent"])

def test_app_exp_01_substantive():
    assert ExplorationClassifier(TEST_POLICY).classify(difference_description="new mech", difference_magnitude=0.5)["is_substantive_exploration"] is True

def test_app_exp_02_cosmetic_rejected():
    assert ExplorationClassifier(TEST_POLICY).classify(difference_description="colour", difference_magnitude=0.01)["is_substantive_exploration"] is False

def test_adv_exp_01_label_only_insufficient():
    r = ExplorationClassifier(TEST_POLICY).classify(difference_description=None, difference_magnitude=None, label="exploration")
    assert r["is_substantive_exploration"] is False and r["reason"] == "label_only"

def test_app_floor_01_zero_genuine_rejected():
    with pytest.raises(DomainGateError) as e:
        ExplorationFloorGate(TEST_POLICY).evaluate(decisions=[{"is_substantive_exploration": False}] * 5)
    assert e.value.invariant == "INV-06"

def test_app_floor_02_genuine_above_floor():
    ExplorationFloorGate(TEST_POLICY).evaluate(decisions=[{"is_substantive_exploration": True}] * 2 + [{"is_substantive_exploration": False}] * 3)

def test_adv_floor_01_cosmetic_only_rejected():
    with pytest.raises(DomainGateError):
        ExplorationFloorGate(TEST_POLICY).evaluate(decisions=[{"is_substantive_exploration": False}] * 10)

def test_app_caus_01_complete_check_ok():
    ConfounderCheckGate().validate({"search_performed": True, "categories_considered": ["a"], "sources_consulted": ["s"], "result_status": "confounder_not_detected", "recorded_at": "2026-01-01T00:00:00Z"})

def test_app_caus_02_empty_rejected():
    with pytest.raises(DomainGateError) as e:
        ConfounderCheckGate().validate(None)
    assert e.value.invariant == "INV-07"

def test_adv_caus_01_cosmetic_status_only_rejected():
    with pytest.raises(DomainGateError):
        ConfounderCheckGate().validate({"status": "none_detected"})

def test_app_cont_01_contradiction_contests_high_confidence():
    r = ContradictionHandler().react(current_status="active", current_confidence=0.95, has_contradiction=True, high_threshold=0.8)
    assert r["status"] == "contested"

def test_app_cont_02_no_contradiction_noop():
    assert ContradictionHandler().react(current_status="active", current_confidence=0.9, has_contradiction=False, high_threshold=0.8)["action"] == "none"

def test_adv_cont_01_cannot_ignore():
    r = ContradictionHandler().react(current_status="active", current_confidence=0.99, has_contradiction=True, high_threshold=0.8)
    assert r["status"] != "active" or r["confidence"] < 0.8

def test_app_context_01_conditioned_ok():
    ContextConditioningGate().validate_scope(conditions={"platform": "t"}, claimed_universal=False)

def test_adv_context_01_universal_without_conditions_rejected():
    with pytest.raises(DomainGateError) as e:
        ContextConditioningGate().validate_scope(conditions=None, claimed_universal=True)
    assert e.value.invariant == "INV-09"

def test_app_infer_01_observed_with_trace():
    assert ObservationInferenceGate().classify(relation_type="observed", has_evidence_trace=True) == "observed"

def test_adv_infer_01_llm_without_evidence_not_observed():
    with pytest.raises(DomainGateError):
        ObservationInferenceGate().classify(relation_type="observed", has_evidence_trace=False)
    assert ObservationInferenceGate().classify(relation_type="inferred", has_evidence_trace=False) == "inferred"

def test_app_clos_01_mutation_after_performance_rejected():
    with pytest.raises(DomainGateError) as e:
        ExperimentClosureGate().validate_mutation(design_locked=False, performance_exists=True, design_changed=True)
    assert e.value.invariant == "INV-11"

def test_app_clos_02_lock_then_performance_ok():
    ExperimentClosureGate().validate_mutation(design_locked=True, performance_exists=True, design_changed=False)

def test_adv_clos_01_posthoc_design_change_rejected():
    with pytest.raises(DomainGateError):
        ExperimentClosureGate().validate_mutation(design_locked=True, performance_exists=False, design_changed=True)

def test_app_path_01_direct_evidence_learning():
    assert PathDependenceGuard().allow_direct_path(from_entity="Evidence", to_entity="Learning", intermediates_present=False)

def test_adv_path_01_missing_intermediates_not_failure():
    assert PathDependenceGuard().allow_direct_path(from_entity="Evidence", to_entity="Learning", intermediates_present=False) is True

def test_app_neg_01_hard_delete_unavailable():
    assert NegativeInformationGuard().hard_delete_allowed() is False

def test_adv_neg_01_hard_delete_blocked():
    assert NegativeInformationGuard().hard_delete_allowed() is False

def test_policy_unspecified_refuses_evaluation():
    with pytest.raises(ValueError, match="UNSPECIFIED"):
        OneShotGate(PolicyConfig()).allow_promotion(proposed_status="active", proposed_confidence=0.9, independence_states=["independent", "independent"])

def test_e2e_prom_01_combined_bypass_blocked():
    with pytest.raises(DomainGateError):
        OneShotGate(TEST_POLICY).allow_promotion(proposed_status="active", proposed_confidence=0.99, independence_states=["unknown"])
    assert ExplorationClassifier(TEST_POLICY).classify(difference_description=None, difference_magnitude=None, label="exploration")["is_substantive_exploration"] is False
    with pytest.raises(DomainGateError):
        ConfounderCheckGate().validate({"status": "none_detected"})

def test_app_adm_persist_integration(db):
    admitted = EvidenceAdmissionGate().admit({"source_type": "api", "source_ref": "ref-int", "observed_at": datetime.now(timezone.utc), "raw_payload": {"ok": True}, "collection_context": {"independence_state": "unknown"}})
    row = EvidenceRepository(db).create(source_type=admitted["source_type"], source_ref=admitted["source_ref"], observed_at=admitted["observed_at"], raw_payload=admitted["raw_payload"], collection_context=admitted["collection_context"])
    assert row["source_ref"] == "ref-int"
