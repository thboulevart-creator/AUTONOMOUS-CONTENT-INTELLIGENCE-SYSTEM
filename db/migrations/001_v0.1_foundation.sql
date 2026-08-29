-- Logical Data Schema V0.1 — Physical PostgreSQL Foundation
-- Source of truth: docs/data-schema/V0.1/LOGICAL-DATA-SCHEMA-V0.1.md (LOCKED)
-- Do not invent entities, cardinalities or semantics beyond the locked contract.

BEGIN;

-- Extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- gen_random_uuid()

-- ---------------------------------------------------------------------------
-- Learning status enum (exact vocabulary from Information Model)
-- ---------------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE learning_status AS ENUM (
        'active',
        'saturated',
        'deprecated',
        'contested',
        'rehabilitated'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ---------------------------------------------------------------------------
-- Core entities (order respects FK dependencies)
-- ---------------------------------------------------------------------------

CREATE TABLE platform (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL UNIQUE,
    rules           JSONB,
    format_capabilities JSONB,
    distribution_characteristics JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE TABLE account (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id         UUID NOT NULL REFERENCES platform(id),
    external_account_ref TEXT,
    name                TEXT NOT NULL,
    constraints         JSONB,
    operating_history   JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

CREATE TABLE audience (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    segments    JSONB,
    behaviours  JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TABLE evidence (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type         TEXT NOT NULL,
    source_ref          TEXT,
    raw_payload         JSONB NOT NULL,
    observed_at         TIMESTAMPTZ NOT NULL,
    collected_at        TIMESTAMPTZ,
    collection_context  JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

CREATE TABLE trend (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    definition  JSONB NOT NULL,
    valid_from  TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    status      TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TABLE mechanism (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    status      TEXT NOT NULL,
    confidence  NUMERIC(5,4),
    valid_from  TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    version     INTEGER NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TABLE pattern (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    status      TEXT NOT NULL,
    confidence  NUMERIC(5,4),
    valid_from  TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    version     INTEGER NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TABLE hypothesis (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement        TEXT NOT NULL,
    expected_outcome JSONB,
    status           TEXT NOT NULL,
    confidence       NUMERIC(5,4),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at       TIMESTAMPTZ
);

CREATE TABLE concept (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT NOT NULL,
    description TEXT,
    origin_type TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TABLE variant (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_id           UUID NOT NULL REFERENCES concept(id),
    name                 TEXT NOT NULL,
    variation_definition JSONB NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at           TIMESTAMPTZ
);

CREATE TABLE content (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_id       UUID REFERENCES concept(id),
    variant_id       UUID REFERENCES variant(id),
    artifact_ref     TEXT NOT NULL,
    content_metadata JSONB,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at       TIMESTAMPTZ,
    CONSTRAINT content_variant_concept_consistency
        CHECK (variant_id IS NULL OR concept_id IS NOT NULL)
);

CREATE TABLE platform_version (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id         UUID NOT NULL REFERENCES content(id),
    platform_id        UUID NOT NULL REFERENCES platform(id),
    adaptation_payload JSONB NOT NULL,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at         TIMESTAMPTZ
);

CREATE TABLE publication (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_version_id      UUID NOT NULL REFERENCES platform_version(id),
    account_id               UUID NOT NULL REFERENCES account(id),
    external_publication_ref TEXT,
    published_at             TIMESTAMPTZ NOT NULL,
    publication_metadata     JSONB,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at               TIMESTAMPTZ
);

-- Performance: append-only + uniqueness (INV-12 / LDS)
CREATE TABLE performance (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id     UUID NOT NULL REFERENCES publication(id),
    observed_at        TIMESTAMPTZ NOT NULL,
    metrics            JSONB NOT NULL,
    scores             JSONB,
    measurement_window JSONB,
    source_ref         TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT performance_publication_observed_unique UNIQUE (publication_id, observed_at)
);

-- Append-only enforcement: forbid UPDATE of existing Performance rows
CREATE OR REPLACE FUNCTION performance_forbid_update()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Performance rows are append-only. UPDATE is forbidden (INV-12 / Logical Data Schema V0.1).';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_performance_forbid_update
    BEFORE UPDATE ON performance
    FOR EACH ROW
    EXECUTE FUNCTION performance_forbid_update();

CREATE TABLE experiment (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_type TEXT NOT NULL CHECK (experiment_type IN ('controlled', 'exploratory')),
    status          TEXT NOT NULL,
    design          JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE TABLE experiment_arm (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiment(id),
    arm_type      TEXT NOT NULL CHECK (arm_type IN ('baseline', 'intervention')),
    variant_id    UUID REFERENCES variant(id),
    content_id    UUID REFERENCES content(id),
    label         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT experiment_arm_xor_variant_content
        CHECK ((variant_id IS NOT NULL AND content_id IS NULL) OR (variant_id IS NULL AND content_id IS NOT NULL))
);

-- Cross-row cardinality for controlled experiments
CREATE OR REPLACE FUNCTION experiment_arm_cardinality_check()
RETURNS TRIGGER AS $$
DECLARE
    exp_id UUID;
    exp_type TEXT;
    baseline_count INTEGER;
    intervention_count INTEGER;
BEGIN
    exp_id := COALESCE(NEW.experiment_id, OLD.experiment_id);
    SELECT experiment_type INTO exp_type FROM experiment WHERE id = exp_id;

    IF exp_type = 'controlled' THEN
        SELECT COUNT(*) INTO baseline_count
        FROM experiment_arm
        WHERE experiment_id = exp_id AND arm_type = 'baseline';

        SELECT COUNT(*) INTO intervention_count
        FROM experiment_arm
        WHERE experiment_id = exp_id AND arm_type = 'intervention';

        IF baseline_count <> 1 THEN
            RAISE EXCEPTION 'Controlled experiment must have exactly one baseline arm (found %).', baseline_count;
        END IF;
        IF intervention_count < 1 THEN
            RAISE EXCEPTION 'Controlled experiment must have at least one intervention arm (found %).', intervention_count;
        END IF;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER trg_experiment_arm_cardinality
    AFTER INSERT OR UPDATE OR DELETE ON experiment_arm
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW
    EXECUTE FUNCTION experiment_arm_cardinality_check();

CREATE TABLE learning (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim       TEXT NOT NULL,
    status      learning_status NOT NULL,
    confidence  NUMERIC(5,4),
    valid_from  TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    version     INTEGER NOT NULL,
    conditions  JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE TABLE learning_provenance (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learning_id UUID NOT NULL REFERENCES learning(id),
    source_type TEXT NOT NULL CHECK (source_type IN (
        'evidence', 'performance', 'experiment', 'hypothesis',
        'mechanism', 'pattern', 'trend', 'learning'
    )),
    source_id   UUID NOT NULL,
    role        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE learning_status_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learning_id UUID NOT NULL REFERENCES learning(id),
    from_status learning_status,
    to_status   learning_status NOT NULL,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason      TEXT
);

CREATE TABLE decision (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_type TEXT NOT NULL,
    rationale     TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at    TIMESTAMPTZ
);

-- Junction tables
CREATE TABLE evidence_learning (
    evidence_id UUID NOT NULL REFERENCES evidence(id),
    learning_id UUID NOT NULL REFERENCES learning(id),
    PRIMARY KEY (evidence_id, learning_id)
);

CREATE TABLE evidence_trend (
    evidence_id UUID NOT NULL REFERENCES evidence(id),
    trend_id    UUID NOT NULL REFERENCES trend(id),
    PRIMARY KEY (evidence_id, trend_id)
);

CREATE TABLE trend_hypothesis (
    trend_id      UUID NOT NULL REFERENCES trend(id),
    hypothesis_id UUID NOT NULL REFERENCES hypothesis(id),
    PRIMARY KEY (trend_id, hypothesis_id)
);

CREATE TABLE trend_mechanism (
    trend_id     UUID NOT NULL REFERENCES trend(id),
    mechanism_id UUID NOT NULL REFERENCES mechanism(id),
    PRIMARY KEY (trend_id, mechanism_id)
);

CREATE TABLE content_mechanism (
    content_id   UUID NOT NULL REFERENCES content(id),
    mechanism_id UUID NOT NULL REFERENCES mechanism(id),
    relation_type TEXT NOT NULL CHECK (relation_type IN ('applied', 'extracted')),
    PRIMARY KEY (content_id, mechanism_id, relation_type)
);

CREATE TABLE content_pattern (
    content_id  UUID NOT NULL REFERENCES content(id),
    pattern_id  UUID NOT NULL REFERENCES pattern(id),
    relation_type TEXT NOT NULL CHECK (relation_type IN ('applied', 'extracted')),
    PRIMARY KEY (content_id, pattern_id, relation_type)
);

CREATE TABLE mechanism_pattern (
    mechanism_id UUID NOT NULL REFERENCES mechanism(id),
    pattern_id   UUID NOT NULL REFERENCES pattern(id),
    PRIMARY KEY (mechanism_id, pattern_id)
);

CREATE TABLE pattern_hypothesis (
    pattern_id    UUID NOT NULL REFERENCES pattern(id),
    hypothesis_id UUID NOT NULL REFERENCES hypothesis(id),
    PRIMARY KEY (pattern_id, hypothesis_id)
);

CREATE TABLE hypothesis_experiment (
    hypothesis_id UUID NOT NULL REFERENCES hypothesis(id),
    experiment_id UUID NOT NULL REFERENCES experiment(id),
    PRIMARY KEY (hypothesis_id, experiment_id)
);

CREATE TABLE experiment_performance (
    experiment_id  UUID NOT NULL REFERENCES experiment(id),
    performance_id UUID NOT NULL REFERENCES performance(id),
    arm_id         UUID REFERENCES experiment_arm(id),
    PRIMARY KEY (experiment_id, performance_id, arm_id)
);

CREATE TABLE performance_learning (
    performance_id UUID NOT NULL REFERENCES performance(id),
    learning_id    UUID NOT NULL REFERENCES learning(id),
    PRIMARY KEY (performance_id, learning_id)
);

CREATE TABLE learning_mechanism (
    learning_id  UUID NOT NULL REFERENCES learning(id),
    mechanism_id UUID NOT NULL REFERENCES mechanism(id),
    PRIMARY KEY (learning_id, mechanism_id)
);

CREATE TABLE learning_pattern (
    learning_id UUID NOT NULL REFERENCES learning(id),
    pattern_id  UUID NOT NULL REFERENCES pattern(id),
    PRIMARY KEY (learning_id, pattern_id)
);

CREATE TABLE learning_hypothesis (
    learning_id   UUID NOT NULL REFERENCES learning(id),
    hypothesis_id UUID NOT NULL REFERENCES hypothesis(id),
    PRIMARY KEY (learning_id, hypothesis_id)
);

CREATE TABLE learning_decision (
    learning_id UUID NOT NULL REFERENCES learning(id),
    decision_id UUID NOT NULL REFERENCES decision(id),
    PRIMARY KEY (learning_id, decision_id)
);

CREATE TABLE learning_audience (
    learning_id UUID NOT NULL REFERENCES learning(id),
    audience_id UUID NOT NULL REFERENCES audience(id),
    PRIMARY KEY (learning_id, audience_id)
);

CREATE TABLE learning_account (
    learning_id UUID NOT NULL REFERENCES learning(id),
    account_id  UUID NOT NULL REFERENCES account(id),
    PRIMARY KEY (learning_id, account_id)
);

CREATE TABLE decision_experiment (
    decision_id   UUID NOT NULL REFERENCES decision(id),
    experiment_id UUID NOT NULL REFERENCES experiment(id),
    PRIMARY KEY (decision_id, experiment_id)
);

CREATE TABLE decision_concept (
    decision_id UUID NOT NULL REFERENCES decision(id),
    concept_id  UUID NOT NULL REFERENCES concept(id),
    PRIMARY KEY (decision_id, concept_id)
);

CREATE TABLE audience_concept (
    audience_id UUID NOT NULL REFERENCES audience(id),
    concept_id  UUID NOT NULL REFERENCES concept(id),
    PRIMARY KEY (audience_id, concept_id)
);

CREATE TABLE audience_hypothesis (
    audience_id   UUID NOT NULL REFERENCES audience(id),
    hypothesis_id UUID NOT NULL REFERENCES hypothesis(id),
    PRIMARY KEY (audience_id, hypothesis_id)
);

CREATE INDEX idx_performance_publication ON performance(publication_id);
CREATE INDEX idx_performance_observed_at ON performance(observed_at);
CREATE INDEX idx_experiment_arm_experiment ON experiment_arm(experiment_id);
CREATE INDEX idx_learning_status ON learning(status);
CREATE INDEX idx_evidence_observed_at ON evidence(observed_at);
CREATE INDEX idx_publication_published_at ON publication(published_at);

COMMIT;
