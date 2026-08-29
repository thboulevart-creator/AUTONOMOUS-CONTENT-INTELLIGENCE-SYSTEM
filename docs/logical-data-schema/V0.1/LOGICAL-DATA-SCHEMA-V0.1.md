# Autonomous Content Intelligence System
## Logical Data Schema V0.1 — DRAFT FOR ADVERSARIAL AUDIT

**Version:** V0.1  
**Status:** DRAFT — NOT YET LOCKED  
**Semantic authority:** Information Model V0.1 — LOCKED  
**Purpose:** Define an implementation-neutral logical schema without changing the locked semantic model.

---

## 1. Scope and non-negotiable rule

This document translates the locked Information Model into implementable data structures: identifiers, attributes, references, cardinalities, enums and constraints.

It does **not** introduce new first-class semantic objects. A schema-level helper table may exist solely to implement an N:M relationship or provenance edge; such a table is not an Information Model object.

If implementation reveals a semantic ambiguity that cannot be resolved without changing the Information Model, the schema must stop and raise a version-change proposal.

---

## 2. Global conventions

### 2.1 Identifiers

Every first-class object has a globally unique `id` of type `UUID`.

### 2.2 Timestamps

All timestamps use timezone-aware `datetime` / ISO-8601 semantics and are stored in UTC.

Standard lifecycle fields:
- `created_at` — required;
- `updated_at` — required.

### 2.3 Optionality

`REQUIRED` means the field must be present for every instance of the object unless an explicit conditional invariant applies.
`OPTIONAL` means null/absence is permitted.

### 2.4 Versioning

Knowledge-bearing objects that are versioned carry an integer `version` starting at 1.

### 2.5 References

A reference field stores the UUID of another first-class object. Referential integrity must be enforceable.

For polymorphic references, the target type must be stored explicitly; an untyped UUID is forbidden.

---

## 3. Enumerations

### 3.1 LearningStatus

`active | saturated | deprecated | contested | rehabilitated`

### 3.2 ExperimentType

`controlled | exploratory`

### 3.3 EvidenceKind

`observation | measurement | external_signal | extracted_observation | other`

This enum describes the form of evidence, not its interpretation or truth value.

### 3.4 ContentStatus

`draft | ready | archived`

### 3.5 PublicationStatus

`scheduled | published | failed | removed`

### 3.6 DecisionType

`produce | amplify | stop | explore | allocate | test`

### 3.7 RelationType

`supporting | derived_from | annotates | constitutes | tests | instantiates | adapts | publishes | measures | updates | informs | targets | constrains | contradicts | supersedes`

Relation types are metadata on explicit relationship records where needed. They do not override the normative semantics of the corresponding relationship.

---

## 4. First-class object schemas

## 4.1 Evidence

**Required fields**

| Field | Type | Cardinality | Meaning |
|---|---|---:|---|
| `id` | UUID | 1 | Identity |
| `kind` | EvidenceKind | 1 | Observation form |
| `observed_at` | datetime | 1 | Time of observation |
| `source_ref` | string | 0..1 | External/internal provenance locator |
| `subject` | string | 1 | What was observed |
| `value` | JSON | 1 | Observed value/payload |
| `collection_context` | JSON | 0..1 | Collection conditions |
| `provenance` | JSON | 0..1 | Source/collection provenance |
| `created_at` | datetime | 1 | Record creation |
| `updated_at` | datetime | 1 | Record update |

**Invariant:** Evidence cannot itself encode a causal conclusion.

---

## 4.2 Trend (optional semantic object)

| Field | Type | Cardinality | Meaning |
|---|---|---:|---|
| `id` | UUID | 1 | Identity |
| `name` | string | 1 | Human-readable identity |
| `description` | text | 1 | Interpretation of the aggregation |
| `valid_from` | datetime | 0..1 | Relevance start |
| `valid_to` | datetime | 0..1 | Relevance end |
| `version` | integer | 1 | Version |
| `status` | string | 1 | Lifecycle state |
| `confidence` | decimal[0,1] | 0..1 | Confidence where applicable |
| `created_at` | datetime | 1 | Creation |
| `updated_at` | datetime | 1 | Update |

Trend instances are derived from linked Evidence; they do not require a mandatory upstream chain beyond the evidence actually available.

---

## 4.3 Mechanism

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `name` | string | 1 |
| `description` | text | 1 |
| `version` | integer | 1 |
| `confidence` | decimal[0,1] | 0..1 |
| `valid_from` | datetime | 0..1 |
| `valid_to` | datetime | 0..1 |
| `status` | string | 1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

A Mechanism is atomic relative to the system taxonomy.

---

## 4.4 Pattern

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `name` | string | 1 |
| `description` | text | 1 |
| `version` | integer | 1 |
| `confidence` | decimal[0,1] | 0..1 |
| `valid_from` | datetime | 0..1 |
| `valid_to` | datetime | 0..1 |
| `status` | string | 1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

---

## 4.5 Hypothesis

| Field | Type | Cardinality | Meaning |
|---|---|---:|---|
| `id` | UUID | 1 | Identity |
| `statement` | text | 1 | Falsifiable proposition |
| `intervention` | JSON | 1 | What is expected to change |
| `context` | JSON | 1 | Explicit contextual conditions; not a generic Context object |
| `expected_outcome` | JSON | 1 | Expected measurable outcome |
| `confidence` | decimal[0,1] | 0..1 | Current expectation/confidence |
| `valid_from` | datetime | 0..1 | Validity |
| `valid_to` | datetime | 0..1 | Validity |
| `version` | integer | 1 | Version |
| `status` | string | 1 | Lifecycle |
| `created_at` | datetime | 1 | Creation |
| `updated_at` | datetime | 1 | Update |

---

## 4.6 Experiment

| Field | Type | Cardinality | Meaning |
|---|---|---:|---|
| `id` | UUID | 1 | Identity |
| `type` | ExperimentType | 1 | Controlled or exploratory |
| `name` | string | 1 | Experiment name |
| `objective` | text | 1 | What is being tested |
| `baseline_ref` | TypedReference | 0..1* | Control/baseline |
| `intervention_refs` | TypedReference[] | 0..N* | Interventions |
| `design` | JSON | 1 | Arms, controls, duration, metrics and protocol |
| `started_at` | datetime | 0..1 | Start |
| `ended_at` | datetime | 0..1 | End |
| `created_at` | datetime | 1 | Creation |
| `updated_at` | datetime | 1 | Update |

`*` Conditional cardinalities are defined in Section 7.

`baseline_ref` and `intervention_refs` are references, not first-class objects.

---

## 4.7 Concept

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `title` | string | 1 |
| `description` | text | 1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

---

## 4.8 Variant

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `concept_ref` | UUID | 1 |
| `name` | string | 1 |
| `variation` | JSON | 1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

---

## 4.9 Content

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `title` | string | 1 |
| `artifact_ref` | string | 1 |
| `metadata` | JSON | 0..1 |
| `status` | ContentStatus | 1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

---

## 4.10 Platform Version

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `content_ref` | UUID | 1 |
| `platform_ref` | UUID | 1 |
| `adaptation` | JSON | 1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

---

## 4.11 Publication

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `platform_version_ref` | UUID | 1 |
| `account_ref` | UUID | 1 |
| `published_at` | datetime | 0..1 |
| `status` | PublicationStatus | 1 |
| `external_publication_ref` | string | 0..1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

Platform is derivable through Platform Version and must not be redundantly stored on Publication in V0.1.

---

## 4.12 Performance

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `publication_ref` | UUID | 1 |
| `observed_at` | datetime | 1 |
| `metrics` | JSON | 1 |
| `scores` | JSON | 0..1 |
| `measurement_window` | JSON | 0..1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

Metrics are extensible and multi-objective. Raw measurements and derived scores must remain distinguishable inside `metrics`/`scores`.

---

## 4.13 Learning

| Field | Type | Cardinality | Meaning |
|---|---|---:|---|
| `id` | UUID | 1 | Identity of the knowledge lineage |
| `claim` | text | 1 | Knowledge statement |
| `confidence` | decimal[0,1] | 1 | Current confidence |
| `status` | LearningStatus | 1 | Knowledge lifecycle |
| `version` | integer | 1 | Knowledge version |
| `valid_from` | datetime | 0..1 | Validity |
| `valid_to` | datetime | 0..1 | Validity |
| `conditions` | JSON | 0..1 | Platform/Audience/Account/time conditions |
| `provenance` | JSON | 1 | Evidence/Performance/Experiment/reasoning provenance |
| `created_at` | datetime | 1 | Creation |
| `updated_at` | datetime | 1 | Update |

Learning is the persisted knowledge claim; Analysis and Inference are not required as separate first-class rows.

---

## 4.14 Decision

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `type` | DecisionType | 1 |
| `rationale` | text | 1 |
| `selected_action` | JSON | 1 |
| `decided_at` | datetime | 1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

Decision records a choice, not execution.

---

## 4.15 Account

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `platform_ref` | UUID | 1 |
| `external_account_ref` | string | 0..1 |
| `name` | string | 1 |
| `constraints` | JSON | 0..1 |
| `history` | JSON | 0..1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

---

## 4.16 Audience

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `name` | string | 1 |
| `description` | text | 1 |
| `segments` | JSON | 0..1 |
| `behaviours` | JSON | 0..1 |
| `historical_responses` | JSON | 0..1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

---

## 4.17 Platform

| Field | Type | Cardinality |
|---|---|---:|
| `id` | UUID | 1 |
| `name` | string | 1 |
| `rules` | JSON | 0..1 |
| `formats` | JSON | 0..1 |
| `distribution_characteristics` | JSON | 0..1 |
| `created_at` | datetime | 1 |
| `updated_at` | datetime | 1 |

---

## 5. Relationship implementation

Every normative N:M relationship is implemented as a relationship table/collection with:

- `id` UUID;
- `source_ref` typed reference;
- `target_ref` typed reference;
- `relationship_type` where needed;
- `created_at`;
- optional `metadata`.

Relationship records are implementation structures, not additional semantic objects.

### Required relationship sets

- Evidence ↔ Learning
- Evidence ↔ Trend
- Trend ↔ Hypothesis
- Trend ↔ Mechanism
- Content ↔ Mechanism
- Content ↔ Pattern
- Mechanism ↔ Pattern
- Pattern ↔ Hypothesis
- Hypothesis ↔ Experiment
- Experiment ↔ Variant/Content
- Experiment ↔ Performance
- Concept → Variant
- Variant → Content
- Content → Platform Version
- Platform Version → Platform
- Platform Version → Publication
- Publication → Account
- Publication → Performance
- Performance ↔ Learning
- Learning ↔ Mechanism/Pattern/Hypothesis/Audience/Account/Decision
- Decision ↔ Experiment/Concept
- Audience ↔ Concept/Hypothesis

Where the Information Model defines an N:1 relationship, a direct foreign key is preferred over a relationship table.

---

## 6. Direct foreign-key rules

The following are direct references:

- `variant.concept_ref → concept.id`
- `platform_version.content_ref → content.id`
- `platform_version.platform_ref → platform.id`
- `publication.platform_version_ref → platform_version.id`
- `publication.account_ref → account.id`
- `performance.publication_ref → publication.id`
- `account.platform_ref → platform.id`

These references are mandatory and enforce referential integrity.

---

## 7. Conditional experiment invariants

### EXP-01 — Controlled baseline

If `experiment.type = controlled`, then:

- `baseline_ref` MUST be present;
- `intervention_refs` MUST contain at least one reference;
- baseline and intervention references MUST identify distinct experimental arms;
- every arm MUST be traceable to a Variant or Content;
- the design MUST identify the target outcome/metrics.

### EXP-02 — Exploratory experiment

If `experiment.type = exploratory`, absence of a baseline is permitted, but this absence must be explicit and must not be interpreted as evidence of causal effect.

### EXP-03 — Experiment result traceability

Every Performance claimed as an Experiment result MUST be traceable to the Experiment either directly or through a Publication belonging to one of its experimental arms.

### EXP-04 — No invented provenance

An Experiment must not acquire an artificial Concept/Hypothesis ancestry solely to satisfy schema constraints.

---

## 8. Learning invariants

### LEARN-01

`confidence` is numeric in [0,1].

### LEARN-02

`status` must be one of the locked lifecycle values.

### LEARN-03

A Learning with `status = contested` MUST have provenance identifying the competing/contradictory evidence or Learning where available.

### LEARN-04

A Learning with `status = rehabilitated` MUST preserve provenance to the earlier state/version and the reason for rehabilitation.

### LEARN-05

Learning cannot state causal certainty solely because it references an Experiment. Its claim must remain supported by provenance and confidence.

### LEARN-06

A newer Learning version must not silently erase the provenance of the previous version.

---

## 9. Temporal invariants

- `valid_from <= valid_to` when both exist.
- `started_at <= ended_at` when both exist.
- `observed_at` cannot be later than `created_at` by default unless the implementation explicitly supports delayed/backfilled observations; if supported, this exception must be represented rather than treated as an error.
- Version numbers within a knowledge lineage are positive integers and monotonically increasing.

---

## 10. Context conditioning

No generic `context` entity exists.

Contextual conditions are represented through explicit references where they correspond to first-class objects:

- Platform → `platform_ref`
- Account → `account_ref`
- Audience → relationship/reference
- Time → timestamps and validity windows

Other context dimensions may be stored as structured attributes (`JSON`) without becoming first-class semantic objects.

A schema implementation must not create a generic Context table merely for convenience.

---

## 11. Causality invariants

1. Evidence and Performance are observations.
2. Statistical association must be represented as an interpretation/provenance, not rewritten as observed fact.
3. Learning claims must preserve provenance and confidence.
4. Experiment existence does not automatically imply causal truth.
5. Cross-platform performance must not be aggregated as though Platform were irrelevant.

---

## 12. Minimality check

No new first-class Information Model object is introduced by this schema.

Schema-only structures allowed:
- relationship/junction tables;
- typed-reference wrappers;
- JSON payloads for extensible metrics, contextual dimensions and experimental design.

This is intentional: V0.1 prioritizes semantic fidelity and implementability over premature normalization.

---

## 13. Open implementation questions for adversarial audit

The following are deliberately exposed for audit rather than silently resolved:

1. Whether `Learning.id + version` adequately represents knowledge lineage or requires a separate immutable lineage key.
2. Whether polymorphic `baseline_ref` / `intervention_refs` are sufficiently type-safe without a dedicated Arm structure.
3. Whether `Performance → Learning` provenance is sufficiently represented by JSON or requires normalized relationship records.
4. Whether `Experiment → Performance` should be direct, publication-derived, or both.
5. Whether `Trend.status`, `Mechanism.status`, `Pattern.status` need controlled enums or may remain implementation-defined.
6. Whether `Hypothesis.context` as JSON is sufficiently explicit to support queryable Platform/Audience/Time conditions.
7. Whether `Performance.metrics` JSON is sufficiently queryable for multi-objective scoring.
8. Whether `source_ref`, `artifact_ref` and external references require normalized source/resource structures.
9. Whether Account → Platform and Platform Version → Platform are sufficient to prevent invalid cross-platform publication paths.
10. Whether all N:M edges require explicit relationship types or whether the normative relationship itself is enough.

These are schema questions, not automatic changes to the Information Model.

---

## 14. Audit gate

This document is **NOT LOCKED**.

Before it can become Logical Data Schema V0.1 — LOCKED, it must pass:

1. internal consistency review;
2. adversarial review by an independent model (Grok);
3. reconciliation of findings;
4. explicit decision on every blocking issue;
5. confirmation that no semantic change has been introduced into Information Model V0.1.
