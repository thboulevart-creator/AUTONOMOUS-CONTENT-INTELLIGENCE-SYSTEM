"""
Phase 1 database test configuration.
Requires a running PostgreSQL instance with a dedicated test database.
"""
import os
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_HOST = os.getenv("ACIS_DB_HOST", "localhost")
DB_PORT = os.getenv("ACIS_DB_PORT", "5432")
DB_USER = os.getenv("ACIS_DB_USER", "acis")
DB_PASSWORD = os.getenv("ACIS_DB_PASSWORD", "acis_test")
DB_NAME = os.getenv("ACIS_DB_NAME", "acis_test")

MIGRATION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "migrations", "001_v0.1_foundation.sql"
)


def _admin_connect():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname="postgres"
    )


def _connect():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME
    )


@pytest.fixture(scope="session", autouse=True)
def migrate_schema():
    """Drop and recreate the test database, then apply the foundation migration."""
    admin = _admin_connect()
    admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = admin.cursor()
    cur.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DB_NAME}' AND pid <> pg_backend_pid();")
    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
    cur.execute(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};")
    cur.close()
    admin.close()

    conn = _connect()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    with open(MIGRATION_PATH, "r") as f:
        sql = f.read()
    cur.execute(sql)
    cur.close()
    conn.close()
    yield


@pytest.fixture
def db():
    """Provide a connection that rolls back after each test."""
    conn = _connect()
    conn.autocommit = False
    yield conn
    conn.rollback()
    conn.close()
