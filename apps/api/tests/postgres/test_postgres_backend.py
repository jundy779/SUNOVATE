"""PostgreSQL-only guarantees (design 15.5). Runs only under `pnpm db:test`.

Every test starts from a fresh TRUNCATE + SIMULATED_DATA seed (autouse fixture in
tests/conftest.py). Direct SQL is used only to observe the database, never to replace
an API assertion.
"""

from __future__ import annotations

import re
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import fields
from datetime import datetime
from typing import Any
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, insert, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from sunovate_api.context import build_runtime
from sunovate_api.core.errors import ApiError
from sunovate_api.db import models as m
from sunovate_api.main import create_app
from sunovate_api.store.dataset import SEED_TIME, build_dataset, sid
from sunovate_api.store.postgres import PostgresBackend, PostgresRepository
from sunovate_api.store.records import (
    ApprovalRequest,
    DocumentChunk,
    DocumentReference,
    DocumentVersion,
    KnowledgeEntry,
    Record,
    Task,
    utcnow,
)
from sunovate_api.testing import (
    TEST_DATABASE_URL,
    login,
    make_client,
    make_settings,
    requires_postgres,
    shared_postgres_backend,
)

pytestmark = requires_postgres

API = "/api/v1"
OWNER = "sim.owner.ppsun"
PERSONAS = [
    "sim.admin",
    "sim.coordinator",
    "sim.owner.ppsun",
    "sim.lead.psun",
    "sim.staff.pppsun",
    "sim.reviewer.akpsun",
    "sim.auditor",
    "sim.readonly.dhtv",
]
PPSUN = sid("team:PPSUN")
DOC_K1, DOC_K2 = sid("doc:K1"), sid("doc:K2")
T4 = sid("task:T4")
APPROVAL_K7 = sid("approval:K7")
STAFF_ID = sid("user:sim.staff.pppsun")
DUPLICATE_MESSAGE = "Versi dengan checksum yang sama sudah terdaftar"


# Helpers -----------------------------------------------------------------------------


def _backend() -> PostgresBackend:
    return shared_postgres_backend()


def _scalar(sql: str, **params: object) -> Any:
    """Observe the database directly (bound parameters only)."""
    with _backend().engine.connect() as conn:
        return conn.execute(text(sql), params).scalar_one()


def _create_knowledge(
    client: TestClient, headers: dict[str, str], **overrides: Any
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": "SIMULASI - Draf uji backend postgres",
        "knowledgeType": "LESSON_LEARNED",
        "summary": "Ringkasan simulasi untuk pengujian backend postgres.",
        "classificationCode": "INTERNAL",
        "sharingScope": "DIRECTORATE",
        "ownerTeamId": str(PPSUN),
    }
    payload.update(overrides)
    response = client.post(f"{API}/knowledge", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    data: dict[str, Any] = response.json()["data"]
    return data


def _seed_ids() -> frozenset[UUID]:
    """Every UUID that occurs in the SIMULATED_DATA dataset (ids and references)."""
    found: set[UUID] = set()
    dataset = build_dataset()
    for dataset_field in fields(dataset):
        for item in getattr(dataset, dataset_field.name):
            values = (
                item if isinstance(item, tuple) else [getattr(item, f.name) for f in fields(item)]
            )
            found.update(v for v in values if isinstance(v, UUID))
    return frozenset(found)


SEED_IDS = _seed_ids()
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")
_VOLATILE_KEYS = frozenset({"accessToken", "expiresAt", "requestId"})


class _Normalizer:
    """NIT 13: placeholders for tokens, request ids, non-seed UUIDs and non-seed times."""

    def __init__(self) -> None:
        self._new: dict[str, str] = {}

    def __call__(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: f"<{key}>" if key in _VOLATILE_KEYS else self(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self(item) for item in value]
        if isinstance(value, str):
            if _UUID_RE.match(value) and UUID(value) not in SEED_IDS:
                return self._new.setdefault(value, f"<new-{len(self._new) + 1}>")
            if _TIMESTAMP_RE.match(value) and datetime.fromisoformat(value) != SEED_TIME:
                return "<ts>"
        return value


def _row(record: Record, model: type[m.Base]) -> dict[str, Any]:
    """Dataclass -> insert row (same rule as db/seed.py; no computed or identity columns)."""
    columns = {c.key for c in model.__table__.columns if c.computed is None and c.identity is None}
    return {f.name: getattr(record, f.name) for f in fields(record) if f.name in columns}


@contextmanager
def _count_statements() -> Iterator[list[str]]:
    statements: list[str] = []

    def listener(*args: Any) -> None:
        statements.append(str(args[2]))

    engine = _backend().engine
    event.listen(engine, "before_cursor_execute", listener)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", listener)


# AC-01.1, AC-01.5: backend selection and persistence ---------------------------------


def test_health_reports_postgres_backend() -> None:
    body = make_client().get(f"{API}/health").json()
    assert body["data"]["dataBackend"] == "postgres"
    assert body["meta"]["dataLabel"] == "SIMULATED_DATA"


def test_data_survives_a_new_backend_and_app() -> None:
    client = make_client()
    entry = _create_knowledge(client, login(client, OWNER))

    assert TEST_DATABASE_URL
    fresh = PostgresBackend(TEST_DATABASE_URL)  # separate engine/pool, nothing shared
    try:
        settings = make_settings()
        other = TestClient(create_app(settings, build_runtime(settings, backend=fresh)))
        response = other.get(f"{API}/knowledge/{entry['id']}", headers=login(other, OWNER))
        assert response.status_code == 200, response.text
        assert response.json()["data"]["title"] == entry["title"]
        assert response.json()["data"]["revision"] == 1
    finally:
        fresh.dispose()


# Mandatory constraint mapping (design 10.2, review MEDIUM): M1-M4 ----------------------


def test_duplicate_checksum_constraint_maps_to_409() -> None:
    """M1: repository level, no API pre-check involved."""
    backend = _backend()
    with backend.session() as repo:
        versions = repo.versions_of(DOC_K2)
    seed_version = versions[0]
    with backend.session() as repo, pytest.raises(ApiError) as caught, repo.transaction():
        repo.insert(
            DocumentVersion(
                document_reference_id=seed_version.document_reference_id,
                version_label="dup",
                checksum_sha256=seed_version.checksum_sha256,
                provider_location="local://simulated/dup.pdf",
                data_origin="USER_ENTERED",
            )
        )
    assert (caught.value.status_code, caught.value.code) == (409, "DUPLICATE_CHECKSUM")
    assert caught.value.message == DUPLICATE_MESSAGE
    with backend.session() as repo:
        assert len(repo.versions_of(DOC_K2)) == len(versions)


def test_separation_of_duties_constraint_maps_to_403() -> None:
    """M2: repository level; decided_by = requested_by is written directly."""
    backend = _backend()
    with backend.session() as repo:
        approval = repo.get_governed(ApprovalRequest, APPROVAL_K7)
    assert approval is not None and approval.status == "PENDING"
    with backend.session() as repo, pytest.raises(ApiError) as caught, repo.transaction():
        repo.update_revisioned(
            ApprovalRequest,
            approval.id,
            expected_revision=approval.revision,
            changes={
                "status": "APPROVED",
                "decided_by": approval.requested_by,
                "decided_at": utcnow(),
                "decision_reason": "uji",
            },
            actor_id=approval.requested_by,
            expected_state={"status": "PENDING"},
        )
    assert (caught.value.status_code, caught.value.code) == (403, "SEPARATION_OF_DUTIES")
    with backend.session() as repo:
        after = repo.get_governed(ApprovalRequest, approval.id)
    assert after is not None
    assert (after.status, after.revision, after.decided_by) == ("PENDING", approval.revision, None)


def test_duplicate_checksum_race_returns_409_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    """M3: the API duplicate pre-check is bypassed; the UNIQUE constraint answers."""
    client = make_client()
    owner = login(client, OWNER)
    versions = client.get(f"{API}/documents/{DOC_K2}/versions", headers=owner).json()["data"]
    count_versions = "SELECT count(*) FROM document_versions WHERE document_reference_id = :d"
    count_audit = "SELECT count(*) FROM audit_logs WHERE action = 'VERSION_REGISTER'"
    versions_before, audit_before = _scalar(count_versions, d=DOC_K2), _scalar(count_audit)

    pre_checks: list[UUID] = []

    def no_versions(self: PostgresRepository, document_id: UUID) -> list[DocumentVersion]:
        pre_checks.append(document_id)
        return []  # the race: the pre-check sees no version yet

    monkeypatch.setattr(PostgresRepository, "versions_of", no_versions)
    response = client.post(
        f"{API}/documents/{DOC_K2}/versions",
        headers=owner,
        json={
            "versionLabel": "v9",
            "checksumSha256": versions[0]["checksumSha256"],
            "providerLocation": "local://simulated/k2-race.pdf",
        },
    )
    assert pre_checks == [DOC_K2]  # the API pre-check ran and found nothing: DB answered
    assert response.status_code == 409, response.text
    body = response.json()
    assert body["code"] == "DUPLICATE_CHECKSUM"
    assert body["message"] == DUPLICATE_MESSAGE
    assert body["details"] is None
    assert body["requestId"]
    # Rolled back: no version row and no success audit row.
    assert _scalar(count_versions, d=DOC_K2) == versions_before
    assert _scalar(count_audit) == audit_before


def test_separation_of_duties_bypass_returns_403_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """M4: the API requester check is bypassed by forging decided_by; the CHECK answers."""
    client = make_client()
    owner = login(client, OWNER)
    entry = _create_knowledge(client, owner)
    submitted = client.post(
        f"{API}/knowledge/{entry['id']}/submit", headers=owner, json={"revision": 1}
    )
    assert submitted.status_code == 200, submitted.text
    approval_id = submitted.json()["data"]["approvalRequestId"]

    original = PostgresRepository.update_revisioned
    forged_ids: list[UUID] = []

    def forged(self: PostgresRepository, kind: Any, record_id: UUID, **kwargs: Any) -> Any:
        if kind is ApprovalRequest:
            current = self.get_governed(ApprovalRequest, record_id)
            assert current is not None
            forged_ids.append(record_id)
            kwargs["changes"] = {**kwargs["changes"], "decided_by": current.requested_by}
        return original(self, kind, record_id, **kwargs)

    monkeypatch.setattr(PostgresRepository, "update_revisioned", forged)
    coordinator = login(client, "sim.coordinator")
    count_approve = "SELECT count(*) FROM audit_logs WHERE action = 'APPROVE'"
    approve_before = _scalar(count_approve)
    response = client.post(
        f"{API}/approvals/{approval_id}/decision",
        headers=coordinator,
        json={"decision": "APPROVE", "revision": 1, "reason": "Lengkap"},
    )
    assert forged_ids == [UUID(approval_id)]  # passed every API check; the CHECK answered
    assert response.status_code == 403, response.text
    body = response.json()
    assert body["code"] == "SEPARATION_OF_DUTIES"
    assert body["message"] == "Pengaju tidak dapat memutuskan permintaannya sendiri"
    assert body["requestId"]
    # Rolled back: approval, knowledge target and audit unchanged.
    with _backend().engine.connect() as conn:
        approval = conn.execute(
            text("SELECT status, revision, decided_by FROM approval_requests WHERE id = :i"),
            {"i": UUID(approval_id)},
        ).one()
        knowledge = conn.execute(
            text("SELECT lifecycle_status, revision FROM knowledge_entries WHERE id = :i"),
            {"i": UUID(entry["id"])},
        ).one()
    assert tuple(approval) == ("PENDING", 1, None)
    assert tuple(knowledge) == ("IN_REVIEW", 2)
    assert _scalar(count_approve) == approve_before


# AC-03.x: concurrency, constraints, atomicity ------------------------------------------


def test_concurrent_revision_updates_have_exactly_one_winner() -> None:
    """AC-03.1: B's UPDATE waits for A's row lock, then sees revision 2 and conflicts."""
    backend = _backend()
    a_updated = threading.Event()
    results: dict[str, object] = {}

    def worker(name: str) -> None:
        try:
            with backend.session() as repo, repo.transaction():
                if name == "B":
                    a_updated.wait(timeout=10)
                task = repo.update_revisioned(
                    Task, T4, expected_revision=1, changes={"progress": 50}, actor_id=STAFF_ID
                )
                if name == "A":
                    a_updated.set()
                    time.sleep(0.3)  # hold the row lock; B is blocked meanwhile
            results[name] = task.revision
        except ApiError as exc:
            results[name] = exc.code
        except BaseException as exc:  # noqa: BLE001 - reported by the assertion below
            results[name] = exc
        finally:
            a_updated.set()  # never leave B waiting if A failed

    threads = [threading.Thread(target=worker, args=(name,)) for name in ("A", "B")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    assert not any(thread.is_alive() for thread in threads)
    assert results == {"A": 2, "B": "REVISION_CONFLICT"}
    assert _scalar("SELECT revision FROM tasks WHERE id = :i", i=T4) == 2


def test_stale_patch_reports_current_revision_from_database() -> None:
    """AC-03.2"""
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    first = client.patch(f"{API}/tasks/{T4}", headers=staff, json={"revision": 1, "progress": 40})
    assert first.status_code == 200, first.text
    stale = client.patch(f"{API}/tasks/{T4}", headers=staff, json={"revision": 1, "progress": 5})
    assert stale.status_code == 409
    assert stale.json()["code"] == "REVISION_CONFLICT"
    current = _scalar("SELECT revision FROM tasks WHERE id = :i", i=T4)
    assert stale.json()["details"] == {"currentRevision": current}
    assert current == 2


def test_duplicate_checksum_is_per_document() -> None:
    """AC-03.3"""
    client = make_client()
    owner = login(client, OWNER)
    checksum = client.get(f"{API}/documents/{DOC_K2}/versions", headers=owner).json()["data"][0][
        "checksumSha256"
    ]
    same_doc = client.post(
        f"{API}/documents/{DOC_K2}/versions",
        headers=owner,
        json={
            "versionLabel": "v1.1",
            "checksumSha256": checksum,
            "providerLocation": "local://simulated/k2-dup.pdf",
        },
    )
    assert same_doc.status_code == 409
    assert same_doc.json()["code"] == "DUPLICATE_CHECKSUM"
    other_doc = client.post(
        f"{API}/documents/{DOC_K1}/versions",
        headers=login(client, "sim.lead.psun"),
        json={
            "versionLabel": "v1.1",
            "checksumSha256": checksum,
            "providerLocation": "local://simulated/k1-v1-1.pdf",
        },
    )
    assert other_doc.status_code == 201, other_doc.text
    assert (
        _scalar("SELECT count(*) FROM document_versions WHERE checksum_sha256 = :c", c=checksum)
        == 2
    )


def test_direct_self_decision_update_violates_check_constraint() -> None:
    """AC-03.4"""
    with pytest.raises(IntegrityError) as caught, _backend().engine.begin() as conn:
        conn.execute(
            text("UPDATE approval_requests SET decided_by = requested_by WHERE id = :i"),
            {"i": APPROVAL_K7},
        )
    orig: Any = caught.value.orig
    assert orig.diag.constraint_name == "ck_approval_requests_separation_of_duties"


def test_failed_submit_rolls_back_every_step(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC-03.5: the approval insert fails after the knowledge update -> nothing is kept."""
    client = make_client(raise_server_exceptions=False)
    owner = login(client, OWNER)
    entry = _create_knowledge(client, owner)
    original = PostgresRepository.insert

    def failing_insert(self: PostgresRepository, record: Record) -> None:
        if isinstance(record, ApprovalRequest):
            raise RuntimeError("simulated insert failure")
        original(self, record)

    monkeypatch.setattr(PostgresRepository, "insert", failing_insert)
    approvals_before = _scalar("SELECT count(*) FROM approval_requests")
    response = client.post(
        f"{API}/knowledge/{entry['id']}/submit", headers=owner, json={"revision": 1}
    )
    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    detail = client.get(f"{API}/knowledge/{entry['id']}", headers=owner).json()["data"]
    assert (detail["lifecycleStatus"], detail["revision"]) == ("DRAFT", 1)
    assert _scalar("SELECT count(*) FROM approval_requests") == approvals_before
    assert _scalar("SELECT count(*) FROM audit_logs WHERE action = 'SUBMIT'") == 0


# AC-02.3, AC-04.x: audit ---------------------------------------------------------------


def test_permission_denial_is_persisted() -> None:
    """AC-02.3: the denial row survives (separate committed connection)."""
    client = make_client()
    sql = (
        "SELECT count(*) FROM audit_logs WHERE action = 'ACCESS_DENIED' AND outcome = 'DENIED'"
        " AND actor_user_id = :u"
    )
    assert _scalar(sql, u=STAFF_ID) == 0
    staff = login(client, "sim.staff.pppsun")
    assert client.get(f"{API}/audit-logs", headers=staff).status_code == 403
    assert _scalar(sql, u=STAFF_ID) == 1


def test_audit_rows_are_persisted_stable_and_append_only() -> None:
    """AC-04.2, D-C9"""
    client = make_client()
    entry = _create_knowledge(client, login(client, OWNER))
    assert (
        _scalar(
            "SELECT count(*) FROM audit_logs WHERE action = 'CREATE' AND entity_id = :i",
            i=UUID(entry["id"]),
        )
        == 1
    )
    auditor = login(client, "sim.auditor")
    first = client.get(f"{API}/audit-logs?pageSize=100", headers=auditor).json()["data"]
    second = client.get(f"{API}/audit-logs?pageSize=100", headers=auditor).json()["data"]
    assert any(item["action"] == "CREATE" and item["entityId"] == entry["id"] for item in first)
    for item in first:
        assert item["createdAt"] == item["updatedAt"] == item["occurredAt"]
    times = {item["id"]: item["occurredAt"] for item in first}
    assert all(times[item["id"]] == item["occurredAt"] for item in second if item["id"] in times)

    assert _scalar("SELECT count(*) FROM audit_logs") > 0
    for statement in ("UPDATE audit_logs SET action = 'TAMPER'", "DELETE FROM audit_logs"):
        with pytest.raises(DBAPIError), _backend().engine.begin() as conn:
            conn.execute(text(statement))
    assert _scalar("SELECT count(*) FROM audit_logs WHERE action = 'TAMPER'") == 0


def _audit_actions(client: TestClient) -> list[tuple[str, str, str]]:
    owner = login(client, OWNER)
    entry = _create_knowledge(client, owner)
    url = f"{API}/knowledge/{entry['id']}"
    assert client.patch(url, headers=owner, json={"revision": 1, "tags": ["c"]}).status_code == 200
    assert client.post(f"{url}/submit", headers=owner, json={"revision": 2}).status_code == 200
    staff = login(client, "sim.staff.pppsun")
    assert client.get(f"{API}/audit-logs", headers=staff).status_code == 403
    assert client.get(f"{API}/search?q=metadata", headers=staff).status_code == 200
    auditor = login(client, "sim.auditor")
    logs = client.get(f"{API}/audit-logs?pageSize=100", headers=auditor).json()["data"]
    return [(log["action"], log["entityType"], log["outcome"]) for log in logs]


def test_audit_order_matches_simulated_backend() -> None:
    """AC-04.3"""
    simulated = _audit_actions(make_client(backend="simulated"))
    postgres = _audit_actions(make_client(backend="postgres"))
    assert postgres == simulated
    assert len(postgres) >= 8


# AC-01.4, AC-02.5, AC-04.4: parity with the simulated backend ----------------------------

_PARITY_PATHS = [
    "/auth/me",
    "/knowledge?pageSize=100",
    f"/knowledge/{sid('knowledge:K1')}",
    f"/knowledge/{sid('knowledge:K2')}",
    f"/knowledge/{sid('knowledge:K3')}",
    f"/knowledge/{sid('knowledge:K7')}",
    "/documents?pageSize=100",
    f"/documents/{DOC_K1}",
    f"/documents/{DOC_K2}/versions",
    "/tasks?pageSize=100",
    "/work-outputs?pageSize=100",
    f"/work-outputs/{sid('wo:WO1')}",
    "/milestones?pageSize=100",
    "/pending-matters?pageSize=100",
    "/follow-ups?pageSize=100",
    "/users?pageSize=100",
    "/teams",
    "/roles",
    "/approvals?pageSize=100",
    "/dashboard/summary",
    "/search?q=metadata",
    "/audit-logs?pageSize=100",
]


def _parity_sequence(client: TestClient) -> list[tuple[str, int, Any]]:
    normalize = _Normalizer()
    results: list[tuple[str, int, Any]] = []
    headers: dict[str, dict[str, str]] = {}
    for persona in PERSONAS:
        response = client.post(
            f"{API}/auth/dev/login", json={"email": f"{persona}@sunovate.local"}
        )
        results.append((f"login {persona}", response.status_code, normalize(response.json())))
        headers[persona] = {"Authorization": f"Bearer {response.json()['data']['accessToken']}"}
    for persona in PERSONAS:
        for path in _PARITY_PATHS:
            response = client.get(f"{API}{path}", headers=headers[persona])
            results.append((f"{persona} {path}", response.status_code, normalize(response.json())))
    created = client.post(
        f"{API}/knowledge",
        headers=headers[OWNER],
        json={
            "title": "SIMULASI - Entri paritas backend",
            "knowledgeType": "LESSON_LEARNED",
            "summary": "Ringkasan simulasi untuk uji paritas backend.",
            "classificationCode": "INTERNAL",
            "ownerTeamId": str(PPSUN),
            "tags": ["paritas", "simulasi"],
        },
    )
    results.append(("create", created.status_code, normalize(created.json())))
    for persona in (OWNER, "sim.staff.pppsun", "sim.auditor"):
        for path in ("/knowledge?pageSize=100", "/audit-logs?pageSize=100"):
            response = client.get(f"{API}{path}", headers=headers[persona])
            results.append(
                (f"after {persona} {path}", response.status_code, normalize(response.json()))
            )
    return results


def test_responses_match_simulated_backend() -> None:
    """AC-01.4, AC-02.5: same requests, same JSON after normalization (NIT 13)."""
    simulated = _parity_sequence(make_client(backend="simulated"))
    postgres = _parity_sequence(make_client(backend="postgres"))
    assert [label for label, _, _ in postgres] == [label for label, _, _ in simulated]
    for expected, actual in zip(simulated, postgres, strict=True):
        assert actual == expected, expected[0]


def _search_results(client: TestClient) -> list[tuple[str, str, int, Any]]:
    results = []
    for persona in PERSONAS:
        headers = login(client, persona)
        for query in ("metadata", "review dokumen hukum", "materi edukasi"):
            response = client.get(f"{API}/search", params={"q": query}, headers=headers)
            results.append((persona, query, response.status_code, response.json()))
    return results


def test_search_matches_simulated_backend_per_persona() -> None:
    """AC-04.4: includes RESTRICTED K3 and DIRECTORATE-shared content."""
    simulated = _search_results(make_client(backend="simulated"))
    postgres = _search_results(make_client(backend="postgres"))
    assert postgres == simulated
    assert any(status == 200 and body["data"] for _, _, status, body in postgres)


# AC-08.2, AC-09.2 ----------------------------------------------------------------------

_BUSINESS_TABLES = [
    "knowledge_entries",
    "document_references",
    "document_versions",
    "document_chunks",
    "tags",
    "knowledge_tags",
    "work_outputs",
    "tasks",
    "milestones",
    "pending_matters",
    "follow_ups",
    "data_quality_issues",
    "users",
    "teams",
]


def _business_counts() -> dict[str, int]:
    # Table names come from the static list above, never from input.
    return {t: int(_scalar(f'SELECT count(*) FROM "{t}"')) for t in _BUSINESS_TABLES}  # noqa: S608


def test_hermes_write_intent_only_creates_a_pending_approval() -> None:
    """AC-08.2: approval row PENDING, executed=false, no other business change."""
    client = make_client()
    owner = login(client, OWNER)
    before = _business_counts()
    response = client.post(
        f"{API}/hermes/query",
        headers=owner,
        json={"question": "Tolong hapus entri SOP pencatatan tindak lanjut rapat"},
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["decision"] == "REQUIRES_HUMAN_APPROVAL"
    with _backend().engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT status, request_type, payload->>'executed' FROM approval_requests"
                " WHERE id = :i"
            ),
            {"i": UUID(data["approvalRequestId"])},
        ).one()
    assert tuple(row) == ("PENDING", "HERMES_WRITE_ACTION", "false")
    assert _business_counts() == before
    k7 = "SELECT revision FROM knowledge_entries WHERE id = :i AND deleted_at IS NULL"
    assert _scalar(k7, i=sid("knowledge:K7")) == 1


def test_patch_tags_replaces_old_rows() -> None:
    """AC-09.2"""
    client = make_client()
    owner = login(client, OWNER)
    entry = _create_knowledge(client, owner, tags=["a", "b"])
    response = client.patch(
        f"{API}/knowledge/{entry['id']}", headers=owner, json={"revision": 1, "tags": ["c"]}
    )
    assert response.status_code == 200, response.text
    assert response.json()["data"]["tags"] == ["c"]
    with _backend().engine.connect() as conn:
        slugs = conn.execute(
            text(
                "SELECT t.slug FROM knowledge_tags kt JOIN tags t ON t.id = kt.tag_id"
                " WHERE kt.knowledge_entry_id = :i ORDER BY kt.position"
            ),
            {"i": UUID(entry["id"])},
        ).scalars().all()
    assert list(slugs) == ["c"]


# NFR-04: statement count does not grow with the data ------------------------------------


def _insert_published_entries(count: int) -> None:
    """Extra PUBLISHED, DIRECTORATE-shared entries with a document, version, chunk and tag."""
    rows: dict[type[m.Base], list[dict[str, Any]]] = {
        m.KnowledgeEntry: [],
        m.DocumentReference: [],
        m.DocumentVersion: [],
        m.DocumentChunk: [],
        m.KnowledgeTag: [],
    }
    for index in range(count):
        entry = KnowledgeEntry(
            title=f"SIMULASI - Entri tambahan {index}",
            knowledge_type="REFERENCE",
            summary="Ringkasan simulasi entri tambahan untuk uji jumlah query.",
            lifecycle_status="PUBLISHED",
            sharing_scope="DIRECTORATE",
            owner_team_id=PPSUN,
            classification_code="INTERNAL",
            published_at=SEED_TIME,
        )
        doc = DocumentReference(
            knowledge_entry_id=entry.id,
            title=entry.title,
            provider_location=f"local://simulated/extra-{index}.pdf",
            owner_team_id=PPSUN,
            classification_code="INTERNAL",
        )
        version = DocumentVersion(
            document_reference_id=doc.id,
            version_label="v1.0",
            checksum_sha256=f"{index:064x}",
            provider_location=doc.provider_location,
        )
        doc.current_version_id = version.id
        chunk = DocumentChunk(
            document_version_id=version.id,
            knowledge_entry_id=entry.id,
            chunk_index=0,
            section_label="Isi",
            content=f"Catatan metadata simulasi tambahan nomor {index}.",
        )
        rows[m.KnowledgeEntry].append(_row(entry, m.KnowledgeEntry))
        rows[m.DocumentReference].append(_row(doc, m.DocumentReference))
        rows[m.DocumentVersion].append(_row(version, m.DocumentVersion))
        rows[m.DocumentChunk].append(_row(chunk, m.DocumentChunk))
        rows[m.KnowledgeTag].append(
            {
                "id": sid(f"ktag:extra:{index}"),
                "knowledge_entry_id": entry.id,
                "tag_id": sid("tag:simulasi"),
                "position": 0,
                "data_origin": "SIMULATED_DATA",
            }
        )
    with _backend().engine.begin() as conn:
        for model, model_rows in rows.items():
            conn.execute(insert(model.__table__), model_rows)


def _statement_counts(client: TestClient, headers: dict[str, str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in ("/knowledge?pageSize=100", "/documents?pageSize=100", "/search?q=metadata"):
        with _count_statements() as statements:
            response = client.get(f"{API}{path}", headers=headers)
        assert response.status_code == 200, response.text
        counts[path] = len(statements)
    return counts


def test_statement_count_does_not_grow_with_data() -> None:
    """NFR-04 (NIT 10): batch loading, no per-record queries."""
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    seed_counts = _statement_counts(client, staff)
    seed_total = len(client.get(f"{API}/knowledge?pageSize=100", headers=staff).json()["data"])
    _insert_published_entries(5)
    grown_total = len(client.get(f"{API}/knowledge?pageSize=100", headers=staff).json()["data"])
    assert grown_total == seed_total + 5  # the extra rows are really visible
    assert _statement_counts(client, staff) == seed_counts


# AC-07.3: per-test reset -----------------------------------------------------------------

_RESET_TITLE = "SIMULASI - Entri uji reset per test"


def test_reset_a_writes() -> None:
    client = make_client()
    _create_knowledge(client, login(client, OWNER), title=_RESET_TITLE)
    assert _scalar("SELECT count(*) FROM knowledge_entries WHERE title = :t", t=_RESET_TITLE) == 1


def test_reset_b_starts_clean() -> None:
    client = make_client()
    titles = {
        item["title"]
        for item in client.get(
            f"{API}/knowledge?pageSize=100", headers=login(client, OWNER)
        ).json()["data"]
    }
    assert _RESET_TITLE not in titles
    assert _scalar("SELECT count(*) FROM knowledge_entries WHERE title = :t", t=_RESET_TITLE) == 0
