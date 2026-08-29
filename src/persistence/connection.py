"""PostgreSQL connection and transaction management for Phase 2."""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor


def _dsn() -> dict:
    return {
        "host": os.getenv("ACIS_DB_HOST", "localhost"),
        "port": os.getenv("ACIS_DB_PORT", "5432"),
        "user": os.getenv("ACIS_DB_USER", "acis"),
        "password": os.getenv("ACIS_DB_PASSWORD", "acis_test"),
        "dbname": os.getenv("ACIS_DB_NAME", "acis_test"),
    }


def get_connection() -> PgConnection:
    """Open a new PostgreSQL connection using environment configuration."""
    conn = psycopg2.connect(**_dsn())
    conn.autocommit = False
    return conn


@contextmanager
def transaction(conn: PgConnection | None = None) -> Generator[PgConnection, None, None]:
    """Transaction context manager. Commits on success, rolls back on failure."""
    owns = conn is None
    if owns:
        conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if owns:
            conn.close()


def dict_cursor(conn: PgConnection):
    return conn.cursor(cursor_factory=RealDictCursor)
