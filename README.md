# AUTONOMOUS-CONTENT-INTELLIGENCE-SYSTEM

Autonomous system for discovering, modeling, testing, learning and exploiting content intelligence.

## Current status

**Information Model V0.1: LOCKED**  
**Operational Specification V0.1: LOCKED**  
**Logical Data Schema V0.1: LOCKED**

The three normative layers of V0.1 are now complete and locked.

The Information Model is the semantic contract.  
The Operational Specification defines the executable operational rules subordinate to that contract.  
The Logical Data Schema is the concrete representation of both.

## Normative hierarchy

```
Information Model V0.1          (LOCKED — semantic authority)
        ↓
Operational Specification V0.1  (LOCKED — operational invariants)
        ↓
Logical Data Schema V0.1        (LOCKED — concrete representation)
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
│   ├── README.md
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

Semantic or structural changes to any of the three locked V0.1 layers require an explicit new version decision. Implementation details (Policy values, application logic, physical database) may evolve without changing the locked documents.
