"""Technical provenance persistence adapter.

This adapter implements the V0.1 ProvenanceRepositoryPort against the
separate technical_provenance PostgreSQL schema. It stores technical facts
only and never mutates domain tables or domain lifecycle state.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import Json

from ..connection import dict_cursor


class ProvenanceRepository:
    """Persistence adapter for the technical provenance store."""

    def __init__(self, conn: PgConnection):
        self.conn = conn

    @staticmethod
    def _mapping(value: Any, name: str) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise TypeError(f"{name} must be a mapping")
        return value

    def record_execution_trace(self, event: Any) -> dict:
        data = self._mapping(event, "event")
        cur = dict_cursor(self.conn)
        cur.execute(
            """
            INSERT INTO technical_provenance.execution_trace (
                execution_id, operation_type, occurred_at,
                input_references, output_references,
                execution_status, technical_metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                str(data["execution_id"]),
                data["operation_type"],
                data["occurred_at"],
                Json(data["input_references"]) if data.get("input_references") is not None else None,
                Json(data["output_references"]) if data.get("output_references") is not None else None,
                data["execution_status"],
                Json(data["technical_metadata"]) if data.get("technical_metadata") is not None else None,
            ),
        )
        return dict(cur.fetchone())

    def record_provider_provenance(self, execution_reference: Any, provider_metadata: Any) -> dict:
        data = self._mapping(provider_metadata, "provider_metadata")
        cur = dict_cursor(self.conn)
        cur.execute(
            """
            INSERT INTO technical_provenance.provider_provenance (
                execution_reference, provider, model, model_version,
                request_parameters, input_reference, output_reference,
                execution_status, intended_provider, actual_provider,
                prompt, seed, temperature, api_version, fallback_reason
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                str(execution_reference),
                data["provider"],
                data["model"],
                data.get("model_version"),
                Json(data["request_parameters"]) if data.get("request_parameters") is not None else None,
                data.get("input_reference"),
                data.get("output_reference"),
                data["execution_status"],
                data.get("intended_provider"),
                data.get("actual_provider"),
                data.get("prompt"),
                data.get("seed"),
                data.get("temperature"),
                data.get("api_version"),
                data.get("fallback_reason"),
            ),
        )
        return dict(cur.fetchone())

    def link_artifact_lineage(self, parent_reference: Any, child_reference: Any, relationship: str) -> dict:
        cur = dict_cursor(self.conn)
        cur.execute(
            """
            INSERT INTO technical_provenance.artifact_lineage (
                parent_reference, child_reference, relationship
            ) VALUES (%s, %s, %s)
            ON CONFLICT (parent_reference, child_reference, relationship)
            DO NOTHING
            RETURNING *
            """,
            (str(parent_reference), str(child_reference), relationship),
        )
        row = cur.fetchone()
        if row is not None:
            return dict(row)

        cur.execute(
            """
            SELECT *
            FROM technical_provenance.artifact_lineage
            WHERE parent_reference = %s
              AND child_reference = %s
              AND relationship = %s
            """,
            (str(parent_reference), str(child_reference), relationship),
        )
        return dict(cur.fetchone())
