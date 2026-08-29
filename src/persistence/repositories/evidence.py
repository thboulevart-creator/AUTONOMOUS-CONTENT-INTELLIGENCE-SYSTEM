"""Evidence persistence — no domain admission gate (Phase 3)."""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import Json

from ..connection import dict_cursor


class EvidenceRepository:
    def __init__(self, conn: PgConnection):
        self.conn = conn

    def create(
        self,
        *,
        source_type: str,
        raw_payload: Any,
        observed_at,
        source_ref: str | None = None,
        collected_at=None,
        collection_context: Any = None,
        evidence_id: UUID | None = None,
    ) -> dict:
        eid = evidence_id or uuid4()
        cur = dict_cursor(self.conn)
        cur.execute(
            """
            INSERT INTO evidence (
                id, source_type, source_ref, raw_payload, observed_at,
                collected_at, collection_context
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                str(eid),
                source_type,
                source_ref,
                Json(raw_payload),
                observed_at,
                collected_at,
                Json(collection_context) if collection_context is not None else None,
            ),
        )
        return dict(cur.fetchone())

    def get_by_id(self, evidence_id: UUID | str, *, include_deleted: bool = False) -> dict | None:
        cur = dict_cursor(self.conn)
        if include_deleted:
            cur.execute("SELECT * FROM evidence WHERE id = %s", (str(evidence_id),))
        else:
            cur.execute(
                "SELECT * FROM evidence WHERE id = %s AND deleted_at IS NULL",
                (str(evidence_id),),
            )
        row = cur.fetchone()
        return dict(row) if row else None

    def soft_delete(self, evidence_id: UUID | str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE evidence SET deleted_at = now(), updated_at = now() WHERE id = %s AND deleted_at IS NULL",
            (str(evidence_id),),
        )
