# TECHNICAL PROVENANCE STORE CONTRACT V0.1

**Project:** Autonomous Content Intelligence System  
**Version:** V0.1  
**Status:** ARCHITECTURAL CONTRACT — NON-LOCKED  
**Scope:** Technical persistence behind `ProvenanceRepositoryPort V0.1`  
**Purpose:** Define the smallest technical storage boundary required to persist execution provenance without extending the V0.1 semantic model.

---

## 1. Authority and precedence

This contract is subordinate to:

1. Information Model V0.1 — LOCKED
2. Operational Specification V0.1 — LOCKED
3. Logical Data Schema V0.1 — LOCKED
4. Existing Domain implementation and gates
5. `ProvenanceRepositoryPort V0.1` — LOCKED Application contract
6. Target Architecture V0.1-Corrected

Nothing in this contract may redefine a Domain entity, invariant, relationship, lifecycle vocabulary, policy rule, or business meaning.

This contract is a **technical storage contract**, not a new semantic model.

---

## 2. Architectural decision

V0.1 has no strict mapping from the three provenance operations to the existing LDS/domain persistence surface.

Therefore the provenance persistence boundary is a **separate technical store** behind the existing `ProvenanceRepositoryPort`.

This decision does **not** modify:

- Information Model V0.1;
- Operational Specification V0.1;
- Logical Data Schema V0.1;
- existing V0.1 domain SQL;
- Domain gates, policy, entities, or repositories;
- the locked Application port surface.

The phrase “existing persistence model” in the Python port means that the Application-facing contract does not prescribe a physical database design. It MUST NOT be interpreted as permission to overload an existing LDS table whose semantics do not match technical provenance.

---

## 3. Boundary

The only permitted dependency direction is:

```text
Application Provenance Service
          ↓
ProvenanceRepositoryPort
          ↓
Technical Provenance Adapter
          ↓
Technical Provenance Store
```

The Technical Store MUST NOT be a Domain dependency.

Domain code MUST NOT import:

- technical store records;
- technical store repositories;
- technical store schema types;
- adapter implementation types.

The Application port remains the only Application-facing persistence boundary for these records.

---

## 4. Store responsibilities

The Technical Store exists only to retain technical execution evidence needed for:

1. execution trace reconstruction;
2. provider invocation provenance;
3. actual technical artifact lineage.

It records technical facts. It does not decide whether an action was valid or permitted.

The store MUST NOT become a second semantic/domain database.

---

## 5. Minimal storage surfaces

The store has exactly three conceptual record surfaces corresponding 1:1 with the locked port operations.

### 5.1 Execution trace record

Required information:

```text
execution_id
operation_type
timestamp
input_references
output_references
execution_status
```

The record MAY carry additional technical metadata needed for reconstruction, provided that such metadata does not introduce domain semantics.

`execution_id` identifies one logical technical execution event. It is not a Domain entity identifier.

### 5.2 Provider provenance record

Required information:

```text
execution_reference
provider
model
model_version
request_parameters
input_reference
output_reference
execution_status
```

Where technically available, the record MAY also retain:

```text
intended_provider
actual_provider
prompt
seed
temperature
api_version
fallback_reason
timestamp
```

If a provider fallback occurs, the stored information MUST preserve the distinction between intended and actual provider. It MUST NOT rewrite the event as though the intended provider executed it.

### 5.3 Artifact lineage record

Required information:

```text
parent_reference
child_reference
relationship
```

The record MAY retain an execution reference as technical metadata where useful, but the Application port does not gain a fourth required argument.

Only actual/observed relationships may be stored.

The store MUST NOT fabricate ancestry because a workflow expects a complete chain.

---

## 6. References to Domain objects

Technical records MAY contain opaque references to existing Domain identifiers, including identifiers for:

```text
Evidence
Experiment
Variant
Content
Platform Version
Publication
Performance
Learning
Decision
```

These references:

- identify existing objects;
- do not create those objects;
- do not duplicate their semantic payload;
- do not establish new normative relationships;
- do not imply that the Technical Store owns their lifecycle.

Preferred representation:

```text
technical record
      │
      ├── opaque domain reference
      └── technical execution metadata
```

Forbidden representation:

```text
technical record
      ↓
copy of Domain object
      ↓
competing semantic authority
```

If a future requirement needs a relationship to become normative, that requirement MUST be handled through the appropriate Information Model / LDS versioning process rather than by silently upgrading a technical reference.

---

## 7. Append-only evidence rule

Technical provenance records are execution evidence.

The Technical Store MUST preserve the original evidence and MUST NOT silently rewrite historical execution facts.

The minimal V0.1 surface therefore provides no generic:

```text
update
 delete
```

operation.

If a future implementation requires correction, the correction mechanism MUST preserve the original evidence and MUST be specified separately before it is added to the contract.

Append-only does not create a Domain lifecycle. Technical records have no Domain status machine.

---

## 8. No technical status machine

Technical execution status is descriptive metadata only.

The store MUST NOT define or expose a lifecycle equivalent to:

```text
Experiment lifecycle
Learning lifecycle
Publication lifecycle
Domain entity lifecycle
```

A value such as `success`, `failed`, `partial`, or `fallback` describes the technical execution event. It MUST NOT be interpreted as a Domain state transition.

No technical execution status may:

- close an Experiment;
- promote Learning;
- authorize Publication;
- change a Domain status;
- override a Domain Gate;
- establish causality.

---

## 9. Provider boundary

The Technical Store may retain provider/model/version information for reproducibility and auditability.

Provider identity remains technical in V0.1.

The store MUST NOT create a normative `Provider` entity, provider lifecycle, provider policy, or provider authority.

Provider metadata MUST NOT be used by the Technical Store to select experimental treatment, authorize publication, or make Domain decisions.

If provider information later becomes a normative experimental variable or a required Domain decision input, that is a future architectural decision requiring the appropriate normative contract revision. It MUST NOT be introduced implicitly through the technical store.

---

## 10. Lineage boundary

Artifact lineage in this store means **technical production lineage**.

Examples include:

```text
input → generated
source → transformed
intermediate → assembled
artifact → final_artifact
```

The store MUST NOT reinterpret existing typed Domain relationships as generic lineage merely for convenience.

In particular, existing relationships such as:

```text
Content → Platform Version → Publication → Performance
Experiment → Experiment Arm → Content/Variant
Learning → provenance sources
```

remain Domain/LDS relationships and retain their existing semantics.

Technical lineage may reference those objects but does not replace their typed relationships.

---

## 11. Domain protection rules

The Technical Store and its adapter MUST NOT:

- create Domain entities;
- update Domain entities;
- delete Domain entities;
- change Domain statuses;
- perform Experiment transitions;
- close an Experiment;
- promote or deprecate Learning;
- rewrite Performance;
- alter experimental assignment;
- apply or override Domain policy;
- bypass Domain Gates;
- infer causal conclusions;
- act as a source of truth for Domain state.

`ExperimentClosureGate` remains the authority for Experiment closure. Performance append-only semantics remain governed by the Domain/LDS/SQL boundary.

---

## 12. Information Model protection

The store MUST NOT introduce first-class V0.1 Information Model objects named or semantically equivalent to:

```text
ExecutionTrace
Provider
ProviderProvenance
ArtifactLineage
TechnicalArtifact
```

The names above identify technical record concepts for this persistence contract; they do not amend the Information Model.

Process records, operational classifications, and provenance metadata remain technical/operational information as permitted by the locked Information Model and Operational Specification.

No generic Context, Model, Policy, Goal, Constraint, Resource, or other forbidden first-class object may be introduced through this store.

---

## 13. Logical Data Schema protection

The Technical Store is outside the V0.1 LDS.

It MUST NOT:

- add columns to V0.1 LDS tables for these technical records;
- repurpose `learning_provenance` as generic provider provenance;
- repurpose `learning_status_history` as execution history;
- repurpose `decision` as execution history;
- overload typed Domain junctions as generic artifact lineage;
- change any V0.1 CHECK constraint, FK, cardinality, or status vocabulary.

The current LDS/domain SQL remains authoritative for Domain state.

A separate technical store schema MAY be introduced later, but it is an infrastructure artifact governed by this contract rather than a modification of the V0.1 LDS.

---

## 14. Mapping to the locked Application port

The mapping is exactly:

| Port operation | Technical Store surface | Result |
|---|---|---|
| `record_execution_trace(event)` | execution trace record | `TraceReference` |
| `record_provider_provenance(execution_reference, provider_metadata)` | provider provenance record | `ProviderProvenanceReference` |
| `link_artifact_lineage(parent_reference, child_reference, relationship)` | artifact lineage record | `LineageReference` |

No fourth persistence operation is introduced.

No read/query API is required by V0.1.

No generic update/delete API is exposed.

---

## 15. Failure isolation

Technical persistence failure is distinct from Domain or provider outcome.

The adapter MUST preserve the distinction between:

```text
ProvenancePersistenceFailure
InvalidProvenanceRecord
```

and Domain/provider outcomes.

A technical persistence failure MUST NOT be translated into:

```text
DomainRejected
ExperimentInvalid
ProviderSucceeded
PublicationSucceeded
```

The Application layer decides whether a provenance failure is fatal, retryable, deferred, or escalated according to the applicable execution policy. The Technical Store itself does not make that policy decision.

---

## 16. Idempotency and duplicate protection

`execution_id` MUST be stable for one logical execution event.

The Technical Store MAY enforce uniqueness for that technical identifier to prevent accidental duplicate records.

Provider provenance is associated with `execution_reference`; it MUST NOT create a competing execution identity.

The exact physical uniqueness/indexing mechanism is an implementation concern and is not a new Domain invariant.

---

## 17. Query boundary

V0.1 does not authorize a business query surface over the Technical Store.

The store MUST NOT become a hidden read model for Domain decisions.

If a future Application use case requires querying technical provenance, the required query surface MUST be specified explicitly and checked against the Domain/LOCKED boundaries before addition.

The absence of a V0.1 query API is deliberate.

---

## 18. Physical implementation freedom

The contract does not prescribe:

- PostgreSQL versus another technical persistence technology;
- table names;
- ORM;
- serialization library;
- indexing strategy;
- partitioning;
- connection management;
- migration tooling.

Any implementation choice is permitted only if it preserves this contract.

A technical store MAY use a separate database/schema/tables/filesystem/object store or equivalent infrastructure boundary, provided that it remains outside the semantic LDS and does not leak implementation details through the Application port.

---

## 19. Conformance requirements

An implementation conforms to this contract only if all requirements below hold.

### TPS-01 — Three-surface minimum

Exactly the three V0.1 provenance capabilities are supported: execution trace, provider provenance, and artifact lineage.

### TPS-02 — Port alignment

Each surface maps 1:1 to the corresponding locked `ProvenanceRepositoryPort` operation.

### TPS-03 — Technical-only semantics

Stored records describe technical execution evidence and do not become Domain state.

### TPS-04 — No Domain mutation

The store and adapter cannot mutate Domain entities or Domain status.

### TPS-05 — No new semantic entities

No new first-class Information Model entity is introduced.

### TPS-06 — No LDS mutation

The V0.1 Logical Data Schema and its physical foundation remain unchanged.

### TPS-07 — No semantic repurposing

Existing Domain tables and relations are not reused when doing so changes their meaning.

### TPS-08 — Actual lineage only

Lineage records observed relationships only; no fabricated ancestry.

### TPS-09 — Provider transparency

Provider substitution remains distinguishable between intended and actual provider where fallback occurs.

### TPS-10 — Evidence preservation

Historical technical records are not silently rewritten.

### TPS-11 — Failure isolation

Technical persistence failures remain distinguishable from Domain/provider outcomes.

### TPS-12 — No Domain query authority

The store is not a source of truth for Domain decisions and exposes no V0.1 business-query API.

### TPS-13 — Opaque references

References to Domain objects are identifiers only; Domain payloads are not duplicated as semantic copies.

### TPS-14 — No technical lifecycle

Technical execution status is descriptive metadata, not a Domain lifecycle.

### TPS-15 — No port expansion

No additional Application persistence method is required by this contract.

---

## 20. Explicit non-responsibilities

The Technical Store is NOT responsible for:

```text
Domain validation
Domain Gate evaluation
Experiment assignment
Experiment closure
Learning promotion
Publication authorization
Provider selection
Quality policy
Economic policy
Performance interpretation
Causal inference
Decision making
```

Those responsibilities remain with their existing architectural authorities.

---

## 21. Implementation gate

This contract does **not** by itself authorize implementation.

The required sequence is:

```text
TECHNICAL PROVENANCE STORE CONTRACT V0.1
              ↓
CONFORMANCE CHECK
              ↓
[PASS]
              ↓
TECHNICAL STORE / ADAPTER DESIGN
              ↓
ADAPTER CONFORMANCE
              ↓
PROVENANCE SERVICE
```

If the conformance check identifies a contradiction with a LOCKED contract, implementation MUST stop and the contradiction must be resolved before proceeding.

---

## 22. Final architectural statement

The V0.1 Technical Provenance Store exists to preserve technical evidence of execution without creating a second semantic model.

Its authority is deliberately narrow:

> **It stores technical facts about what happened; it does not decide what the system was allowed to do.**

Any future expansion that would make provenance normative, queryable for Domain decisions, or semantically authoritative requires a new architectural decision and the appropriate normative contract revision before implementation.
