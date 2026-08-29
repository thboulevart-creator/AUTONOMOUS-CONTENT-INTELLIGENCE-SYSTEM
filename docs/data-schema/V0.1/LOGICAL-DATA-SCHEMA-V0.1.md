# Autonomous Content Intelligence System
## Logical Data Schema V0.1 — AUDIT CANDIDATE

**Status:** AUDIT CANDIDATE — NOT LOCKED  
**Version:** V0.1  
**Semantic contract:** Information Model V0.1 — LOCKED  
**Purpose:** Concrete logical representation of the locked Information Model, independent of a final database engine.

---

## 1. Schema rules

1. UUID is the canonical primary-key type for first-class entities.
2. Every first-class entity has `id`, `created_at`, and where relevant `updated_at`.
3. Foreign keys are explicit; N:M relationships use explicit junction tables.
4. No generic polymorphic foreign key is permitted where a typed alternative can be represented with a discriminator + constrained nullable FKs.
5. Soft deletion is used for provenance-bearing entities; destructive cascade deletion is forbidden for knowledge, evidence, experiment, publication, performance and learning records.
6. Timestamps are stored as timezone-aware timestamps.
7. JSON is permitted for payloads whose internal structure is intentionally extensible, but normative identifiers and relationships are relational and queryable.
8. The schema does not encode causality automatically.

---

## 2. Core entities

### 2.1 evidence
- `id UUID PK`
- `source_type TEXT NOT NULL`
- `source_ref TEXT NULL`
- `raw_payload JSONB NOT NULL`
- `observed_at TIMESTAMPTZ NOT NULL`
- `collected_at TIMESTAMPTZ NULL`
- `collection_context JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

Evidence is observation/provenance, not interpretation.

### 2.2 trend
Optional persisted derived object.
- `id UUID PK`
- `definition JSONB NOT NULL`
- `valid_from TIMESTAMPTZ NULL`
- `valid_until TIMESTAMPTZ NULL`
- `status TEXT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

Trend may also be implemented later as a derived view without changing the Information Model.

### 2.3 platform
- `id UUID PK`
- `name TEXT NOT NULL UNIQUE`
- `rules JSONB NULL`
- `format_capabilities JSONB NULL`
- `distribution_characteristics JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.4 account
- `id UUID PK`
- `platform_id UUID NOT NULL FK -> platform.id`
- `external_account_ref TEXT NULL`
- `name TEXT NOT NULL`
- `constraints JSONB NULL`
- `operating_history JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.5 audience
- `id UUID PK`
- `name TEXT NOT NULL`
- `segments JSONB NULL`
- `behaviours JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.6 mechanism
- `id UUID PK`
- `name TEXT NOT NULL`
- `description TEXT NOT NULL`
- `status TEXT NOT NULL`
- `confidence NUMERIC(5,4) NULL`
- `valid_from TIMESTAMPTZ NULL`
- `valid_until TIMESTAMPTZ NULL`
- `version INTEGER NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.7 pattern
- `id UUID PK`
- `name TEXT NOT NULL`
- `description TEXT NOT NULL`
- `status TEXT NOT NULL`
- `confidence NUMERIC(5,4) NULL`
- `valid_from TIMESTAMPTZ NULL`
- `valid_until TIMESTAMPTZ NULL`
- `version INTEGER NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.8 hypothesis
- `id UUID PK`
- `statement TEXT NOT NULL`
- `expected_outcome JSONB NULL`
- `status TEXT NOT NULL`
- `confidence NUMERIC(5,4) NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.9 concept
- `id UUID PK`
- `title TEXT NOT NULL`
- `description TEXT NULL`
- `origin_type TEXT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.10 variant
- `id UUID PK`
- `concept_id UUID NOT NULL FK -> concept.id`
- `name TEXT NOT NULL`
- `variation_definition JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.11 content
- `id UUID PK`
- `concept_id UUID NULL FK -> concept.id`
- `variant_id UUID NULL FK -> variant.id`
- `artifact_ref TEXT NOT NULL`
- `content_metadata JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

Constraint: if `variant_id` is non-null, its `concept_id` must equal `content.concept_id` when `concept_id` is present. Content may exist without Concept/Variant for exploration.

### 2.12 platform_version
- `id UUID PK`
- `content_id UUID NOT NULL FK -> content.id`
- `platform_id UUID NOT NULL FK -> platform.id`
- `adaptation_payload JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.13 publication
- `id UUID PK`
- `platform_version_id UUID NOT NULL FK -> platform_version.id`
- `account_id UUID NOT NULL FK -> account.id`
- `external_publication_ref TEXT NULL`
- `published_at TIMESTAMPTZ NOT NULL`
- `publication_metadata JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

Constraint: publication.account_id.platform_id must equal platform_version.platform_id.

### 2.14 performance
Performance is append-only at snapshot level.
- `id UUID PK`
- `publication_id UUID NOT NULL FK -> publication.id`
- `observed_at TIMESTAMPTZ NOT NULL`
- `metrics JSONB NOT NULL`
- `scores JSONB NULL`
- `measurement_window JSONB NULL`
- `source_ref TEXT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

Invariant: existing Performance rows are never overwritten to represent a later observation. New observations create new rows.

### 2.15 experiment
- `id UUID PK`
- `experiment_type TEXT NOT NULL` (`controlled` | `exploratory`)
- `status TEXT NOT NULL`
- `design JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

Baseline and interventions are represented through typed experiment arms, not a polymorphic FK.

### 2.16 experiment_arm
- `id UUID PK`
- `experiment_id UUID NOT NULL FK -> experiment.id`
- `arm_type TEXT NOT NULL` (`baseline` | `intervention`)
- `variant_id UUID NULL FK -> variant.id`
- `content_id UUID NULL FK -> content.id`
- `label TEXT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

Constraints:
- exactly one of `variant_id` or `content_id` must be non-null;
- each controlled Experiment has exactly one baseline arm;
- each controlled Experiment has at least one intervention arm;
- exploratory Experiments may have zero baseline arms;
- an arm cannot simultaneously be baseline and intervention.

### 2.17 learning
- `id UUID PK`
- `claim TEXT NOT NULL`
- `status TEXT NOT NULL` (`active` | `saturated` | `deprecated` | `contested` | `rehabilitated`)
- `confidence NUMERIC(5,4) NULL`
- `valid_from TIMESTAMPTZ NULL`
- `valid_until TIMESTAMPTZ NULL`
- `version INTEGER NOT NULL`
- `conditions JSONB NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

### 2.18 learning_provenance
Structured provenance for Learning.
- `id UUID PK`
- `learning_id UUID NOT NULL FK -> learning.id`
- `source_type TEXT NOT NULL` (`evidence` | `performance` | `experiment` | `hypothesis` | `mechanism` | `pattern` | `trend` | `learning`)
- `source_id UUID NOT NULL`
- `role TEXT NULL`
- `created_at TIMESTAMPTZ NOT NULL`

`source_type + source_id` is a typed logical reference. Application/service validation must ensure the referenced record exists in the declared source table; a database-native FK cannot be used across heterogeneous tables without introducing separate junction tables.

### 2.19 learning_status_history
- `id UUID PK`
- `learning_id UUID NOT NULL FK -> learning.id`
- `from_status TEXT NULL`
- `to_status TEXT NOT NULL`
- `changed_at TIMESTAMPTZ NOT NULL`
- `reason TEXT NULL`

### 2.20 decision
- `id UUID PK`
- `decision_type TEXT NOT NULL`
- `rationale TEXT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`
- `deleted_at TIMESTAMPTZ NULL`

---

## 3. Junction tables / relations

### evidence_learning
- `evidence_id UUID FK -> evidence.id`
- `learning_id UUID FK -> learning.id`
- PK (`evidence_id`, `learning_id`)

### evidence_trend
- `evidence_id UUID FK -> evidence.id`
- `trend_id UUID FK -> trend.id`
- PK (`evidence_id`, `trend_id`)

### trend_hypothesis
- `trend_id UUID FK -> trend.id`
- `hypothesis_id UUID FK -> hypothesis.id`
- PK (`trend_id`, `hypothesis_id`)

### trend_mechanism
- `trend_id UUID FK -> trend.id`
- `mechanism_id UUID FK -> mechanism.id`
- PK (`trend_id`, `mechanism_id`)

### content_mechanism
- `content_id UUID FK -> content.id`
- `mechanism_id UUID FK -> mechanism.id`
- `relation_type TEXT NOT NULL` (`applied` | `extracted`)
- PK (`content_id`, `mechanism_id`, `relation_type`)

### content_pattern
- `content_id UUID FK -> content.id`
- `pattern_id UUID FK -> pattern.id`
- `relation_type TEXT NOT NULL` (`applied` | `extracted`)
- PK (`content_id`, `pattern_id`, `relation_type`)

### mechanism_pattern
- `mechanism_id UUID FK -> mechanism.id`
- `pattern_id UUID FK -> pattern.id`
- PK (`mechanism_id`, `pattern_id`)

### pattern_hypothesis
- `pattern_id UUID FK -> pattern.id`
- `hypothesis_id UUID FK -> hypothesis.id`
- PK (`pattern_id`, `hypothesis_id`)

### hypothesis_experiment
- `hypothesis_id UUID FK -> hypothesis.id`
- `experiment_id UUID FK -> experiment.id`
- PK (`hypothesis_id`, `experiment_id`)

### experiment_performance
- `experiment_id UUID FK -> experiment.id`
- `performance_id UUID FK -> performance.id`
- `arm_id UUID NULL FK -> experiment_arm.id`
- PK (`experiment_id`, `performance_id`, `arm_id`)

Constraint: when `arm_id` is present, `arm_id.experiment_id = experiment_id`.

### performance_learning
- `performance_id UUID FK -> performance.id`
- `learning_id UUID FK -> learning.id`
- PK (`performance_id`, `learning_id`)

### learning_mechanism
- `learning_id UUID FK -> learning.id`
- `mechanism_id UUID FK -> mechanism.id`
- PK (`learning_id`, `mechanism_id`)

### learning_pattern
- `learning_id UUID FK -> learning.id`
- `pattern_id UUID FK -> pattern.id`
- PK (`learning_id`, `pattern_id`)

### learning_hypothesis
- `learning_id UUID FK -> learning.id`
- `hypothesis_id UUID FK -> hypothesis.id`
- PK (`learning_id`, `hypothesis_id`)

### learning_decision
- `learning_id UUID FK -> learning.id`
- `decision_id UUID FK -> decision.id`
- PK (`learning_id`, `decision_id`)

### learning_audience
- `learning_id UUID FK -> learning.id`
- `audience_id UUID FK -> audience.id`
- PK (`learning_id`, `audience_id`)

### learning_account
- `learning_id UUID FK -> learning.id`
- `account_id UUID FK -> account.id`
- PK (`learning_id`, `account_id`)

### decision_experiment
- `decision_id UUID FK -> decision.id`
- `experiment_id UUID FK -> experiment.id`
- PK (`decision_id`, `experiment_id`)

### decision_concept
- `decision_id UUID FK -> decision.id`
- `concept_id UUID FK -> concept.id`
- PK (`decision_id`, `concept_id`)

### audience_concept
- `audience_id UUID FK -> audience.id`
- `concept_id UUID FK -> concept.id`
- PK (`audience_id`, `concept_id`)

### audience_hypothesis
- `audience_id UUID FK -> audience.id`
- `hypothesis_id UUID FK -> hypothesis.id`
- PK (`audience_id`, `hypothesis_id`)

---

## 4. Explicit invariants

### Experiment
1. `experiment_type = controlled` => exactly one baseline arm and >=1 intervention arm.
2. `experiment_type = exploratory` => baseline arm is optional.
3. Every arm references exactly one Variant or Content.
4. Every Experiment/Performance association must be attributable to the Experiment and, where experimental attribution is required, to an arm.

### Publication / Platform
5. Publication Account and Platform Version must belong to the same Platform.
6. Performance is always attached to exactly one Publication.
7. Performance observations are append-only; later observations never overwrite earlier snapshots.

### Learning
8. Learning must have at least one structured provenance source.
9. Learning status is enumerated and status changes are recorded in `learning_status_history`.
10. Learning provenance does not imply causality.
11. A causal claim requires appropriate experimental evidence; schema relationships alone never upgrade an association to causality.

### Provenance / deletion
12. Provenance-bearing rows are soft-deleted rather than destructively cascaded.
13. Foreign-key relationships to historical evidence, performance, experiment and learning records must remain resolvable.

### Context
14. No generic `context` table exists.
15. Platform, Account and Audience are explicit dimensions. Temporal validity is represented by timestamps/validity fields.

### Cross-platform analysis
16. Performance remains attached to Publication -> Platform Version -> Platform and cannot be detached from that context.
17. Cross-platform aggregation is an analysis/query decision, not a loss of source context.

---

## 5. Deliberate implementation boundaries

The following are intentionally not separate first-class tables in V0.1:

- Analysis
- Inference
- Baseline
- Intervention
- Metric
- Score
- Knowledge Claim
- Context
- Model
- Policy
- Goal
- Constraint
- Resource
- Saturation

JSONB is used only where the structure is extensible or payload-like. Core semantics, identifiers, cardinalities and provenance links remain relational.

---

## 6. Schema status

This is the **concrete audit candidate** for Logical Data Schema V0.1.

It is subordinate to and must remain semantically faithful to:

`docs/information-model/V0.1/INFORMATION-MODEL-V0.1.md`

The Information Model is LOCKED. Any issue found here that cannot be resolved without changing object meaning, relationship semantics or locked invariants must be raised as an explicit Information Model Change Request rather than silently changing the model.

**Current status: NOT LOCKED — awaiting adversarial audit.**
