# APPLICATION INTERFACE SPECIFICATION V0.1

**Project:** Autonomous Content Intelligence System  
**Repository:** `AUTONOMOUS-CONTENT-INTELLIGENCE-SYSTEM`  
**Version:** V0.1  
**Status:** ARCHITECTURAL CONTRACT — PRE-IMPLEMENTATION  
**Scope:** Application interfaces only  
**Application implementation:** NOT YET STARTED

---

# 1. PURPOSE

This document defines the exact interface contracts that will govern the future `src/application/` layer.

It is the implementation boundary between:

```text
LOCKED CONTRACTS
      ↓
DOMAIN
      ↓
APPLICATION INTERFACES
      ↓
PERSISTENCE / PROVIDERS / PLATFORM ADAPTERS
```

The purpose is to prevent implementation from:

- inventing duplicate domain abstractions;
- bypassing domain gates;
- placing business orchestration in repositories;
- allowing providers to become authorities;
- allowing publishing adapters to contain policy;
- silently changing experimental treatment;
- losing execution provenance;
- coupling the Application Layer directly to concrete infrastructure.

This document defines interfaces and boundaries. It does **not** define implementation algorithms and does **not** authorize application coding by itself.

---

# 2. AUTHORITATIVE CONTRACTS

The interfaces defined here are subordinate to:

1. Information Model V0.1 — LOCKED
2. Operational Specification V0.1 — LOCKED
3. Logical Data Schema V0.1
4. Existing Domain implementation
5. Existing persistence interfaces

The Application Layer has no authority to redefine semantic meaning or domain invariants.

The `CONTRACT-TO-APPLICATION-MAPPING-V0.1.md` is the immediate architectural predecessor of this specification and establishes the repository-level mapping on which these interfaces are based.

---

# 3. GLOBAL INTERFACE RULES

## 3.1 Dependency direction

```text
Application
    ↓
Domain contracts / gates
    ↓
Persistence interfaces

Application
    ↓
Provider interfaces
    ↓
External providers

Application
    ↓
Platform adapter interfaces
    ↓
External platforms
```

Repositories, providers and platform adapters never call Application orchestration services.

## 3.2 Domain authority

Application services invoke domain gates. They do not reproduce gate logic.

A domain rejection is a valid application outcome.

```text
Application Command
      ↓
Domain Gate
      ├── PASS → continue
      └── FAIL → stop / defer / escalate
```

## 3.3 No silent degradation

An unavailable provider, insufficient budget, invalid experiment state or failed external side effect must produce an explicit result.

No interface may encode silent fallback as success.

## 3.4 No new semantic entities

The interfaces MUST NOT introduce first-class domain entities such as:

```text
ProductionPlan
CreativeStrategy
Provider
CostDecision
Avatar
ExecutionTrace
```

unless a future LOCKED contract explicitly authorizes them.

These may exist as application-level DTOs, commands or technical records only where they do not become competing semantic authorities.

---

# 4. APPLICATION COMMAND / RESULT CONVENTION

Application interfaces use a command/result boundary conceptually equivalent to:

```text
Command
  ↓
Application Service
  ↓
Result
```

Commands contain references and execution intent. They do not redefine domain entities.

Results must make explicit at minimum:

```text
success / rejected / deferred / escalated / failed
reason
relevant entity reference(s)
```

Domain failures must preserve the originating gate/invariant information supplied by `DomainGateError`.

---

# 5. PERSISTENCE PORTS

The Application Layer depends on persistence through repository interfaces. Existing repository implementations remain infrastructure.

## 5.1 Decision port

Existing implementation:

```text
src/persistence/repositories/decision.py
```

Required application-facing operations:

```text
DecisionRepositoryPort
    get_by_id(decision_id)
    create(decision_data)
```

The application may use the existing implementation directly through an adapter, but orchestration code must not depend on database details.

Constraint:

> DecisionRepository does not classify exploration or execute business workflows.

---

# 6. EVIDENCE PORT

Existing implementation:

```text
src/persistence/repositories/evidence.py
```

Required operations:

```text
EvidenceRepositoryPort
    get_by_id(evidence_id)
    create(evidence_data)
    soft_delete(evidence_id)
```

Application responsibility:

```text
receive evidence
    ↓
EvidenceAdmissionGate
    ↓
EvidenceRepositoryPort.create()
```

The repository must not decide evidence admissibility.

---

# 7. EXPERIMENT PORT

Existing implementation:

```text
src/persistence/repositories/experiment.py
```

Required operations:

```text
ExperimentRepositoryPort
    get_by_id(experiment_id)
    create(experiment_data)
    add_arm(experiment_id, arm_data)
    get_arms(experiment_id)
```

Application responsibility:

- orchestrate lifecycle;
- coordinate declared assignment;
- invoke applicable integrity/closure gates;
- persist authorized state.

The repository does not determine whether an experiment is valid for closure.

---

# 8. PERFORMANCE PORT

Existing implementation:

```text
src/persistence/repositories/performance.py
```

Required operations:

```text
PerformanceRepositoryPort
    append(performance_snapshot)
    get_by_id(performance_id)
    list_for_publication(publication_id)
```

There is intentionally no update operation.

Constraint:

> Performance observations are append-only and cannot be rewritten by Application orchestration.

---

# 9. LEARNING PORT

Existing implementation:

```text
src/persistence/repositories/learning.py
```

Application-facing operations include the existing persistence capabilities for:

```text
create/read Learning
add provenance
get provenance
link evidence
status history
```

The Application Layer must invoke the applicable domain gates before strong Learning promotion.

Learning persistence does not authorize causal inference by itself.

---

# 10. PUBLICATION PERSISTENCE GAP

The physical schema contains a `publication` table, but the mapped repository surface contains no dedicated:

```text
src/persistence/repositories/publication.py
```

Therefore the Application Layer MUST NOT invent direct SQL access as a workaround.

The implementation phase must introduce a persistence port/adapter for Publication before publication orchestration is implemented.

Conceptual port:

```text
PublicationRepositoryPort
    create(publication_data)
    get_by_id(publication_id)
    update_state(publication_id, state)
```

The exact mutation semantics must remain compatible with the Logical Data Schema and must not create unsupported domain states.

This is an infrastructure/interface gap, not permission to alter the LOCKED Information Model.

---

# 11. DOMAIN GATE PORT

The Application Layer depends on the existing domain gate implementations in:

```text
src/domain/gates.py
```

The application-facing abstraction may be expressed conceptually as:

```text
DomainGatePort
    check(context) → GateResult
```

but implementations must continue to use the existing named domain gates and their semantics.

Required gate mapping:

| Invariant | Existing authority | Application checkpoint |
|---|---|---|
| INV-01 | `EvidenceAdmissionGate` | before Evidence admission |
| INV-02 | `IndependenceClassifier` | before independence-dependent claims |
| INV-03 | `ReplicationChecker` | before replication claims |
| INV-04 | `OneShotGate` | before strong Learning promotion |
| INV-05 | `ExplorationClassifier` | before exploration accounting |
| INV-06 | `ExplorationFloorGate` | at applicable decision windows |
| INV-07 | `ConfounderCheckGate` | before applicable causal promotion |
| INV-08 | `ContradictionHandler` | on contradiction handling |
| INV-09 | `ContextConditioningGate` | before context-scoped Learning promotion |
| INV-10 | `ObservationInferenceGate` | during observed/inferred extraction |
| INV-11 | `ExperimentClosureGate` | before experiment closure |
| INV-12 | persistence/schema | at Performance write boundary |
| INV-13 | Information Model | architecture-wide graph constraint |
| INV-14 | persistence/workflow | preserve negative/failed information |

The Application Layer must not replace these with simplified boolean checks.

---

# 12. ORCHESTRATION INTERFACES

## 12.1 Decision Router

Conceptual interface:

```text
DecisionRouter
    route(decision_id) → WorkflowRoute
```

Responsibilities:

- load Decision;
- determine the applicable workflow;
- invoke required domain checkpoints;
- select the next authorized application operation.

Must not:

- redefine Decision semantics;
- impose a mandatory global pipeline;
- classify exploration independently of the domain authority.

## 12.2 Production Planner

Conceptual interface:

```text
ProductionPlanner
    plan(request) → ProductionExecutionRequest
```

`ProductionExecutionRequest` is an application-level execution structure, not a new domain entity.

It may reference existing:

```text
Decision
Concept
Variant
Content
Platform Version
Experiment
```

It must not create a normative `ProductionPlan` entity.

## 12.3 Cost Controller

Conceptual interface:

```text
CostController
    authorize(request) → CostAuthorization
```

Possible outcomes:

```text
AUTHORIZED
REFUSED
DEFERRED
ESCALATED
```

The controller may evaluate resource constraints but cannot override Domain Policy.

If changing provider or production quality would alter experimental treatment, the controller must not silently make that change.

## 12.4 Autonomy Controller

Conceptual interface:

```text
AutonomyController
    evaluate(command) → ExecutionDisposition
```

Supported dispositions:

```text
RUN
PAUSE
STOP
DEFER
ESCALATE
```

Authority order:

```text
LOCKED contracts
    ↓
Domain Policy / Gates
    ↓
Autonomy Controller
```

Autonomy cannot override a domain rejection.

---

# 13. EXPERIMENTATION INTERFACES

## 13.1 Experiment Runner

```text
ExperimentRunner
    start(experiment_id)
    execute(experiment_id)
    evaluate(experiment_id)
    close(experiment_id)
```

Each operation must invoke the applicable domain gates.

The runner coordinates; it does not redefine experiment semantics.

## 13.2 Assignment

```text
ExperimentAssignment
    assign(experiment_id, variant_or_content_reference)
        → AssignmentResult
```

Assignment must follow the declared experiment design.

The creative layer cannot mutate treatment assignment after the fact.

## 13.3 Confounder Control

```text
ConfounderControl
    assess(experiment_context)
        → ConfounderAssessment
```

The result must preserve the distinction between:

```text
confounder detected
confounder not detected
assessment unavailable
```

Absence of a detected confounder is not itself a causal conclusion.

## 13.4 Experiment Integrity

```text
ExperimentIntegrity
    validate(experiment_id, transition)
        → IntegrityResult
```

It coordinates INV-02/03/04/07/08/11 checks without creating new experimental semantics.

---

# 14. CREATIVE INTERFACES

## 14.1 Strategy Selector

```text
StrategySelector
    select(execution_context) → StrategySelection
```

The returned strategy is an application execution choice.

It is not a new domain entity.

## 14.2 Avatar Strategy

```text
AvatarStrategy
    execute(assigned_treatment) → ProductionRequest
```

Avatar is a production capability/treatment, not a V0.1 domain entity.

## 14.3 No-Avatar Strategy

```text
NoAvatarStrategy
    execute(assigned_control) → ProductionRequest
```

The control strategy cannot modify experiment assignment.

---

# 15. PROVIDER PORTS

Providers are technical ports/adapters.

## 15.1 LLM

```text
LLMProvider
    generate(request) → ProviderResult
```

## 15.2 Image

```text
ImageProvider
    generate(request) → ProviderResult
```

## 15.3 Video

```text
VideoProvider
    generate(request) → ProviderResult
```

## 15.4 Voice

```text
VoiceProvider
    generate(request) → ProviderResult
```

## 15.5 Avatar

```text
AvatarProvider
    generate(request) → ProviderResult
```

Provider results must expose enough technical information for provenance when available, including:

```text
provider
model
model_version
request_parameters
input_reference
output_reference
execution_status
```

Where technically available:

```text
prompt
seed
temperature
API version
fallback reason
```

Providers must not:

- decide domain policy;
- decide experimental treatment;
- write repositories directly;
- bypass quality or domain checkpoints.

---

# 16. PROVENANCE INTERFACES

## 16.1 Execution Trace

```text
ExecutionTrace
    record(event) → TraceReference
```

The trace is technical/application provenance, not a new domain entity.

## 16.2 Provider Provenance

```text
ProviderProvenance
    record(execution_reference, provider_metadata)
```

It must preserve intended-versus-actual provider information when a fallback occurs.

## 16.3 Artifact Lineage

```text
ArtifactLineage
    link(parent_reference, child_reference, relationship)
```

Lineage must represent actual relationships only.

The system must never fabricate a complete ancestry chain merely because the target architecture expects one to be useful.

---

# 17. PUBLISHING INTERFACES

## 17.1 Publication Service

```text
PublicationService
    publish(publication_request) → PublicationResult
```

The service coordinates:

```text
Platform Version
    ↓
PublicationRepositoryPort
    ↓
PlatformAdapter
```

## 17.2 Idempotency

```text
IdempotencyPort
    resolve(intent_key) → ExistingOrNewPublication
    register(intent_key, publication_reference)
```

The same publication intent must not produce an unintended duplicate on retry.

## 17.3 Platform Adapter

```text
PlatformAdapter
    publish(request) → ExternalPublicationResult
    read_state(external_publication_id) → ExternalPublicationState
```

The adapter may translate external API semantics.

It must not contain:

- experiment policy;
- domain gates;
- economic policy;
- learning logic.

---

# 18. PERFORMANCE INGESTION INTERFACE

```text
PerformanceIngestion
    append(observation) → PerformanceReference
```

The observation must reference the actual Publication.

The ingestion layer must never rewrite an existing Performance record.

Conceptual path:

```text
External Platform
      ↓
PerformanceIngestion
      ↓
PerformanceRepositoryPort.append()
      ↓
Performance
```

Performance remains an observation. The application must not convert it directly into causal Learning without the applicable domain checks.

---

# 19. QUALITY CONTROL INTERFACE

```text
QualityControl
    validate_or_transform(artifact) → QualityResult
```

Quality control may reject or transform technical artifacts.

Every material transformation that matters to attribution/provenance must remain traceable.

Quality control must not silently change an experimental treatment classification.

---

# 20. APPLICATION COMPOSITION ROOT

The Application Layer must have one explicit composition boundary where concrete implementations are assembled:

```text
Application Composition Root
        ├── Domain gates
        ├── Repository adapters
        ├── Provider adapters
        ├── Platform adapters
        └── Application services
```

Business services must depend on ports/interfaces rather than concrete external clients.

This prevents provider or database details from leaking into orchestration logic.

---

# 21. TRANSACTION / SIDE-EFFECT BOUNDARIES

Domain-significant persistence and external side effects must be separated conceptually.

For publishing:

```text
validate domain state
        ↓
create/resolve publication intent
        ↓
external publish
        ↓
record actual publication identity/state
        ↓
measure later
```

A failed external call must not be represented as successful publication merely because an application command was accepted.

Where a partial external success occurs, the application must preserve enough state to distinguish it from a clean failure.

---

# 22. ERROR CONTRACT

Application interfaces must distinguish at least:

```text
DomainRejected
InfrastructureFailure
ProviderFailure
ExternalPlatformFailure
InvalidExperimentState
BudgetRefused
Deferred
Escalated
```

These are application/technical outcome categories, not additions to the Information Model.

A `DomainGateError` must preserve:

```text
gate
invariant
reason
entity_id (when present)
```

The Application Layer may translate this into an application result but must not erase the originating invariant.

---

# 23. OBSERVABILITY CONTRACT

Every application execution that can materially affect attribution, experimentation or publication must expose a reconstructable execution reference.

At minimum:

```text
execution_reference
timestamp
operation
status
entity reference(s)
```

Provider executions additionally expose provider metadata where available.

Observability records are not a replacement for domain provenance.

---

# 24. FORBIDDEN DEPENDENCIES

The following dependencies are prohibited:

```text
Repository → Application Service
Provider → Repository
Provider → Domain Policy
Platform Adapter → Experiment Policy
Creative Strategy → Experiment Assignment Authority
Cost Controller → Domain Override
Application → direct SQL for mapped repositories
```

The following are also prohibited:

```text
Application → duplicated gate logic
Application → fabricated domain entities
Application → silent provider fallback
Application → silent publication success
```

---

# 25. INTERFACE-TO-WORKSTREAM MATRIX

| Workstream | Primary interfaces | Existing authority | Main boundary |
|---|---|---|---|
| WS1 Domain Enforcement | `DomainGatePort`, `DecisionRouter`, `ProductionPlanner`, `CostController`, `AutonomyController` | `src/domain/gates.py`, `policy.py`, `errors.py` | application orchestrates; domain decides |
| WS2 Provenance | `ExecutionTrace`, `ProviderProvenance`, `ArtifactLineage` | existing Learning provenance + locked provenance rules | trace technical execution without shadow domain model |
| WS3 Experimental Integrity | `ExperimentRunner`, `ExperimentAssignment`, `ConfounderControl`, `ExperimentIntegrity`, creative strategies | experiment repository + domain gates | assignment is controlled; creative execution cannot redefine treatment |
| WS4 Reliable Publication | `PublicationService`, `PublicationRepositoryPort`, `IdempotencyPort`, `PlatformAdapter`, `PerformanceIngestion` | publication/performance schema + PerformanceRepository | external side effect is explicit and attributable |

---

# 26. IMPLEMENTATION GATE

No `src/application/` implementation should begin until the following are confirmed:

### IF-01
Every Application service has a named contract and dependency boundary.

### IF-02
Every protected transition has a named existing domain gate or explicitly documented schema/persistence authority.

### IF-03
Every persistence dependency maps to an existing repository or a documented infrastructure gap.

### IF-04
Publication persistence is resolved before implementing reliable publishing.

### IF-05
Provider interfaces can return sufficient provenance metadata.

### IF-06
Experimental assignment is separated from creative execution.

### IF-07
Cost control cannot silently modify treatment.

### IF-08
External publication success/failure/partial success is observable.

### IF-09
No Application interface introduces a competing semantic model.

### IF-10
The resulting dependency graph respects Domain / Application / Persistence / Adapter boundaries.

---

# 27. FINAL INTERFACE CONTRACT

The future application architecture is therefore constrained to this form:

```text
                    LOCKED CONTRACTS
                           │
                           ▼
                      DOMAIN GATES
                           │
                           ▼
                APPLICATION SERVICES
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   PERSISTENCE PORTS   PROVIDER PORTS   PLATFORM PORTS
          │                │                │
          ▼                ▼                ▼
     REPOSITORIES      AI PROVIDERS     PLATFORMS
```

The Application Layer owns **coordination**.

The Domain owns **semantic validity and invariants**.

Persistence owns **durable state**.

Providers own **technical generation/execution**.

Platform adapters own **external side effects and external-state translation**.

No layer may silently assume another layer's authority.

> **This document is the final architectural interface boundary before implementation. Implementation must conform to these interfaces, the Contract-to-Application Mapping, the Corrected Target Architecture, and the three LOCKED contracts.**
