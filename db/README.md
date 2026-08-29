# PostgreSQL Foundation V0.1

Physical implementation of the locked Logical Data Schema V0.1.

## Source of truth

- `docs/data-schema/V0.1/LOGICAL-DATA-SCHEMA-V0.1.md` (LOCKED)
- `docs/operational-specification/V0.1/OPERATIONAL-SPECIFICATION-V0.1.md` (LOCKED)
- `docs/information-model/V0.1/INFORMATION-MODEL-V0.1.md` (LOCKED)

## Migration

```bash
psql -U acis -d acis_test -f db/migrations/001_v0.1_foundation.sql
```

## Tests

```bash
./scripts/run_db_tests.sh
```

Required environment (defaults shown):

- `ACIS_DB_HOST=localhost`
- `ACIS_DB_PORT=5432`
- `ACIS_DB_USER=acis`
- `ACIS_DB_PASSWORD=acis_test`
- `ACIS_DB_NAME=acis_test`

## What is enforced physically

- UUID primary keys
- Typed foreign keys
- Soft-delete columns on provenance-bearing tables
- `UNIQUE (publication_id, observed_at)` on performance
- Trigger forbidding UPDATE on performance (append-only)
- experiment_arm XOR (variant_id / content_id)
- experiment_arm arm_type ∈ {baseline, intervention}
- Deferred constraint trigger for controlled experiment arm cardinality
- Learning status enum matching Information Model vocabulary
- No tables for forbidden first-class entities
- No forced pipeline constraints

## What is NOT enforced here (application layer)

Independence computation, one-shot gate, confounder check structure, exploration classification, materiality, policy values, promotion logic.
