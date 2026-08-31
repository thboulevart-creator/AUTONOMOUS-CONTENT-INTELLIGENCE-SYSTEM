# TECHNICAL PROVENANCE STORE DESIGN / ADAPTER CONFORMANCE SPECIFICATION V0.1

**Project:** Autonomous Content Intelligence System  
**Version:** V0.1  
**Status:** ARCHITECTURAL IMPLEMENTATION CONTRACT — NON-LOCKED  
**Scope:** Technical Provenance Store + Adapter boundary  
**Implementation:** NOT AUTHORIZED BY THIS DOCUMENT ALONE

---

## 1. Purpose

This document converts the accepted `TECHNICAL PROVENANCE STORE CONTRACT V0.1` into an implementation-facing design and conformance boundary.

It answers:

> How may the future Provenance Adapter satisfy the locked `ProvenanceRepositoryPort V0.1` without modifying the Domain, the three LOCKED contracts, or the V0.1 LDS SQL surface?

Required dependency direction:

```text
Application Provenance Service
          ↓
ProvenanceRepositoryPort V0.1
          ↓
Technical Provenance Adapter
          ↓
Technical Provenance Store
```

No business logic is introduced by this document.

---

## 2. Authority

Precedence is:

1. Information Model V0.1 — LOCKED
2. Operational Specification V0.1 — LOCKED
3. Logical Data Schema V0.1 — LOCKED
4. Existing Domain implementation and gates
5. `ProvenanceRepositoryPort V0.1` — LOCKED
6. `TECHNICAL PROVENANCE STORE CONTRACT V0.1`
7. This document

If this document conflicts with a higher authority, this document is wrong and must be corrected before implementation.

---

## 3. Repository reality checked

The current repository was inspected before defining this boundary.

### Application

`src/application/ports.py` currently exposes the locked three-method `ProvenanceRepositoryPort`:

```text
record_execution_trace(event)
record_provider_provenance(execution_reference, provider_metadata)
link_artifact_lineage(parent_reference, child_reference, relationship)
```

`src/application/provenance.py` contains structural protocol stubs for the three technical concerns. They do not replace the persistence port.

### Persistence

`src/persistence/repositories/` contains domain repositories, including Decision, Evidence, Experiment, Learning, Performance and Publication repositories. No provenance-specific repository or adapter exists.

### SQL

`db/migrations/001_v0.1_foundation.sql` contains the V0.1 LDS/domain foundation. No dedicated `ExecutionTrace`, `ProviderProvenance`, or `ArtifactLineage` tables exist.

Therefore the adapter cannot legitimately satisfy the port by repurposing an existing LDS table whose semantics differ from technical provenance.

---

## 4. Design decision

The adapter targets a **separate technical provenance store outside the V0.1 Logical Data Schema**.

It MUST NOT implement technical provenance by overloading:

```text
learning_provenance
learning_status_history
decision
content / platform_version / publication
experiment / experiment_arm
typed domain junctions
```

These remain authoritative for their existing meanings.

No change is authorized or required to:

```text
docs/information-model/V0.1/
docs/operational-specification/V0.1/
docs/data-schema/V0.1/
db/migrations/001_v0.1_foundation.sql
src/domain/
existing domain repositories
```

---

## 5. Adapter responsibility

The adapter is an infrastructure implementation of the locked Application port.

It is responsible for:

- accepting the three port operations;
- validating technical record shape required by the Technical Store Contract;
- persisting technical records;
- returning technical references;
- preserving append-only evidence;
- preserving provider substitution visibility;
- preserving actual artifact lineage;
- isolating technical persistence failures.

It is NOT responsible for:

- Domain validation or gate evaluation;
- Experiment assignment or closure;
- Learning promotion;
- Publication authorization;
- Provider selection;
- policy decisions;
- causal inference;
- Domain state mutation.

---

## 6. Adapter placement

The adapter belongs below the Application port and outside the Domain.

A future implementation may use a location such as:

```text
src/persistence/adapters/provenance.py
```

or an equivalent infrastructure location. The exact path is implementation freedom.

The dependency direction MUST remain:

```text
Application → Port → Adapter → Technical Store
```

Domain code MUST NOT import adapter or Technical Store types.

---

## 7. Port-to-store mapping

The mapping is strictly one-to-one.

| Locked port operation | Adapter responsibility | Technical surface | Result |
|---|---|---|---|
| `record_execution_trace(event)` | validate + persist event | execution trace record | `TraceReference` |
| `record_provider_provenance(execution_reference, provider_metadata)` | validate + persist provider record | provider provenance record | `ProviderProvenanceReference` |
| `link_artifact_lineage(parent_reference, child_reference, relationship)` | validate + persist actual edge | lineage record | `LineageReference` |

No fourth Application persistence operation is introduced.

---

## 8. Execution trace mapping

The adapter MUST preserve at minimum:

```text
execution_id
operation_type
timestamp
input_references
output_references
execution_status
```

Additional metadata is permitted only when it remains technical and reconstructive.

Execution status is descriptive technical metadata. It MUST NOT become Experiment, Learning, Publication or other Domain status and MUST NOT establish causality.

---

## 9. Provider provenance mapping

The adapter MUST preserve at minimum:

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

Where available it MAY preserve:

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

When fallback occurs, intended and actual provider MUST remain distinguishable.

The adapter MUST NOT create a Provider domain entity, select experimental treatment, authorize publication, alter policy, or make provider identity normative.

---

## 10. Artifact lineage mapping

The adapter MUST persist only supplied/observed technical relationships:

```text
parent_reference
child_reference
relationship
```

Examples:

```text
input → generated
source → transformed
intermediate → assembled
artifact → final_artifact
```

It MUST NOT fabricate ancestry.

Typed Domain relationships remain authoritative, including:

```text
Content → Platform Version → Publication → Performance
Experiment → Experiment Arm → Content / Variant
Learning → provenance sources
```

Technical lineage may reference these objects but never replaces their typed relationships.

---

## 11. Reference boundary

Technical records may contain opaque identifiers for existing Domain objects, including:

```text
Evidence, Experiment, Variant, Content, Platform Version,
Publication, Performance, Learning, Decision
```

References:

- identify existing objects;
- do not create them;
- do not duplicate their semantic payload;
- do not create new normative relationships;
- do not transfer lifecycle ownership to the Technical Store.

Forbidden:

```text
Domain object → copied semantic object → second source of truth
```

Allowed:

```text
Domain object ID → opaque technical reference
```

---

## 12. Technical store physical boundary

The Technical Store MUST remain physically and semantically distinguishable from the V0.1 LDS.

It MAY use a separate database, database schema, technical tables, filesystem/object store, or equivalent mechanism, provided it remains outside the semantic LDS.

This document does not prescribe PostgreSQL, ORM, table names, indexes, partitioning, or migration tooling.

A physical implementation MUST NOT silently modify the V0.1 domain SQL.

---

## 13. Append-only rule

The adapter exposes no generic update/delete operation through the V0.1 port.

Historical technical evidence MUST NOT be silently rewritten.

Future correction semantics require a separate contract before addition.

This rule does not create a technical lifecycle machine.

---

## 14. Failure isolation

The adapter MUST preserve the distinction between:

```text
ProvenancePersistenceFailure
InvalidProvenanceRecord
```

and Domain/provider outcomes.

It MUST NOT translate technical persistence failure into:

```text
DomainRejected
ExperimentInvalid
ProviderSucceeded
PublicationSucceeded
```

The Application layer may later decide whether a technical failure is fatal, retryable, deferred or escalated.

---

## 15. Idempotency boundary

`execution_id` is the stable technical identity of one logical execution event.

The Technical Store MAY enforce uniqueness for that identifier.

The adapter MUST NOT create a competing execution identity or publication-style idempotency model.

---

## 16. Query boundary

V0.1 exposes no business query API over the Technical Store.

The adapter MUST NOT become an alternative source of truth for:

```text
Domain status
Experiment validity
Learning status
Publication state
causal conclusions
```

Any future query requirement requires a new explicit contract and conformance review.

---

## 17. Dependency restrictions

### Adapter may depend on

```text
ProvenanceRepositoryPort
Technical Store implementation
technical serialization/persistence infrastructure
technical error definitions
```

### Domain must not depend on

```text
Technical Store
Provenance Adapter
technical provenance record types
technical store schema
```

Provider/platform SDK details are not exposed through the Application persistence port.

---

## 18. Adapter conformance matrix

| ID | Requirement | Pass condition |
|---|---|---|
| ADP-01 | Port surface | All 3 locked methods exist with equivalent semantics |
| ADP-02 | No port expansion | No fourth provenance persistence method |
| ADP-03 | Technical-only storage | Records remain implementation provenance |
| ADP-04 | Domain isolation | Adapter cannot mutate Domain state |
| ADP-05 | No semantic entities | No Provider/Trace/Lineage Domain entity introduced |
| ADP-06 | No LDS mutation | V0.1 LDS and foundation SQL unchanged |
| ADP-07 | No semantic repurposing | Existing domain tables retain their meaning |
| ADP-08 | Execution integrity | Required execution fields survive persistence |
| ADP-09 | Provider transparency | Intended/actual provider distinction survives fallback |
| ADP-10 | Actual lineage | Only supplied/observed lineage edges persist |
| ADP-11 | Reference opacity | Domain payloads are not duplicated |
| ADP-12 | Append-only | Existing technical evidence is not silently rewritten/deleted |
| ADP-13 | Failure isolation | Technical failures remain distinguishable |
| ADP-14 | No business query authority | No V0.1 business-query API |
| ADP-15 | Stable execution identity | `execution_id` remains stable per logical event |
| ADP-16 | No Domain lifecycle | Technical status cannot change Domain status |
| ADP-17 | No gate bypass | Adapter cannot replace/bypass Domain Gates |
| ADP-18 | No causal inference | Adapter records facts only |
| ADP-19 | Technical boundary | Store remains outside LDS semantic authority |
| ADP-20 | Traceability | Each adapter operation maps to the locked port and store contract |

---

## 19. Required tests before implementation acceptance

At minimum:

- **CT-01 Surface:** adapter satisfies the exact three-method port.
- **CT-02 Execution:** valid execution record persists without Domain mutation.
- **CT-03 Validation:** missing required execution information is rejected as invalid technical input.
- **CT-04 Provider:** provider metadata persists against the supplied execution reference.
- **CT-05 Fallback:** intended/actual provider and fallback reason remain observable when supplied.
- **CT-06 Lineage:** supplied actual parent/child edge persists.
- **CT-07 No fabrication:** adapter never invents additional lineage.
- **CT-08 Domain isolation:** no Domain entity/status/gate/policy mutation.
- **CT-09 Existing-table protection:** no repurposing of LDS provenance/lifecycle tables.
- **CT-10 Append-only:** no generic update/delete through the port and no silent history rewrite.
- **CT-11 Failure isolation:** persistence failure remains technical.
- **CT-12 Reference opacity:** Domain identifiers may be referenced without semantic copies.
- **CT-13 Query boundary:** no business-query authority exists.
- **CT-14 SQL preservation:** implementation does not require modification of V0.1 LDS migration.

---

## 20. Adversarial pre-implementation checks

The following attacks MUST be rejected:

1. **Existing-table shortcut:** technical provenance in `learning_provenance`.
2. **Status shortcut:** execution status written as Learning/Experiment/Publication status.
3. **Provider entity invention:** new Provider Domain entity.
4. **Lineage inflation:** Content/Variant records created only for technical intermediates.
5. **Shadow model:** Technical Store becomes authoritative through business queries.
6. **Silent fallback:** Provider B recorded while Provider A substitution disappears.
7. **Fabricated ancestry:** missing parent inferred from expected workflow.
8. **Gate bypass:** provenance treated as authorization for a Domain operation.
9. **Failure laundering:** technical persistence failure reported as Domain/provider success.
10. **Port expansion:** read/update/delete/domain-transition methods added to V0.1 provenance port.

---

## 21. Non-goals

This specification does NOT define:

- concrete SQL tables or migrations;
- ORM models;
- Provenance Service logic;
- provider integration;
- publication integration;
- experiment lifecycle;
- new Domain gates;
- new Information Model entities;
- a technical status machine;
- a business analytics/query layer.

---

## 22. Implementation gate

This document does **not** authorize implementation by itself.

Required sequence:

```text
Technical Provenance Store Contract V0.1
        ↓
THIS DESIGN / CONFORMANCE SPECIFICATION
        ↓
PRE-IMPLEMENTATION CONFORMANCE CHECK
        ↓
[PASS]
        ↓
ADAPTER IMPLEMENTATION
        ↓
ADAPTER CONFORMANCE TESTS
        ↓
POST-IMPLEMENTATION AUDIT
```

If a contradiction with a higher authority appears, implementation stops.

---

## 23. Final design verdict

The current repository supports this clean boundary:

```text
                 APPLICATION
                     │
                     ▼
        ProvenanceRepositoryPort V0.1
                     │
                     ▼
          Technical Provenance Adapter
                     │
                     ▼
          Technical Provenance Store

        X no Domain mutation
        X no LDS modification
        X no semantic entity invention
        X no business query authority
        X no fabricated lineage
        X no hidden provider substitution
```

**DESIGN VERDICT: CONFORMANT / IMPLEMENTATION-READY IN PRINCIPLE, subject to the pre-implementation and adapter conformance tests above.**

> The adapter records technical evidence; it does not become an authority over semantic state.
