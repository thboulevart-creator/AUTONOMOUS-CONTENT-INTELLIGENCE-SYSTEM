# CONTRACT-TO-APPLICATION MAPPING V0.1

**Project:** Autonomous Content Intelligence System  
**Repository:** `AUTONOMOUS-CONTENT-INTELLIGENCE-SYSTEM`  
**Version:** V0.1  
**Status:** ARCHITECTURAL CONTRACT — PRE-IMPLEMENTATION  
**Scope:** Contract-to-Application mapping only  
**Application implementation:** NOT YET STARTED

---

## 1. PURPOSE

This document is the explicit bridge between the existing locked/domain/persistence system and the future Application Layer defined by `ARCHITECTURE-TARGET-V0.1-CORRECTED.md`.

It is intentionally derived from the **real repository**, not from the target architecture in isolation.

For every future application responsibility it identifies:

- the authoritative contract;
- the existing repository/module that already owns relevant behaviour or data;
- the persistence interface already available;
- the future application responsibility;
- the boundary that must not be crossed;
- whether a new application component is required;
- whether a persistence gap exists;
- the implementation constraint that must be preserved.

This document does **not** authorize implementation by itself. It prevents implementation from inventing duplicate abstractions or bypassing existing contracts.

---

# 2. AUTHORITATIVE HIERARCHY

The future Application Layer is subordinate to the following existing hierarchy:

```text
Information Model V0.1 — LOCKED
        ↓
Operational Specification V0.1 — LOCKED
        ↓
Logical Data Schema V0.1
        ↓
Existing Domain Layer
        ↓
Future Application Layer
        ↓
Persistence / External Adapters
```

The Information Model remains the semantic authority. It explicitly defines the system as a graph rather than a mandatory linear pipeline, distinguishes observation from causality, makes experimentation explicit when causal confidence is sought, and requires path-dependent provenance. fileciteturn163file0

The Operational Specification defines the executable invariants INV-01 through INV-14 and explicitly states that operational classifications and provenance metadata are not new first-class Information Model objects. fileciteturn164file0

The current physical foundation implements the locked logical model through PostgreSQL tables, foreign keys, experiment-arm constraints and append-only Performance enforcement. fileciteturn168file0

---

# 3. EXISTING REPOSITORY SURFACE

## 3.1 Domain — already authoritative

| File | Existing responsibility | Application consequence |
|---|---|---|
| `src/domain/gates.py` | Implements domain gates for INV-01, INV-02, INV-03, INV-04, INV-05/06, INV-07, INV-08, INV-09, INV-10, INV-11, plus guards | Application services MUST invoke these gates; they MUST NOT reimplement them. |
| `src/domain/policy.py` | `PolicyConfig` and explicit `require()` for unspecified production parameters | Application may consume policy; it cannot silently invent production values or override policy. |
| `src/domain/errors.py` | Structured `DomainGateError` carrying gate, invariant, reason and optional entity ID | Application translates/handles rejection; it does not reinterpret the invariant. |

The real gate implementation confirms that the domain already owns the validation logic. For example, `EvidenceAdmissionGate`, `IndependenceClassifier`, `ReplicationChecker`, `OneShotGate`, `ExplorationFloorGate`, `ConfounderCheckGate`, `ContextConditioningGate`, `ObservationInferenceGate` and `ExperimentClosureGate` are implemented in `gates.py`. fileciteturn157file0

`PolicyConfig.require()` deliberately raises when a production parameter remains `UNSPECIFIED`; this is a protected boundary against silently choosing operational policy in the Application Layer. fileciteturn158file0

---

## 3.2 Persistence — already available

| File | Existing interface | Future use |
|---|---|---|
| `src/persistence/repositories/decision.py` | `create()`, `get_by_id()` | Decision loading/persistence for orchestration |
| `src/persistence/repositories/evidence.py` | `create()`, `get_by_id()`, `soft_delete()` | Evidence admission workflow persistence |
| `src/persistence/repositories/experiment.py` | `create()`, `get_by_id()`, `add_arm()`, `get_arms()` | Experiment execution/assignment persistence |
| `src/persistence/repositories/performance.py` | append-only `append()`, `get_by_id()`, `list_for_publication()` | Performance recording; no mutation workflow |
| `src/persistence/repositories/learning.py` | create/read, provenance, status history, evidence links | Learning persistence and provenance |
| `src/persistence/repositories/__init__.py` | repository package surface | Composition only; not an orchestration layer |

The repository implementations explicitly avoid embedding domain gate logic: `EvidenceRepository` states that admission belongs to Phase 3/domain, `ExperimentRepository` states that closure-gate logic is absent, and `DecisionRepository` states that exploration classification is absent. fileciteturn167file0turn160file0turn159file0

`PerformanceRepository` is explicitly append-only and exposes no `update()` method. fileciteturn161file0

`LearningRepository` already provides persisted provenance and status history, including evidence linkage. fileciteturn162file0

---

# 4. LOCKED CONTRACT → APPLICATION RESPONSIBILITY MAP

## 4.1 Information Model objects

| Locked object | Existing physical/persistence evidence | Future Application responsibility | Boundary |
|---|---|---|---|
| Evidence | `EvidenceRepository`; `evidence` table | admission, validation, enrichment/orchestration | gate decides admissibility; repository only persists |
| Trend | `trend` table in foundation | discovery/aggregation workflow | no generic Context or new Trend authority |
| Mechanism | `mechanism` table | extraction/validation workflow | observed vs inferred distinction remains governed by INV-10 |
| Pattern | `pattern` table | extraction/validation workflow | no replacement taxonomy invented by application |
| Hypothesis | `hypothesis` table | hypothesis creation/update orchestration | application does not redefine semantic meaning |
| Experiment | `ExperimentRepository`; `experiment` + `experiment_arm` | experiment lifecycle and execution | closure and design integrity remain domain-governed |
| Concept | `concept` table | creation workflow | no new CreativeStrategy entity |
| Variant | `variant` table; experiment arms reference it | variant generation/assignment | assignment cannot be silently changed by creative logic |
| Content | `content` table | production coordination | artifact generation remains adapter/provider work |
| Platform Version | `platform_version` table | adaptation workflow | platform-specific adaptation must remain distinct from Content |
| Publication | `publication` table | external publication orchestration | external side effect must be handled by publishing adapter boundary |
| Performance | `PerformanceRepository`; `performance` table | measurement ingestion/orchestration | append-only; observation, not causal conclusion |
| Learning | `LearningRepository`; `learning` + provenance/history | promotion/update orchestration | OneShot, contradiction, context and confounder rules remain authoritative |
| Decision | `DecisionRepository`; `decision` table | decision execution/orchestration | Decision is not execution itself |
| Account | `account` table | platform/account context selection | no generic Context replacement |
| Audience | `audience` table | audience/context selection | must remain explicit contextual dimension |
| Platform | `platform` table | platform capability/context selection | must not be collapsed into provider identity |

The Information Model explicitly defines these as the durable semantic concepts and rejects additional first-class objects such as generic Context, Analysis, Inference, Model, Policy, Goal, Constraint, Resource and Saturation Object for V0.1. fileciteturn163file0

---

# 5. WORKSTREAM 1 — APPLICATION-LEVEL DOMAIN ENFORCEMENT

## 5.1 Exact mapping

| Future component | Contract(s) | Existing authority/interface | Application action | Must NOT do |
|---|---|---|---|---|
| `orchestration.decision_router` | Information Model + Operational Spec | `DecisionRepository`; domain gates | load decision, determine applicable workflow, invoke required gates | classify exploration or invent invariants |
| `orchestration.production_planner` | Operational Spec | Content/Variant/Concept schema | prepare executable work from authorized decision | create `ProductionPlan` as a new semantic object |
| `orchestration.cost_controller` | Operational Spec + Policy | `PolicyConfig`; Account constraints | evaluate economic feasibility | override domain requirements or silently alter experiment treatment |
| `orchestration.autonomy_controller` | Operational Spec + Policy | domain errors/gates | RUN / PAUSE / STOP / DEFER / ESCALATE | become a higher authority than Domain |
| application gate checkpoint | all applicable INV-* | `src/domain/gates.py` | call existing gate before protected transition | duplicate gate implementation |

The gate implementation is already centralized in `src/domain/gates.py`. fileciteturn157file0

## 5.2 Exact gate ownership

| Invariant | Existing gate/class | Application responsibility |
|---|---|---|
| INV-01 | `EvidenceAdmissionGate` | call before admitting Evidence |
| INV-02 | `IndependenceClassifier` | obtain/route classifications; never treat UNKNOWN as independent |
| INV-03 | `ReplicationChecker` | invoke for replication claims |
| INV-04 | `OneShotGate` | invoke before strong Learning promotion |
| INV-05 | `ExplorationClassifier` | invoke/log classification before counting exploration |
| INV-06 | `ExplorationFloorGate` | invoke on defined decision windows |
| INV-07 | `ConfounderCheckGate` | require valid confounder record before applicable causal promotion |
| INV-08 | `ContradictionHandler` | orchestrate resulting status/confidence transition |
| INV-09 | `ContextConditioningGate` | validate scope of Learning claims |
| INV-10 | `ObservationInferenceGate` | distinguish observed/inferred extraction |
| INV-11 | `ExperimentClosureGate` | validate experiment design/closure mutations |
| INV-12 | persistence + schema | use append-only Performance interface |
| INV-13 | Information Model | never impose mandatory global chain |
| INV-14 | persistence + workflow | preserve failed/negative information |

The Operational Specification explicitly defines these invariants and their protected failure modes. fileciteturn164file0

---

# 6. WORKSTREAM 2 — PROVENANCE AND EXECUTION TRACEABILITY

## 6.1 Existing evidence

The current persistence layer already contains partial provenance infrastructure:

- `LearningRepository.add_provenance()` persists source type, source ID and role;
- `LearningRepository.get_provenance()` reconstructs those links;
- `LearningRepository.link_evidence()` links Evidence to Learning;
- status history is separately persisted. fileciteturn162file0

The Information Model requires provenance to be path-dependent: the system records the provenance actually present and must not fabricate missing ancestry. fileciteturn163file0

## 6.2 Future components

| Future component | Authoritative contract | Existing interface | Future responsibility | Boundary |
|---|---|---|---|---|
| `provenance.execution_trace` | Operational Spec + path-dependent provenance | no dedicated execution-trace repository currently identified | record application execution events needed for reconstruction | must not become a new semantic model |
| `provenance.provider_provenance` | Operational provenance | no dedicated provider provenance repository currently identified | record provider/model/version/request metadata when technically available | Provider remains technical adapter |
| `provenance.artifact_lineage` | Information Model relationships | Content/Variant/Platform Version persistence | preserve actual artifact lineage | never fabricate missing Concept/Hypothesis/Experiment ancestry |

### Required trace

Where the actual path exists, the application must make it reconstructable as:

```text
Decision
→ production execution
→ provider/model
→ artifact
→ Platform Version
→ Publication
→ Performance
→ Learning
```

This is a **traceability target**, not a permission to invent entities or edges that did not exist. The Information Model expressly forbids fabricated complete chains. fileciteturn163file0

---

# 7. WORKSTREAM 3 — EXPERIMENTAL INTEGRITY

## 7.1 Existing experiment boundary

`ExperimentRepository` currently provides persistence for an Experiment and its Arms and explicitly contains no closure-gate logic. fileciteturn160file0

The physical schema reinforces the arm semantics: controlled experiments require exactly one baseline and at least one intervention, and each arm must point to either a Variant or Content. fileciteturn168file0

The Operational Specification makes INV-11 non-negotiable and requires pre-declared success/failure/stop criteria. fileciteturn164file0

## 7.2 Exact future mapping

| Future component | Contract | Existing support | Responsibility | Forbidden |
|---|---|---|---|---|
| `experimentation.experiment_runner` | Information Model + Operational Spec | `ExperimentRepository` + experiment schema | orchestrate experiment lifecycle | bypass closure/design gates |
| `experimentation.assignment` | Experiment semantics | `ExperimentRepository.add_arm()` | assign treatment/control according to declared design | creative layer silently reassigning treatment |
| `experimentation.confounder_control` | INV-07 | `ConfounderCheckGate`, `PolicyConfig` | collect/validate confounder search record | invent causal conclusion from “none detected” |
| `experimentation.experiment_integrity` | INV-02/03/04/07/08/11 | corresponding domain gates | coordinate checks | create new experimental semantics |
| `creative.strategy_selector` | Information Model | Concept/Variant/Experiment data | select execution strategy within assigned constraints | become experiment authority |
| `creative.avatar_strategy` | experiment assignment + production | no existing avatar component | execute assigned Avatar treatment | create Avatar entity |
| `creative.no_avatar_strategy` | experiment assignment + production | no existing no-avatar component | execute assigned control | alter assignment |

The Information Model explicitly says Baseline and Intervention are not first-class objects in V0.1. fileciteturn163file0

## 7.3 Provider changes

Providers are implementation variables, not semantic authorities. If a fallback occurs, the application/provenance layer must retain enough evidence to distinguish intended provider from actual provider where the information exists.

A cost decision must not silently mutate treatment. `PolicyConfig` is the authoritative policy interface and rejects unspecified production values rather than choosing them implicitly. fileciteturn158file0

---

# 8. WORKSTREAM 4 — RELIABLE PUBLICATION

## 8.1 Existing persistence boundary

The physical schema already contains `platform_version` and `publication`, with foreign-key links from Publication to Platform Version and Account. Performance then references Publication. fileciteturn168file0

`PerformanceRepository.append()` requires `publication_id`, observed time and metrics and therefore already anchors measurement to the publication identity. fileciteturn161file0

## 8.2 Future mapping

| Future component | Contract | Existing support | Responsibility | Current gap |
|---|---|---|---|---|
| `publishing.publication_service` | Information Model + Operational Spec | `publication` table; no dedicated PublicationRepository currently identified | coordinate publication request/state and persistence | dedicated repository/service boundary still to be designed |
| `publishing.idempotency` | reliable external side-effect handling | no current idempotency component identified | stable publication intent/idempotency handling | new application infrastructure required |
| `publishing.platform adapters` | implementation boundary | no platform adapter identified | call external platform APIs | no domain policy in adapter |
| Performance ingestion | INV-12 | `PerformanceRepository` | append snapshots against actual Publication | must never update existing Performance |

### Important current repository fact

There is **no `src/persistence/repositories/publication.py` currently present** in the repository surface inspected for V0.1. The physical database does contain a `publication` table. Therefore the mapping records a **persistence-interface gap**, not a semantic-model gap.

This must be resolved during implementation design without changing the Information Model.

---

# 9. PROVIDER / ADAPTER BOUNDARY

The target architecture defines providers as technical adapters. The current repository contains no normative provider implementation in `src/domain/` or `src/persistence/repositories/`.

| Boundary | Authority | Future responsibility | Forbidden |
|---|---|---|---|
| LLM provider | technical provider | execute model request | decide domain policy |
| image provider | technical provider | generate image asset | decide experiment treatment |
| video provider | technical provider | generate video asset | define Content semantics |
| voice provider | technical provider | generate voice asset | bypass quality/gates |
| avatar provider | technical provider | execute avatar production | become Avatar domain authority |
| platform adapter | external adapter | publish/read external state | contain experiment policy |

The absence of current provider implementations is intentional architectural scope: these are future adapters, not missing LOCKED domain objects.

---

# 10. PERSISTENCE MAPPING — FILE BY FILE

## Existing files

| Repository file | Semantic objects touched | Used by future application | Constraint |
|---|---|---|---|
| `decision.py` | Decision | decision orchestration | no exploration classification |
| `evidence.py` | Evidence | evidence workflow | admission remains domain-owned |
| `experiment.py` | Experiment, Experiment Arm | experimentation | no closure-gate logic |
| `performance.py` | Performance | measurement/learning loop | append-only |
| `learning.py` | Learning, Learning provenance, status history, Evidence links | learning/provenance | no promotion gates |
| `__init__.py` | repository package | dependency composition | no orchestration |

The repositories are persistence components, not business workflow engines. This is consistent with the target architecture and with the repository source itself. fileciteturn159file0turn160file0turn161file0turn162file0

## Database foundation

`db/migrations/001_v0.1_foundation.sql` establishes the physical representation for the core semantic objects and includes explicit constraints for controlled experiment arms and append-only Performance. fileciteturn168file0

The migration therefore acts as the physical boundary the Application Layer must respect; it is not a substitute for domain validation.

---

# 11. TEST SURFACE

The repository contains a test foundation including:

```text
db/tests/test_phase1_foundation.py
db/tests/test_phase2_persistence.py
db/tests/test_phase3_domain_gates.py
```

The Application Layer must eventually add application-level conformance tests without weakening or replacing the existing domain/persistence tests.

The correct future testing direction is:

```text
LOCKED contract tests
        ↓
Domain gate tests
        ↓
Persistence constraint tests
        ↓
Application conformance tests
        ↓
Adapter integration tests
```

No application implementation is authorized by this mapping alone.

---

# 12. NEW COMPONENTS VS EXISTING COMPONENTS

## Reuse directly

The following must be reused rather than recreated:

```text
src/domain/gates.py
src/domain/policy.py
src/domain/errors.py

src/persistence/repositories/decision.py
src/persistence/repositories/evidence.py
src/persistence/repositories/experiment.py
src/persistence/repositories/performance.py
src/persistence/repositories/learning.py
```

## Future application components

The following are architectural targets, not currently existing files:

```text
src/application/orchestration/*
src/application/experimentation/*
src/application/creative/*
src/application/production/*
src/application/provenance/*
src/application/publishing/*
src/application/providers/*
```

They must be introduced only after their interfaces have been designed against this mapping.

## Known infrastructure gaps

At minimum, the mapping identifies these future interfaces as not currently present:

1. dedicated publication persistence interface;
2. publication idempotency mechanism;
3. external platform adapters;
4. provider adapters;
5. application execution trace mechanism;
6. provider/artifact provenance mechanism beyond existing Learning provenance.

These are **implementation gaps**, not reasons to modify the LOCKED semantic model.

---

# 13. DEPENDENCY RULES

The dependency direction is fixed:

```text
Application
    ↓
Domain
    ↓
Persistence interfaces

Application
    ↓
External Adapters
    ↓
External systems
```

The following are prohibited:

```text
Repository → Application orchestration
Provider → Domain policy
Provider → Repository orchestration
Platform adapter → Experiment policy
Creative selector → Experiment assignment authority
Cost controller → silent treatment mutation
Application → duplicated gate logic
```

---

# 14. CONTRACT-TO-APPLICATION ACCEPTANCE CHECKLIST

Before application implementation begins, the following must be demonstrable:

- [x] All three normative contract locations are identified in the real repository.
- [x] Existing Domain gate authority is identified.
- [x] Existing Policy authority is identified.
- [x] Existing repository interfaces are identified file by file.
- [x] Existing physical Publication representation is identified.
- [x] Performance append-only boundary is identified.
- [x] Existing Learning provenance facilities are identified.
- [x] Experiment-arm persistence boundary is identified.
- [x] Four surviving architectural workstreams are mapped.
- [x] Future Application responsibilities are separated from existing Domain responsibilities.
- [x] Future provider/platform responsibilities are separated from Application/Domain.
- [x] Known persistence/adapter gaps are explicitly recorded.
- [x] No new V0.1 semantic object is introduced by this mapping.
- [x] No LOCKED contract is modified by this mapping.

---

# 15. FINAL MAPPING VERDICT

**STATUS: MAPPED — READY FOR APPLICATION INTERFACE DESIGN**

The repository contains a functioning semantic/domain/persistence foundation that the future Application Layer must orchestrate rather than replace.

The four surviving workstreams are now mapped to concrete contracts and existing repository boundaries:

```text
1. Domain enforcement
   → src/domain/gates.py / policy.py / errors.py

2. Provenance / execution traceability
   → existing Learning provenance + future application trace infrastructure

3. Experimental integrity
   → ExperimentRepository + experiment_arm + domain gates

4. Reliable publication
   → publication schema + future Publication persistence/service + external adapters
```

The principal unresolved items are **implementation interfaces**, not semantic architecture:

```text
PublicationRepository/interface
Idempotency
Provider adapters
Platform adapters
Execution trace
Extended provider/artifact provenance
```

These must be designed next without modifying the three LOCKED contracts or bypassing the existing domain/persistence boundaries.

> **Architectural rule:** if implementation requires a semantic decision not answered by this mapping and the existing LOCKED contracts, stop and raise the decision explicitly. Do not silently invent an abstraction.
