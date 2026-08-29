"""Learning + provenance + status history persistence. No promotion gates."""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import Json

from ..connection import dict_cursor


class LearningRepository:
    def __init__(self, conn: PgConnection):
        self.conn = conn

    def create(self, *, claim: str, status: str, version: int = 1, confidence: float | None = None, conditions: Any = None, learning_id: UUID | None = None) -> dict:
        lid = learning_id or uuid4()
        cur = dict_cursor(self.conn)
        cur.execute(
            "INSERT INTO learning (id, claim, status, confidence, version, conditions) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
            (str(lid), claim, status, confidence, version, Json(conditions) if conditions is not None else None),
        )
        row = dict(cur.fetchone())
        cur.execute(
            "INSERT INTO learning_status_history (id, learning_id, from_status, to_status, reason) VALUES (%s, %s, NULL, %s, %s)",
            (str(uuid4()), str(lid), status, "created"),
        )
        return row

    def get_by_id(self, learning_id: UUID | str, *, include_deleted: bool = False) -> dict | None:
        cur = dict_cursor(self.conn)
        if include_deleted:
            cur.execute("SELECT * FROM learning WHERE id = %s", (str(learning_id),))
        else:
            cur.execute("SELECT * FROM learning WHERE id = %s AND deleted_at IS NULL", (str(learning_id),))
        row = cur.fetchone()
        return dict(row) if row else None

    def add_provenance(self, *, learning_id: UUID | str, source_type: str, source_id: UUID | str, role: str | None = None) -> dict:
        cur = dict_cursor(self.conn)
        pid = uuid4()
        cur.execute(
            "INSERT INTO learning_provenance (id, learning_id, source_type, source_id, role) VALUES (%s, %s, %s, %s, %s) RETURNING *",
            (str(pid), str(learning_id), source_type, str(source_id), role),
        )
        return dict(cur.fetchone())

    def get_provenance(self, learning_id: UUID | str) -> list[dict]:
        cur = dict_cursor(self.conn)
        cur.execute("SELECT * FROM learning_provenance WHERE learning_id = %s ORDER BY created_at", (str(learning_id),))
        return [dict(r) for r in cur.fetchall()]

    def record_status(self, *, learning_id: UUID | str, to_status: str, from_status: str | None = None, reason: str | None = None) -> dict:
        cur = dict_cursor(self.conn)
        cur.execute("UPDATE learning SET status = %s, updated_at = now() WHERE id = %s RETURNING *", (to_status, str(learning_id)))
        row = dict(cur.fetchone())
        cur.execute(
            "INSERT INTO learning_status_history (id, learning_id, from_status, to_status, reason) VALUES (%s, %s, %s, %s, %s)",
            (str(uuid4()), str(learning_id), from_status, to_status, reason),
        )
        return row

    def get_status_history(self, learning_id: UUID | str) -> list[dict]:
        cur = dict_cursor(self.conn)
        cur.execute("SELECT * FROM learning_status_history WHERE learning_id = %s ORDER BY changed_at", (str(learning_id),))
        return [dict(r) for r in cur.fetchall()]

    def link_evidence(self, learning_id: UUID | str, evidence_id: UUID | str) -> None:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO evidence_learning (evidence_id, learning_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (str(evidence_id), str(learning_id)))

    def get_linked_evidence_ids(self, learning_id: UUID | str) -> list[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT evidence_id FROM evidence_learning WHERE learning_id = %s", (str(learning_id),))
        return [str(r[0]) for r in cur.fetchall()]
