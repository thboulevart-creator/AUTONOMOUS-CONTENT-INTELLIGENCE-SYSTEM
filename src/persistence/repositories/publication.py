"""Publication persistence — durable publication identity and metadata.

This repository owns persistence only. Publication orchestration, external
platform calls, idempotency policy and domain validation remain outside it.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import Json

from ..connection import dict_cursor


class PublicationRepository:
    """Persist Publication records without owning publication workflow policy."""

    def __init__(self, conn: PgConnection):
        self.conn = conn

    def create(
        self,
        *,
        platform_version_id: UUID | str,
        account_id: UUID | str,
        published_at,
        external_publication_ref: str | None = None,
        publication_metadata: Any = None,
        publication_id: UUID | None = None,
    ) -> dict:
        pid = publication_id or uuid4()
        cur = dict_cursor(self.conn)
        cur.execute(
            """
            INSERT INTO publication (
                id, platform_version_id, account_id, external_publication_ref,
                published_at, publication_metadata
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                str(pid),
                str(platform_version_id),
                str(account_id),
                external_publication_ref,
                published_at,
                Json(publication_metadata) if publication_metadata is not None else None,
            ),
        )
        return dict(cur.fetchone())

    def get_by_id(self, publication_id: UUID | str) -> dict | None:
        cur = dict_cursor(self.conn)
        cur.execute(
            "SELECT * FROM publication WHERE id = %s AND deleted_at IS NULL",
            (str(publication_id),),
        )
        row = cur.fetchone()
        return dict(row) if row else None
