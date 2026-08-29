# PostgreSQL Foundation V0.1

Physical implementation of the locked Logical Data Schema V0.1.

## Source of truth

- `docs/data-schema/V0.1/LOGICAL-DATA-SCHEMA-V0.1.md` (LOCKED)
- `docs/operational-specification/V0.1/OPERATIONAL-SPECIFICATION-V0.1.md` (LOCKED)
- `docs/information-model/V0.1/INFORMATION-MODEL-V0.1.md` (LOCKED)

## Prerequisites

- Ubuntu/Debian host (or equivalent) with ability to install packages
- Python 3.10+
- Root or sudo for initial PostgreSQL package install and cluster start

```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-client postgresql-contrib
```

## Quick start (reproducible)

```bash
# 1. Start PostgreSQL cluster
bash scripts/start_postgres.sh

# 2. Create/reset isolated test database + apply migration + run tests
bash scripts/run_db_tests.sh
```

Expected result:

```text
19 passed
```

## Environment variables (test-only defaults)

| Variable | Default |
|----------|---------|
| `ACIS_DB_HOST` | `localhost` |
| `ACIS_DB_PORT` | `5432` |
| `ACIS_DB_USER` | `acis` |
| `ACIS_DB_PASSWORD` | `acis_test` |
| `ACIS_DB_NAME` | `acis_test` |

These are **development/test credentials only**. Do not use them in production.

## Individual steps

```bash
bash scripts/start_postgres.sh          # start cluster if down
bash scripts/init_test_db.sh            # drop/create acis_test
# migration is applied automatically by pytest conftest
python3 -m pytest db/tests/ -v
```

## Migration

```bash
psql -U acis -d acis_test -f db/migrations/001_v0.1_foundation.sql
```

(The test suite applies this automatically via `db/tests/conftest.py`.)

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

## Troubleshooting

| Symptom | Action |
|---------|--------|
| `pg_ctlcluster: command not found` | Install `postgresql` package |
| Cluster status `down` | `bash scripts/start_postgres.sh` |
| Connection refused | Wait a few seconds after start; check `pg_lsclusters` |
| Role does not exist | `bash scripts/init_test_db.sh` |

## CI note

A CI job should:

1. Install PostgreSQL package (or use a service container)
2. Start the cluster / wait for readiness
3. Run `bash scripts/run_db_tests.sh`

No Docker is required on hosts that already provide the PostgreSQL packages.
