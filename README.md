# AUTONOMOUS-CONTENT-INTELLIGENCE-SYSTEM

Autonomous system for discovering, modeling, testing, learning and exploiting content intelligence.

## Current status

**Information Model V0.1: LOCKED**

The project is now moving to the next layer: **Logical Data Schema V0.1**.

The Information Model is the semantic contract. The data schema must implement it without silently changing its meaning.

## Repository structure

```text
docs/
└── information-model/
    ├── README.md
    └── V0.1/
        ├── INFORMATION-MODEL-V0.1.md
        └── DECISIONS.md
```

## Versioning rule

Semantic changes to the Information Model require an explicit version decision. Schema-level implementation details may evolve within the schema layer as long as they remain faithful to the locked Information Model.
