# APPLICATION INTERFACE SPECIFICATION V0.1 — ERRATA

**Project:** Autonomous Content Intelligence System  
**Version:** V0.1-ERRATA  
**Status:** ARCHITECTURAL CONTRACT — PRE-IMPLEMENTATION / CORRECTIVE  
**Purpose:** Record and close interface/documentation corrections identified during conformance review.

---

# 1. R-01 — PUBLICATION PERSISTENCE REQUIREMENT RECONFIRMED

The repository contains:

```text
src/persistence/repositories/publication.py
```

Its persistence surface is intentionally:

```text
PublicationRepository
    create(...)
    get_by_id(publication_id)
```

It deliberately does **not** expose `update_state()` because the V0.1 Logical Data Schema does not define a first-class Publication state field. No unsupported domain state is therefore introduced.

Accordingly, the Application Interface Specification must not require a persistence-level `update_state()` operation at V0.1.

Publication workflow state, idempotency and external platform semantics remain Application/Adapter concerns and must remain compatible with the locked schema.

This errata supersedes any contrary statement in the interface specification.

---

# 2. R-02 — DUPLICATE PUBLICATION SERVICE REMOVED

`PublicationService` has one authoritative application-interface definition:

```text
src/application/publishing.py
```

The duplicate `PublicationService` declaration has been removed from:

```text
src/application/services.py
```

The publishing boundary is therefore owned by the publishing module rather than duplicated across application interface modules.

No business logic has been introduced.

---

# 3. R-03 — APPLICATION IMPLEMENTATION STATUS CORRECTED

The Application Layer now contains a real interface-only skeleton under:

```text
src/application/
```

Therefore the previous metadata statement:

```text
Application implementation: NOT YET STARTED
```

is clarified as:

```text
Application skeleton: CREATED
Application service implementation: STARTED only where explicitly authorized
Business logic implementation: limited to approved service contracts
```

---

# 4. R-04 — EXPERIMENT STATUS LIFECYCLE CLOSED AS NON-NORMATIVE

The previous Application Interface Specification section defining:

```text
ExperimentRunner
    start(experiment_id)
    execute(experiment_id)
    evaluate(experiment_id)
    close(experiment_id)
```

is superseded by:

```text
ExperimentRunner Contract V0.1
```

at:

```text
docs/target-architecture/V0.1/EXPERIMENT-RUNNER-CONTRACT-V0.1.md
```

The reason is normative, not stylistic:

- Information Model V0.1 defines no Experiment lifecycle vocabulary;
- Operational Specification V0.1 defines no Experiment status transition machine;
- Logical Data Schema V0.1 stores `experiment.status` as open text rather than a lifecycle enum/check;
- Domain gates, including `ExperimentClosureGate`, do not define status transitions;
- the existing persistence repository exposes only `create`, `get_by_id`, `add_arm`, and `get_arms`.

Therefore V0.1 MUST NOT invent:

```text
start
execute
complete
close
transition_status
```

as normative Experiment lifecycle operations.

The frozen runner contract is limited to the persistence operations already authorized by the repository boundary and preserves `status` without interpreting it.

`ExperimentClosureGate` remains the sole Domain authority for INV-11 and is not replaced by an Application lifecycle machine.

---

# 5. SCOPE CONTROL

This errata:

- closes the identified R-01 interface discrepancy by reconfirming the schema-compatible Publication persistence boundary;
- removes the duplicate `PublicationService` interface;
- corrects the Application implementation-status metadata;
- resolves the Experiment status/lifecycle discrepancy as R-02 of the normative gap review;
- does not create a new domain entity;
- does not modify the four workstreams;
- does not change domain authority;
- does not change persistence into an orchestration layer;
- does not modify the three LOCKED contracts.

> **The errata closes the residual interface discrepancies without reopening the architecture or inventing an Experiment lifecycle that V0.1 does not define.**
