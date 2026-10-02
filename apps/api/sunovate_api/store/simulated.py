"""In-memory runtime store (DATA_BACKEND=simulated).

Not persistent: every process restart reloads the SIMULATED_DATA dataset.
SQLAlchemy-backed repositories are a PROPOSED next step (ADR-007).
"""

from __future__ import annotations

import threading
from collections.abc import Iterable
from typing import Any
from uuid import UUID

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
    KnowledgeEntry,
    Milestone,
    PendingMatter,
    Permission,
    Record,
    Role,
    Task,
    Team,
    User,
    WorkOutput,
)


def _index[R: Record](items: Iterable[R]) -> dict[UUID, R]:
    return {item.id: item for item in items}


class SimulatedStore:
    def __init__(self, dataset: Dataset | None = None) -> None:
        ds = dataset or build_dataset()
        self.lock = threading.RLock()
        self.classifications: dict[str, DataClassification] = {
            c.code: c for c in ds.classifications
        }
        self.teams: dict[UUID, Team] = _index(ds.teams)
        self.roles: dict[UUID, Role] = _index(ds.roles)
        self.permissions: dict[UUID, Permission] = _index(ds.permissions)
        self.role_permissions: dict[UUID, set[UUID]] = {}
        for role_id, perm_id in ds.role_permissions:
            self.role_permissions.setdefault(role_id, set()).add(perm_id)
        self.users: dict[UUID, User] = _index(ds.users)
        self.memberships = list(ds.memberships)
        self.user_roles = list(ds.user_roles)
        self.knowledge: dict[UUID, KnowledgeEntry] = _index(ds.knowledge)
        self.documents: dict[UUID, DocumentReference] = _index(ds.documents)
        self.versions: dict[UUID, DocumentVersion] = _index(ds.versions)
        self.chunks: dict[UUID, DocumentChunk] = _index(ds.chunks)
        self.work_outputs: dict[UUID, WorkOutput] = _index(ds.work_outputs)
        self.tasks: dict[UUID, Task] = _index(ds.tasks)
        self.milestones: dict[UUID, Milestone] = _index(ds.milestones)
        self.pending_matters: dict[UUID, PendingMatter] = _index(ds.pending_matters)
        self.follow_ups: dict[UUID, FollowUp] = _index(ds.follow_ups)
        self.approvals: dict[UUID, ApprovalRequest] = _index(ds.approvals)
        self.data_quality_issues: dict[UUID, DataQualityIssue] = _index(ds.data_quality_issues)
        self.audit_logs: list[AuditLog] = list(ds.audit_logs)
        self.conversations: dict[UUID, AiConversation] = {}
        self.messages: dict[UUID, AiMessage] = {}
        self.citations: list[AiCitation] = []
        self.feedback: list[AiFeedback] = []

    # Lookups -----------------------------------------------------------------

    def user_by_email(self, email: str) -> User | None:
        wanted = email.strip().lower()
        return next((u for u in self.users.values() if u.email == wanted), None)

    def team_code(self, team_id: UUID | None) -> str | None:
        team = self.teams.get(team_id) if team_id else None
        return team.code if team else None

    def classification_rank(self, code: str) -> int | None:
        item = self.classifications.get(code)
        return item.rank if item else None

    def versions_of(self, document_id: UUID) -> list[DocumentVersion]:
        return sorted(
            (v for v in self.versions.values() if v.document_reference_id == document_id),
            key=lambda v: v.created_at,
        )

    def chunks_of_entry(self, entry_id: UUID) -> list[DocumentChunk]:
        current_versions = {
            d.current_version_id
            for d in self.documents.values()
            if d.knowledge_entry_id == entry_id and d.deleted_at is None
        }
        return sorted(
            (
                c
                for c in self.chunks.values()
                if c.knowledge_entry_id == entry_id and c.document_version_id in current_versions
            ),
            key=lambda c: c.chunk_index,
        )

    # Append-only audit -------------------------------------------------------

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
        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            outcome=outcome,
            request_id=request_id_var.get(),
            detail=detail or {},
        )
        with self.lock:
            self.audit_logs.append(entry)
        return entry
