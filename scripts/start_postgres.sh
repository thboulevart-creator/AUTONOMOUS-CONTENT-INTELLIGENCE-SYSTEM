#!/usr/bin/env bash
# Start the local PostgreSQL cluster used for V0.1 tests.
# Intended for Ubuntu/Debian hosts with the postgresql package installed.
set -euo pipefail

CLUSTER_VERSION="${PG_CLUSTER_VERSION:-16}"
CLUSTER_NAME="${PG_CLUSTER_NAME:-main}"

if ! command -v pg_ctlcluster >/dev/null 2>&1; then
  echo "ERROR: pg_ctlcluster not found. Install PostgreSQL first:"
  echo "  sudo apt-get update && sudo apt-get install -y postgresql postgresql-client"
  exit 1
fi

status=$(pg_lsclusters | awk -v v="$CLUSTER_VERSION" -v n="$CLUSTER_NAME" '$1==v && $2==n {print $4}')
if [ "$status" = "online" ]; then
  echo "PostgreSQL ${CLUSTER_VERSION}/${CLUSTER_NAME} already online."
else
  echo "Starting PostgreSQL ${CLUSTER_VERSION}/${CLUSTER_NAME}..."
  pg_ctlcluster "$CLUSTER_VERSION" "$CLUSTER_NAME" start
fi

pg_lsclusters
echo "SELECT version();" | su - postgres -c "psql -t -A" 2>/dev/null || true
