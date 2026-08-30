from __future__ import annotations

import inspect

from src.application.ports import ProvenanceRepositoryPort


class FakeProvenanceRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def record_execution_trace(self, event):
        self.calls.append(("record_execution_trace", (event,), {}))
        return event

    def record_provider_provenance(self, execution_reference, provider_metadata):
        self.calls.append(
            (
                "record_provider_provenance",
                (execution_reference, provider_metadata),
                {},
            )
        )
        return provider_metadata

    def link_artifact_lineage(self, parent_reference, child_reference, relationship):
        self.calls.append(
            (
                "link_artifact_lineage",
                (parent_reference, child_reference, relationship),
                {},
            )
        )
        return relationship


def test_port_exposes_only_the_minimal_three_operations() -> None:
    public_methods = {
        name
        for name, member in inspect.getmembers(ProvenanceRepositoryPort)
        if not name.startswith("_") and callable(member)
    }

    assert public_methods == {
        "record_execution_trace",
        "record_provider_provenance",
        "link_artifact_lineage",
    }


def test_fake_repository_satisfies_structural_port() -> None:
    repository = FakeProvenanceRepository()
    assert isinstance(repository, ProvenanceRepositoryPort)


def test_port_has_no_domain_lifecycle_or_business_operations() -> None:
    forbidden = {
        "create",
        "update",
        "delete",
        "transition",
        "start",
        "complete",
        "close",
        "publish",
        "evaluate",
    }
    public_methods = {
        name
        for name, member in inspect.getmembers(ProvenanceRepositoryPort)
        if not name.startswith("_") and callable(member)
    }
    assert forbidden.isdisjoint(public_methods)


def test_fake_repository_records_only_the_three_contract_operations() -> None:
    repository = FakeProvenanceRepository()

    repository.record_execution_trace({"event": "generation_started"})
    repository.record_provider_provenance("exec-1", {"provider": "test"})
    repository.link_artifact_lineage("artifact-a", "artifact-b", "derived_from")

    assert repository.calls == [
        (
            "record_execution_trace",
            ({"event": "generation_started"},),
            {},
        ),
        (
            "record_provider_provenance",
            ("exec-1", {"provider": "test"}),
            {},
        ),
        (
            "link_artifact_lineage",
            ("artifact-a", "artifact-b", "derived_from"),
            {},
        ),
    ]
