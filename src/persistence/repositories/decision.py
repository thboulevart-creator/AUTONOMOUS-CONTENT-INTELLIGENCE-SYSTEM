"""Decision persistence — no exploration classification."""
from __future__ import annotations

from uuid import UUID, uuid4

from psycopg2.extensions import connection as PgConnection

from ..connection import dict_cursor


class DecisionRepository:
    def __init__(self, conn: PgConnection):
        self.conn = conn

    def create(
        self,
        *,
        decision_type: str,
        rationale: str | None = None,
        decision_id: UUID | None = None,
    ) -> dict:
        did = decision_id or uuid4()
        cur = dict_cursor(self.conn)
        cur.execute(
            """
            INSERT INTO decision (id, decision_type, rationale)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (str(did), decision_type, rationale),
        )
        return dict(cur.fetchone())

    def get_by_id(self, decision_id: UUID | str) -> dict | None:
        cur = dict_cursor(self.conn)
        cur.execute(
            "SELECT * FROM decision WHERE id = %s AND deleted_at IS NULL",
            (str(decision_id),),
        )
        row = cur.fetchone()
        return dict(row) if row else None
