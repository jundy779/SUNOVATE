"""In-memory record types for the SIMULATED_DATA runtime store.

Field names mirror the PostgreSQL schema in `sunovate_api.db.models` so the same
dataset can seed both the runtime store and the database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID, uuid4

SIMULATED = "SIMULATED_DATA"


def utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(kw_only=True)
class Record:
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    data_origin: str = SIMULATED


@dataclass(kw_only=True)
class Governed(Record):
    """A business record with ownership, classification, revision and soft delete."""

    owner_team_id: UUID
    classification_code: str
    owner_user_id: UUID | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None
    revision: int = 1
    deleted_at: datetime | None = None

    def is_directorate_shared(self) -> bool:
        """Readable outside the owner team. Only knowledge may be shared (see BR-07)."""
        return False


# Identity and access ---------------------------------------------------------


@dataclass(kw_only=True)
class DataClassification(Record):
    code: str
    rank: int
    label: str
    description: str


@dataclass(kw_only=True)
class Team(Record):
    code: str
    name: str
    description: str
    validation_status: str = "NEEDS_MENTOR_VALIDATION"
    status: str = "ACTIVE"


@dataclass(kw_only=True)
class Role(Record):
    code: str
    name: str
    description: str


@dataclass(kw_only=True)
class Permission(Record):
    code: str
    description: str


@dataclass(kw_only=True)
class User(Record):
    email: str
    display_name: str
    clearance_code: str
    status: str = "ACTIVE"


@dataclass(kw_only=True)
class TeamMembership(Record):
    user_id: UUID
    team_id: UUID


@dataclass(kw_only=True)
class RevokedToken(Record):
    """A signed-out session token, kept until it would have expired anyway (AUD-05)."""

    token_id: str
    user_id: UUID
    expires_at: datetime


@dataclass(kw_only=True)
class SecureDocumentReader(Record):
    document_id: UUID
    user_id: UUID
    granted_by: UUID | None = None


@dataclass(kw_only=True)
class UserRole(Record):
    user_id: UUID
    role_id: UUID
    team_id: UUID | None = None


# Knowledge -------------------------------------------------------------------


@dataclass(kw_only=True)
class KnowledgeEntry(Governed):
    title: str
    knowledge_type: str
    summary: str
    lifecycle_status: str = "DRAFT"
    sharing_scope: str = "TEAM"
    version_label: str = "v0.1"
    effective_date: date | None = None
    source_note: str | None = None
    tags: list[str] = field(default_factory=list)
    published_at: datetime | None = None

    def is_directorate_shared(self) -> bool:
        return self.sharing_scope == "DIRECTORATE" and self.lifecycle_status == "PUBLISHED"


@dataclass(kw_only=True)
class DocumentReference(Governed):
    knowledge_entry_id: UUID | None
    title: str
    provider: str = "LOCAL_REFERENCE"
    provider_location: str
    mime_type: str = "application/pdf"
    current_version_id: UUID | None = None
    status: str = "ACTIVE"


@dataclass(kw_only=True)
class DocumentVersion(Record):
    document_reference_id: UUID
    version_label: str
    checksum_sha256: str
    size_bytes: int | None = None
    provider_location: str
    extraction_status: str = "EXTRACTED"
    created_by: UUID | None = None


@dataclass(kw_only=True)
class DocumentChunk(Record):
    document_version_id: UUID
    knowledge_entry_id: UUID
    chunk_index: int
    section_label: str
    content: str


# Work management -------------------------------------------------------------


@dataclass(kw_only=True)
class WorkOutput(Governed):
    title: str
    description: str
    status: str = "NOT_STARTED"
    priority: str = "NORMAL"
    progress: int = 0
    target_date: date | None = None


@dataclass(kw_only=True)
class Task(Governed):
    work_output_id: UUID | None
    title: str
    status: str = "NOT_STARTED"
    priority: str = "NORMAL"
    progress: int = 0
    due_date: date | None = None
    assignee_user_id: UUID | None = None


@dataclass(kw_only=True)
class Milestone(Governed):
    work_output_id: UUID
    title: str
    status: str = "PLANNED"
    due_date: date | None = None


@dataclass(kw_only=True)
class PendingMatter(Governed):
    title: str
    description: str
    status: str = "OPEN"
    due_date: date | None = None


@dataclass(kw_only=True)
class FollowUp(Governed):
    pending_matter_id: UUID | None
    title: str
    status: str = "OPEN"
    due_date: date | None = None


# Governance ------------------------------------------------------------------


@dataclass(kw_only=True)
class ApprovalRequest(Governed):
    request_type: str
    target_entity_type: str
    target_entity_id: UUID | None
    status: str = "PENDING"
    requested_by: UUID
    decided_by: UUID | None = None
    decided_at: datetime | None = None
    decision_reason: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class AuditLog(Record):
    occurred_at: datetime = field(default_factory=utcnow)
    actor_user_id: UUID | None
    action: str
    entity_type: str
    entity_id: UUID | None = None
    outcome: str = "SUCCESS"
    request_id: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class DataQualityIssue(Governed):
    entity_type: str
    entity_id: UUID
    issue_type: str
    severity: str
    description: str
    status: str = "OPEN"


# Hermes ----------------------------------------------------------------------


@dataclass(kw_only=True)
class AiConversation(Record):
    user_id: UUID
    title: str
    channel: str = "WEB"


@dataclass(kw_only=True)
class AiMessage(Record):
    conversation_id: UUID
    role: str
    content: str
    decision: str | None = None
    classification_code: str = "INTERNAL"


@dataclass(kw_only=True)
class AiCitation(Record):
    message_id: UUID
    citation_index: int
    knowledge_entry_id: UUID
    document_chunk_id: UUID
    score: float


@dataclass(kw_only=True)
class AiFeedback(Record):
    message_id: UUID
    user_id: UUID
    rating: str
    comment: str | None = None
