# TARGET ARCHITECTURE V0.1 — CORRECTED SPECIFICATION

**Project:** Autonomous Content Intelligence System  
**Repository:** `AUTONOMOUS-CONTENT-INTELLIGENCE-SYSTEM`  
**Version:** V0.1-CORRECTED  
**Status:** DRAFT — NON-NORMATIVE  
**Supersedes:** Target Architecture V0.1 as architectural working specification  
**Does NOT modify:** Information Model V0.1, Operational Specification V0.1, Logical Data Schema V0.1

---

# 1. PURPOSE

This document defines the corrected target architecture for the future application layer of the Autonomous Content Intelligence System.

It incorporates the findings that survived adversarial confrontation between:

1. the original Target Architecture V0.1;
2. the Perplexity adversarial audit;
3. the actual repository structure and existing implementation.

The purpose is not to redesign the existing system.

The purpose is to define the future application layer that will operate **around the existing domain and persistence layers without bypassing, duplicating, or redefining them**.

---

# 2. ARCHITECTURAL AUTHORITY

The following hierarchy is mandatory:

```text
LOCKED CONTRACTS
│
├── Information Model V0.1
├── Operational Specification V0.1
└── Logical Data Schema V0.1
        │
        ▼
DOMAIN
│
├── domain/gates.py
├── domain/policy.py
└── domain/errors.py
        │
        ▼
APPLICATION
│
└── Target Architecture V0.1-Corrected
        │
        ▼
PERSISTENCE / EXTERNAL ADAPTERS
```

The application layer does not have authority to redefine domain semantics.

The application layer may orchestrate execution, call domain gates, select implementation providers, manage workflows, and coordinate external systems.

It may not:

- redefine LOCKED entities;
- redefine domain invariants;
- bypass domain gates;
- override domain policy;
- turn providers into normative authorities;
- turn repositories into business orchestrators.

---

# 3. EXISTING SYSTEM — PRESERVATION RULE

The following components are considered existing protected infrastructure:

```text
docs/information-model/V0.1/
docs/operational-specification/V0.1/
docs/data-schema/V0.1/

src/domain/
src/persistence/
```

In particular:

```text
src/domain/gates.py
src/domain/policy.py
src/domain/errors.py
src/persistence/repositories/
```

must not be modified merely to accommodate the future application architecture.

The application must adapt to these contracts and interfaces.

---

# 4. TARGET APPLICATION LAYER

The future application layer is conceptually organized as:

```text
src/application/

├── orchestration/
│   ├── decision_router
│   ├── production_planner
│   ├── cost_controller
│   └── autonomy_controller
│
├── experimentation/
│   ├── experiment_runner
│   ├── assignment
│   ├── confounder_control
│   └── experiment_integrity
│
├── creative/
│   ├── strategy_selector
│   ├── avatar_strategy
│   └── no_avatar_strategy
│
├── production/
│   ├── script
│   ├── visual
│   ├── voice
│   ├── avatar
│   ├── assembly
│   └── quality_control
│
├── provenance/
│   ├── execution_trace
│   ├── provider_provenance
│   └── artifact_lineage
│
├── publishing/
│   ├── publication_service
│   ├── idempotency
│   └── platform adapters
│
└── providers/
    ├── llm
    ├── image
    ├── video
    ├── voice
    └── avatar
```

This structure is an implementation proposal, not a new semantic model.

The exact module decomposition may evolve without changing the LOCKED contracts.

---

# 5. FOUR SURVIVING ARCHITECTURAL WORKSTREAMS

The adversarial audit produces four actual architectural workstreams.

---

# WORKSTREAM 1 — APPLICATION-LEVEL DOMAIN ENFORCEMENT

## 5.1 Problem

The repository already contains domain gates.

The problem is not the absence of gates.

The problem is that the future application layer must guarantee that workflows cannot simply execute around them.

Therefore:

> Domain Gates are domain authorities; Application Services are responsible for invoking them at the correct workflow boundaries.

## 5.2 Responsibility

The application layer is responsible for:

- receiving an application command;
- loading the relevant domain state;
- invoking the applicable domain gate;
- refusing execution when the gate fails;
- performing the authorized transition;
- persisting the resulting state;
- recording the execution/provenance.

## 5.3 Boundary

The application layer MUST NOT duplicate the logic contained in `domain/gates.py`.

Incorrect:

```text
Application
    ↓
reimplementation of gate logic
    ↓
execute
```

Correct:

```text
Application Service
        ↓
Existing Domain Gate
        ↓
PASS / FAIL
        ↓
authorized execution
```

## 5.4 Required workflow principle

Any application workflow that causes a domain-significant state transition must have an explicit gate checkpoint.

Conceptually:

```text
Decision
   ↓
[Gate]
   ↓
Production
   ↓
[Gate]
   ↓
Content
   ↓
[Gate]
   ↓
Publication
   ↓
[Gate]
   ↓
Performance
   ↓
[Gate]
   ↓
Learning
```

The exact mapping between transitions and existing gates must be established against the Operational Specification before implementation.

No new gate should be invented simply because the application needs one.

## 5.5 Domain Policy authority

`domain/policy.py` remains authoritative.

The application cannot lower a domain requirement because:

- a provider is expensive;
- a provider is unavailable;
- the budget is low;
- publication is urgent;
- an experiment is inconvenient.

If a domain requirement cannot be satisfied:

```text
DO NOT DEGRADE SILENTLY
DO NOT OVERRIDE
DO NOT BYPASS

→ refuse / defer / escalate
```

---

# WORKSTREAM 2 — PROVENANCE AND EXECUTION TRACEABILITY

## 6.1 Problem

The existing domain model records important scientific objects such as:

```text
Decision
Experiment
Variant
Content
Performance
Learning
```

But the future production pipeline introduces implementation-level events that must remain reconstructable.

Examples:

- provider;
- model;
- model version;
- prompt;
- seed;
- parameters;
- generated asset;
- quality-control modification;
- timestamp;
- fallback;
- cost decision.

These must not become a second semantic model.

## 6.2 Responsibility

A future provenance mechanism must allow reconstruction of:

```text
Decision
   ↓
Production Plan
   ↓
Creative choice
   ↓
Generation request
   ↓
Provider
   ↓
Model/version
   ↓
Parameters
   ↓
Intermediate artifacts
   ↓
Quality-control transformations
   ↓
Final Content
   ↓
Platform Version
   ↓
Publication
```

## 6.3 Provenance principle

Every externally generated artifact must have sufficient provenance to answer:

> What produced this artifact, using which implementation, under which parameters, and from which upstream decision?

At minimum:

```text
provider
model
model_version
request_parameters
timestamp
input_reference
output_reference
execution_status
```

Where technically applicable:

```text
prompt
seed
temperature
API/version
fallback_reason
quality_level
```

## 6.4 Metadata boundary

Metadata must not become a shadow domain model.

Three categories are distinguished.

### A. Domain information

Examples:

```text
status
type
relationships
experiment role
baseline/intervention
```

These belong to the existing domain/data model.

### B. Experimental information

Examples:

```text
treatment
control
baseline
assignment
confounder
```

These belong to the experimental representation already authorized by the contracts.

### C. Implementation provenance

Examples:

```text
provider
model version
prompt
seed
temperature
API version
execution timestamp
technical error
```

These may be represented through the existing artifact/provenance mechanisms.

The application must never use metadata to hide domain information that should be modeled explicitly.

---

# WORKSTREAM 3 — EXPERIMENTAL INTEGRITY

## 7.1 Problem

The avatar/no-avatar question is not fundamentally a content-generation problem.

It is an experimental-design problem.

The system must be capable of determining whether performance differences are attributable to the intended treatment rather than:

- provider differences;
- production quality differences;
- platform differences;
- audience differences;
- timing;
- novelty;
- topic;
- cost-driven routing.

## 7.2 Avatar architecture

Avatar remains:

```text
CAPABILITY / PRODUCTION RESOURCE
```

and NOT:

```text
NEW DOMAIN ENTITY
```

The application may contain:

```text
creative/avatar_strategy
creative/no_avatar_strategy
production/avatar
```

but these modules must not create a competing semantic model.

## 7.3 Experimental assignment

When avatar/no-avatar is being tested as an experimental variable, assignment must be controlled by the experimentation layer rather than by a free-form creative selector.

Conceptually:

```text
Experiment
     ↓
Assignment
     ├── Treatment: Avatar
     └── Control: No Avatar
```

The creative layer may determine how the assigned treatment is executed.

It must not silently alter the experimental assignment.

## 7.4 Confounder control

The experimentation layer must record relevant confounders.

Potential confounders include:

```text
platform
account
publication timing
topic
audience
production quality
provider
model
novelty
budget-driven quality changes
```

The exact confounder representation must remain compatible with the LOCKED experimental model.

## 7.5 Provider changes

A provider is an implementation variable.

If provider selection changes the treatment materially, that change must be observable.

Therefore:

```text
Provider A
    ↓
failure
    ↓
Provider B
```

must never become invisible.

The system must record:

```text
original provider
actual provider
reason
timestamp
impact
```

If the provider change compromises experimental validity, the experiment/variant must be marked accordingly using the existing domain semantics.

The application must not invent a new semantic status merely for convenience.

## 7.6 Cost Controller boundary

The Cost Controller is:

```text
RESOURCE CONSTRAINT
```

not:

```text
EXPERIMENTAL AUTHORITY
```

It may answer:

> Can we afford this execution?

It must not silently answer:

> Therefore, change the experimental treatment.

Correct:

```text
Experiment requires Provider A
        ↓
Cost Controller
        ↓
Budget insufficient
        ↓
REFUSE / DEFER / ESCALATE
```

or, where explicitly permitted by the experiment policy:

```text
change provider
        ↓
record change
        ↓
assess experimental validity
```

Incorrect:

```text
Budget low
    ↓
silently downgrade production
    ↓
publish
    ↓
learn
```

---

# WORKSTREAM 4 — RELIABLE PUBLICATION

## 8.1 Problem

Publishing is an external side-effect boundary.

A publication may:

- succeed;
- fail;
- partially succeed;
- be retried;
- be duplicated;
- subsequently be removed.

The application must therefore treat publication as a stateful external operation.

## 8.2 Publishing boundary

The architecture becomes:

```text
Content
   ↓
Platform Version
   ↓
Publication Request
   ↓
Platform Adapter
   ↓
External Platform
```

The domain remains independent of the concrete platform API.

## 8.3 Idempotence

Retries must not accidentally create duplicate publications.

The publishing layer must therefore maintain an idempotency mechanism based on a stable publication identity.

Conceptually:

```text
Publication Intent
       ↓
Idempotency Key
       ↓
Platform Adapter
       ↓
External Publication
```

A retry of the same intent must resolve to the existing publication rather than create an unintended second publication.

## 8.4 Partial success

The application must distinguish at least:

```text
pending
published
partially_published
failed
removed
```

provided these states can be represented without contradicting the LOCKED data model.

If the existing schema already provides equivalent semantics, the existing representation must be reused.

## 8.5 Attribution

Performance must be associated with what was actually published.

Not merely:

```text
what the system intended to publish
```

but:

```text
what the platform actually received / exposed
```

Therefore:

```text
Platform Version
       ↓
Publication
       ↓
External Platform Identity
       ↓
Performance
```

must remain reconstructable.

---

# 9. CROSS-WORKSTREAM CONTROL FLOW

The four workstreams must operate together.

A future execution should conceptually resemble:

```text
                ┌──────────────────────┐
                │      DECISION        │
                └──────────┬───────────┘
                           │
                           ▼
                  APPLICATION ORCHESTRATOR
                           │
                           ▼
                     DOMAIN GATE
                           │
                           ▼
                  EXPERIMENT / STRATEGY
                           │
                 ┌─────────┴─────────┐
                 │                   │
              Avatar             No Avatar
                 │                   │
                 └─────────┬─────────┘
                           │
                           ▼
                    COST CHECK
                           │
                    ┌──────┴──────┐
                    │             │
                  PASS          REFUSE
                    │             │
                    ▼             └──→ STOP / DEFER
                PRODUCTION
                    │
                    ▼
              PROVIDER EXECUTION
                    │
                    ▼
                PROVENANCE
                    │
                    ▼
              QUALITY CONTROL
                    │
                    ▼
                CONTENT
                    │
                    ▼
             PLATFORM VERSION
                    │
                    ▼
              DOMAIN CHECK
                    │
                    ▼
                PUBLISHING
                    │
                    ▼
             PUBLICATION STATE
                    │
                    ▼
                PERFORMANCE
                    │
                    ▼
             EXPERIMENT CHECK
                    │
                    ▼
                 LEARNING
                    │
                    ▼
              DECISION UPDATE
```

This is a target execution model, not a claim that every path must be strictly linear.

The system remains graph-oriented.

---

# 10. AUTONOMY MODEL

Autonomy must be implemented as controlled execution, not unrestricted recursion.

The application must support:

```text
RUN
PAUSE
STOP
DEFER
ESCALATE
```

The autonomy controller must be subordinate to:

```text
Domain Policy
Operational Specification
Experimental integrity
Budget constraints
Human approval requirements
```

## 10.1 Mandatory stop conditions

The target architecture must provide mechanisms capable of stopping execution when applicable conditions occur, including:

```text
unresolved contradiction
budget exhaustion
repeated degradation
experimental invalidity
provider instability
publication failure pattern
integrity violation
```

The exact numerical thresholds are not invented here.

They must be defined by the relevant policy/specification layer before implementation.

## 10.2 Human control

Human approval is an application control boundary.

The architecture must support:

```text
AUTO
REVIEW_REQUIRED
BLOCKED
```

where required by policy.

The exact categories requiring human approval remain an architectural/policy decision and must not be guessed during implementation.

---

# 11. RESPONSIBILITY MATRIX

| Responsibility | Domain | Application | Persistence | Provider | Platform Adapter |
|---|---|---|---|---|---|
| Define invariants | **YES** | NO | NO | NO | NO |
| Validate domain rules | **YES** | invokes | NO | NO | NO |
| Orchestrate workflows | NO | **YES** | NO | NO | NO |
| Select implementation provider | NO | **YES** | NO | NO | NO |
| Generate asset | NO | coordinates | NO | **YES** | NO |
| Persist state | NO | coordinates | **YES** | NO | NO |
| Define experimental semantics | **YES / LOCKED** | executes | NO | NO | NO |
| Assign experiment treatment | according to contract | **YES** | stores | NO | NO |
| Decide economic feasibility | NO | **YES** | stores evidence | NO | NO |
| Override domain policy | NO | **NEVER** | NO | NO | NO |
| Publish externally | NO | coordinates | records | NO | **YES** |
| Trace provider execution | NO | **YES** | stores | supplies technical data | NO |
| Create new domain entities | **ONLY via contract evolution** | NO | NO | NO | NO |

---

# 12. DEPENDENCY RULES

The target dependency direction is:

```text
application
    ↓
domain
    ↓
persistence interfaces
```

with external adapters at the boundary.

Providers and publishing adapters must not become authorities over domain decisions.

Repositories must not call orchestration services.

Providers must not call repositories.

Publishing adapters must not contain experimental policy.

---

# 13. WHAT IS EXPLICITLY NOT PART OF THIS ARCHITECTURE

The following are deliberately excluded.

### No new domain model

No new first-class entities for:

```text
Creative Strategy
Avatar Strategy
Provider
Cost Decision
Production Plan
```

unless a future contract version explicitly authorizes them.

### No modification of LOCKED contracts

No modification of:

```text
Information Model V0.1
Operational Specification V0.1
Logical Data Schema V0.1
```

as part of this architecture work.

### No repository orchestration

No business workflows inside:

```text
src/persistence/repositories/
```

### No provider authority

Providers execute technical requests.

They do not decide domain policy.

### No silent fallback

No provider substitution that becomes invisible to the experimental/provenance layer.

---

# 14. IMPLEMENTATION ORDER

The architecture must not be implemented arbitrarily.

The recommended sequence is:

```text
PHASE A
Architecture specification
        ↓
PHASE B
Contract-to-application mapping
        ↓
PHASE C
Gate enforcement design
        ↓
PHASE D
Provenance design
        ↓
PHASE E
Experimental integrity design
        ↓
PHASE F
Publishing/idempotency design
        ↓
PHASE G
Autonomy control design
        ↓
PHASE H
Tests / conformance
        ↓
PHASE I
Implementation
```

No implementation should begin before the exact interfaces and existing repository boundaries have been mapped.

---

# 15. ACCEPTANCE CONDITIONS

The corrected Target Architecture can be considered architecturally coherent when the following can be demonstrated:

### AC-01

No application workflow can perform a protected domain transition without the applicable domain validation.

### AC-02

No Cost Controller decision can silently modify an experimental treatment.

### AC-03

No provider substitution can become invisible in provenance.

### AC-04

Avatar/no-avatar experiments remain attributable to the intended treatment rather than uncontrolled production differences.

### AC-05

A published artifact can be reconstructed from:

```text
Decision
→ production
→ provider
→ artifact
→ platform version
→ publication
→ performance
→ learning
```

### AC-06

A failed or partial publication cannot silently corrupt attribution.

### AC-07

Repositories remain persistence components rather than orchestration engines.

### AC-08

Providers remain technical adapters.

### AC-09

Domain Policy remains authoritative over economic optimization.

### AC-10

The system can be paused/stopped without destroying accumulated evidence.

---

# 16. FINAL ARCHITECTURAL VERDICT

The corrected Target Architecture does not replace the existing system.

It surrounds it.

The architecture therefore follows this principle:

```text
                EXISTING LOCKED SYSTEM
                       ▲
                       │
             domain authority
                       │
        ┌──────────────┴──────────────┐
        │                             │
        │      FUTURE APPLICATION     │
        │                             │
        │ orchestration               │
        │ experimentation             │
        │ production                  │
        │ provenance                  │
        │ publishing                  │
        │ providers                   │
        │ autonomy control            │
        │                             │
        └──────────────┬──────────────┘
                       │
                       ▼
                 EXTERNAL WORLD
             AI providers / platforms
```

The central architectural rule is:

> **The future application layer may coordinate the system, but it may never become more authoritative than the domain contracts that already exist.**

The existing system remains the source of semantic truth.

The new application layer becomes the source of execution coordination.

The persistence layer remains the source of durable state.

External providers and platforms remain replaceable adapters.

This preserves the work already completed while creating the missing execution architecture required for an autonomous content intelligence system.
