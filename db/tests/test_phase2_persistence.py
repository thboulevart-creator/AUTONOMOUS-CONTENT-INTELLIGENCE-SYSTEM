"""
Phase 2 — Core Persistence + Provenance integration tests.
All tests execute against real PostgreSQL.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
import psycopg2
from psycopg2 import errors

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.persistence.connection import get_connection, transaction
from src.persistence.repositories import (
    EvidenceRepository,
    LearningRepository,
    PerformanceRepository,
    ExperimentRepository,
    DecisionRepository,
)


def _helpers(conn):
    cur = conn.cursor()
    plat = str(uuid4())
    cur.execute("INSERT INTO platform (id, name) VALUES (%s, %s)", (plat, f"p-{plat[:8]}"))
    acc = str(uuid4())
    cur.execute("INSERT INTO account (id, platform_id, name) VALUES (%s, %s, %s)", (acc, plat, f"a-{acc[:8]}"))
    content = str(uuid4())
    cur.execute("INSERT INTO content (id, artifact_ref) VALUES (%s, %s)", (content, f"art-{content[:8]}"))
    pv = str(uuid4())
    cur.execute("INSERT INTO platform_version (id, content_id, platform_id, adaptation_payload) VALUES (%s, %s, %s, %s)", (pv, content, plat, "{}"))
    pub = str(uuid4())
    cur.execute("INSERT INTO publication (id, platform_version_id, account_id, published_at) VALUES (%s, %s, %s, now())", (pub, pv, acc))
    return {"platform": plat, "account": acc, "content": content, "publication": pub}


@pytest.fixture
def conn(db):
    yield db


def test_persist_01_evidence_create_read(conn):
    repo = EvidenceRepository(conn)
    now = datetime.now(timezone.utc)
    created = repo.create(source_type="test", raw_payload={"k": "v"}, observed_at=now, source_ref="ref-1", collection_context={"independence": "unknown"})
    got = repo.get_by_id(created["id"])
    assert got is not None
    assert got["source_type"] == "test"
    assert got["source_ref"] == "ref-1"
    assert got["raw_payload"] == {"k": "v"}
    assert got["collection_context"] == {"independence": "unknown"}


def test_persist_02_evidence_jsonb_roundtrip(conn):
    repo = EvidenceRepository(conn)
    ctx = {"a": 1, "nested": {"x": [1, 2, 3]}, "unknown_key": True}
    created = repo.create(source_type="jsonb", raw_payload={"payload": True}, observed_at=datetime.now(timezone.utc), collection_context=ctx)
    got = repo.get_by_id(created["id"])
    assert got["collection_context"] == ctx


def test_persist_03_evidence_soft_delete(conn):
    repo = EvidenceRepository(conn)
    created = repo.create(source_type="soft", raw_payload={}, observed_at=datetime.now(timezone.utc))
    eid = created["id"]
    repo.soft_delete(eid)
    assert repo.get_by_id(eid) is None
    hist = repo.get_by_id(eid, include_deleted=True)
    assert hist is not None
    assert hist["deleted_at"] is not None


def test_persist_04_learning_create_read(conn):
    repo = LearningRepository(conn)
    created = repo.create(claim="c1", status="active", confidence=0.5)
    got = repo.get_by_id(created["id"])
    assert got["claim"] == "c1"
    assert got["status"] == "active"
    assert float(got["confidence"]) == 0.5


def test_persist_05_learning_provenance_multiple(conn):
    ev = EvidenceRepository(conn)
    lr = LearningRepository(conn)
    e1 = ev.create(source_type="a", raw_payload={}, observed_at=datetime.now(timezone.utc))
    e2 = ev.create(source_type="b", raw_payload={}, observed_at=datetime.now(timezone.utc))
    learning = lr.create(claim="multi", status="active")
    lr.add_provenance(learning_id=learning["id"], source_type="evidence", source_id=e1["id"])
    lr.add_provenance(learning_id=learning["id"], source_type="evidence", source_id=e2["id"])
    prov = lr.get_provenance(learning["id"])
    assert len(prov) == 2
    source_ids = {str(p["source_id"]) for p in prov}
    assert str(e1["id"]) in source_ids
    assert str(e2["id"]) in source_ids


def test_persist_06_learning_status_history(conn):
    lr = LearningRepository(conn)
    learning = lr.create(claim="hist", status="active")
    lr.record_status(learning_id=learning["id"], from_status="active", to_status="contested", reason="conflict")
    lr.record_status(learning_id=learning["id"], from_status="contested", to_status="rehabilitated", reason="resolved")
    hist = lr.get_status_history(learning["id"])
    statuses = [h["to_status"] for h in hist]
    assert statuses[0] == "active"
    assert "contested" in statuses
    assert statuses[-1] == "rehabilitated"


def test_persist_07_experiment_create_read(conn):
    repo = ExperimentRepository(conn)
    design = {"closure": "predeclared", "metric": "ctr"}
    created = repo.create(experiment_type="exploratory", design=design)
    got = repo.get_by_id(created["id"])
    assert got["experiment_type"] == "exploratory"
    assert got["design"] == design


def test_persist_08_experiment_arms_valid(conn):
    cur = conn.cursor()
    c1, c2 = str(uuid4()), str(uuid4())
    cur.execute("INSERT INTO content (id, artifact_ref) VALUES (%s, %s)", (c1, "c1"))
    cur.execute("INSERT INTO content (id, artifact_ref) VALUES (%s, %s)", (c2, "c2"))
    repo = ExperimentRepository(conn)
    exp = repo.create(experiment_type="controlled")
    repo.add_arm(experiment_id=exp["id"], arm_type="baseline", content_id=c1)
    repo.add_arm(experiment_id=exp["id"], arm_type="intervention", content_id=c2)
    conn.commit()
    arms = repo.get_arms(exp["id"])
    types = {a["arm_type"] for a in arms}
    assert types == {"baseline", "intervention"}


def test_persist_09_performance_append(conn):
    ids = _helpers(conn)
    repo = PerformanceRepository(conn)
    p1 = repo.append(publication_id=ids["publication"], observed_at="2026-01-01 10:00:00+00", metrics={"views": 1})
    p2 = repo.append(publication_id=ids["publication"], observed_at="2026-01-01 11:00:00+00", metrics={"views": 2})
    rows = repo.list_for_publication(ids["publication"])
    assert len(rows) == 2
    assert str(p1["id"]) != str(p2["id"])


def test_persist_10_performance_no_update_api(conn):
    assert not hasattr(PerformanceRepository, "update")
    ids = _helpers(conn)
    repo = PerformanceRepository(conn)
    p = repo.append(publication_id=ids["publication"], observed_at=datetime.now(timezone.utc), metrics={"views": 1})
    cur = conn.cursor()
    with pytest.raises(Exception) as exc:
        cur.execute("UPDATE performance SET metrics = %s WHERE id = %s", ('{"views": 999}', str(p["id"])))
        conn.commit()
    assert "append-only" in str(exc.value).lower() or "forbidden" in str(exc.value).lower()


def test_persist_11_decision_create_read(conn):
    repo = DecisionRepository(conn)
    created = repo.create(decision_type="explore", rationale="test")
    got = repo.get_by_id(created["id"])
    assert got["decision_type"] == "explore"
    assert got["rationale"] == "test"


def test_persist_12_junction_evidence_learning(conn):
    ev = EvidenceRepository(conn)
    lr = LearningRepository(conn)
    e = ev.create(source_type="j", raw_payload={}, observed_at=datetime.now(timezone.utc))
    learning = lr.create(claim="j", status="active")
    lr.link_evidence(learning["id"], e["id"])
    linked = lr.get_linked_evidence_ids(learning["id"])
    assert str(e["id"]) in linked


def test_persist_13_transaction_rollback(conn):
    outer = get_connection()
    try:
        with pytest.raises(Exception):
            with transaction(outer):
                ev = EvidenceRepository(outer)
                e = ev.create(source_type="tx", raw_payload={}, observed_at=datetime.now(timezone.utc))
                cur = outer.cursor()
                cur.execute("INSERT INTO account (id, platform_id, name) VALUES (%s, %s, %s)", (str(uuid4()), str(uuid4()), "orphan"))
        check = get_connection()
        try:
            cur = check.cursor()
            cur.execute("SELECT COUNT(*) FROM evidence WHERE source_type = 'tx'")
            assert cur.fetchone()[0] == 0
        finally:
            check.close()
    finally:
        outer.close()


def test_persist_14_provenance_traversal(conn):
    ev = EvidenceRepository(conn)
    lr = LearningRepository(conn)
    e = ev.create(source_type="trav", raw_payload={}, observed_at=datetime.now(timezone.utc))
    learning = lr.create(claim="trav", status="active")
    lr.link_evidence(learning["id"], e["id"])
    lr.add_provenance(learning_id=learning["id"], source_type="evidence", source_id=e["id"])
    prov = lr.get_provenance(learning["id"])
    assert any(str(p["source_id"]) == str(e["id"]) for p in prov)
    linked = lr.get_linked_evidence_ids(learning["id"])
    assert str(e["id"]) in linked


def test_persist_15_missing_ancestry_no_fabrication(conn):
    ev = EvidenceRepository(conn)
    lr = LearningRepository(conn)
    e = ev.create(source_type="alone", raw_payload={}, observed_at=datetime.now(timezone.utc))
    learning = lr.create(claim="alone", status="active")
    linked = lr.get_linked_evidence_ids(learning["id"])
    assert str(e["id"]) not in linked
    prov = lr.get_provenance(learning["id"])
    assert all(str(p["source_id"]) != str(e["id"]) for p in prov)


def test_adv_persist_01_no_hard_delete_api(conn):
    assert not hasattr(EvidenceRepository, "hard_delete")
    assert not hasattr(EvidenceRepository, "delete")


def test_adv_persist_02_performance_overwrite_rejected(conn):
    ids = _helpers(conn)
    repo = PerformanceRepository(conn)
    p = repo.append(publication_id=ids["publication"], observed_at=datetime.now(timezone.utc), metrics={"v": 1})
    cur = conn.cursor()
    with pytest.raises(Exception):
        cur.execute("UPDATE performance SET metrics = '{}' WHERE id = %s", (str(p["id"]),))
        conn.commit()


def test_adv_persist_03_performance_duplicate_rejected(conn):
    ids = _helpers(conn)
    repo = PerformanceRepository(conn)
    ts = "2026-03-01 12:00:00+00"
    repo.append(publication_id=ids["publication"], observed_at=ts, metrics={"v": 1})
    with pytest.raises(errors.UniqueViolation):
        repo.append(publication_id=ids["publication"], observed_at=ts, metrics={"v": 2})
        conn.commit()


def test_adv_persist_04_invalid_fk_rejected(conn):
    with pytest.raises(errors.ForeignKeyViolation):
        cur = conn.cursor()
        cur.execute("INSERT INTO account (id, platform_id, name) VALUES (%s, %s, %s)", (str(uuid4()), str(uuid4()), "orphan"))
        conn.commit()


def test_adv_persist_05_jsonb_unknown_fields_survive(conn):
    repo = EvidenceRepository(conn)
    payload = {"known": 1, "totally_unknown_xyz": {"deep": True}}
    created = repo.create(source_type="jsonb-adv", raw_payload=payload, observed_at=datetime.now(timezone.utc))
    got = repo.get_by_id(created["id"])
    assert got["raw_payload"] == payload


def test_adv_persist_06_no_fake_provenance(conn):
    ev = EvidenceRepository(conn)
    lr = LearningRepository(conn)
    e = ev.create(source_type="nofake", raw_payload={}, observed_at=datetime.now(timezone.utc))
    learning = lr.create(claim="nofake", status="active")
    assert lr.get_linked_evidence_ids(learning["id"]) == []
    assert lr.get_provenance(learning["id"]) == []


def test_adv_persist_07_transaction_atomicity(conn):
    outer = get_connection()
    try:
        with pytest.raises(Exception):
            with transaction(outer):
                lr = LearningRepository(outer)
                learning = lr.create(claim="partial", status="active")
                cur = outer.cursor()
                cur.execute("INSERT INTO learning_provenance (id, learning_id, source_type, source_id) VALUES (%s, %s, %s, %s)", (str(uuid4()), str(learning["id"]), "invalid_type", str(uuid4())))
        check = get_connection()
        try:
            cur = check.cursor()
            cur.execute("SELECT COUNT(*) FROM learning WHERE claim = 'partial'")
            assert cur.fetchone()[0] == 0
        finally:
            check.close()
    finally:
        outer.close()


def test_adv_persist_08_direct_path_no_pipeline(conn):
    ev = EvidenceRepository(conn)
    lr = LearningRepository(conn)
    e = ev.create(source_type="direct", raw_payload={}, observed_at=datetime.now(timezone.utc))
    learning = lr.create(claim="direct", status="active")
    lr.link_evidence(learning["id"], e["id"])
    assert lr.get_linked_evidence_ids(learning["id"]) == [str(e["id"])]


def test_postgres_backend(conn):
    cur = conn.cursor()
    cur.execute("SELECT version()")
    version = cur.fetchone()[0]
    assert "PostgreSQL" in version
