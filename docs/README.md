# Documentation

This directory contains the normative architecture and data-model specifications of the Autonomous Content Intelligence System.

## Normative hierarchy

1. **Information Model V0.1** — LOCKED (semantic authority)  
2. **Operational Specification V0.1** — LOCKED (operational invariants)  
3. **Logical Data Schema V0.1** — concrete representation (current candidate under adversarial audit)

The hierarchy is documentary only. The system remains a path-dependent graph; no mandatory linear pipeline is imposed.

## Versioning rule

The Information Model V0.1 and Operational Specification V0.1 are locked. Changes to their objects, semantics, relationships, invariants or cardinalities require an explicit version change.

The Logical Data Schema must implement the locked higher layers rather than silently modifying them.
