from __future__ import annotations

import pytest

from src.application.evidence import EvidenceAdmissionService
from src.domain.errors import DomainGateError


class SpyGate:
    def __init__(self, result=None, error: Exception | None = None):
        self.result = result
        self.error = error
        self.calls: list[dict] = []

    def admit(self, candidate: dict) -> dict:
        self.calls.append(candidate)
        if self.error is not None:
            raise self.error
        return self.result if self.result is not None else candidate


class SpyRepository:
    def __init__(self):
        self.calls: list[dict] = []
        self.result = {"id": "evidence-1"}

    def create(self, **evidence_data):
        self.calls.append(evidence_data)
        return self.result


def test_admit_calls_gate_before_persistence_and_returns_repository_result():
    candidate = {
        "source_type": "social_post",
        "source_ref": "source-1",
        "observed_at": "2026-08-30T12:00:00Z",
        "raw_payload": {"text": "example"},
    }
    gate = SpyGate()
    repository = SpyRepository()
    service = EvidenceAdmissionService(gate=gate, repository=repository)

    result = service.admit(candidate)

    assert result == {"id": "evidence-1"}
    assert gate.calls == [candidate]
    assert repository.calls == [
        {
            "source_type": "social_post",
            "raw_payload": {"text": "example"},
            "observed_at": "2026-08-30T12:00:00Z",
            "source_ref": "source-1",
            "collected_at": None,
            "collection_context": None,
            "evidence_id": None,
        }
    ]


def test_admit_does_not_persist_when_domain_gate_rejects():
    candidate = {"source_type": "social_post"}
    gate_error = DomainGateError(
        gate="EvidenceAdmissionGate",
        invariant="INV-01",
        reason="Incomplete Evidence",
    )
    gate = SpyGate(error=gate_error)
    repository = SpyRepository()
    service = EvidenceAdmissionService(gate=gate, repository=repository)

    with pytest.raises(DomainGateError):
        service.admit(candidate)

    assert gate.calls == [candidate]
    assert repository.calls == []


def test_admit_maps_optional_persistence_fields_without_mutating_candidate():
    candidate = {
        "id": "evidence-42",
        "source_type": "social_post",
        "source_ref": "source-1",
        "observed_at": "2026-08-30T12:00:00Z",
        "raw_payload": {"text": "example"},
        "collected_at": "2026-08-30T12:01:00Z",
        "collection_context": {"collector": "test"},
    }
    admitted = dict(candidate)
    gate = SpyGate(result=admitted)
    repository = SpyRepository()
    service = EvidenceAdmissionService(gate=gate, repository=repository)

    service.admit(candidate)

    assert repository.calls == [
        {
            "source_type": "social_post",
            "raw_payload": {"text": "example"},
            "observed_at": "2026-08-30T12:00:00Z",
            "source_ref": "source-1",
            "collected_at": "2026-08-30T12:01:00Z",
            "collection_context": {"collector": "test"},
            "evidence_id": "evidence-42",
        }
    ]
    assert candidate == admitted
