# AUTONOMOUS-CONTENT-INTELLIGENCE-SYSTEM

Autonomous system for discovering, modeling, testing, learning and exploiting content intelligence.

## Current status

**Information Model V0.1: LOCKED**  
**Operational Specification V0.1: LOCKED**

The project is now moving to the next layer: **Logical Data Schema V0.1** (adversarial audit in progress).

The Information Model is the semantic contract.  
The Operational Specification defines the executable operational rules subordinate to that contract.  
The data schema must implement both without silently changing their meaning.

## Normative hierarchy

```
Information Model V0.1          (LOCKED — semantic authority)
        ↓
Operational Specification V0.1  (LOCKED — operational invariants)
        ↓
Logical Data Schema V0.1        (concrete representation)
```

This hierarchy is purely documentary. The system itself remains a **path-dependent graph**, never a mandatory linear pipeline.

## Repository structure

```text
docs/
├── information-model/
│   ├── README.md
│   └── V0.1/
│       ├── INFORMATION-MODEL-V0.1.md
│       └── DECISIONS.md
├── operational-specification/
│   └── V0.1/
│       └── OPERATIONAL-SPECIFICATION-V0.1.md
├── data-schema/
│   └── V0.1/
│       └── LOGICAL-DATA-SCHEMA-V0.1.md
└── logical-data-schema/          # historical draft (superseded)
    └── V0.1/
        └── LOGICAL-DATA-SCHEMA-V0.1.md
```

## Versioning rule

Semantic changes to the Information Model or Operational Specification require an explicit version decision. Schema-level implementation details may evolve within the schema layer as long as they remain faithful to the locked higher layers.
