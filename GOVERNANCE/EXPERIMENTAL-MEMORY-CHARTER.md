# Experimental Memory — Architectural Requirement

**Status:** RESERVED / INITIAL REQUIREMENT — not a final specification

## Purpose

The system shall progressively incorporate an **experimental memory** that records and preserves the history of learning-oriented experimentation.

The memory is intended to support a controlled loop of:

**observation → hypothesis → experiment → result → candidate explanation → tested explanation → knowledge → new hypothesis**

## Minimum architectural principle

The system must not learn only from whether an outcome was successful or unsuccessful. It must seek to retain and distinguish the **explanations that were actually tested**, including explanations that were rejected, inconclusive, or only partially supported.

## Intended future scope

The detailed specification remains to be designed. It is expected to define, at minimum:

- hypotheses and their context;
- experiment identity, inputs and conditions;
- observed results and measurements;
- candidate explanations and tests performed against them;
- successful, failed, rejected and inconclusive experiments;
- confidence/evidence status of derived knowledge;
- links between experiments, conclusions and subsequent experiments;
- provenance, reproducibility and auditability;
- safeguards preventing unvalidated learning from silently changing system behaviour;
- rollback/versioning requirements for any approved adaptation.

## Non-goal at this stage

This document does **not** define the final data model, storage mechanism, learning algorithm, promotion criteria, or autonomous adaptation policy. Those must be designed and adversarially reviewed before implementation.

## Cross-system principle

This requirement is intended to remain compatible with the broader architecture shared by the project's autonomous systems: they should be capable of **experimenting, learning, and improving under control**, rather than adapting blindly from raw outcomes.
