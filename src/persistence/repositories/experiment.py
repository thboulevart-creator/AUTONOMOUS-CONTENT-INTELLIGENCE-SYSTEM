"""Experiment + Experiment Arm persistence. No closure-gate logic."""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import Json

from ..connection import dict_cursor


class ExperimentRepository:
    def __init__(self, conn: PgConnection):
        self.conn = conn

    def create(self, *, experiment_type: str, status: str = "draft", design: Any = None, experiment_id: UUID | None = None) -> dict:
        eid = experiment_id or uuid4()
        cur = dict_cursor(self.conn)
        cur.execute(
            "INSERT INTO experiment (id, experiment_type, status, design) VALUES (%s, %s, %s, %s) RETURNING *",
            (str(eid), experiment_type, status, Json(design) if design is not None else None),
        )
        return dict(cur.fetchone())

    def get_by_id(self, experiment_id: UUID | str) -> dict | None:
        cur = dict_cursor(self.conn)
        cur.execute("SELECT * FROM experiment WHERE id = %s AND deleted_at IS NULL", (str(experiment_id),))
        row = cur.fetchone()
        return dict(row) if row else None

    def add_arm(self, *, experiment_id: UUID | str, arm_type: str, content_id: UUID | str | None = None, variant_id: UUID | str | None = None, label: str | None = None, arm_id: UUID | None = None) -> dict:
        aid = arm_id or uuid4()
        cur = dict_cursor(self.conn)
        cur.execute(
            "INSERT INTO experiment_arm (id, experiment_id, arm_type, content_id, variant_id, label) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
            (str(aid), str(experiment_id), arm_type, str(content_id) if content_id else None, str(variant_id) if variant_id else None, label),
        )
        return dict(cur.fetchone())

    def get_arms(self, experiment_id: UUID | str) -> list[dict]:
        cur = dict_cursor(self.conn)
        cur.execute("SELECT * FROM experiment_arm WHERE experiment_id = %s ORDER BY created_at", (str(experiment_id),))
        return [dict(r) for r in cur.fetchall()]
