from __future__ import annotations

import ast
import inspect

import src.application.provenance as provenance_module
from src.application.provenance import ProvenanceService


class SpyProvenanceRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def record_execution_trace(self, event):
        self.calls.append(("record_execution_trace", (event,), {}))
        return {"trace_reference": "trace-1"}

    def record_provider_provenance(self, execution_reference, provider_metadata):
        self.calls.append(
            (
                "record_provider_provenance",
                (execution_reference, provider_metadata),
                {},
            )
        )
        return {"provider_reference": "provider-1"}

    def link_artifact_lineage(self, parent_reference, child_reference, relationship):
        self.calls.append(
            (
                "link_artifact_lineage",
                (parent_reference, child_reference, relationship),
                {},
            )
        )
        return {"lineage_reference": "lineage-1"}


class FailingProvenanceRepository(SpyProvenanceRepository):
    def record_execution_trace(self, event):
        raise RuntimeError("provenance persistence failure")


def test_service_has_exactly_the_three_authorized_operations() -> None:
    public_methods = {
        name
        for name, member in inspect.getmembers(ProvenanceService)
        if not name.startswith("_") and callable(member)
    }
    assert public_methods == {
        "record_execution_trace",
        "record_provider_provenance",
        "link_artifact_lineage",
    }


def test_service_delegates_execution_trace_and_propagates_result() -> None:
    repository = SpyProvenanceRepository()
    service = ProvenanceService(repository=repository)
    event = {"execution_id": "exec-1", "operation_type": "generation"}

    result = service.record_execution_trace(event)

    assert result == {"trace_reference": "trace-1"}
    assert repository.calls == [("record_execution_trace", (event,), {})]


def test_service_delegates_provider_provenance_without_rewriting_metadata() -> None:
    repository = SpyProvenanceRepository()
    service = ProvenanceService(repository=repository)
    metadata = {
        "provider": "provider-a",
        "model": "model-a",
        "fallback_reason": "timeout",
    }

    result = service.record_provider_provenance("exec-1", metadata)

    assert result == {"provider_reference": "provider-1"}
    assert repository.calls == [
        ("record_provider_provenance", ("exec-1", metadata), {})
    ]


def test_service_delegates_actual_lineage_without_inference() -> None:
    repository = SpyProvenanceRepository()
    service = ProvenanceService(repository=repository)

    result = service.link_artifact_lineage("artifact-a", "artifact-b", "derived_from")

    assert result == {"lineage_reference": "lineage-1"}
    assert repository.calls == [
        ("link_artifact_lineage", ("artifact-a", "artifact-b", "derived_from"), {})
    ]


def test_service_preserves_repository_failures() -> None:
    service = ProvenanceService(repository=FailingProvenanceRepository())

    try:
        service.record_execution_trace({"execution_id": "exec-1"})
    except RuntimeError as exc:
        assert str(exc) == "provenance persistence failure"
    else:
        raise AssertionError("repository failure was swallowed or translated")


def test_service_module_has_no_infrastructure_or_domain_imports() -> None:
    source = inspect.getsource(provenance_module)
    tree = ast.parse(source)
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_names.add(node.module or "")

    forbidden_fragments = (
        "psycopg",
        "sqlalchemy",
        "src.persistence",
        "provider",
        "platform",
    )
    assert not any(
        fragment in imported_name.lower()
        for imported_name in imported_names
        for fragment in forbidden_fragments
    )
    assert "technical_provenance" not in source


def test_service_does_not_expose_query_update_or_delete_surface() -> None:
    forbidden = {
        "get",
        "list",
        "query",
        "update",
        "delete",
        "create",
        "transition",
        "publish",
        "evaluate",
    }
    public_methods = {
        name
        for name, member in inspect.getmembers(ProvenanceService)
        if not name.startswith("_") and callable(member)
    }
    assert forbidden.isdisjoint(public_methods)
