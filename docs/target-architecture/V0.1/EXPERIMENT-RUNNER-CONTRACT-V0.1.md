# EXPERIMENT RUNNER CONTRACT V0.1

**Project:** Autonomous Content Intelligence System  
**Version:** V0.1  
**Status:** FROZEN APPLICATION CONTRACT  
**Authority:** subordinate to the 3 LOCKED contracts, Domain, and persistence boundaries

---

## 1. Normative decision

`Experiment.status` has no normative lifecycle vocabulary in V0.1.

Therefore `ExperimentRunner` MUST NOT introduce a state machine or lifecycle methods such as:

```text
start()
execute()
evaluate()
close()
transition_status()
```

The runner is an application coordinator for the persistence operations that are already contractually and physically available.

---

## 2. Frozen persistence boundary

The runner depends only on `ExperimentRepositoryPort`:

```text
get_by_id(experiment_id)
create(*, experiment_type, status, design, experiment_id)
add_arm(*, experiment_id, arm_type, content_id, variant_id, label, arm_id)
get_arms(experiment_id)
```

No direct SQL access is permitted.

No additional persistence operation is introduced by this contract.

---

## 3. Application interface

```text
ExperimentRunner
    create(...)
        -> persisted Experiment reference

    get(experiment_id)
        -> Experiment | not found

    add_arm(...)
        -> persisted Experiment Arm

    get_arms(experiment_id)
        -> ordered Experiment Arms
```

The runner performs orchestration only. It does not redefine Experiment semantics or interpret `status` as a lifecycle.

---

## 4. Domain boundary

The runner MUST NOT reproduce domain rules.

Where a domain gate is applicable to a future workflow, the runner invokes the existing gate from `src/domain/gates.py`.

`ExperimentClosureGate` remains authoritative for INV-11 and is not reimplemented in Application.

This V0.1 runner contract does not create a new closure operation because V0.1 does not define a normative Experiment lifecycle.

---

## 5. Status rule

`status` is persisted as V0.1 data but has no Application-owned vocabulary or transition semantics.

The runner MUST:

- preserve supplied status on creation;
- return persisted status unchanged;
- never manufacture allowed status values;
- never infer transitions from status strings;
- never expose a `transition_status()` operation.

The default `status="draft"` is an existing repository default, not a normative lifecycle declaration.

---

## 6. Experiment arms

`add_arm()` delegates to the existing repository surface and must preserve the existing domain/schema vocabulary:

```text
baseline
intervention
```

The Application layer must not introduce additional arm types.

The SQL/domain constraints remain authoritative for arm validity and cardinality.

---

## 7. Forbidden dependencies

`ExperimentRunner` MUST NOT depend directly on:

- PostgreSQL/psycopg2;
- SQL statements;
- concrete provider clients;
- platform APIs;
- repository internals;
- a new Experiment state machine;
- a new Experiment domain entity.

---

## 8. Conformance requirements

A conforming implementation must demonstrate:

1. dependency only on `ExperimentRepositoryPort` for persistence;
2. exact delegation of the four frozen operations;
3. no lifecycle/status transition API;
4. no status interpretation;
5. no domain-rule reimplementation;
6. no direct SQL/infrastructure dependency.

---

## 9. Implementation gate

Implementation is authorized only after these conformance conditions pass.

```text
R-02 RESOLVED
    ↓
ExperimentRepositoryPort FROZEN
    ↓
ExperimentRunner Contract FROZEN
    ↓
Conformance Tests PASS
    ↓
Implementation
```
