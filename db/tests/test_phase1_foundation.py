"""
Phase 1 — PostgreSQL Foundation V0.1
Database conformance tests derived from LOCKED Logical Data Schema + Operational Specification.
"""
import pytest
import psycopg2
from psycopg2 import errors
from uuid import uuid4


def _insert_platform(cur):
    pid = str(uuid4())
    cur.execute(
        "INSERT INTO platform (id, name) VALUES (%s, %s) RETURNING id;",
        (pid, f"plat-{pid[:8]}"),
    )
    return cur.fetchone()[0]


def _insert_account(cur, platform_id):
    aid = str(uuid4())
    cur.execute(
        "INSERT INTO account (id, platform_id, name) VALUES (%s, %s, %s) RETURNING id;",
        (aid, platform_id, f"acc-{aid[:8]}"),
    )
    return cur.fetchone()[0]


def _insert_content(cur):
    cid = str(uuid4())
    cur.execute(
        "INSERT INTO content (id, artifact_ref) VALUES (%s, %s) RETURNING id;",
        (cid, f"artifact-{cid[:8]}"),
    )
    return cur.fetchone()[0]


def _insert_platform_version(cur, content_id, platform_id):
    pvid = str(uuid4())
    cur.execute(
        "INSERT INTO platform_version (id, content_id, platform_id, adaptation_payload) VALUES (%s, %s, %s, %s) RETURNING id;",
        (pvid, content_id, platform_id, "{}"),
    )
    return cur.fetchone()[0]


def _insert_publication(cur, platform_version_id, account_id):
    pubid = str(uuid4())
    cur.execute(
        "INSERT INTO publication (id, platform_version_id, account_id, published_at) VALUES (%s, %s, %s, now()) RETURNING id;",
        (pubid, platform_version_id, account_id),
    )
    return cur.fetchone()[0]


def _insert_experiment(cur, exp_type="exploratory"):
    eid = str(uuid4())
    cur.execute(
        "INSERT INTO experiment (id, experiment_type, status) VALUES (%s, %s, %s) RETURNING id;",
        (eid, exp_type, "draft"),
    )
    return cur.fetchone()[0]


def test_db_fk_01_invalid_fk_rejected(db):
    """Requirement: All typed FKs (Logical Data Schema). Attack: invalid platform_id. Expected: FK violation."""
    cur = db.cursor()
    with pytest.raises(errors.ForeignKeyViolation):
        cur.execute(
            "INSERT INTO account (id, platform_id, name) VALUES (%s, %s, %s);",
            (str(uuid4()), str(uuid4()), "orphan"),
        )
        db.commit()


def test_db_perf_01_insert_allowed(db):
    """Requirement: INV-12 / LDS — new snapshot can be inserted."""
    cur = db.cursor()
    plat = _insert_platform(cur)
    acc = _insert_account(cur, plat)
    content = _insert_content(cur)
    pv = _insert_platform_version(cur, content, plat)
    pub = _insert_publication(cur, pv, acc)
    cur.execute(
        "INSERT INTO performance (id, publication_id, observed_at, metrics) VALUES (%s, %s, now(), %s);",
        (str(uuid4()), pub, '{"views": 1}'),
    )
    db.commit()


def test_db_perf_01_duplicate_timestamp_rejected(db):
    """Requirement: UNIQUE(publication_id, observed_at)."""
    cur = db.cursor()
    plat = _insert_platform(cur)
    acc = _insert_account(cur, plat)
    content = _insert_content(cur)
    pv = _insert_platform_version(cur, content, plat)
    pub = _insert_publication(cur, pv, acc)
    ts = "2026-01-01 12:00:00+00"
    cur.execute(
        "INSERT INTO performance (id, publication_id, observed_at, metrics) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), pub, ts, '{"views": 1}'),
    )
    with pytest.raises(errors.UniqueViolation):
        cur.execute(
            "INSERT INTO performance (id, publication_id, observed_at, metrics) VALUES (%s, %s, %s, %s);",
            (str(uuid4()), pub, ts, '{"views": 2}'),
        )
        db.commit()


def test_db_perf_01_update_rejected(db):
    """Requirement: INV-12 append-only — UPDATE forbidden."""
    cur = db.cursor()
    plat = _insert_platform(cur)
    acc = _insert_account(cur, plat)
    content = _insert_content(cur)
    pv = _insert_platform_version(cur, content, plat)
    pub = _insert_publication(cur, pv, acc)
    perf_id = str(uuid4())
    cur.execute(
        "INSERT INTO performance (id, publication_id, observed_at, metrics) VALUES (%s, %s, now(), %s);",
        (perf_id, pub, '{"views": 1}'),
    )
    db.commit()
    with pytest.raises(Exception) as exc:
        cur.execute(
            "UPDATE performance SET metrics = %s WHERE id = %s;",
            ('{"views": 999}', perf_id),
        )
        db.commit()
    assert "append-only" in str(exc.value).lower() or "forbidden" in str(exc.value).lower()


def test_db_perf_01_upsert_cannot_overwrite(db):
    """Requirement: UPSERT must not overwrite existing observation."""
    cur = db.cursor()
    plat = _insert_platform(cur)
    acc = _insert_account(cur, plat)
    content = _insert_content(cur)
    pv = _insert_platform_version(cur, content, plat)
    pub = _insert_publication(cur, pv, acc)
    ts = "2026-02-01 10:00:00+00"
    cur.execute(
        "INSERT INTO performance (id, publication_id, observed_at, metrics) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), pub, ts, '{"views": 1}'),
    )
    db.commit()
    with pytest.raises(Exception):
        cur.execute(
            """
            INSERT INTO performance (id, publication_id, observed_at, metrics)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (publication_id, observed_at)
            DO UPDATE SET metrics = EXCLUDED.metrics;
            """,
            (str(uuid4()), pub, ts, '{"views": 999}'),
        )
        db.commit()


def test_db_arm_01_xor_both_rejected(db):
    cur = db.cursor()
    exp = _insert_experiment(cur, "exploratory")
    content = _insert_content(cur)
    concept_id = str(uuid4())
    cur.execute("INSERT INTO concept (id, title) VALUES (%s, %s);", (concept_id, "c"))
    variant_id = str(uuid4())
    cur.execute(
        "INSERT INTO variant (id, concept_id, name, variation_definition) VALUES (%s, %s, %s, %s);",
        (variant_id, concept_id, "v", "{}"),
    )
    with pytest.raises(errors.CheckViolation):
        cur.execute(
            "INSERT INTO experiment_arm (id, experiment_id, arm_type, variant_id, content_id) VALUES (%s, %s, %s, %s, %s);",
            (str(uuid4()), exp, "intervention", variant_id, content),
        )
        db.commit()


def test_db_arm_01_xor_neither_rejected(db):
    cur = db.cursor()
    exp = _insert_experiment(cur, "exploratory")
    with pytest.raises(errors.CheckViolation):
        cur.execute(
            "INSERT INTO experiment_arm (id, experiment_id, arm_type) VALUES (%s, %s, %s);",
            (str(uuid4()), exp, "intervention"),
        )
        db.commit()


def test_db_arm_01_invalid_arm_type_rejected(db):
    cur = db.cursor()
    exp = _insert_experiment(cur, "exploratory")
    content = _insert_content(cur)
    with pytest.raises(errors.CheckViolation):
        cur.execute(
            "INSERT INTO experiment_arm (id, experiment_id, arm_type, content_id) VALUES (%s, %s, %s, %s);",
            (str(uuid4()), exp, "control", content),
        )
        db.commit()


def test_db_arm_01_controlled_no_baseline_rejected(db):
    cur = db.cursor()
    exp = _insert_experiment(cur, "controlled")
    content = _insert_content(cur)
    cur.execute(
        "INSERT INTO experiment_arm (id, experiment_id, arm_type, content_id) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), exp, "intervention", content),
    )
    with pytest.raises(Exception) as exc:
        db.commit()
    assert "baseline" in str(exc.value).lower()


def test_db_arm_01_controlled_two_baselines_rejected(db):
    cur = db.cursor()
    exp = _insert_experiment(cur, "controlled")
    c1 = _insert_content(cur)
    c2 = _insert_content(cur)
    c3 = _insert_content(cur)
    cur.execute(
        "INSERT INTO experiment_arm (id, experiment_id, arm_type, content_id) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), exp, "baseline", c1),
    )
    cur.execute(
        "INSERT INTO experiment_arm (id, experiment_id, arm_type, content_id) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), exp, "baseline", c2),
    )
    cur.execute(
        "INSERT INTO experiment_arm (id, experiment_id, arm_type, content_id) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), exp, "intervention", c3),
    )
    with pytest.raises(Exception) as exc:
        db.commit()
    assert "baseline" in str(exc.value).lower()


def test_db_arm_01_controlled_valid(db):
    cur = db.cursor()
    exp = _insert_experiment(cur, "controlled")
    c1 = _insert_content(cur)
    c2 = _insert_content(cur)
    cur.execute(
        "INSERT INTO experiment_arm (id, experiment_id, arm_type, content_id) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), exp, "baseline", c1),
    )
    cur.execute(
        "INSERT INTO experiment_arm (id, experiment_id, arm_type, content_id) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), exp, "intervention", c2),
    )
    db.commit()


def test_db_arm_01_exploratory_no_baseline_allowed(db):
    cur = db.cursor()
    exp = _insert_experiment(cur, "exploratory")
    content = _insert_content(cur)
    cur.execute(
        "INSERT INTO experiment_arm (id, experiment_id, arm_type, content_id) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), exp, "intervention", content),
    )
    db.commit()


def test_db_soft_01_soft_deleted_row_still_present(db):
    cur = db.cursor()
    eid = str(uuid4())
    cur.execute(
        "INSERT INTO evidence (id, source_type, raw_payload, observed_at, deleted_at) VALUES (%s, %s, %s, now(), now()) RETURNING id;",
        (eid, "test", "{}"),
    )
    cur.execute("SELECT id, deleted_at FROM evidence WHERE id = %s;", (eid,))
    row = cur.fetchone()
    assert row is not None
    assert row[1] is not None


def test_db_soft_01_no_cascade_destroy(db):
    cur = db.cursor()
    lid = str(uuid4())
    cur.execute(
        "INSERT INTO learning (id, claim, status, version) VALUES (%s, %s, %s, 1);",
        (lid, "claim", "active"),
    )
    cur.execute(
        "INSERT INTO learning_provenance (id, learning_id, source_type, source_id) VALUES (%s, %s, %s, %s);",
        (str(uuid4()), lid, "evidence", str(uuid4())),
    )
    cur.execute("UPDATE learning SET deleted_at = now() WHERE id = %s;", (lid,))
    cur.execute("SELECT COUNT(*) FROM learning WHERE id = %s;", (lid,))
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT COUNT(*) FROM learning_provenance WHERE learning_id = %s;", (lid,))
    assert cur.fetchone()[0] == 1
    db.commit()


def test_db_status_01_valid_statuses(db):
    cur = db.cursor()
    for status in ("active", "saturated", "deprecated", "contested", "rehabilitated"):
        cur.execute(
            "INSERT INTO learning (id, claim, status, version) VALUES (%s, %s, %s, 1);",
            (str(uuid4()), f"claim-{status}", status),
        )
    db.commit()


def test_db_status_01_invalid_status_rejected(db):
    cur = db.cursor()
    with pytest.raises(Exception):
        cur.execute(
            "INSERT INTO learning (id, claim, status, version) VALUES (%s, %s, %s, 1);",
            (str(uuid4()), "bad", "provisional"),
        )
        db.commit()


def test_db_path_01_direct_evidence_to_learning(db):
    """INV-13 path-dependent: direct Evidence → Learning without intermediates."""
    cur = db.cursor()
    eid = str(uuid4())
    cur.execute(
        "INSERT INTO evidence (id, source_type, raw_payload, observed_at) VALUES (%s, %s, %s, now());",
        (eid, "test", "{}"),
    )
    lid = str(uuid4())
    cur.execute(
        "INSERT INTO learning (id, claim, status, version) VALUES (%s, %s, %s, 1);",
        (lid, "direct", "active"),
    )
    cur.execute(
        "INSERT INTO evidence_learning (evidence_id, learning_id) VALUES (%s, %s);",
        (eid, lid),
    )
    db.commit()


def test_db_path_01_direct_performance_to_learning(db):
    cur = db.cursor()
    plat = _insert_platform(cur)
    acc = _insert_account(cur, plat)
    content = _insert_content(cur)
    pv = _insert_platform_version(cur, content, plat)
    pub = _insert_publication(cur, pv, acc)
    perf = str(uuid4())
    cur.execute(
        "INSERT INTO performance (id, publication_id, observed_at, metrics) VALUES (%s, %s, now(), %s);",
        (perf, pub, "{}"),
    )
    lid = str(uuid4())
    cur.execute(
        "INSERT INTO learning (id, claim, status, version) VALUES (%s, %s, %s, 1);",
        (lid, "from-perf", "active"),
    )
    cur.execute(
        "INSERT INTO performance_learning (performance_id, learning_id) VALUES (%s, %s);",
        (perf, lid),
    )
    db.commit()


def test_no_forbidden_tables(db):
    """Confirm no tables for forbidden first-class entities."""
    cur = db.cursor()
    forbidden = [
        "context", "signal", "observation", "baseline", "intervention",
        "knowledge_claim", "metric", "score", "analysis", "inference",
        "model", "policy", "goal", "constraint", "resource", "saturation",
        "independence", "confounder", "materiality", "exploration",
    ]
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
    tables = {r[0] for r in cur.fetchall()}
    for name in forbidden:
        assert name not in tables, f"Forbidden table '{name}' must not exist"
