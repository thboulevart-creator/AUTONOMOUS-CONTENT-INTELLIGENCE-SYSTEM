#!/usr/bin/env bash
# Run Phase 1 PostgreSQL foundation tests against a live PostgreSQL instance.
set -euo pipefail
cd "$(dirname "$0")/.."

export ACIS_DB_HOST="${ACIS_DB_HOST:-localhost}"
export ACIS_DB_PORT="${ACIS_DB_PORT:-5432}"
export ACIS_DB_USER="${ACIS_DB_USER:-acis}"
export ACIS_DB_PASSWORD="${ACIS_DB_PASSWORD:-acis_test}"
export ACIS_DB_NAME="${ACIS_DB_NAME:-acis_test}"

echo "==> Ensuring PostgreSQL is running..."
bash scripts/start_postgres.sh

echo "==> Initialising isolated test database..."
bash scripts/init_test_db.sh

echo "==> Installing Python test dependencies..."
pip3 install -q -r db/requirements.txt

echo "==> Running Phase 1 foundation tests..."
python3 -m pytest db/tests/ -v --tb=short
