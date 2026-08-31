# TECHNICAL PROVENANCE STORE CONTRACT V0.1

**Project:** Autonomous Content Intelligence System  
**Version:** V0.1  
**Status:** ARCHITECTURAL CONTRACT — NON-LOCKED  
**Scope:** Technical persistence behind `ProvenanceRepositoryPort V0.1`  
**Purpose:** Define the smallest concrete technical storage boundary required to persist execution provenance without extending the V0.1 semantic model.

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

## 2. Concrete storage decision

V0.1 selects **PostgreSQL in a dedicated technical schema** as the physical Technical Provenance Store.

The repository already uses PostgreSQL and exposes a shared connection/transaction boundary through `src/persistence/connection.py`. The provenance store therefore reuses the existing database infrastructure without reusing the semantic tables of the LOCKED LDS.

The physical boundary is:

```text
PostgreSQL database
│
├── existing V0.1 domain schema
│   ├── evidence
│   ├── content
│   ├── platform_version
│   ├── publication
│   ├── performance
│   ├── experiment
│   ├── experiment_arm
│   ├── learning
│   ├── learning_provenance
│   ├── learning_status_history
│   ├── decision
│   └── existing domain junctions
│
└── technical_provenance
    ├── execution_trace
    ├── provider_provenance
    └── artifact_lineage
```

The technical schema is infrastructure, not part of the V0.1 Logical Data Schema.

### 2.1 Foundation protection

`db/migrations/001_v0.1_foundation.sql` MUST NOT be edited to add provenance tables.

The technical store, when implemented, MUST be introduced through a separate technical migration or equivalent infrastructure provisioning step.

That separate migration is not an amendment to the V0.1 LDS. It MUST NOT alter existing domain tables, constraints, foreign keys, cardinalities, or status vocabularies.

### 2.2 Why PostgreSQL is selected

This choice minimizes infrastructure surface because the real repository already uses PostgreSQL through `src/persistence/connection.py`.

The existing connection helper exposes `get_connection()` and transaction handling, while keeping database details below the Application boundary. The provenance adapter may reuse that infrastructure but owns the technical schema semantics.

The decision therefore avoids introducing a second database technology or an external persistence service solely for V0.1 provenance.

---

## 3. Architectural boundary

The only permitted dependency direction is:

```text
Application Provenance Service
          ↓
ProvenanceRepositoryPort
          ↓
Technical Provenance Adapter
          ↓
technical_provenance schema
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

The store has exactly three V0.1 record surfaces corresponding 1:1 with the locked port operations:

```text
technical_provenance.execution_trace
technical_provenance.provider_provenance
technical_provenance.artifact_lineage
```

No fourth V0.1 provenance record type is authorized by this contract.

---

## 6. Execution trace record

### 6.1 Required logical fields

The physical record MUST support:

```text
execution_id
operation_type
timestamp
input_references
output_references
execution_status
```

The record MAY carry additional technical metadata required for reconstruction, provided that the metadata does not introduce Domain semantics.

`execution_id` identifies one logical technical execution event. It is not a Domain entity identifier.

### 6.2 Semantics

Allowed content:

- application operation identity;
- execution timestamp;
- technical input references;
- technical output references;
- technical execution outcome;
- implementation metadata necessary to reconstruct execution.

Forbidden content:

- Domain transition authority;
- Domain gate replacement;
- fabricated causality;
- duplicated Domain entities;
- business lifecycle state.

---

## 7. Provider provenance record

### 7.1 Required logical fields

The physical record MUST support:

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

Where technically available, it MAY retain:

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

### 7.2 Fallback transparency

If:

```text
intended provider = A
actual provider   = B
```

the record MUST preserve the distinction. It MUST NOT rewrite the event as though A executed it.

### 7.3 Forbidden semantics

Provider provenance MUST NOT:

- assign experimental treatment;
- alter experiment assignment;
- authorize publication;
- authorize spending;
- determine Domain policy;
- establish causal conclusions;
- create a provider lifecycle.

Provider identity remains technical in V0.1.

---

## 8. Artifact lineage record

### 8.1 Required logical fields

```text
parent_reference
child_reference
relationship
```

The record MAY retain an execution reference as technical metadata, but the locked Application port remains exactly the three-argument lineage operation.

### 8.2 Actuality rule

Only actual/observed relationships may be stored.

The adapter MUST NOT fabricate ancestry because a workflow expects a complete chain.

### 8.3 Domain relationship protection

Existing typed Domain relationships remain authoritative, including:

```text
Content → Platform Version → Publication
Experiment → Experiment Arm → Content/Variant
Learning → provenance sources
```

Technical lineage MAY reference those objects but MUST NOT replace or reinterpret their typed Domain relationships.

---

## 9. Domain references

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
- do not give the Technical Store lifecycle ownership.

The technical schema MUST NOT introduce SQL foreign keys into the existing Domain schema solely for these references.

Preferred representation:

```text
technical record
      │
      ├── opaque domain reference
      └── technical metadata
```

Forbidden representation:

```text
technical record
      ↓
copy of Domain object
      ↓
competing semantic authority
```

---

## 10. Append-only evidence rule

Technical provenance records are execution evidence.

The Technical Store MUST preserve original evidence and MUST NOT silently rewrite historical execution facts.

The V0.1 Application surface therefore provides no generic:

```text
update
 delete
```

operation.

If a future implementation requires correction, the correction mechanism MUST preserve the original evidence and MUST be specified separately before being added to the contract.

Append-only evidence does not create a Domain lifecycle.

---

## 11. Technical status boundary

The store may record descriptive execution outcomes such as:

```text
success
failed
partial
fallback
```

These are technical facts only.

They MUST NOT become or mirror lifecycle states for:

```text
Experiment
Learning
Publication
Content
Decision
```

No technical status may close an Experiment, promote Learning, authorize Publication, change Domain status, override a Domain Gate, or establish causality.

---

## 12. Domain and LOCKED protection

The Technical Store and adapter MUST NOT:

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

`ExperimentClosureGate` remains the authority for Experiment closure. Performance append-only semantics remain governed by the existing Domain/LDS/SQL boundary.

---

## 13. Information Model protection

The Technical Store MUST NOT introduce first-class V0.1 Information Model objects named or semantically equivalent to:

```text
ExecutionTrace
Provider
ProviderProvenance
ArtifactLineage
TechnicalArtifact
```

These names identify technical record surfaces only; they do not amend the Information Model.

No generic Context, Model, Policy, Goal, Constraint, Resource, or other forbidden first-class object may be introduced through this store.

---

## 14. Logical Data Schema protection

The Technical Store is outside the V0.1 LDS.

It MUST NOT:

- add columns to V0.1 LDS tables for these technical records;
- repurpose `learning_provenance` as generic provider provenance;
- repurpose `learning_status_history` as execution history;
- repurpose `decision` as execution history;
- overload typed Domain junctions as generic artifact lineage;
- change any V0.1 CHECK constraint, FK, cardinality, or status vocabulary.

The current LDS/domain SQL remains authoritative for Domain state.

---

## 15. Mapping to the locked Application port

The mapping is exactly:

| Port operation | Technical Store surface | Result |
|---|---|---|
| `record_execution_trace(event)` | `technical_provenance.execution_trace` | `TraceReference` |
| `record_provider_provenance(execution_reference, provider_metadata)` | `technical_provenance.provider_provenance` | `ProviderProvenanceReference` |
| `link_artifact_lineage(parent_reference, child_reference, relationship)` | `technical_provenance.artifact_lineage` | `LineageReference` |

No fourth persistence operation is introduced.

No read/query API is required by V0.1.

No generic update/delete API is exposed.

---

## 16. Failure isolation

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

## 17. Idempotency and duplicate protection

`execution_id` MUST be stable for one logical execution event.

The Technical Store SHOULD enforce uniqueness for that technical identifier where practical.

Provider provenance is associated with `execution_reference`; it MUST NOT create a competing execution identity.

Lineage duplicate handling MAY use a technical uniqueness rule appropriate to the store, but that rule is not a Domain invariant.

---

## 18. Query boundary

V0.1 does not authorize a business query surface over the Technical Store.

The store MUST NOT become a hidden read model for Domain decisions.

If a future Application use case requires querying technical provenance, the required query surface MUST be specified explicitly and checked against the Domain/LOCKED boundaries before addition.

---

## 19. Physical schema contract

The concrete physical schema boundary is fixed for V0.1 as:

```text
schema: technical_provenance

relations:
  execution_trace
  provider_provenance
  artifact_lineage
```

The physical implementation MUST be PostgreSQL-compatible and MUST preserve the logical fields and boundaries defined in sections 6–18.

### 19.1 Required physical isolation

The technical relations MUST be distinct from the existing LDS relations.

They MUST NOT be added to or merged with:

```text
content
platform_version
publication
performance
experiment
experiment_arm
learning
learning_provenance
learning_status_history
decision
```

### 19.2 Required migration isolation

The technical schema MUST be provisioned through a migration/artifact separate from `001_v0.1_foundation.sql`.

The existing foundation migration remains immutable for this purpose.

### 19.3 Foreign-key policy

No foreign key from the technical schema to Domain tables is required or authorized merely to represent an opaque technical reference.

The technical store therefore cannot impose new Domain cardinality or lifecycle constraints.

### 19.4 Physical naming

The names above are the V0.1 technical storage names. They are infrastructure names and do not constitute new Information Model entity names.

---

## 20. Conformance requirements

An implementation conforms to this contract only if all requirements below hold.

### TPS-01 — PostgreSQL technical boundary

The implementation uses the dedicated `technical_provenance` PostgreSQL schema or a mechanically equivalent isolated PostgreSQL namespace preserving the same boundary.

### TPS-02 — Three-surface minimum

Exactly the three V0.1 provenance capabilities are supported: execution trace, provider provenance, and artifact lineage.

### TPS-03 — Port alignment

Each surface maps 1:1 to the corresponding locked `ProvenanceRepositoryPort` operation.

### TPS-04 — Technical-only semantics

Stored records describe technical execution evidence and do not become Domain state.

### TPS-05 — No Domain mutation

The store and adapter cannot mutate Domain entities or Domain status.

### TPS-06 — No new semantic entities

No new first-class Information Model entity is introduced.

### TPS-07 — No LDS mutation

The V0.1 Logical Data Schema and its physical foundation remain unchanged.

### TPS-08 — No semantic repurposing

Existing Domain tables and relations are not reused when doing so changes their meaning.

### TPS-09 — Actual lineage only

Lineage records observed relationships only; no fabricated ancestry.

### TPS-10 — Provider transparency

Provider substitution remains distinguishable between intended and actual provider where fallback occurs.

### TPS-11 — Evidence preservation

Historical technical records are not silently rewritten.

### TPS-12 — Failure isolation

Technical persistence failures remain distinguishable from Domain/provider outcomes.

### TPS-13 — No Domain query authority

The store is not a source of truth for Domain decisions and exposes no V0.1 business-query API.

### TPS-14 — Opaque references

References to Domain objects are identifiers only; Domain payloads are not duplicated as semantic copies.

### TPS-15 — No technical lifecycle

Technical execution status is descriptive metadata, not a Domain lifecycle.

### TPS-16 — Foundation isolation

`db/migrations/001_v0.1_foundation.sql` is not modified to provide technical provenance.

### TPS-17 — No port expansion

No additional Application persistence method is required by this contract.

---

## 21. Implementation gate

This contract permits the following sequence only after the store contract conformance check passes:

```text
TECHNICAL PROVENANCE STORE CONTRACT V0.1
              ↓
STORE CONTRACT CONFORMANCE CHECK
              ↓
[PASS]
              ↓
TECHNICAL PROVENANCE MIGRATION
              ↓
ADAPTER IMPLEMENTATION
              ↓
ADAPTER CONFORMANCE
              ↓
PROVENANCE SERVICE
```

If the conformance check identifies a contradiction with a LOCKED contract or with the real repository boundary, implementation MUST stop and the contradiction must be resolved first.

---

## 22. Final decision

The concrete V0.1 storage strategy is therefore:

```text
Existing PostgreSQL infrastructure
            ↓
     technical_provenance
            │
     ┌──────┼──────┐
     ▼      ▼      ▼
 execution provider lineage
   trace   provenance
     │      │      │
     └──────┼──────┘
            ▼
    Provenance Adapter
            ▼
 ProvenanceRepositoryPort
```

The Technical Provenance Store is deliberately isolated from the semantic model.

> **It stores technical evidence of what happened; it does not become authority over what the system was allowed to do.**

Any future expansion of its semantics, query authority, lifecycle, or normative relationships requires a new architectural decision and conformance review before implementation.
