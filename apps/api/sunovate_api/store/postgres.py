"""PostgreSQL runtime backend (DATA_BACKEND=postgres), an implementation of `Repository`.

ADR-015 (PROPOSED): one Session per request, explicit `transaction()`, natural order
(created_at, id), audit order by `seq`, tags in tags/knowledge_tags with `position`.
SQLAlchemy Core statements on the tables in `db/models.py`, mapped to the dataclasses in
`store/records.py`. SQL only narrows candidates; `AuthorizationService.can_read`/`can_write`
stays the final decision. All values are bound parameters. Driver messages and the database
URL never reach responses or logs.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable, Collection, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import fields
from datetime import UTC, datetime
from typing import Any, Final
from uuid import UUID, uuid4

import psycopg
from sqlalchemy import (
    ColumnElement,
    Engine,
    Select,
    Table,
    and_,
    create_engine,
    delete,
    false,
    func,
    insert,
    or_,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Result, RowMapping
from sqlalchemy.exc import (
    IntegrityError,
    InterfaceError,
    OperationalError,
    SQLAlchemyError,
)
from sqlalchemy.exc import TimeoutError as PoolTimeoutError
from sqlalchemy.orm import Session
from sqlalchemy.sql import Executable

from ..core.config import DataBackendName
from ..core.errors import ApiError, invalid_state, not_found, revision_conflict, sqlstate_of
from ..core.logging import request_id_var
from ..db import models as m
from ..db.urls import sync_database_url
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
    RevokedToken,
    Role,
    SecureDocumentReader,
    Task,
    Team,
    User,
    WorkOutput,
    utcnow,
)
from .repository import PrincipalFacts, ReadScope, TextSearchCandidates, check_fields

logger = logging.getLogger("sunovate")


def _table(model: type[m.Base]) -> Table:
    table = model.__table__
    assert isinstance(table, Table)
    return table


# Record kind -> table. Governed kinds plus every kind read or inserted here.
_TABLES: Final[dict[type[Record], Table]] = {
    DataClassification: _table(m.DataClassification),
    Team: _table(m.Team),
    User: _table(m.User),
    Role: _table(m.Role),
    Permission: _table(m.Permission),
    KnowledgeEntry: _table(m.KnowledgeEntry),
    DocumentReference: _table(m.DocumentReference),
    DocumentVersion: _table(m.DocumentVersion),
    DocumentChunk: _table(m.DocumentChunk),
    WorkOutput: _table(m.WorkOutput),
    Task: _table(m.Task),
    Milestone: _table(m.Milestone),
    PendingMatter: _table(m.PendingMatter),
    FollowUp: _table(m.FollowUp),
    ApprovalRequest: _table(m.ApprovalRequest),
    DataQualityIssue: _table(m.DataQualityIssue),
    AuditLog: _table(m.AuditLog),
    AiConversation: _table(m.AiConversation),
    AiMessage: _table(m.AiMessage),
    AiCitation: _table(m.AiCitation),
    AiFeedback: _table(m.AiFeedback),
    SecureDocumentReader: _table(m.SecureDocumentReader),
    RevokedToken: _table(m.RevokedToken),
}

# Record types accepted by insert() (design 5.1); anything else -> TypeError.
_INSERTABLE: Final = (
    KnowledgeEntry,
    DocumentReference,
    WorkOutput,
    Task,
    Milestone,
    PendingMatter,
    FollowUp,
    ApprovalRequest,
    DocumentVersion,
    DocumentChunk,
    AiConversation,
    AiMessage,
    AiCitation,
    AiFeedback,
)

_USER_ROLES = _table(m.UserRole)
_ROLE_PERMISSIONS = _table(m.RolePermission)
_MEMBERSHIPS = _table(m.TeamMembership)
_TAGS = _table(m.Tag)
_KNOWLEDGE_TAGS = _table(m.KnowledgeTag)

_DUPLICATE_CHECKSUM = "uq_document_versions_reference_checksum"
_SEPARATION_OF_DUTIES = "ck_approval_requests_separation_of_duties"
_FTS_WORD = re.compile(r"[a-z0-9]+")


def _tables_of(kind: type[Record]) -> Table:
    table = _TABLES.get(kind)
    if table is None:
        raise TypeError(f"Jenis record tidak didukung: {kind.__name__}")
    return table


def _mapped_names(kind: type[Record], table: Table) -> list[str]:
    """Dataclass fields that are writable table columns (no computed or identity columns)."""
    columns = {c.key for c in table.columns if c.computed is None and c.identity is None}
    return [f.name for f in fields(kind) if f.name in columns]


def _to_row(record: Record, table: Table) -> dict[str, Any]:
    return {name: getattr(record, name) for name in _mapped_names(type(record), table)}


def _normalize(value: Any) -> Any:
    return value.astimezone(UTC) if isinstance(value, datetime) else value


def _from_row[R: Record](kind: type[R], row: RowMapping) -> R:
    values = {key: _normalize(value) for key, value in row.items()}
    if kind is AuditLog:
        # audit_logs has no created_at/updated_at: both equal occurred_at (design 7, D-C9).
        values["created_at"] = values["updated_at"] = values["occurred_at"]
    return kind(**values)


def _condition(table: Table, name: str, value: object) -> ColumnElement[bool]:
    column = table.c[name]
    return column.is_(None) if value is None else column == value


def _checked_columns(kind: type[Record], table: Table, names: Iterable[str]) -> None:
    for name in names:
        if name not in table.c:
            raise ValueError(f"Kolom tidak dikenal untuk {kind.__name__}: {name}")


def _integrity_error(exc: IntegrityError) -> ApiError | None:
    """Map known constraint violations to API errors (design 10.2); None = re-raise."""
    orig = exc.orig
    name = orig.diag.constraint_name if isinstance(orig, psycopg.Error) else None
    if name == _DUPLICATE_CHECKSUM:
        logger.info("constraint violation", extra={"constraint": name})
        return ApiError(
            409, "DUPLICATE_CHECKSUM", "Versi dengan checksum yang sama sudah terdaftar"
        )
    if name == _SEPARATION_OF_DUTIES:
        logger.warning("constraint violation", extra={"constraint": name})
        return ApiError(
            403, "SEPARATION_OF_DUTIES", "Pengaju tidak dapat memutuskan permintaannya sendiri"
        )
    return None


# SQLSTATE of transient, retryable conditions that are not connectivity failures:
# 57014 query_canceled (statement_timeout), 55P03 lock_not_available (lock_timeout),
# 40P01 deadlock_detected, 40001 serialization_failure.
_BUSY_SQLSTATES: Final = frozenset({"57014", "55P03", "40P01", "40001"})
_RETRY_AFTER_SECONDS: Final = "5"


def database_error_to_api(exc: Exception) -> ApiError:
    """Classify a driver/pool error: busy/timeout (DATABASE_BUSY) or unreachable (default).

    Never includes driver text; the client only sees stable codes and fixed messages.
    """
    if isinstance(exc, OperationalError) and sqlstate_of(exc) in _BUSY_SQLSTATES:
        return ApiError(
            503,
            "DATABASE_BUSY",
            "Database sedang sibuk atau permintaan melewati batas waktu. Silakan coba lagi",
            headers={"Retry-After": _RETRY_AFTER_SECONDS},
        )
    return ApiError(503, "DATABASE_UNAVAILABLE", "Database tidak dapat dijangkau")


def _run[T](fn: Callable[[], T]) -> T:
    """Run a database call; driver failures become 503 without driver details."""
    try:
        return fn()
    except (OperationalError, InterfaceError, PoolTimeoutError) as exc:
        error = database_error_to_api(exc)
        extra: dict[str, object] = {"errorType": type(exc).__name__, "code": error.code}
        state = sqlstate_of(exc)
        if state is not None:
            extra["sqlstate"] = state
        logger.error("database error", extra=extra)
        raise error from None


class PostgresRepository:
    """Repository untuk satu request; dipakai berurutan oleh dependency dan handler (bisa di
    thread threadpool berbeda, tidak pernah konkuren)."""

    def __init__(self, engine: Engine, session: Session) -> None:
        self._engine = engine
        self._session = session
        self._depth = 0  # transaction depth; the only "transaction open" marker (design 5.1)
        self._teams_cache: list[Team] | None = None
        self._classifications_cache: list[DataClassification] | None = None

    # Execution helpers -------------------------------------------------------

    def _execute(self, statement: Executable) -> Result[*tuple[Any, ...]]:
        return _run(lambda: self._session.execute(statement))

    def _rows(self, statement: Executable) -> list[RowMapping]:
        return list(self._execute(statement).mappings())

    def _select(self, kind: type[Record]) -> tuple[Table, Select[Any]]:
        table = _tables_of(kind)
        return table, select(*(table.c[name] for name in _mapped_names(kind, table)))

    def _require_transaction(self) -> None:
        if self._depth == 0:
            raise RuntimeError("write di luar transaction()")

    # Transactions ------------------------------------------------------------

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Reentrant; the outermost exit commits, or rolls back on any exception."""
        self._depth += 1
        try:
            yield
            if self._depth == 1:
                _run(self._session.commit)
        except BaseException:
            if self._depth == 1:
                try:
                    self._session.rollback()
                except SQLAlchemyError:
                    logger.warning("rollback gagal", extra={"errorType": "rollback"})
            raise  # the original exception
        finally:
            self._depth -= 1

    # Reference data and identity (cached per request, design 5.3) ---------------

    def classifications(self) -> list[DataClassification]:
        if self._classifications_cache is None:
            table, statement = self._select(DataClassification)
            rows = self._rows(statement.order_by(table.c.rank))
            self._classifications_cache = [_from_row(DataClassification, r) for r in rows]
        return list(self._classifications_cache)

    def classification_rank(self, code: str) -> int | None:
        return next((c.rank for c in self.classifications() if c.code == code), None)

    def teams(self) -> list[Team]:
        if self._teams_cache is None:
            table, statement = self._select(Team)
            rows = self._rows(statement.order_by(table.c.created_at, table.c.id))
            self._teams_cache = [_from_row(Team, r) for r in rows]
        return list(self._teams_cache)

    def team(self, team_id: UUID) -> Team | None:
        return next((t for t in self.teams() if t.id == team_id), None)

    def team_code(self, team_id: UUID | None) -> str | None:
        team = self.team(team_id) if team_id else None
        return team.code if team else None

    def _ordered[R: Record](self, kind: type[R]) -> list[R]:
        table, statement = self._select(kind)
        rows = self._rows(statement.order_by(table.c.created_at, table.c.id))
        return [_from_row(kind, r) for r in rows]

    def users(self) -> list[User]:
        return self._ordered(User)

    def user(self, user_id: UUID) -> User | None:
        table, statement = self._select(User)
        rows = self._rows(statement.where(table.c.id == user_id))
        return _from_row(User, rows[0]) if rows else None

    def user_by_email(self, email: str) -> User | None:
        table, statement = self._select(User)
        rows = self._rows(statement.where(table.c.email == email.strip().lower()))
        return _from_row(User, rows[0]) if rows else None

    def is_token_revoked(self, token_id: str) -> bool:
        table = _TABLES[RevokedToken]
        rows = self._rows(select(table.c.id).where(table.c.token_id == token_id).limit(1))
        return bool(rows)

    def revoke_token(self, token_id: str, user_id: UUID, expires_at: datetime) -> None:
        self._require_transaction()
        table = _TABLES[RevokedToken]
        self._execute(
            pg_insert(table)
            .values(token_id=token_id, user_id=user_id, expires_at=expires_at)
            .on_conflict_do_nothing(constraint="uq_revoked_tokens_token_id")
        )

    def purge_revoked_tokens(self, before: datetime) -> int:
        self._require_transaction()
        table = _TABLES[RevokedToken]
        result = self._execute(
            delete(table).where(table.c.expires_at <= before).returning(table.c.id)
        )
        return len(result.fetchall())

    def secure_reader_ids(self, document_id: UUID) -> frozenset[UUID]:
        table = _TABLES[SecureDocumentReader]
        rows = self._rows(select(table.c.user_id).where(table.c.document_id == document_id))
        return frozenset(row["user_id"] for row in rows)

    def add_secure_reader(self, document_id: UUID, user_id: UUID, granted_by: UUID | None) -> bool:
        self._require_transaction()
        table = _TABLES[SecureDocumentReader]
        statement = (
            pg_insert(table)
            .values(document_id=document_id, user_id=user_id, granted_by=granted_by)
            .on_conflict_do_nothing(constraint="uq_secure_document_readers_document_user")
            .returning(table.c.id)
        )
        return self._execute(statement).first() is not None

    def remove_secure_reader(self, document_id: UUID, user_id: UUID) -> bool:
        self._require_transaction()
        table = _TABLES[SecureDocumentReader]
        statement = (
            delete(table)
            .where(table.c.document_id == document_id, table.c.user_id == user_id)
            .returning(table.c.id)
        )
        return self._execute(statement).first() is not None

    def principal_facts(self, user_id: UUID) -> PrincipalFacts | None:
        user = self.user(user_id)
        if user is None:
            return None
        roles, permissions = _TABLES[Role], _TABLES[Permission]
        grants = self._rows(
            select(roles.c.code.label("role_code"), permissions.c.code.label("permission_code"))
            .select_from(
                _USER_ROLES.join(roles, roles.c.id == _USER_ROLES.c.role_id)
                .outerjoin(_ROLE_PERMISSIONS, _ROLE_PERMISSIONS.c.role_id == roles.c.id)
                .outerjoin(permissions, permissions.c.id == _ROLE_PERMISSIONS.c.permission_id)
            )
            .where(_USER_ROLES.c.user_id == user_id)
        )
        memberships = self._rows(
            select(_MEMBERSHIPS.c.team_id).where(_MEMBERSHIPS.c.user_id == user_id)
        )
        return PrincipalFacts(
            user=user,
            role_codes=frozenset(str(row["role_code"]) for row in grants),
            # Roles without permissions still count as roles (NIT 3).
            permission_codes=frozenset(
                str(row["permission_code"])
                for row in grants
                if row["permission_code"] is not None
            ),
            team_ids=frozenset(row["team_id"] for row in memberships),
        )

    def roles(self) -> list[Role]:
        return self._ordered(Role)

    def permissions(self) -> list[Permission]:
        return self._ordered(Permission)

    def permission_codes_by_role(self) -> dict[UUID, frozenset[str]]:
        permissions = _TABLES[Permission]
        rows = self._rows(
            select(_ROLE_PERMISSIONS.c.role_id, permissions.c.code).select_from(
                _ROLE_PERMISSIONS.join(
                    permissions, permissions.c.id == _ROLE_PERMISSIONS.c.permission_id
                )
            )
        )
        result: dict[UUID, set[str]] = {}
        for row in rows:
            result.setdefault(row["role_id"], set()).add(row["code"])
        return {role_id: frozenset(codes) for role_id, codes in result.items()}

    def role_codes_by_user(self) -> dict[UUID, frozenset[str]]:
        roles = _TABLES[Role]
        rows = self._rows(
            select(_USER_ROLES.c.user_id, roles.c.code).select_from(
                _USER_ROLES.join(roles, roles.c.id == _USER_ROLES.c.role_id)
            )
        )
        result: dict[UUID, set[str]] = {}
        for row in rows:
            result.setdefault(row["user_id"], set()).add(row["code"])
        return {user_id: frozenset(codes) for user_id, codes in result.items()}

    def team_ids_by_user(self) -> dict[UUID, frozenset[UUID]]:
        rows = self._rows(select(_MEMBERSHIPS.c.user_id, _MEMBERSHIPS.c.team_id))
        result: dict[UUID, set[UUID]] = {}
        for row in rows:
            result.setdefault(row["user_id"], set()).add(row["team_id"])
        return {user_id: frozenset(ids) for user_id, ids in result.items()}

    # Governed records --------------------------------------------------------

    def _with_tags[R: Record](self, records: list[R]) -> list[R]:
        """Fill KnowledgeEntry.tags with one batch query (design 8)."""
        entries = [r for r in records if isinstance(r, KnowledgeEntry)]
        if not entries:
            return records
        rows = self._rows(
            select(_KNOWLEDGE_TAGS.c.knowledge_entry_id, _TAGS.c.slug)
            .select_from(_KNOWLEDGE_TAGS.join(_TAGS, _TAGS.c.id == _KNOWLEDGE_TAGS.c.tag_id))
            .where(_KNOWLEDGE_TAGS.c.knowledge_entry_id.in_([e.id for e in entries]))
            .order_by(
                _KNOWLEDGE_TAGS.c.knowledge_entry_id, _KNOWLEDGE_TAGS.c.position, _TAGS.c.slug
            )
        )
        tags: dict[UUID, list[str]] = {}
        for row in rows:
            tags.setdefault(row["knowledge_entry_id"], []).append(row["slug"])
        for entry in entries:
            entry.tags = tags.get(entry.id, [])
        return records

    def get_governed[G: Governed](self, kind: type[G], record_id: UUID) -> G | None:
        table, statement = self._select(kind)
        rows = self._rows(statement.where(table.c.id == record_id))
        return self._with_tags([_from_row(kind, rows[0])])[0] if rows else None

    def get_governed_many[G: Governed](
        self, kind: type[G], ids: Collection[UUID]
    ) -> dict[UUID, G]:
        if not ids:
            return {}
        table, statement = self._select(kind)
        rows = self._rows(statement.where(table.c.id.in_(list(ids))))
        return {r.id: r for r in self._with_tags([_from_row(kind, row) for row in rows])}

    def list_governed[G: Governed](
        self,
        kind: type[G],
        *,
        scope: ReadScope | None = None,
        where: Mapping[str, object] | None = None,
    ) -> list[G]:
        conditions = dict(where or {})
        check_fields(kind, conditions, for_update=False)
        table, statement = self._select(kind)
        _checked_columns(kind, table, conditions)
        predicates: list[ColumnElement[bool]] = [
            _condition(table, name, value) for name, value in conditions.items()
        ]
        if scope is not None:
            predicates.extend(self._scope_predicates(table, scope))
        if predicates:
            statement = statement.where(and_(*predicates))
        rows = self._rows(statement.order_by(table.c.created_at, table.c.id))
        return self._with_tags([_from_row(kind, row) for row in rows])

    @staticmethod
    def _scope_predicates(table: Table, scope: ReadScope) -> list[ColumnElement[bool]]:
        """Design 6.2: narrowing only; the Python check after this stays final."""
        codes = sorted(scope.classification_codes)
        predicates: list[ColumnElement[bool]] = [
            table.c.deleted_at.is_(None),
            table.c.classification_code.in_(codes) if codes else false(),
        ]
        if scope.team_ids is not None:
            team_ids = sorted(scope.team_ids)
            team_predicate: ColumnElement[bool] = (
                table.c.owner_team_id.in_(team_ids) if team_ids else false()
            )
            if scope.include_directorate_published:
                team_predicate = or_(
                    team_predicate,
                    and_(
                        table.c.sharing_scope == "DIRECTORATE",
                        table.c.lifecycle_status == "PUBLISHED",
                    ),
                )
            predicates.append(team_predicate)
        return predicates

    # Documents and chunks ----------------------------------------------------

    def version_classifications(self, version_ids: Collection[UUID]) -> dict[UUID, str]:
        ids = list(set(version_ids))
        if not ids:
            return {}
        versions = _TABLES[DocumentVersion]
        documents = _TABLES[DocumentReference]
        rows = self._rows(
            select(versions.c.id, documents.c.classification_code)
            .join(documents, versions.c.document_reference_id == documents.c.id)
            .where(versions.c.id.in_(ids))
        )
        return {row["id"]: row["classification_code"] for row in rows}

    def versions_of(self, document_id: UUID) -> list[DocumentVersion]:
        table, statement = self._select(DocumentVersion)
        rows = self._rows(
            statement.where(table.c.document_reference_id == document_id).order_by(
                table.c.created_at, table.c.id
            )
        )
        return [_from_row(DocumentVersion, r) for r in rows]

    def chunks_of_entry(self, entry_id: UUID) -> list[DocumentChunk]:
        return self.chunks_of_entries([entry_id]).get(entry_id, [])

    def chunks_of_entries(self, entry_ids: Sequence[UUID]) -> dict[UUID, list[DocumentChunk]]:
        """Chunks of the current version of each entry's non-deleted documents (NIT 2)."""
        if not entry_ids:
            return {}
        chunks, documents = _TABLES[DocumentChunk], _TABLES[DocumentReference]
        _, statement = self._select(DocumentChunk)
        rows = self._rows(
            statement.select_from(
                chunks.join(
                    documents,
                    and_(
                        documents.c.current_version_id == chunks.c.document_version_id,
                        documents.c.knowledge_entry_id == chunks.c.knowledge_entry_id,
                        documents.c.deleted_at.is_(None),
                    ),
                )
            )
            .where(chunks.c.knowledge_entry_id.in_(list(entry_ids)))
            .order_by(
                chunks.c.knowledge_entry_id,
                chunks.c.chunk_index,
                chunks.c.created_at,
                chunks.c.id,
            )
        )
        grouped: dict[UUID, list[DocumentChunk]] = {}
        for row in rows:
            chunk = _from_row(DocumentChunk, row)
            grouped.setdefault(chunk.knowledge_entry_id, []).append(chunk)
        return grouped

    def text_search_candidates(
        self,
        entry_ids: Sequence[UUID],
        query: str,
        *,
        classification_codes: Collection[str],
    ) -> TextSearchCandidates:
        """Use GIN-backed FTS to preselect authorized entries and current chunks.

        ``entry_ids`` has already passed the final Python authorization check.
        Keeping that restriction inside both SQL statements prevents the text
        index from revealing records outside the caller's scope.
        """
        authorized_ids = frozenset(entry_ids)
        words = tuple(dict.fromkeys(_FTS_WORD.findall(query.lower())))
        allowed_codes = tuple(classification_codes)
        if not authorized_ids or not words:
            return TextSearchCandidates(frozenset(), {})

        entries = _TABLES[KnowledgeEntry]
        chunks, documents = _TABLES[DocumentChunk], _TABLES[DocumentReference]
        queries = [func.plainto_tsquery("simple", word) for word in words]
        entry_match = or_(*(entries.c.search_vector.op("@@")(item) for item in queries))
        chunk_match = or_(*(chunks.c.search_vector.op("@@")(item) for item in queries))

        entry_rows = self._rows(
            select(entries.c.id).where(entries.c.id.in_(list(authorized_ids)), entry_match)
        )
        _, chunk_statement = self._select(DocumentChunk)
        chunk_rows = self._rows(
            chunk_statement.select_from(
                chunks.join(
                    documents,
                    and_(
                        documents.c.current_version_id == chunks.c.document_version_id,
                        documents.c.knowledge_entry_id == chunks.c.knowledge_entry_id,
                        documents.c.deleted_at.is_(None),
                    ),
                )
            )
            .where(
                chunks.c.knowledge_entry_id.in_(list(authorized_ids)),
                documents.c.classification_code.in_(allowed_codes) if allowed_codes else false(),
                chunk_match,
            )
            .order_by(
                chunks.c.knowledge_entry_id,
                chunks.c.chunk_index,
                chunks.c.created_at,
                chunks.c.id,
            )
        )
        grouped: dict[UUID, list[DocumentChunk]] = {}
        for row in chunk_rows:
            chunk = _from_row(DocumentChunk, row)
            grouped.setdefault(chunk.knowledge_entry_id, []).append(chunk)
        matched_ids = frozenset(
            {row["id"] for row in entry_rows} | set(grouped)
        )
        return TextSearchCandidates(matched_ids, grouped)

    # Hermes ------------------------------------------------------------------

    def conversation(self, conversation_id: UUID) -> AiConversation | None:
        table, statement = self._select(AiConversation)
        rows = self._rows(statement.where(table.c.id == conversation_id))
        return _from_row(AiConversation, rows[0]) if rows else None

    def message(self, message_id: UUID) -> AiMessage | None:
        table, statement = self._select(AiMessage)
        rows = self._rows(statement.where(table.c.id == message_id))
        return _from_row(AiMessage, rows[0]) if rows else None

    # Append-only audit -------------------------------------------------------

    def audit_logs(self, action: str | None = None) -> list[AuditLog]:
        table, statement = self._select(AuditLog)
        if action:
            statement = statement.where(table.c.action == action)
        rows = self._rows(statement.order_by(table.c.seq.desc()))
        return [_from_row(AuditLog, r) for r in rows]

    @staticmethod
    def _audit_entry(
        *,
        actor_user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None,
        outcome: str,
        detail: dict[str, Any] | None,
    ) -> AuditLog:
        now = utcnow()
        return AuditLog(
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
        entry = self._audit_entry(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            outcome=outcome,
            detail=detail,
        )
        table = _TABLES[AuditLog]
        with self.transaction():  # joins an open transaction, else commits immediately
            self._execute(insert(table).values(**_to_row(entry, table)))
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
        """Committed on a separate pooled connection: survives a business rollback (D-05)."""
        entry = self._audit_entry(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            outcome="DENIED",
            detail=detail,
        )
        table = _TABLES[AuditLog]
        row = _to_row(entry, table)

        def write() -> None:
            with self._engine.begin() as conn:
                conn.execute(insert(table).values(**row))

        _run(write)
        return entry

    # Writes ------------------------------------------------------------------

    def _sync_tags(
        self, entry_id: UUID, slugs: Sequence[str], data_origin: str, *, replace: bool
    ) -> None:
        """Design 8: upsert tags, then (re)write knowledge_tags with input positions."""
        if replace:
            self._execute(
                delete(_KNOWLEDGE_TAGS).where(_KNOWLEDGE_TAGS.c.knowledge_entry_id == entry_id)
            )
        unique = list(dict.fromkeys(slugs))
        if not unique:
            return
        now = utcnow()
        self._execute(
            pg_insert(_TAGS)
            .values(
                [
                    {
                        "id": uuid4(),
                        "slug": slug,
                        "label": slug.title(),
                        "created_at": now,
                        "updated_at": now,
                        "data_origin": data_origin,
                    }
                    for slug in unique
                ]
            )
            .on_conflict_do_nothing(index_elements=[_TAGS.c.slug])
        )
        tag_ids = {
            row["slug"]: row["id"]
            for row in self._rows(select(_TAGS.c.id, _TAGS.c.slug).where(_TAGS.c.slug.in_(unique)))
        }
        self._execute(
            insert(_KNOWLEDGE_TAGS).values(
                [
                    {
                        "id": uuid4(),
                        "knowledge_entry_id": entry_id,
                        "tag_id": tag_ids[slug],
                        "position": position,
                        "created_at": now,
                        "updated_at": now,
                        "data_origin": data_origin,
                    }
                    for position, slug in enumerate(unique)
                ]
            )
        )

    def insert(self, record: Record) -> None:
        self._require_transaction()
        if not isinstance(record, _INSERTABLE):
            raise TypeError(f"insert tidak mendukung {type(record).__name__}")
        table = _tables_of(type(record))
        try:
            self._execute(insert(table).values(**_to_row(record, table)))
            if isinstance(record, KnowledgeEntry):
                self._sync_tags(record.id, record.tags, record.data_origin, replace=False)
        except IntegrityError as exc:
            mapped = _integrity_error(exc)
            if mapped is None:
                raise
            raise mapped from None

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
        table = _tables_of(kind)
        column_changes = {name: value for name, value in changes.items() if name != "tags"}
        _checked_columns(kind, table, column_changes)
        _checked_columns(kind, table, state)
        tags = changes.get("tags")
        if "tags" in changes and not isinstance(tags, list):
            raise ValueError("tags harus berupa list")

        _, returning = self._select(kind)
        statement = (
            update(table)
            .where(
                table.c.id == record_id,
                table.c.revision == expected_revision,
                *(_condition(table, name, value) for name, value in state.items()),
            )
            .values(
                **column_changes,
                revision=table.c.revision + 1,
                updated_at=utcnow(),
                updated_by=actor_id,
            )
            .returning(*returning.selected_columns)
        )
        try:
            rows = self._rows(statement)
            if rows and isinstance(tags, list):
                self._sync_tags(
                    record_id, [str(t) for t in tags], str(rows[0]["data_origin"]), replace=True
                )
        except IntegrityError as exc:
            mapped = _integrity_error(exc)
            if mapped is None:
                raise
            raise mapped from None
        if rows:
            return self._with_tags([_from_row(kind, rows[0])])[0]

        # 0 rows: same order as the simulated backend (404 -> 409 revision -> 409 state).
        current = self._rows(
            select(table.c.revision, *(table.c[name] for name in state)).where(
                table.c.id == record_id
            )
        )
        if not current:
            raise not_found()
        if current[0]["revision"] != expected_revision:
            raise revision_conflict(int(current[0]["revision"]))
        raise invalid_state("Data tidak lagi dalam status yang diharapkan")


class PostgresBackend:
    """One Engine (pool) per process; one PostgresRepository + Session per request."""

    name: DataBackendName = "postgres"

    def __init__(self, database_url: str) -> None:
        # ValueError without the URL when the scheme is not allowed (db/urls.py).
        # No connection is opened here: a down database does not break startup or /health.
        self._engine = create_engine(
            sync_database_url(database_url),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=10,
            hide_parameters=True,
            connect_args={
                "connect_timeout": 5,
                # UTC0 = POSIX form of UTC: same offset, but accepted without the server's
                # tzdata directory (the pgserver build used by `pnpm db:test` has none).
                "options": "-c timezone=UTC0 -c statement_timeout=15000",
            },
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    @contextmanager
    def session(self) -> Iterator[PostgresRepository]:
        session = Session(self._engine)
        try:
            yield PostgresRepository(self._engine, session)
        finally:
            try:
                session.close()
            except SQLAlchemyError as exc:
                logger.warning("session close gagal", extra={"errorType": type(exc).__name__})

    def dispose(self) -> None:
        self._engine.dispose()

    def close(self) -> None:
        self.dispose()
