# PROVENANCE REPOSITORY PORT V0.1 — FINAL SPECIFICATION

**Project:** Autonomous Content Intelligence System  
**Repository:** `AUTONOMOUS-CONTENT-INTELLIGENCE-SYSTEM`  
**Version:** V0.1  
**Status:** ARCHITECTURAL CONTRACT — PRE-IMPLEMENTATION  
**Scope:** Application → technical provenance persistence boundary  
**Implementation:** NOT DEFINED BY THIS DOCUMENT

---

# 1. PURPOSE

This document freezes the minimal Application persistence port required to persist technical execution provenance without modifying the Domain, the Information Model V0.1, the Operational Specification V0.1, or the Logical Data Schema V0.1.

The port is derived from the repository's actual V0.1 persistence surface and from the previously established Technical Store strategy: provenance is an application/infrastructure concern and must not become a second semantic domain model.

This document defines the port only. It does not authorize an implementation, SQL migration, provider integration, or Provenance Service implementation.

---

# 2. AUTHORITY AND PRECEDENCE

The port is subordinate to:

1. Information Model V0.1 — LOCKED
2. Operational Specification V0.1 — LOCKED
3. Logical Data Schema V0.1 — LOCKED
4. Existing Domain implementation
5. Existing persistence contracts
6. Target Architecture V0.1-Corrected
7. Application Interface Specification V0.1

Nothing in this port may redefine a LOCKED entity, invariant, relationship, status vocabulary, or business rule.

---

# 3. REPOSITORY REALITY

The current physical V0.1 schema contains domain persistence for objects including `evidence`, `content`, `platform_version`, `publication`, `performance`, `experiment`, `experiment_arm`, `learning`, and `decision`, plus their declared junction tables.

It does not contain dedicated V0.1 tables for:

```text
ExecutionTrace
ProviderProvenance
ArtifactLineage
```

The existing persistence layer therefore remains the persistence authority for domain state, while this port targets a separate technical provenance store/adapter surface.

No V0.1 SQL modification is part of this contract.

---

# 4. PORT BOUNDARY

The dependency direction is:

```text
Application Provenance Service
          ↓
ProvenanceRepositoryPort
          ↓
Technical Provenance Adapter / Store
```

The port MUST NOT expose:

- SQL details;
- database table names;
- ORM models;
- provider SDK types;
- platform SDK types;
- domain mutation commands;
- domain gate decisions.

The adapter owns the technical persistence mechanism.

---

# 5. MINIMAL PORT

The port contains exactly three persistence capabilities.

```text
ProvenanceRepositoryPort

    append_execution_trace(trace_record)
        → TraceReference

    record_provider_provenance(provider_record)
        → ProviderProvenanceReference

    record_artifact_lineage(lineage_record)
        → LineageReference
```

These operations are append/record operations. V0.1 provides no generic update or delete operation for provenance records.

A read/query surface is deliberately excluded from the minimal V0.1 port unless a concrete Provenance Service requirement proves it necessary and a subsequent contract revision authorizes it.

---

# 6. `append_execution_trace`

## Purpose

Persist a technical record of an application execution event.

## Minimum input

```text
execution_id
operation_type
timestamp
input_references
output_references
execution_status
```

The references identify existing objects or technical artifacts; they do not create new domain entities.

## Output

```text
TraceReference
```

The returned reference is technical and may be used by the other provenance operations.

## Allowed semantics

The record may describe:

- what application operation executed;
- when it executed;
- which references entered the operation;
- which references resulted;
- whether the technical execution succeeded, failed, or otherwise ended.

## Forbidden semantics

It MUST NOT:

- decide whether a domain transition is valid;
- replace a domain status;
- replace a domain gate result;
- infer causality;
- create a second representation of `Decision`, `Experiment`, `Content`, `Publication`, or `Learning`.

---

# 7. `record_provider_provenance`

## Purpose

Persist the technical identity and execution details of an external provider invocation.

## Minimum input

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

Where technically available, the record may additionally contain:

```text
prompt
seed
temperature
api_version
fallback_reason
timestamp
```

## Output

```text
ProviderProvenanceReference
```

## Required fallback visibility

If the intended provider differs from the actual provider, the technical record MUST preserve enough information to distinguish them.

Conceptually:

```text
intended_provider
actual_provider
fallback_reason
```

A provider substitution MUST NOT be represented as if the originally selected provider executed the request.

## Forbidden semantics

Provider provenance MUST NOT:

- select experimental treatment;
- approve a domain transition;
- authorize publication;
- determine economic policy;
- become a normative provider entity.

---

# 8. `record_artifact_lineage`

## Purpose

Persist an actual technical relationship between artifacts.

## Minimum input

```text
parent_reference
child_reference
relationship
execution_reference
```

## Output

```text
LineageReference
```

## Lineage rule

Only observed/actual relationships may be recorded.

The adapter MUST NOT fabricate an ancestry chain merely because a target workflow expects one.

Examples of legitimate relationships include:

```text
source → generated
input → output
intermediate → transformed
artifact → final_artifact
```

The vocabulary of `relationship` is technical unless a future LOCKED contract explicitly makes a relationship semantic.

---

# 9. REFERENCE RULES

Technical provenance may reference existing domain identifiers such as:

```text
Decision
Experiment
Variant
Content
Platform Version
Publication
Performance
Learning
```

These are references only.

The port MUST NOT persist duplicated domain payloads whose purpose is to become an alternative source of semantic truth.

Preferred pattern:

```text
technical provenance
        │
        ├── reference → domain object
        └── technical metadata
```

Forbidden pattern:

```text
technical provenance
        ↓
copy of domain object
        ↓
competing semantic authority
```

---

# 10. APPEND / MUTABILITY RULE

V0.1 provenance records are treated as execution evidence.

Therefore the minimal port exposes no generic mutation operation:

```text
NO update(...)
NO delete(...)
```

If a technical correction is required, the future implementation must use an explicit technical mechanism that preserves the original evidence rather than silently rewriting history. Such a mechanism is outside this V0.1 port unless separately specified.

---

# 11. TRANSACTION BOUNDARY

The port does not own domain transactions.

The Application layer determines when a provenance record is emitted relative to an application operation.

The technical adapter guarantees persistence according to its own storage contract.

The port MUST NOT imply distributed atomicity between:

```text
Domain persistence
External provider
Technical provenance store
```

unless a later architecture explicitly specifies such coordination.

A provenance persistence failure must therefore remain distinguishable from the success/failure of the underlying provider or domain operation.

---

# 12. ERROR CONTRACT

The port must expose technical failure distinctly from domain failure.

At minimum, implementations must be able to distinguish:

```text
ProvenancePersistenceFailure
InvalidProvenanceRecord
```

A provenance persistence error MUST NOT be converted into:

```text
DomainRejected
ExperimentInvalid
ProviderSucceeded
PublicationSucceeded
```

by the adapter.

The Application layer may decide whether a provenance failure causes stop, retry, defer, or escalation according to the applicable execution policy.

---

# 13. IDEMPOTENCY / DUPLICATE PROTECTION

The minimal port does not introduce a second publication-style idempotency system.

However, `execution_id` must be stable for one logical execution event so that the technical adapter can prevent accidental duplication where its storage contract requires it.

Provider records are associated with an execution reference rather than being used as an alternative execution identity.

The exact technical uniqueness constraint is an adapter/store concern and is not a new domain invariant.

---

# 14. DOMAIN AND LOCKED PROTECTION

The port has no authority to:

```text
create Domain entities
change Domain entities
close Experiments
promote Learning
rewrite Performance
classify causality
change experimental assignment
```

In particular:

```text
ExperimentClosureGate
        remains Domain authority

Performance append-only rule
        remains SQL/domain persistence authority

Information Model
        remains semantic authority
```

The provenance port records evidence about execution; it does not authorize the execution it records.

---

# 15. NO SQL V0.1 CHANGE

This specification does NOT require changes to:

```text
db/migrations/001_v0.1_foundation.sql
```

It does not add:

```text
execution_trace
provider_provenance
artifact_lineage
```

tables to the Logical Data Schema V0.1.

A future technical store may use a separate persistence mechanism, but its introduction must remain outside the semantic SQL model unless a future LOCKED contract explicitly changes that decision.

---

# 16. CONFORMANCE REQUIREMENTS

An implementation of `ProvenanceRepositoryPort V0.1` is conformant only if all of the following hold:

### PRP-01

All three operations exist with equivalent semantics:

```text
append_execution_trace
record_provider_provenance
record_artifact_lineage
```

### PRP-02

No operation mutates Domain state.

### PRP-03

No operation introduces a new domain entity.

### PRP-04

Provider substitutions remain observable.

### PRP-05

Artifact lineage records actual relationships only.

### PRP-06

Execution records remain technical provenance, not business decisions.

### PRP-07

The implementation exposes no SQL/ORM/provider SDK details through the Application port.

### PRP-08

No operation silently converts technical persistence failure into domain or provider success.

### PRP-09

No SQL V0.1 modification is required for conformance.

### PRP-10

The port cannot bypass or replace existing Domain Gates.

---

# 17. EXPLICIT NON-RESPONSIBILITIES

The port is NOT responsible for:

```text
Domain validation
Experiment assignment
Experiment closure
Cost authorization
Provider selection
Quality policy
Publication authorization
Performance interpretation
Learning promotion
Causal inference
```

Those responsibilities remain with their existing architectural authorities.

---

# 18. IMPLEMENTATION SEQUENCE

This specification authorizes the following next architectural sequence only:

```text
PROVENANCE REPOSITORY PORT V0.1
        ↓
PORT CONFORMANCE TESTS
        ↓
TECHNICAL PROVENANCE ADAPTER
        ↓
ADAPTER CONFORMANCE TEST
        ↓
PROVENANCE SERVICE
        ↓
POST-IMPLEMENTATION CONFORMANCE AUDIT
```

No step implies permission to modify the three LOCKED contracts or the V0.1 SQL schema.

---

# 19. FINAL CONTRACT VERDICT

The minimal persistence boundary for Provenance V0.1 is therefore:

```text
                    APPLICATION
                         │
                         ▼
             ProvenanceRepositoryPort
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
 append execution   record provider   record artifact
     trace            provenance        lineage
          │              │              │
          └──────────────┼──────────────┘
                         ▼
             TECHNICAL PROVENANCE STORE
```

The port is deliberately narrower than a generic repository abstraction.

Its authority is limited to **recording technical execution evidence**.

> **It records what happened; it does not decide what is allowed to happen.**

This is the final V0.1 persistence contract for the Provenance Application Service, subject to its own conformance check before implementation.
