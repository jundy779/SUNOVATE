"""In-memory runtime store (DATA_BACKEND=simulated), an implementation of `Repository`.

Not persistent: every process restart reloads the SIMULATED_DATA dataset.
All storage is private to this file; callers use the `Repository` methods only.
"""

from __future__ import annotations

import threading
from collections.abc import Collection, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import Any, cast
from uuid import UUID

from ..core.config import DataBackendName
from ..core.errors import invalid_state, not_found, revision_conflict
from ..core.logging import request_id_var
from .dataset import Dataset, build_dataset
from .records import (
    AiCitation,
    AiConversation,
    AiFeedback,
    AiMessage,
    ApprovalRequest,
    AuditLog,
    DataClassification,
    DataQualityIssue,
    DocumentChunk,
    DocumentReference,
    DocumentVersion,
    FollowUp,
    Governed,
    KnowledgeEntry,
    Milestone,
    PendingMatter,
    Permission,
    Record,
    Role,
    Task,
    Team,
    TeamMembership,
    User,
    UserRole,
    WorkOutput,
    utcnow,
)
from .repository import PrincipalFacts, ReadScope, check_fields

# Governed kind -> name of the private dict holding it.
_GOVERNED: dict[type[Governed], str] = {
    KnowledgeEntry: "_knowledge",
    DocumentReference: "_documents",
    WorkOutput: "_work_outputs",
    Task: "_tasks",
    Milestone: "_milestones",
    PendingMatter: "_pending_matters",
    FollowUp: "_follow_ups",
    ApprovalRequest: "_approvals",
    DataQualityIssue: "_data_quality_issues",
}


def _index[R: Record](items: Iterable[R]) -> dict[UUID, R]:
    return {item.id: item for item in items}


def _natural[R: Record](items: Iterable[R]) -> list[R]:
    """Natural order shared by every backend: (created_at, id) ascending."""
    return sorted(items, key=lambda r: (r.created_at, r.id))


class SimulatedStore:
    def __init__(self, dataset: Dataset | None = None) -> None:
        ds = dataset or build_dataset()
        self.lock = threading.RLock()  # used only by transaction() and snapshots
        self._tx = threading.local()  # transaction depth per thread
        self._classifications: dict[str, DataClassification] = {
            c.code: c for c in ds.classifications
        }
        self._teams: dict[UUID, Team] = _index(ds.teams)
        self._roles: dict[UUID, Role] = _index(ds.roles)
        self._permissions: dict[UUID, Permission] = _index(ds.permissions)
        self._role_permissions: dict[UUID, set[UUID]] = {}
        for role_id, perm_id in ds.role_permissions:
            self._role_permissions.setdefault(role_id, set()).add(perm_id)
        self._users: dict[UUID, User] = _index(ds.users)
        self._memberships: list[TeamMembership] = list(ds.memberships)
        self._user_roles: list[UserRole] = list(ds.user_roles)
        self._knowledge: dict[UUID, KnowledgeEntry] = _index(ds.knowledge)
        self._documents: dict[UUID, DocumentReference] = _index(ds.documents)
        self._versions: dict[UUID, DocumentVersion] = _index(ds.versions)
        self._chunks: dict[UUID, DocumentChunk] = _index(ds.chunks)
        self._work_outputs: dict[UUID, WorkOutput] = _index(ds.work_outputs)
        self._tasks: dict[UUID, Task] = _index(ds.tasks)
        self._milestones: dict[UUID, Milestone] = _index(ds.milestones)
        self._pending_matters: dict[UUID, PendingMatter] = _index(ds.pending_matters)
        self._follow_ups: dict[UUID, FollowUp] = _index(ds.follow_ups)
        self._approvals: dict[UUID, ApprovalRequest] = _index(ds.approvals)
        self._data_quality_issues: dict[UUID, DataQualityIssue] = _index(ds.data_quality_issues)
        self._audit_logs: list[AuditLog] = list(ds.audit_logs)
        self._conversations: dict[UUID, AiConversation] = {}
        self._messages: dict[UUID, AiMessage] = {}
        self._citations: list[AiCitation] = []
        self._feedback: list[AiFeedback] = []

    # Transactions ------------------------------------------------------------

    def _depth(self) -> int:
        return cast(int, getattr(self._tx, "depth", 0))

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Reentrant; holds the store lock. No rollback (in-memory, current behavior)."""
        with self.lock:
            self._tx.depth = self._depth() + 1
            try:
                yield
            finally:
                self._tx.depth = self._depth() - 1

    def _require_transaction(self) -> None:
        if self._depth() == 0:
            raise RuntimeError("write di luar transaction()")

    def _governed[G: Governed](self, kind: type[G]) -> dict[UUID, G]:
        attribute = _GOVERNED.get(kind)
        if attribute is None:
            raise TypeError(f"Jenis record tidak didukung: {kind.__name__}")
        return cast(dict[UUID, G], getattr(self, attribute))

    # Reference data and identity ---------------------------------------------

    def classifications(self) -> list[DataClassification]:
        with self.lock:
            values = list(self._classifications.values())
        return sorted(values, key=lambda c: c.rank)

    def classification_rank(self, code: str) -> int | None:
        item = self._classifications.get(code)
        return item.rank if item else None

    def teams(self) -> list[Team]:
        with self.lock:
            values = list(self._teams.values())
        return _natural(values)

    def team(self, team_id: UUID) -> Team | None:
        return self._teams.get(team_id)

    def team_code(self, team_id: UUID | None) -> str | None:
        team = self._teams.get(team_id) if team_id else None
        return team.code if team else None

    def users(self) -> list[User]:
        with self.lock:
            values = list(self._users.values())
        return _natural(values)

    def user(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    def user_by_email(self, email: str) -> User | None:
        wanted = email.strip().lower()
        return next((u for u in self.users() if u.email == wanted), None)

    def principal_facts(self, user_id: UUID) -> PrincipalFacts | None:
        with self.lock:
            user = self._users.get(user_id)
            if user is None:
                return None
            role_ids = {ur.role_id for ur in self._user_roles if ur.user_id == user_id}
            permission_ids: set[UUID] = set()
            for role_id in role_ids:
                permission_ids |= self._role_permissions.get(role_id, set())
            return PrincipalFacts(
                user=user,
                role_codes=frozenset(self._roles[r].code for r in role_ids),
                permission_codes=frozenset(self._permissions[p].code for p in permission_ids),
                team_ids=frozenset(m.team_id for m in self._memberships if m.user_id == user_id),
            )

    def roles(self) -> list[Role]:
        with self.lock:
            values = list(self._roles.values())
        return _natural(values)

    def permissions(self) -> list[Permission]:
        with self.lock:
            values = list(self._permissions.values())
        return _natural(values)

    def permission_codes_by_role(self) -> dict[UUID, frozenset[str]]:
        with self.lock:
            return {
                role_id: frozenset(self._permissions[p].code for p in perm_ids)
                for role_id, perm_ids in self._role_permissions.items()
            }

    def role_codes_by_user(self) -> dict[UUID, frozenset[str]]:
        with self.lock:
            pairs = [(ur.user_id, self._roles[ur.role_id].code) for ur in self._user_roles]
        result: dict[UUID, set[str]] = {}
        for user_id, code in pairs:
            result.setdefault(user_id, set()).add(code)
        return {user_id: frozenset(codes) for user_id, codes in result.items()}

    def team_ids_by_user(self) -> dict[UUID, frozenset[UUID]]:
        with self.lock:
            pairs = [(m.user_id, m.team_id) for m in self._memberships]
        result: dict[UUID, set[UUID]] = {}
        for user_id, team_id in pairs:
            result.setdefault(user_id, set()).add(team_id)
        return {user_id: frozenset(ids) for user_id, ids in result.items()}

    # Governed records --------------------------------------------------------

    def get_governed[G: Governed](self, kind: type[G], record_id: UUID) -> G | None:
        return self._governed(kind).get(record_id)

    def get_governed_many[G: Governed](
        self, kind: type[G], ids: Collection[UUID]
    ) -> dict[UUID, G]:
        if not ids:
            return {}
        items = self._governed(kind)
        with self.lock:
            return {i: items[i] for i in ids if i in items}

    def list_governed[G: Governed](
        self,
        kind: type[G],
        *,
        scope: ReadScope | None = None,  # ignored: the Python authorization check is final
        where: Mapping[str, object] | None = None,
    ) -> list[G]:
        conditions = dict(where or {})
        check_fields(kind, conditions, for_update=False)
        items = self._governed(kind)
        with self.lock:
            values = list(items.values())
        selected = [
            r
            for r in values
            if all(
                getattr(r, name) is None if expected is None else getattr(r, name) == expected
                for name, expected in conditions.items()
            )
        ]
        return _natural(selected)

    # Documents and chunks ----------------------------------------------------

    def versions_of(self, document_id: UUID) -> list[DocumentVersion]:
        with self.lock:
            values = list(self._versions.values())
        return _natural(v for v in values if v.document_reference_id == document_id)

    def chunks_of_entry(self, entry_id: UUID) -> list[DocumentChunk]:
        return self.chunks_of_entries([entry_id]).get(entry_id, [])

    def chunks_of_entries(self, entry_ids: Sequence[UUID]) -> dict[UUID, list[DocumentChunk]]:
        """Chunks of the current version of each entry's non-deleted documents."""
        if not entry_ids:
            return {}
        wanted = set(entry_ids)
        with self.lock:
            documents = list(self._documents.values())
            chunks = list(self._chunks.values())
        current: dict[UUID, set[UUID | None]] = {}
        for doc in documents:
            entry_id = doc.knowledge_entry_id
            if entry_id is not None and entry_id in wanted and doc.deleted_at is None:
                current.setdefault(entry_id, set()).add(doc.current_version_id)
        grouped: dict[UUID, list[DocumentChunk]] = {}
        for chunk in chunks:
            if chunk.document_version_id in current.get(chunk.knowledge_entry_id, set()):
                grouped.setdefault(chunk.knowledge_entry_id, []).append(chunk)
        return {
            entry_id: sorted(items, key=lambda c: (c.chunk_index, c.created_at, c.id))
            for entry_id, items in grouped.items()
        }

    # Hermes ------------------------------------------------------------------

    def conversation(self, conversation_id: UUID) -> AiConversation | None:
        return self._conversations.get(conversation_id)

    def message(self, message_id: UUID) -> AiMessage | None:
        return self._messages.get(message_id)

    # Append-only audit -------------------------------------------------------

    def audit_logs(self, action: str | None = None) -> list[AuditLog]:
        with self.lock:
            logs = list(reversed(self._audit_logs))
        if action:
            logs = [entry for entry in logs if entry.action == action]
        return logs

    def audit(
        self,
        *,
        actor_user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        outcome: str = "SUCCESS",
        detail: dict[str, Any] | None = None,
    ) -> AuditLog:
        now = utcnow()
        entry = AuditLog(
            occurred_at=now,
            created_at=now,
            updated_at=now,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            outcome=outcome,
            request_id=request_id_var.get(),
            detail=detail or {},
        )
        with self.transaction():  # joins an open transaction, else commits immediately
            self._audit_logs.append(entry)
        return entry

    def audit_denial(
        self,
        *,
        actor_user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        detail: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.audit(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            outcome="DENIED",
            detail=detail,
        )

    # Writes ------------------------------------------------------------------

    def insert(self, record: Record) -> None:
        self._require_transaction()
        with self.lock:
            match record:
                case KnowledgeEntry():
                    self._knowledge[record.id] = record
                case DocumentReference():
                    self._documents[record.id] = record
                case WorkOutput():
                    self._work_outputs[record.id] = record
                case Task():
                    self._tasks[record.id] = record
                case Milestone():
                    self._milestones[record.id] = record
                case PendingMatter():
                    self._pending_matters[record.id] = record
                case FollowUp():
                    self._follow_ups[record.id] = record
                case ApprovalRequest():
                    self._approvals[record.id] = record
                case DocumentVersion():
                    self._versions[record.id] = record
                case DocumentChunk():
                    self._chunks[record.id] = record
                case AiConversation():
                    self._conversations[record.id] = record
                case AiMessage():
                    self._messages[record.id] = record
                case AiCitation():
                    self._citations.append(record)
                case AiFeedback():
                    self._feedback.append(record)
                case _:
                    raise TypeError(f"insert tidak mendukung {type(record).__name__}")

    def update_revisioned[G: Governed](
        self,
        kind: type[G],
        record_id: UUID,
        *,
        expected_revision: int,
        changes: Mapping[str, object],
        actor_id: UUID,
        expected_state: Mapping[str, object] | None = None,
    ) -> G:
        self._require_transaction()
        check_fields(kind, changes, for_update=True)
        state = dict(expected_state or {})
        check_fields(kind, state, for_update=False)
        items = self._governed(kind)
        with self.lock:
            record = items.get(record_id)
            if record is None:
                raise not_found()
            if record.revision != expected_revision:
                raise revision_conflict(record.revision)
            if any(getattr(record, name) != value for name, value in state.items()):
                raise invalid_state("Data tidak lagi dalam status yang diharapkan")
            for name, value in changes.items():
                setattr(record, name, value)
            record.revision += 1
            record.updated_at = utcnow()
            record.updated_by = actor_id
            return record


class SimulatedBackend:
    """Every request session yields the same shared in-memory store."""

    name: DataBackendName = "simulated"

    def __init__(self, store: SimulatedStore) -> None:
        self.store = store

    @contextmanager
    def session(self) -> Iterator[SimulatedStore]:
        yield self.store

    def close(self) -> None:
        """Nothing to release: the in-memory store has no pool."""
