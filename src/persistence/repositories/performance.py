"""Performance persistence — append-only. No update API."""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import Json

from ..connection import dict_cursor


class PerformanceRepository:
    """Append-only Performance snapshots. Explicitly does NOT expose update()."""

    def __init__(self, conn: PgConnection):
        self.conn = conn

    def append(
        self,
        *,
        publication_id: UUID | str,
        observed_at,
        metrics: Any,
        scores: Any = None,
        measurement_window: Any = None,
        source_ref: str | None = None,
        performance_id: UUID | None = None,
    ) -> dict:
        pid = performance_id or uuid4()
        cur = dict_cursor(self.conn)
        cur.execute(
            """
            INSERT INTO performance (
                id, publication_id, observed_at, metrics, scores,
                measurement_window, source_ref
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                str(pid),
                str(publication_id),
                observed_at,
                Json(metrics),
                Json(scores) if scores is not None else None,
                Json(measurement_window) if measurement_window is not None else None,
                source_ref,
            ),
        )
        return dict(cur.fetchone())

    def get_by_id(self, performance_id: UUID | str) -> dict | None:
        cur = dict_cursor(self.conn)
        cur.execute("SELECT * FROM performance WHERE id = %s", (str(performance_id),))
        row = cur.fetchone()
        return dict(row) if row else None

    def list_for_publication(self, publication_id: UUID | str) -> list[dict]:
        cur = dict_cursor(self.conn)
        cur.execute(
            "SELECT * FROM performance WHERE publication_id = %s ORDER BY observed_at",
            (str(publication_id),),
        )
        return [dict(r) for r in cur.fetchall()]
