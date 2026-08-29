#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export ACIS_DB_HOST="${ACIS_DB_HOST:-localhost}"
export ACIS_DB_PORT="${ACIS_DB_PORT:-5432}"
export ACIS_DB_USER="${ACIS_DB_USER:-acis}"
export ACIS_DB_PASSWORD="${ACIS_DB_PASSWORD:-acis_test}"
export ACIS_DB_NAME="${ACIS_DB_NAME:-acis_test}"

pip3 install -q -r db/requirements.txt
python3 -m pytest db/tests/ -v --tb=short
