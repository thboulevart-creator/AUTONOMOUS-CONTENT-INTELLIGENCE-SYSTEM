# Autonomous Content Intelligence System
## Information Model V0.1 — LOCKED

**Status:** LOCKED  
**Version:** V0.1  
**Scope:** Semantic / information model only  
**Next layer:** Logical Data Schema V0.1

---

## 1. Purpose

This document defines the semantic information model of the Autonomous Content Intelligence System.

It specifies the durable concepts the system must be able to represent and the relationships between them. It is intentionally independent of implementation technology.

The model is a **graph**, not a mandatory linear pipeline. Multiple valid paths may exist, including observation, discovery, experimentation, creation, publication, measurement, learning and decision loops.

The model must not infer causality merely from association.

---

## 2. Locked design principles

1. **Graph over chain.** No single mandatory lifecycle exists for every object.
2. **Observation is not causality.** Signals, Evidence and Performance describe observations; they do not by themselves establish causal knowledge.
3. **Experimentation is explicit when causal confidence is sought.** Controlled experiments may increase confidence but do not make every result automatically causal.
4. **Context is dimensional, not a generic catch-all object.** Platform, Account, Audience and time/contextual dimensions are represented explicitly.
5. **Learning is versioned knowledge.** It carries provenance, confidence, validity and status and can supersede or contradict earlier learning.
6. **Traceability is path-dependent.** The system records the provenance actually present; it does not fabricate a complete chain where none existed.
7. **Platform and Audience matter.** Knowledge about content effectiveness is interpreted conditionally on relevant platform, account, audience and temporal context.
8. **Minimality.** No additional first-class object is introduced unless it carries information that cannot reasonably be represented by an existing object.

---

## 3. Objects

### 3.1 Evidence — REQUIRED

An observed fact or structured observation, including its collection context and provenance. Evidence subsumes the former Signal/Observation distinction.

**Must not represent:** an interpretation, hypothesis or causal conclusion.

### 3.2 Trend — OPTIONAL

A derived aggregation of coherent Evidence/observations over time and context. Trend is not required for every discovery path.

**Must not represent:** a mechanism or causal explanation.

### 3.3 Mechanism — REQUIRED

An atomic unit of content functioning or audience response, such as a curiosity gap, pattern interrupt or emotional payoff.

**Must not represent:** a complete recurring configuration of mechanisms or a finished content artifact.

### 3.4 Pattern — REQUIRED

A recurring configuration of one or more Mechanisms plus relevant contextual characteristics that tends to be associated with an effect.

**Must not represent:** a single atomic Mechanism.

### 3.5 Hypothesis — REQUIRED

A falsifiable proposition of the form: if intervention X is applied in context Y, outcome Z is expected, with an explicit confidence/expectation where applicable.

A Hypothesis is not mandatory for every creation path.

### 3.6 Experiment — REQUIRED

A structured test design for one or more Hypotheses. It specifies what is being tested and, where applicable, controlled comparison information.

For a controlled Experiment, structured references to the **baseline/control** and **intervention(s)** are required. Baseline and Intervention are not separate first-class objects in V0.1.

### 3.7 Concept — REQUIRED

An original editorial/narrative idea that can be instantiated as content. It may originate from a Hypothesis, Learning or exploration.

### 3.8 Variant — REQUIRED

A controlled or identifiable variation of a Concept. It is useful for experimentation and comparative analysis.

### 3.9 Content — REQUIRED

A concrete multimedia artifact that can be adapted for publication.

### 3.10 Platform Version — REQUIRED

A platform-specific adaptation of Content, including format, duration, ratio, text, rhythm, CTA or other platform-specific changes.

### 3.11 Publication — REQUIRED

The act/event of publishing a Platform Version through an Account on a Platform at a specific time.

### 3.12 Performance — REQUIRED

A set of raw and derived metrics associated with a Publication, including time-scoped snapshots where required. Performance may also contain multi-objective scores.

Performance is observation, not conclusion.

### 3.13 Learning — REQUIRED

A versioned knowledge claim/update derived from evidence, analysis, inference and/or experimentation. Learning records provenance, confidence, validity and status.

Minimum status vocabulary:
- `active`
- `saturated`
- `deprecated`
- `contested`
- `rehabilitated`

Learning may invalidate, supersede or qualify earlier Learning.

### 3.14 Decision — REQUIRED

An action-selection record: produce, amplify, stop, explore, allocate, test, etc. A Decision is not the execution itself.

### 3.15 Account — REQUIRED

A managed identity/account on a Platform, including relevant operating history and constraints.

### 3.16 Audience — REQUIRED

A representation of a target or observed audience, including segments, behaviours and historical responses.

### 3.17 Platform — REQUIRED

A publishing/distribution environment whose rules, formats and distribution characteristics materially affect content and performance.

---

## 4. Process concepts intentionally not first-class objects

### Analysis
Structured processing of Performance/Evidence, such as comparisons, anomaly detection and decomposition. It is a process/result provenance concept in V0.1, not a mandatory persistent top-level object.

### Inference
A provisional conclusion derived from analysis, correlation, lift or surprise. It is captured through Learning provenance and/or the relevant evidence of reasoning rather than as a mandatory top-level object.

### Baseline / Intervention
Represented as structured properties/references of Experiment rather than separate objects.

### Metric / Score
Represented within Performance rather than separate mandatory objects.

### Knowledge Claim
Represented by Learning.

### Context
There is deliberately no generic Context object. Relevant dimensions are represented explicitly (Platform, Account, Audience, time/temporal context and other specific contextual attributes as needed).

---

## 5. Relationship model

The following are the normative relationships for V0.1. Relations are generally optional unless explicitly constrained by the object semantics.

| Relationship | Cardinality | Type / meaning |
|---|---|---|
| Evidence → Learning | N:M | provenance / support |
| Evidence → Trend | N:M | aggregation / derivation |
| Trend → Hypothesis | N:M | input/opportunity |
| Trend ↔ Mechanism | N:M | associative/discovery |
| Content → Mechanism | N:M | annotation / extraction |
| Content → Pattern | N:M | annotation / extraction |
| Mechanism ↔ Pattern | N:M | constitutive |
| Pattern → Hypothesis | N:M | hypothesis generation |
| Hypothesis ↔ Experiment | N:M | test relationship |
| Experiment → Variant | N:M | experimental arm |
| Experiment → Content | N:M | experimental arm |
| Experiment → Performance | N:M | experiment-result linkage, directly or through Publications |
| Concept → Variant | 1:N | variation |
| Variant → Content | 1:N | instantiation |
| Content → Platform Version | 1:N | adaptation |
| Platform Version → Platform | N:1 | platform context |
| Platform Version → Publication | 1:N | publication events |
| Publication → Account | N:1 | publishing identity |
| Publication → Performance | 1:N | measured snapshots/results |
| Performance → Learning | N:M | learning input |
| Learning → Mechanism | N:M | knowledge update |
| Learning → Pattern | N:M | knowledge update |
| Learning → Hypothesis | N:M | hypothesis update |
| Learning → Decision | N:M | decision support |
| Decision → Experiment | N:M | decision to test |
| Decision → Concept | N:M | decision to create |
| Audience → Concept | N:M | opportunity/constraint |
| Audience → Hypothesis | N:M | contextual condition |
| Learning → Audience | N:M | audience knowledge update |
| Learning → Account | N:M | account-specific knowledge update |

Relations may be traversed in either direction by queries; the semantic model does not require duplicated inverse edges in storage.

---

## 6. Causality policy

The system must preserve the following distinction:

**Evidence / Performance → observed fact**  
**Analysis / Inference → provisional interpretation or statistical relationship**  
**Learning → versioned knowledge claim with confidence and conditions**

A performance result must never automatically be encoded as a causal statement.

Example: a high-performing hook may be associated with higher retention. The system may record that association as Learning with provenance and confidence. Causal confidence requires an appropriate experimental design and replication; the model itself does not declare causality merely because an Experiment exists.

---

## 7. Temporal and contextual requirements

Knowledge-bearing objects, especially Trend, Mechanism, Pattern, Hypothesis and Learning, must be capable of representing:

- creation timestamp;
- observation/update timestamp where relevant;
- version;
- confidence where applicable;
- validity/relevance period where applicable;
- lifecycle status where applicable;
- provenance/history sufficient to understand updates.

Effectiveness knowledge must be conditionable on relevant Platform, Audience, Account and temporal context. The model must not require indiscriminate cross-platform aggregation.

---

## 8. Experiment requirements

An Experiment must distinguish, when applicable:

- the Hypothesis being tested;
- baseline/control reference;
- intervention reference(s);
- the Variant/Content participating in each arm;
- resulting Publications and/or Performance;
- the resulting Learning/provisional conclusion.

For a **controlled Experiment**, `baseline_ref` and `intervention_refs` are mandatory semantic requirements. Exploratory experiments may use a different design when no control is appropriate, but that absence must be explicit rather than inferred.

---

## 9. Traceability invariant

Traceability is **path-dependent**.

If a Content was created directly from exploration, the system must not invent a Hypothesis or Experiment merely to complete a chain.

If a Content was created from a Hypothesis and tested through an Experiment, the available links should permit traversal through the actual path to Publication, Performance and Learning.

Both upward and downward provenance must be supported wherever the corresponding relationships actually exist.

---

## 10. Lifecycle / knowledge-state invariant

Learning must support at minimum the states:

`active → saturated → deprecated`

and the ability to mark competing knowledge as:

`contested`

and later restore a previously deprecated/contested knowledge claim as:

`rehabilitated`

Status is not proof of truth. It is the current system state of the knowledge claim.

---

## 11. Minimality decisions

The following are intentionally **not** first-class V0.1 objects:

- generic Context;
- Signal as a separate object (merged into Evidence);
- Observation as a separate object (merged into Evidence);
- Baseline;
- Intervention;
- Knowledge Claim;
- Metric;
- Score;
- Analysis;
- Inference;
- Model;
- Policy;
- Goal;
- Constraint;
- Resource;
- Saturation object.

They may be introduced in a later version only if implementation evidence demonstrates that the existing model cannot represent the required information without ambiguity or loss.

---

## 12. Version lock

This document is the normative **Information Model V0.1**.

The Logical Data Schema must implement this model; it must not silently change object semantics, cardinalities, relationship meanings or invariants.

Any semantic modification discovered during schema design must be reported as a proposed Information Model change and must trigger an explicit version decision before incorporation.

**V0.1 is LOCKED.**
