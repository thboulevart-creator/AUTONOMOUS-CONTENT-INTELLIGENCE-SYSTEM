from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.application.ports import ProvenanceRepositoryPort
from src.persistence.repositories.provenance import ProvenanceRepository


class FakeCursor:
    def __init__(self, rows=None):
        self.rows = list(rows or [])
        self.calls = []

    def execute(self, sql, params):
        self.calls.append((sql, params))

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None


class FakeConnection:
    pass


def install_cursor(monkeypatch, cursor):
    monkeypatch.setattr(
        "src.persistence.repositories.provenance.dict_cursor",
        lambda conn: cursor,
    )


def test_adapter_satisfies_port_shape():
    assert isinstance(ProvenanceRepository(FakeConnection()), ProvenanceRepositoryPort)


def test_record_execution_trace_maps_only_technical_store(monkeypatch):
    cursor = FakeCursor([{"execution_id": "e1"}])
    install_cursor(monkeypatch, cursor)
    repo = ProvenanceRepository(FakeConnection())

    result = repo.record_execution_trace(
        {
            "execution_id": uuid4(),
            "operation_type": "provider_call",
            "occurred_at": datetime.now(timezone.utc),
            "input_references": ["artifact:a"],
            "output_references": ["artifact:b"],
            "execution_status": "success",
            "technical_metadata": {"attempt": 1},
        }
    )

    assert result == {"execution_id": "e1"}
    sql, _ = cursor.calls[0]
    assert "technical_provenance.execution_trace" in sql
    assert "INSERT INTO content" not in sql
    assert "INSERT INTO experiment" not in sql
    assert "INSERT INTO learning" not in sql


def test_record_provider_provenance_maps_provider_metadata(monkeypatch):
    cursor = FakeCursor([{"provider": "test-provider"}])
    install_cursor(monkeypatch, cursor)
    repo = ProvenanceRepository(FakeConnection())
    execution_id = uuid4()

    result = repo.record_provider_provenance(
        execution_id,
        {
            "provider": "test-provider",
            "model": "test-model",
            "model_version": "v1",
            "request_parameters": {"temperature": 0.2},
            "execution_status": "success",
            "prompt": "technical test",
            "seed": "42",
        },
    )

    assert result == {"provider": "test-provider"}
    sql, params = cursor.calls[0]
    assert "technical_provenance.provider_provenance" in sql
    assert params[0] == str(execution_id)
    assert "INSERT INTO learning_provenance" not in sql


def test_link_artifact_lineage_is_idempotent(monkeypatch):
    cursor = FakeCursor([None, {"parent_reference": "a", "child_reference": "b"}])
    install_cursor(monkeypatch, cursor)
    repo = ProvenanceRepository(FakeConnection())

    result = repo.link_artifact_lineage("a", "b", "generated_from")

    assert result["parent_reference"] == "a"
    assert len(cursor.calls) == 2
    assert "ON CONFLICT (parent_reference, child_reference, relationship)" in cursor.calls[0][0]
    assert "SELECT *" in cursor.calls[1][0]


def test_non_mapping_inputs_are_rejected_before_sql(monkeypatch):
    cursor = FakeCursor()
    install_cursor(monkeypatch, cursor)
    repo = ProvenanceRepository(FakeConnection())

    with pytest.raises(TypeError):
        repo.record_execution_trace([])

    with pytest.raises(TypeError):
        repo.record_provider_provenance("e1", [])

    assert cursor.calls == []
