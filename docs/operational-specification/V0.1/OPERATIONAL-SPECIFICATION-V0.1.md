# Autonomous Content Intelligence System
## Operational Specification V0.1 — LOCKED

**Status:** LOCKED  
**Version:** V0.1  
**Scope:** Operational layer only  
**Semantic authority:** [Information Model V0.1](../../information-model/V0.1/INFORMATION-MODEL-V0.1.md) — LOCKED  
**Concrete representation:** [Logical Data Schema V0.1](../../data-schema/V0.1/LOGICAL-DATA-SCHEMA-V0.1.md)

---

## 1. Status / Scope

This document defines the operational rules that make the system executable while remaining strictly subordinate to the locked Information Model.

- No new first-class Information Model objects are introduced.
- No semantic modification of the Information Model is permitted.
- The system remains a path-dependent graph; no mandatory linear pipeline is imposed.
- Operational classifications, provenance metadata and process records are not first-class Information Model objects.

**Operational Specification V0.1 is LOCKED.**  
Any future modification requires an explicit new normative version. Silent changes to V0.1 are forbidden.

---

## 2. Normative Hierarchy

1. **Information Model V0.1** (LOCKED) — absolute authority.  
2. **This Operational Specification V0.1** (LOCKED) — operational invariants and process rules.  
3. **Logical Data Schema V0.1** — concrete representation.  
4. **Policy Parameters** — configurable within bounds that cannot violate invariants.  
5. **Implementation Freedom** — choices that do not alter normative behaviour.

Any proposal that requires modification of the Information Model is rejected.

---

## 3. Architectural Principles

- Graph over chain. Path-dependent provenance.  
- Observation / Evidence ≠ interpretation / Learning.  
- Trend is optional.  
- No generic Context object.  
- Performance is append-only observation.  
- Learning is versioned, status-bearing, and conditionable.  
- Experiment uses experiment_arm (baseline / intervention) as defined in the schema.  
- Soft-delete for provenance-bearing records.  
- Causality is never inferred from association alone.

---

## 4. Non-Negotiable Operational Invariants

**INV-01 — Evidence Admission Gate**  
An Observation becomes admissible Evidence only when it carries at minimum: `source_type`, a resolvable `source_ref` (or equivalent provenance locator), `observed_at`, and a non-empty payload. Insufficient observations remain rejected / non-admissible.  
*Rationale:* Prevents noise injection.  
*Failure mode blocked:* Artificial promotion of incomplete data.

**INV-02 — Independence of Evidence**  
Two Evidence records are independent only when their **primary_event_identity** (when available) and **upstream_identity** (when available) differ, and neither is derived from the other.

Normative rules:  
- Same primary_event_identity → dependent.  
- Same upstream_identity (API, dataset, syndication root, or normalised source lineage) → dependent.  
- Detectable republication / syndication (same primary content + temporal proximity within policy window, or shared external event identifier) → dependent.  
- Explicit derivation link → dependent.  
- Payload difference alone is **never** sufficient to declare independence.

When primary_event_identity or upstream_identity cannot be determined, independence status = **UNKNOWN**.  
**UNKNOWN must never be counted as independent corroboration.**

*Note:* `primary_event_identity`, `upstream_identity` and independence state are operational classifications / provenance metadata. They are **not** first-class Information Model objects.

*Rationale:* Closes payload-mutation and same-upstream attacks.  
*Failure mode blocked:* Evidence splitting, syndication attack, same-upstream corroboration, artificial N-evidence counts.

**INV-03 — Independence of Replication**  
A second Experiment is an independent replication only if it differs on at least one material dimension among: Audience, Platform, Account, temporal window, or intervention definition. A new `experiment_id` with identical content, audience, context and period is not independent.  
*Rationale:* Prevents fake replication.  
*Failure mode blocked:* Fake replication.

**INV-04 — One-shot Gate**  
A single success (one Publication / one performance Evidence) can never produce a Learning with status `active` and confidence ≥ high_threshold.  
*Rationale:* Prevents one-shot winners.  
*Failure mode blocked:* One-shot winner.

**INV-05 — Substantive Exploration**  
An action or Experiment may be classified as exploration only if it satisfies all of:  
1. introduces an identifiable difference relative to existing exploitation baselines;  
2. the difference is relevant to the hypothesis or uncertainty being tested;  
3. the difference is measurable or auditable by a declared method;  
4. the difference has a plausible capacity to produce new information (discriminating power).

Purely cosmetic changes (wording tweaks, colour, duration below materiality threshold, etc.) do not qualify.  
A difference below the declared materiality threshold cannot be counted as exploration.  
The classification must be auditable.

*Note:* Exploration classification, materiality metadata and materiality method are operational classifications / provenance metadata. They are **not** first-class Information Model objects.

*Rationale:* Prevents cosmetic exploration and mode collapse.  
*Failure mode blocked:* Cosmetic exploration, exploration collapse via micro-variations.

**INV-06 — Exploration Floor**  
`exploration_floor_ratio` must be > 0 on every defined decision window. The ratio is calculated only over actions that satisfy INV-05. No valid configuration may set the floor to 0.  
*Rationale:* Guarantees ongoing genuine exploration.  
*Failure mode blocked:* Exploration collapse.

**INV-07 — Confounder Check**  
Before a causal Learning can reach status `active` + confidence ≥ high_threshold, a confounder check must be performed and recorded. The record must contain:  
1. declared search perimeter;  
2. categories of confounders considered relevant (amplification, algorithm change, external event, audience shift, distribution change, timing anomaly, external campaign, influencer effect, etc.);  
3. sources actually consulted;  
4. result status: `confounder_detected` | `confounder_not_detected` | `confounder_unknown` | `search_insufficient`.

A bare “none detected” without the above structure is invalid.  
`search_insufficient` or missing check blocks high-confidence causal promotion.  
Absence of detected confounder ≠ proof of absence of confounder.

*Note:* Confounder-check metadata is a process record attached to Learning provenance. It is **not** a first-class Information Model object.

*Rationale:* Prevents false causal attribution.  
*Failure mode blocked:* False causality, influencer amplification, algorithm shift, audience shift.

**INV-08 — Contradiction Handling**  
Recorded contradictory Evidence or Experiment results must be able to place or keep a Learning in `contested`, reduce its confidence, or block promotion. A Learning cannot simply ignore known contradictions while remaining high-confidence active.  
*Rationale:* Maintains knowledge integrity.  
*Failure mode blocked:* Ignoring contradictory evidence.

**INV-09 — Context Conditioning**  
A Learning must not be universalised beyond the Platform / Account / Audience / temporal conditions that actually support it.  
*Rationale:* Information Model requirement.  
*Failure mode blocked:* Over-generalisation after audience or platform shift.

**INV-10 — Observation ≠ Inference**  
Mechanism / Pattern extractions must distinguish observed from inferred. A pure LLM proposal does not become a fact. Traceability to Evidence and/or Content is mandatory.  
*Rationale:* Information Model.  
*Failure mode blocked:* Confidence inflation on pure inference.

**INV-11 — Experiment Closure Pre-declaration**  
Success / failure / stop criteria of an Experiment must be declared before results are observed. Post-hoc modification of criteria is forbidden.  
*Rationale:* Prevents opportunistic closure.  
*Failure mode blocked:* Post-hoc experiment closure.

**INV-12 — Performance Append-only + Contextual**  
Performance records are append-only snapshots and must remain linkable to Publication, Platform, Account, Audience and time.  
*Rationale:* Information Model.

**INV-13 — Path-dependent Feedback**  
Processes form possible loops, never mandatory chains. No rule of the form “A must precede B must precede C”.

**INV-14 — Negative Information Preservation**  
Failed Experiments and negative Evidence remain recorded and usable for Learning (including contested status or confidence reduction).

---

## 5. Policy Parameters

| Parameter | Allowed range | Role | Protected invariant(s) |
|-----------|---------------|------|------------------------|
| `min_independent_corroborations` | ≥ 2 | Minimum independent Evidence for strong promotion | INV-02, INV-04 |
| `high_confidence_threshold` | 0.70 – 0.95 | Threshold for “high” confidence | INV-04, INV-07 |
| `exploration_floor_ratio` | 0.05 – 0.40 | Minimum fraction of genuine exploration actions | INV-06 |
| `materiality_threshold` | declared numeric or feature-delta method, bounded away from zero | Minimum difference required for substantive exploration | INV-05 |
| `materiality_method` | declared (embedding distance, feature delta, rule-based, …) | Auditability of materiality calculation | INV-05 |
| `syndication_temporal_window` | 1 h – 7 d | Window for detecting republication | INV-02 |
| `confounder_categories` | ordered list of relevant categories | Scope of required search | INV-07 |
| `confounder_min_sources` | ≥ 1 (platform signals + known amplifiers at minimum) | Minimum search effort | INV-07 |
| `phase_thresholds` | declared windows + recurrence + source-diversity rules | Classification of isolated / burst / emerging / established / saturated | Phase process |
| `decision_window` | declared temporal window for floor calculation | Auditability of exploration floor | INV-06 |
| `replication_min_dimensions` | ≥ 1 | Minimum differing dimensions for independent replication | INV-03 |

No Policy Parameter may be set so as to violate any Non-Negotiable Invariant.

---

## 6. Implementation Freedom

An engineer may freely choose:  
- concrete storage technology and indexing;  
- exact algorithms for embedding / feature extraction used in materiality (provided the method is declared and auditable);  
- exact sources consulted inside the declared confounder perimeter;  
- UI / monitoring / alerting;  
- scheduling and batch vs streaming execution;  
- additional non-normative metadata fields;  
- physical-schema optimisations that preserve logical constraints.

These choices must not alter the normative behaviour defined by the invariants.

---

## 7. Operational Processes (minimal)

- **Observation → Evidence Admission** (INV-01)  
- **Independence / Corroboration** (INV-02, UNKNOWN rule)  
- **Mechanism / Pattern Extraction** (INV-10)  
- **Trend / Phase** (isolated | burst | emerging | established | saturated) — thresholds are Policy  
- **Hypothesis**  
- **Experiment** (controlled = exactly one baseline arm + ≥1 intervention arm; exploratory allows optional baseline; INV-11)  
- **Performance** (INV-12)  
- **Learning Promotion** (INV-04 + independent corroboration / replication + INV-07 when causal)  
- **Contradiction** (INV-08)  
- **Exploration / Exploitation** (INV-05 + INV-06)  
- **Decision**  
- **Feedback** (path-dependent, INV-13)

All processes remain optional paths inside the graph.

---

## 8. Buildability Conditions

An engineer can implement every process above without inventing new fundamental rules, provided:  
- independence status is stored as `independent` | `dependent` | `unknown`;  
- confounder-check records contain the five required elements;  
- materiality method and threshold are declared and logged;  
- exploration classification is logged with the difference that justified it.

No additional first-class entity is required.

---

## 9. Adversarial Threat Model (required tests)

| ID | Attack | Expected outcome under V0.1 |
|----|--------|---------------------------|
| A | One-shot winner | Blocked by INV-04 |
| B | Evidence splitting | Blocked by INV-02 (payload difference insufficient) |
| C | Same-upstream corroboration | Blocked by upstream_identity / primary_event_identity |
| D | Fake replication | Blocked by INV-03 |
| E | Cosmetic exploration | Blocked by INV-05 + materiality |
| F | Exploration collapse | Blocked by INV-06 + INV-05 |
| G | False causal attribution | Blocked by INV-07 |
| H | Influencer amplification | Detected or marked unknown by confounder check |
| I | Algorithm shift | Same |
| J | Audience shift | Context conditioning + confounder check |
| K | Contradictory evidence | INV-08 forces contested / confidence drop |
| L | Burst 48 h | Phase thresholds (Policy) can classify as burst |
| M | Slow trend | Phase thresholds can classify as emerging / established |
| N | Post-hoc experiment closure | Blocked by INV-11 |

---

## 10. Version Lock

This document is the normative **Operational Specification V0.1**.

It is subordinate to the locked Information Model and must not alter its semantics, objects, relations or invariants.

**Operational Specification V0.1 is LOCKED.**

Any semantic or operational modification requires an explicit new version decision.
