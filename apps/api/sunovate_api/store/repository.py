"""Data access interface shared by every runtime backend (ADR-015, PROPOSED).

Modules, AuthorizationService, RetrievalService and HermesGateway depend only on
`Repository`. Authorization is still decided in Python (`AuthorizationService.can_read`);
`ReadScope` is a narrowing hint that may never widen what is returned.
No SQLAlchemy import here: this module must stay backend-neutral.
"""

from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any, Final, Protocol
from uuid import UUID

from ..core.config import DataBackendName
from .records import (
    AiConversation,
    AiMessage,
    AuditLog,
    DataClassification,
    DocumentChunk,
    DocumentVersion,
    Governed,
    KnowledgeEntry,
    Permission,
    Record,
    Role,
    Team,
    User,
)

# Fields managed by `update_revisioned` itself; callers may never set them.
UPDATE_FORBIDDEN: Final = frozenset(
    {"id", "revision", "created_at", "created_by", "updated_at", "updated_by"}
)


def check_fields(kind: type[Record], names: Iterable[str], *, for_update: bool) -> None:
    """Reject names that are not dataclass fields of `kind` (programming error -> 500).

    `tags` is not a table column; it is accepted only as an update of `KnowledgeEntry`.
    """
    allowed = {f.name for f in fields(kind)}
    tags_allowed = for_update and issubclass(kind, KnowledgeEntry)
    if not tags_allowed:
        allowed.discard("tags")
    for name in names:
        if name not in allowed:
            raise ValueError(f"Field tidak dikenal untuk {kind.__name__}: {name}")
        if for_update and name in UPDATE_FORBIDDEN:
            raise ValueError(f"Field {name} tidak boleh diubah lewat update_revisioned")


@dataclass(frozen=True)
class ReadScope:
    """SQL narrowing hint. May narrow, never widen; `can_read` stays final."""

    classification_codes: frozenset[str]  # codes with rank <= the effective limit
    team_ids: frozenset[UUID] | None  # None = no team predicate
    include_directorate_published: bool  # only True for KnowledgeEntry


@dataclass(frozen=True)
class PrincipalFacts:
    user: User
    role_codes: frozenset[str]
    permission_codes: frozenset[str]
    team_ids: frozenset[UUID]


@dataclass(frozen=True)
class TextSearchCandidates:
    """Entries/chunks preselected by the active backend's text index.

    PostgreSQL uses its GIN-backed ``search_vector`` columns. The simulated
    backend returns the supplied records so the shared lexical scorer remains
    deterministic in tests and local demonstrations.
    """

    entry_ids: frozenset[UUID]
    chunks_by_entry: dict[UUID, list[DocumentChunk]]


class Repository(Protocol):
    """Synchronous data access for one request. See design section 5.1 for semantics."""

    # Transactions ------------------------------------------------------------
    def transaction(self) -> AbstractContextManager[None]: ...

    # Reference data and identity -----------------------------------------------
    def classifications(self) -> list[DataClassification]: ...  # rank ascending
    def classification_rank(self, code: str) -> int | None: ...
    def teams(self) -> list[Team]: ...  # (created_at, id)
    def team(self, team_id: UUID) -> Team | None: ...
    def team_code(self, team_id: UUID | None) -> str | None: ...
    def users(self) -> list[User]: ...
    def user(self, user_id: UUID) -> User | None: ...
    def user_by_email(self, email: str) -> User | None: ...

    # Revoked session tokens (AUD-05). Writes require an open transaction().
    def is_token_revoked(self, token_id: str) -> bool: ...
    def revoke_token(self, token_id: str, user_id: UUID, expires_at: datetime) -> None: ...
    def purge_revoked_tokens(self, before: datetime) -> int: ...

    # RAHASIA reader grants (ADR-020). Writes require an open transaction().
    def secure_reader_ids(self, document_id: UUID) -> frozenset[UUID]: ...

    def add_secure_reader(
        self, document_id: UUID, user_id: UUID, granted_by: UUID | None
    ) -> bool: ...  # False when the grant already existed

    def remove_secure_reader(self, document_id: UUID, user_id: UUID) -> bool: ...
    def principal_facts(self, user_id: UUID) -> PrincipalFacts | None: ...
    def roles(self) -> list[Role]: ...
    def permissions(self) -> list[Permission]: ...
    def permission_codes_by_role(self) -> dict[UUID, frozenset[str]]: ...
    def role_codes_by_user(self) -> dict[UUID, frozenset[str]]: ...
    def team_ids_by_user(self) -> dict[UUID, frozenset[UUID]]: ...

    # Governed records ----------------------------------------------------------
    def get_governed[G: Governed](self, kind: type[G], record_id: UUID) -> G | None: ...
    def get_governed_many[G: Governed](
        self, kind: type[G], ids: Collection[UUID]
    ) -> dict[UUID, G]: ...
    def list_governed[G: Governed](
        self,
        kind: type[G],
        *,
        scope: ReadScope | None = None,
        where: Mapping[str, object] | None = None,
    ) -> list[G]: ...

    # Documents and chunks ------------------------------------------------------
    def versions_of(self, document_id: UUID) -> list[DocumentVersion]: ...
    def chunks_of_entry(self, entry_id: UUID) -> list[DocumentChunk]: ...
    def version_classifications(self, version_ids: Collection[UUID]) -> dict[UUID, str]: ...
    # ^ document classification per document version, in one query (AUD-02 batch check)
    def chunks_of_entries(self, entry_ids: Sequence[UUID]) -> dict[UUID, list[DocumentChunk]]: ...
    def text_search_candidates(
        self,
        entry_ids: Sequence[UUID],
        query: str,
        *,
        classification_codes: Collection[str],
    ) -> TextSearchCandidates: ...

    # Hermes --------------------------------------------------------------------
    def conversation(self, conversation_id: UUID) -> AiConversation | None: ...
    def message(self, message_id: UUID) -> AiMessage | None: ...

    # Audit ---------------------------------------------------------------------
    def audit_logs(self, action: str | None = None) -> list[AuditLog]: ...  # newest first
    def audit(
        self,
        *,
        actor_user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        outcome: str = "SUCCESS",
        detail: dict[str, Any] | None = None,
    ) -> AuditLog: ...
    def audit_denial(
        self,
        *,
        actor_user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        detail: dict[str, Any] | None = None,
    ) -> AuditLog: ...

    # Writes --------------------------------------------------------------------
    def insert(self, record: Record) -> None: ...
    def update_revisioned[G: Governed](
        self,
        kind: type[G],
        record_id: UUID,
        *,
        expected_revision: int,
        changes: Mapping[str, object],
        actor_id: UUID,
        expected_state: Mapping[str, object] | None = None,
    ) -> G: ...


class DataBackend(Protocol):
    name: DataBackendName

    def session(self) -> AbstractContextManager[Repository]: ...

    def close(self) -> None:
        """Release process-level resources (connection pool) at application shutdown."""
        ...
