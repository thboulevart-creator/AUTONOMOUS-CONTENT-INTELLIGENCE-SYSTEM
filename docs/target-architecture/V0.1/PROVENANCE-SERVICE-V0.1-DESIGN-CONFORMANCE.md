# PROVENANCE SERVICE V0.1 — DESIGN / CONFORMANCE SPECIFICATION

**Project:** Autonomous Content Intelligence System  
**Version:** V0.1  
**Status:** PRE-IMPLEMENTATION — DESIGN CONTRACT  
**Scope:** Application orchestration boundary for technical provenance

## 1. Purpose

Define the smallest Application Service boundary that exposes technical provenance persistence through the already LOCKED `ProvenanceRepositoryPort V0.1`.

The service is deliberately thin:

```text
Application workflow
       ↓
ProvenanceService
       ↓
ProvenanceRepositoryPort
       ↓
ProvenanceRepository
       ↓
technical_provenance
```

It records technical execution evidence through the port. It does not decide what the system is allowed to do.

## 2. Authority

This design is subordinate to:

1. Information Model V0.1 — LOCKED
2. Operational Specification V0.1 — LOCKED
3. Logical Data Schema V0.1 — LOCKED
4. Existing Domain implementation and gates
5. `PROVENANCE-REPOSITORY-PORT-V0.1.md` — LOCKED
6. `TECHNICAL-PROVENANCE-STORE-CONTRACT-V0.1.md`
7. Application Interface Specification V0.1

Any contradiction with a higher authority blocks implementation.

## 3. Exact service surface

V0.1 exposes exactly the three already-authorized provenance operations:

```text
record_execution_trace(event) → TraceReference
record_provider_provenance(execution_reference, provider_metadata)
    → ProviderProvenanceReference
link_artifact_lineage(parent_reference, child_reference, relationship)
    → LineageReference
```

No V0.1 query, update, delete, provider-selection, authorization, or policy method is introduced.

## 4. Delegation rule

Each operation MUST delegate to the corresponding `ProvenanceRepositoryPort` operation without changing its technical meaning.

```text
service.record_execution_trace(event)
    → port.record_execution_trace(event)

service.record_provider_provenance(execution_reference, metadata)
    → port.record_provider_provenance(execution_reference, metadata)

service.link_artifact_lineage(parent, child, relationship)
    → port.link_artifact_lineage(parent, child, relationship)
```

The service returns the technical reference/result supplied by the port.

The service MUST NOT directly call the concrete adapter, SQL, PostgreSQL, ORM, provider SDK, or platform SDK.

## 5. Technical input semantics

### Execution trace

The event follows the Technical Store Contract and supports at minimum:

```text
execution_id
operation_type
timestamp/occurred_at
input_references
output_references
execution_status
```

The service MUST NOT fabricate references, causality, execution outcomes, or Domain state.

### Provider provenance

The metadata supports the Technical Store Contract fields including:

```text
provider
model
model_version
request_parameters
input_reference
output_reference
execution_status
```

and, when available:

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

The service passes provider metadata through. It does not select providers or rewrite fallback information.

### Artifact lineage

Only actual relationships supplied by the caller are recorded:

```text
parent_reference
child_reference
relationship
```

The service MUST NOT infer or complete missing ancestry.

## 6. Domain boundary

The Provenance Service is an Application service, not a Domain authority.

It MUST NOT:

- create, update, or delete Domain entities;
- change Domain status;
- close Experiments;
- promote Learning;
- rewrite Performance;
- alter experimental assignment;
- authorize publication;
- infer causality;
- implement or duplicate Domain Gates;
- turn technical provenance into a semantic Domain relationship.

Existing Domain authorities remain unchanged.

## 7. Provider and experiment boundaries

Provider identity remains technical.

The service MUST NOT select, substitute, authorize, or invoke providers. Provider execution occurs outside this service.

The service MUST NOT assign treatment, modify Experiment Arms, decide baseline/intervention, or determine causal validity.

A provider fallback may be recorded as technical provenance when supplied by the caller, but it MUST NOT silently change experimental treatment.

## 8. Failure boundary

Technical persistence failures remain technical failures.

The service MUST preserve the distinction between:

```text
ProvenancePersistenceFailure
InvalidProvenanceRecord
```

and Domain/provider/platform outcomes.

It MUST NOT translate a provenance failure into `DomainRejected`, `ProviderSucceeded`, `PublicationSucceeded`, or another unrelated result.

It MUST NOT silently swallow a persistence failure.

## 9. Append-only and idempotency boundary

The service exposes no update or delete operation.

It does not create a second idempotency mechanism. Duplicate handling remains owned by the validated Technical Store/adapter contract.

In particular:

- stable `execution_id` remains a technical concern;
- lineage uniqueness/idempotency remains a technical concern;
- no publication-style intent key is introduced;
- technical duplicate handling is not promoted to a Domain invariant.

## 10. Transaction boundary

The service does not claim distributed atomicity between:

```text
Domain persistence
External provider
Technical provenance store
```

If several provenance records are emitted for one workflow, the service may delegate them in the actual execution order, but it MUST NOT invent transaction guarantees absent from the port/store contracts.

## 11. Query boundary

V0.1 exposes no provenance query/read model.

The service MUST NOT become a hidden read authority for Domain decisions.

Any future provenance query capability requires a new contract and conformance review.

## 12. Conformance requirements

### PSV-01 — Port-only persistence dependency

The service depends on `ProvenanceRepositoryPort`, not the concrete repository.

### PSV-02 — Exact surface

Exactly the three authorized operations are exposed. No V0.1 query/update/delete expansion exists.

### PSV-03 — Pure delegation

Arguments retain equivalent technical meaning and returned references are propagated.

### PSV-04 — No Domain mutation

The service has no Domain persistence authority and produces no Domain state mutation.

### PSV-05 — No Gate duplication

No Domain Gate logic is implemented or reproduced.

### PSV-06 — No provider authority

No provider selection, fallback policy, provider SDK call, or provider business rule exists in the service.

### PSV-07 — Actual lineage only

The service never fabricates ancestry or lineage edges.

### PSV-08 — Provider transparency

Intended-versus-actual provider information is preserved when supplied.

### PSV-09 — Failure isolation

Technical persistence failures remain technically identifiable.

### PSV-10 — No infrastructure leakage

No SQL, database connection, ORM model, technical schema object, provider SDK, or platform SDK crosses the service boundary.

### PSV-11 — No shadow model

The service defines no alternative Domain entity, lifecycle, policy, or semantic authority.

### PSV-12 — No query authority

No V0.1 business query API is exposed.

### PSV-13 — Append-only boundary

No generic update/delete path is exposed.

### PSV-14 — Transaction honesty

No unsupported distributed transaction guarantee is claimed.

### PSV-15 — LOCKED protection

The Information Model, Operational Specification, and LDS remain untouched and semantically unchanged.

## 13. Required conformance tests before implementation acceptance

1. Fake port receives exactly one corresponding call per service operation.
2. Arguments are passed without semantic rewriting.
3. Returned technical references are propagated unchanged.
4. Port persistence failures remain identifiable.
5. No direct concrete-adapter dependency exists in the service.
6. No SQL/database/provider/platform dependency exists in the service.
7. No Domain repository or Domain mutation is invoked.
8. No Domain Gate logic is duplicated.
9. Provider metadata is passed through unchanged.
10. Lineage inputs are passed through unchanged; no ancestry is synthesized.
11. No query/update/delete surface exists.
12. Real adapter can be injected through the Application composition boundary.
13. End-to-end service calls reach the already validated Technical Store.
14. Domain table state remains unchanged during provenance service execution.

The service tests are distinct from adapter PostgreSQL conformance tests.

## 14. Implementation gate

Implementation is authorized only if this design remains conformant with:

```text
3 LOCKED contracts
      ↓
ProvenanceRepositoryPort V0.1
      ↓
Technical Provenance Store Contract V0.1
      ↓
real repository surface
      ↓
validated PostgreSQL adapter
```

If a contradiction appears, implementation stops and the smallest conflicting element is corrected before code is written.

## 15. Final design decision

```text
Application workflow
       ↓
ProvenanceService
       ↓
ProvenanceRepositoryPort
       ↓
validated ProvenanceRepository
       ↓
technical_provenance
```

The Provenance Service is a thin Application façade over the locked persistence port. It records technical evidence and has no authority over Domain semantics, policy, experiment assignment, provider selection, publication authorization, or causality.
