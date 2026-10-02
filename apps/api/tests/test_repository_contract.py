"""Repository contract (design 5.1), run on both backends (postgres only under db:test)."""

import threading
from collections.abc import Iterator
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from sunovate_api.core.errors import ApiError
from sunovate_api.store.dataset import sid
from sunovate_api.store.records import KnowledgeEntry, Task
from sunovate_api.store.repository import Repository
from sunovate_api.store.simulated import SimulatedBackend, SimulatedStore
from sunovate_api.testing import requires_postgres, shared_postgres_backend

T4 = sid("task:T4")
K2 = sid("knowledge:K2")
ACTOR = sid("user:sim.owner.ppsun")


@pytest.fixture(params=["simulated", pytest.param("postgres", marks=requires_postgres)])
def repo(request: pytest.FixtureRequest) -> Iterator[Repository]:
    if request.param == "postgres":
        with shared_postgres_backend().session() as session:
            yield session
        return
    backend = SimulatedBackend(SimulatedStore())
    with backend.session() as simulated:
        yield simulated


def _entry() -> KnowledgeEntry:
    return KnowledgeEntry(
        title="SIMULASI - Entri uji kontrak repository",
        knowledge_type="LESSON_LEARNED",
        summary="Ringkasan simulasi untuk uji kontrak repository.",
        owner_team_id=sid("team:PPSUN"),
        classification_code="INTERNAL",
    )


def test_insert_outside_transaction_raises(repo: Repository) -> None:
    entry = _entry()
    with pytest.raises(RuntimeError, match=r"write di luar transaction\(\)"):
        repo.insert(entry)
    assert repo.get_governed(KnowledgeEntry, entry.id) is None


def test_update_outside_transaction_raises(repo: Repository) -> None:
    with pytest.raises(RuntimeError, match=r"write di luar transaction\(\)"):
        repo.update_revisioned(
            Task, T4, expected_revision=1, changes={"progress": 10}, actor_id=ACTOR
        )
    task = repo.get_governed(Task, T4)
    assert task is not None and task.revision == 1


def test_writes_inside_transaction(repo: Repository) -> None:
    entry = _entry()
    with repo.transaction():
        repo.insert(entry)
        with repo.transaction():  # reentrant
            updated = repo.update_revisioned(
                Task, T4, expected_revision=1, changes={"progress": 10}, actor_id=ACTOR
            )
    assert repo.get_governed(KnowledgeEntry, entry.id) is not None
    assert (updated.revision, updated.progress, updated.updated_by) == (2, 10, ACTOR)


def test_update_revisioned_error_order(repo: Repository) -> None:
    with repo.transaction():
        with pytest.raises(ApiError) as missing:
            repo.update_revisioned(Task, uuid4(), expected_revision=1, changes={}, actor_id=ACTOR)
        assert missing.value.status_code == 404
        with pytest.raises(ApiError) as stale:
            repo.update_revisioned(
                Task, T4, expected_revision=7, changes={}, actor_id=ACTOR,
                expected_state={"status": "NO_SUCH_STATUS"},
            )
        assert stale.value.code == "REVISION_CONFLICT"
        assert stale.value.details == {"currentRevision": 1}
        with pytest.raises(ApiError) as state:
            repo.update_revisioned(
                Task, T4, expected_revision=1, changes={}, actor_id=ACTOR,
                expected_state={"status": "NO_SUCH_STATUS"},
            )
        assert state.value.code == "INVALID_STATE"
    task = repo.get_governed(Task, T4)
    assert task is not None and task.revision == 1


@pytest.mark.parametrize("field", ["revision", "id", "created_by", "unknown_field"])
def test_update_revisioned_rejects_forbidden_or_unknown_fields(
    repo: Repository, field: str
) -> None:
    with repo.transaction(), pytest.raises(ValueError):
        repo.update_revisioned(Task, T4, expected_revision=1, changes={field: 1}, actor_id=ACTOR)
    task = repo.get_governed(Task, T4)
    assert task is not None and task.revision == 1


def test_list_governed_rejects_unknown_where_field(repo: Repository) -> None:
    with pytest.raises(ValueError):
        repo.list_governed(Task, where={"unknown_field": 1})


def test_audit_uses_one_timestamp(repo: Repository) -> None:
    entry = repo.audit(actor_user_id=ACTOR, action="TEST", entity_type="test")
    denial = repo.audit_denial(actor_user_id=None, action="TEST", entity_type="test")
    for log in (entry, denial):
        assert log.created_at == log.updated_at == log.occurred_at
    assert denial.outcome == "DENIED"
    assert [log.id for log in repo.audit_logs("TEST")] == [denial.id, entry.id]


def test_get_governed_many(repo: Repository) -> None:
    assert repo.get_governed_many(KnowledgeEntry, []) == {}
    found = repo.get_governed_many(KnowledgeEntry, [K2, uuid4()])
    assert set(found) == {K2}


def test_transaction_depth_is_thread_local() -> None:
    """One SimulatedStore is shared by concurrent requests: depth must be per thread."""
    store = SimulatedStore()
    entered, release = threading.Event(), threading.Event()

    def hold_transaction() -> None:
        with store.transaction():
            entered.set()
            release.wait(timeout=10)

    worker = threading.Thread(target=hold_transaction)
    worker.start()
    try:
        assert entered.wait(timeout=10)
        with pytest.raises(RuntimeError, match=r"write di luar transaction\(\)"):
            store.insert(_entry())
    finally:
        release.set()
        worker.join(timeout=10)
    assert not worker.is_alive()


@requires_postgres
def test_failed_rollback_keeps_the_original_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A rollback that fails itself must not replace the ApiError that caused it (rule 5.1)."""
    rollbacks: list[str] = []

    def broken_rollback() -> None:
        rollbacks.append("called")
        raise SQLAlchemyError("simulated rollback failure")

    with shared_postgres_backend().session() as repo:
        monkeypatch.setattr(repo._session, "rollback", broken_rollback)
        with pytest.raises(ApiError) as caught, repo.transaction():
            repo.update_revisioned(
                Task, T4, expected_revision=7, changes={"progress": 10}, actor_id=ACTOR
            )
    assert rollbacks == ["called"]
    assert (caught.value.status_code, caught.value.code) == (409, "REVISION_CONFLICT")
    assert caught.value.details == {"currentRevision": 1}
    with shared_postgres_backend().session() as fresh:
        task = fresh.get_governed(Task, T4)
    assert task is not None and task.revision == 1
