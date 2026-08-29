#!/usr/bin/env bash
# Create/reset the isolated Phase 1 test database.
set -euo pipefail

export ACIS_DB_HOST="${ACIS_DB_HOST:-localhost}"
export ACIS_DB_PORT="${ACIS_DB_PORT:-5432}"
export ACIS_DB_USER="${ACIS_DB_USER:-acis}"
export ACIS_DB_PASSWORD="${ACIS_DB_PASSWORD:-acis_test}"
export ACIS_DB_NAME="${ACIS_DB_NAME:-acis_test}"

echo "Ensuring role and database exist..."
su - postgres -c "psql -v ON_ERROR_STOP=1" <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${ACIS_DB_USER}') THEN
    CREATE ROLE ${ACIS_DB_USER} LOGIN PASSWORD '${ACIS_DB_PASSWORD}' SUPERUSER;
  END IF;
END
\$\$;
SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
 WHERE datname = '${ACIS_DB_NAME}' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ${ACIS_DB_NAME};
CREATE DATABASE ${ACIS_DB_NAME} OWNER ${ACIS_DB_USER};
SQL

echo "Test database ${ACIS_DB_NAME} ready (owner ${ACIS_DB_USER})."
