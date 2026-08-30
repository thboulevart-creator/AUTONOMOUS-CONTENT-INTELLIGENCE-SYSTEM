from __future__ import annotations

from uuid import UUID

from src.application.experiment import ExperimentRunner


class FakeExperimentRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def get_by_id(self, experiment_id):
        self.calls.append(("get_by_id", (experiment_id,), {}))
        return {"id": experiment_id, "status": "arbitrary-v0.1-status"}

    def create(self, **kwargs):
        self.calls.append(("create", (), kwargs))
        return kwargs

    def add_arm(self, **kwargs):
        self.calls.append(("add_arm", (), kwargs))
        return kwargs

    def get_arms(self, experiment_id):
        self.calls.append(("get_arms", (experiment_id,), {}))
        return [{"experiment_id": experiment_id, "arm_type": "baseline"}]


def test_create_delegates_without_interpreting_status() -> None:
    repository = FakeExperimentRepository()
    runner = ExperimentRunner(repository=repository)

    result = runner.create(
        experiment_type="controlled",
        status="arbitrary-v0.1-status",
        design={"hypothesis": "test"},
    )

    assert result["status"] == "arbitrary-v0.1-status"
    assert repository.calls == [
        (
            "create",
            (),
            {
                "experiment_type": "controlled",
                "status": "arbitrary-v0.1-status",
                "design": {"hypothesis": "test"},
                "experiment_id": None,
            },
        )
    ]


def test_get_delegates_exactly() -> None:
    repository = FakeExperimentRepository()
    runner = ExperimentRunner(repository=repository)
    experiment_id = UUID("00000000-0000-0000-0000-000000000001")

    result = runner.get(experiment_id)

    assert result["id"] == experiment_id
    assert repository.calls == [("get_by_id", (experiment_id,), {})]


def test_add_arm_delegates_exactly() -> None:
    repository = FakeExperimentRepository()
    runner = ExperimentRunner(repository=repository)
    experiment_id = UUID("00000000-0000-0000-0000-000000000002")
    arm_id = UUID("00000000-0000-0000-0000-000000000003")

    runner.add_arm(
        experiment_id=experiment_id,
        arm_type="intervention",
        label="treatment-a",
        arm_id=arm_id,
    )

    assert repository.calls == [
        (
            "add_arm",
            (),
            {
                "experiment_id": experiment_id,
                "arm_type": "intervention",
                "content_id": None,
                "variant_id": None,
                "label": "treatment-a",
                "arm_id": arm_id,
            },
        )
    ]


def test_get_arms_delegates_exactly() -> None:
    repository = FakeExperimentRepository()
    runner = ExperimentRunner(repository=repository)
    experiment_id = UUID("00000000-0000-0000-0000-000000000004")

    assert runner.get_arms(experiment_id) == [
        {"experiment_id": experiment_id, "arm_type": "baseline"}
    ]
    assert repository.calls == [("get_arms", (experiment_id,), {})]


def test_runner_has_no_normative_lifecycle_api() -> None:
    forbidden = {"start", "execute", "evaluate", "close", "transition_status"}
    assert forbidden.isdisjoint(set(dir(ExperimentRunner)))
