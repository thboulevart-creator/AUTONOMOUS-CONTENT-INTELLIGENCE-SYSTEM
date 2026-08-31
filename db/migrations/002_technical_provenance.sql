-- Technical Provenance Store V0.1
-- Scope: technical provenance only; outside the LOCKED Logical Data Schema.
-- This migration MUST NOT modify or redefine any V0.1 domain table.
-- Source contract:
-- docs/target-architecture/V0.1/TECHNICAL-PROVENANCE-STORE-CONTRACT-V0.1.md
-- Port contract:
-- docs/target-architecture/V0.1/PROVENANCE-REPOSITORY-PORT-V0.1.md

BEGIN;

CREATE SCHEMA technical_provenance;

CREATE TABLE technical_provenance.execution_trace (
    execution_id       UUID PRIMARY KEY,
    operation_type     TEXT NOT NULL,
    occurred_at        TIMESTAMPTZ NOT NULL,
    input_references   JSONB,
    output_references  JSONB,
    execution_status   TEXT NOT NULL,
    technical_metadata JSONB
);

CREATE TABLE technical_provenance.provider_provenance (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_reference UUID NOT NULL,
    provider            TEXT NOT NULL,
    model               TEXT NOT NULL,
    model_version       TEXT,
    request_parameters  JSONB,
    input_reference     TEXT,
    output_reference    TEXT,
    execution_status    TEXT NOT NULL,
    intended_provider   TEXT,
    actual_provider     TEXT,
    prompt              TEXT,
    seed                TEXT,
    temperature         NUMERIC,
    api_version         TEXT,
    fallback_reason     TEXT,
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE technical_provenance.artifact_lineage (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_reference   TEXT NOT NULL,
    child_reference    TEXT NOT NULL,
    relationship       TEXT NOT NULL,
    recorded_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_artifact_lineage_edge
        UNIQUE (parent_reference, child_reference, relationship)
);

CREATE OR REPLACE FUNCTION technical_provenance.reject_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'technical provenance records are append-only: % is not permitted on %.%',
        TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME;
END;
$$;

CREATE TRIGGER execution_trace_append_only
BEFORE UPDATE OR DELETE OR TRUNCATE
ON technical_provenance.execution_trace
FOR EACH STATEMENT
EXECUTE FUNCTION technical_provenance.reject_mutation();

CREATE TRIGGER provider_provenance_append_only
BEFORE UPDATE OR DELETE OR TRUNCATE
ON technical_provenance.provider_provenance
FOR EACH STATEMENT
EXECUTE FUNCTION technical_provenance.reject_mutation();

CREATE TRIGGER artifact_lineage_append_only
BEFORE UPDATE OR DELETE OR TRUNCATE
ON technical_provenance.artifact_lineage
FOR EACH STATEMENT
EXECUTE FUNCTION technical_provenance.reject_mutation();

COMMIT;
