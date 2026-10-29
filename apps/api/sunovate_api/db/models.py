"""PostgreSQL schema (SQLAlchemy 2). PROPOSED physical model; see docs/04-data/database-schema.md.

Rules: UUID keys, timestamps, revision for optimistic concurrency, classification and
ownership on business records, soft delete, `data_origin` label, no file BLOBs.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Index,
    Integer,
    MetaData,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

DATA_ORIGINS = "'SIMULATED_DATA','USER_ENTERED','INTEGRATION'"


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )


def _fk(target: str, *, nullable: bool = True, ondelete: str | None = None) -> Any:
    return mapped_column(
        UUID(as_uuid=True), ForeignKey(target, ondelete=ondelete), nullable=nullable, index=True
    )


class TimestampMixin:
    id: Mapped[uuid.UUID] = _uuid_pk()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_origin: Mapped[str] = mapped_column(String(32), server_default="SIMULATED_DATA")


class GovernedMixin(TimestampMixin):
    """Ownership, classification, actors, revision and soft delete."""

    owner_team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id"), index=True
    )
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    classification_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("data_classifications.code"), index=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    revision: Mapped[int] = mapped_column(Integer, server_default="1")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# Identity and access ---------------------------------------------------------


class DataClassification(Base, TimestampMixin):
    __tablename__ = "data_classifications"
    code: Mapped[str] = mapped_column(String(32), unique=True)
    rank: Mapped[int] = mapped_column(Integer, unique=True)
    label: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)


class Team(Base, TimestampMixin):
    __tablename__ = "teams"
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    validation_status: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), server_default="ACTIVE")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(320), unique=True)
    display_name: Mapped[str] = mapped_column(String(255))
    clearance_code: Mapped[str] = mapped_column(String(32), ForeignKey("data_classifications.code"))
    status: Mapped[str] = mapped_column(String(16), server_default="ACTIVE")


class TeamMembership(Base, TimestampMixin):
    __tablename__ = "team_memberships"
    __table_args__ = (UniqueConstraint("user_id", "team_id", name="uq_team_memberships_user_team"),)
    user_id: Mapped[uuid.UUID] = _fk("users.id", nullable=False, ondelete="CASCADE")
    team_id: Mapped[uuid.UUID] = _fk("teams.id", nullable=False, ondelete="CASCADE")


class RevokedToken(Base, TimestampMixin):
    """Session tokens revoked at logout; rows past `expires_at` may be purged (AUD-05)."""

    __tablename__ = "revoked_tokens"
    __table_args__ = (UniqueConstraint("token_id", name="uq_revoked_tokens_token_id"),)
    token_id: Mapped[str] = mapped_column(String(32), nullable=False)
    user_id: Mapped[uuid.UUID] = _fk("users.id", nullable=False, ondelete="CASCADE")
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )


class SecureDocumentReader(Base, TimestampMixin):
    """Reader grant for a RAHASIA document (ADR-020). The document itself lives in the vault,
    so document_id has no foreign key; grant history is kept in audit_logs."""

    __tablename__ = "secure_document_readers"
    __table_args__ = (
        UniqueConstraint("document_id", "user_id", name="uq_secure_document_readers_document_user"),
    )
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = _fk("users.id", nullable=False, ondelete="CASCADE")
    granted_by: Mapped[uuid.UUID | None] = _fk("users.id", ondelete="SET NULL")


class Role(Base, TimestampMixin):
    __tablename__ = "roles"
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text)


class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"
    code: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str] = mapped_column(Text)


class RolePermission(Base, TimestampMixin):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permissions_role_permission"),
    )
    role_id: Mapped[uuid.UUID] = _fk("roles.id", nullable=False, ondelete="CASCADE")
    permission_id: Mapped[uuid.UUID] = _fk("permissions.id", nullable=False, ondelete="CASCADE")


class UserRole(Base, TimestampMixin):
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "team_id", name="uq_user_roles_user_role_team"),
    )
    user_id: Mapped[uuid.UUID] = _fk("users.id", nullable=False, ondelete="CASCADE")
    role_id: Mapped[uuid.UUID] = _fk("roles.id", nullable=False, ondelete="CASCADE")
    team_id: Mapped[uuid.UUID | None] = _fk("teams.id")


# Knowledge -------------------------------------------------------------------


class KnowledgeEntry(Base, GovernedMixin):
    __tablename__ = "knowledge_entries"
    __table_args__ = (
        CheckConstraint(
            "lifecycle_status IN ('DRAFT','IN_REVIEW','PUBLISHED','SUPERSEDED','ARCHIVED')",
            name="lifecycle_status",
        ),
        CheckConstraint("sharing_scope IN ('TEAM','DIRECTORATE')", name="sharing_scope"),
        CheckConstraint(f"data_origin IN ({DATA_ORIGINS})", name="data_origin"),
        Index("ix_knowledge_entries_search_vector", "search_vector", postgresql_using="gin"),
    )
    title: Mapped[str] = mapped_column(String(255))
    knowledge_type: Mapped[str] = mapped_column(String(32), index=True)
    summary: Mapped[str] = mapped_column(Text)
    lifecycle_status: Mapped[str] = mapped_column(String(16), server_default="DRAFT", index=True)
    sharing_scope: Mapped[str] = mapped_column(String(16), server_default="TEAM")
    version_label: Mapped[str] = mapped_column(String(64), server_default="v0.1")
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    superseded_by_id: Mapped[uuid.UUID | None] = _fk("knowledge_entries.id")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    search_vector: Mapped[Any] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(summary, ''))",
            persisted=True,
        ),
    )


class DocumentReference(Base, GovernedMixin):
    """Reference to a file held by a document provider. The file itself is never stored."""

    __tablename__ = "document_references"
    knowledge_entry_id: Mapped[uuid.UUID | None] = _fk("knowledge_entries.id")
    title: Mapped[str] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(32), server_default="LOCAL_REFERENCE")
    provider_location: Mapped[str] = mapped_column(Text)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(128))
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(16), server_default="ACTIVE")


class DocumentVersion(Base, TimestampMixin):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint(
            "document_reference_id",
            "checksum_sha256",
            name="uq_document_versions_reference_checksum",
        ),
        CheckConstraint("checksum_sha256 ~ '^[a-f0-9]{64}$'", name="checksum_format"),
        CheckConstraint(
            "extraction_status IN ('PENDING','EXTRACTED','FAILED','QUARANTINED','NOT_APPLICABLE')",
            name="extraction_status",
        ),
    )
    document_reference_id: Mapped[uuid.UUID] = _fk(
        "document_references.id", nullable=False, ondelete="CASCADE"
    )
    version_label: Mapped[str] = mapped_column(String(64))
    checksum_sha256: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    provider_location: Mapped[str] = mapped_column(Text)
    extraction_status: Mapped[str] = mapped_column(String(16), server_default="PENDING")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = _fk("users.id")


class DocumentChunk(Base, TimestampMixin):
    """Derived retrieval text; rebuildable from the source version."""

    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint(
            "document_version_id", "chunk_index", name="uq_document_chunks_version_index"
        ),
        Index("ix_document_chunks_search_vector", "search_vector", postgresql_using="gin"),
    )
    document_version_id: Mapped[uuid.UUID] = _fk(
        "document_versions.id", nullable=False, ondelete="CASCADE"
    )
    knowledge_entry_id: Mapped[uuid.UUID] = _fk(
        "knowledge_entries.id", nullable=False, ondelete="CASCADE"
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    section_label: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    search_vector: Mapped[Any] = mapped_column(
        TSVECTOR, Computed("to_tsvector('simple', coalesce(content, ''))", persisted=True)
    )


class EmbeddingReference(Base, TimestampMixin):
    """Vector per chunk and model. Untyped dimension and no ANN index until a model is
    approved (ADR-009)."""

    __tablename__ = "embedding_references"
    __table_args__ = (
        UniqueConstraint(
            "document_chunk_id", "model_name", name="uq_embedding_references_chunk_model"
        ),
    )
    document_chunk_id: Mapped[uuid.UUID] = _fk(
        "document_chunks.id", nullable=False, ondelete="CASCADE"
    )
    model_name: Mapped[str] = mapped_column(String(128))
    dimensions: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[Any] = mapped_column(Vector())


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    label: Mapped[str] = mapped_column(String(128))


class KnowledgeTag(Base, TimestampMixin):
    __tablename__ = "knowledge_tags"
    __table_args__ = (
        UniqueConstraint("knowledge_entry_id", "tag_id", name="uq_knowledge_tags_entry_tag"),
        CheckConstraint("position >= 0", name="position"),
    )
    knowledge_entry_id: Mapped[uuid.UUID] = _fk(
        "knowledge_entries.id", nullable=False, ondelete="CASCADE"
    )
    tag_id: Mapped[uuid.UUID] = _fk("tags.id", nullable=False, ondelete="CASCADE")
    # Revision 0002: urutan tag sesuai input (0-based).
    position: Mapped[int] = mapped_column(Integer, server_default="0")


class RegulationRelation(Base, TimestampMixin):
    __tablename__ = "regulation_relations"
    __table_args__ = (
        UniqueConstraint(
            "source_entry_id",
            "target_entry_id",
            "relation_type",
            name="uq_regulation_relations_source_target_type",
        ),
        CheckConstraint(
            "relation_type IN ('AMENDS','REVOKES','IMPLEMENTS','REFERENCES','SUPERSEDES')",
            name="relation_type",
        ),
        CheckConstraint("source_entry_id <> target_entry_id", name="no_self_relation"),
    )
    source_entry_id: Mapped[uuid.UUID] = _fk("knowledge_entries.id", nullable=False)
    target_entry_id: Mapped[uuid.UUID] = _fk("knowledge_entries.id", nullable=False)
    relation_type: Mapped[str] = mapped_column(String(16))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = _fk("users.id")


# Work management -------------------------------------------------------------

TASK_STATUS_CHECK = (
    "status IN ('NOT_STARTED','IN_PROGRESS','WAITING_INTERNAL','WAITING_EXTERNAL','ON_HOLD',"
    "'COMPLETED','CANCELLED')"
)


class WorkOutput(Base, GovernedMixin):
    __tablename__ = "work_outputs"
    __table_args__ = (
        CheckConstraint(TASK_STATUS_CHECK, name="status"),
        CheckConstraint("progress BETWEEN 0 AND 100", name="progress"),
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), server_default="NOT_STARTED")
    priority: Mapped[str] = mapped_column(String(16), server_default="NORMAL")
    progress: Mapped[int] = mapped_column(Integer, server_default="0")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class Task(Base, GovernedMixin):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(TASK_STATUS_CHECK, name="status"),
        CheckConstraint("progress BETWEEN 0 AND 100", name="progress"),
    )
    work_output_id: Mapped[uuid.UUID | None] = _fk("work_outputs.id")
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), server_default="NOT_STARTED")
    priority: Mapped[str] = mapped_column(String(16), server_default="NORMAL")
    progress: Mapped[int] = mapped_column(Integer, server_default="0")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    assignee_user_id: Mapped[uuid.UUID | None] = _fk("users.id")


class Milestone(Base, GovernedMixin):
    __tablename__ = "milestones"
    __table_args__ = (
        CheckConstraint("status IN ('PLANNED','ACHIEVED','MISSED','CANCELLED')", name="status"),
    )
    work_output_id: Mapped[uuid.UUID] = _fk("work_outputs.id", nullable=False, ondelete="CASCADE")
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(16), server_default="PLANNED")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class PendingMatter(Base, GovernedMixin):
    __tablename__ = "pending_matters"
    __table_args__ = (
        CheckConstraint("status IN ('OPEN','IN_PROGRESS','RESOLVED','CANCELLED')", name="status"),
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), server_default="OPEN")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class FollowUp(Base, GovernedMixin):
    __tablename__ = "follow_ups"
    __table_args__ = (CheckConstraint("status IN ('OPEN','DONE','CANCELLED')", name="status"),)
    pending_matter_id: Mapped[uuid.UUID | None] = _fk("pending_matters.id")
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(16), server_default="OPEN")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)


# Hermes ----------------------------------------------------------------------


class AiConversation(Base, TimestampMixin):
    __tablename__ = "ai_conversations"
    user_id: Mapped[uuid.UUID] = _fk("users.id", nullable=False)
    title: Mapped[str] = mapped_column(String(255))
    channel: Mapped[str] = mapped_column(String(16), server_default="WEB")


class AiMessage(Base, TimestampMixin):
    __tablename__ = "ai_messages"
    __table_args__ = (CheckConstraint("role IN ('USER','ASSISTANT')", name="role"),)
    conversation_id: Mapped[uuid.UUID] = _fk(
        "ai_conversations.id", nullable=False, ondelete="CASCADE"
    )
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    decision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    classification_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("data_classifications.code")
    )
    prompt_version: Mapped[str | None] = mapped_column(String(32), nullable=True)


class AiCitation(Base, TimestampMixin):
    __tablename__ = "ai_citations"
    __table_args__ = (
        UniqueConstraint("message_id", "citation_index", name="uq_ai_citations_message_index"),
    )
    message_id: Mapped[uuid.UUID] = _fk("ai_messages.id", nullable=False, ondelete="CASCADE")
    citation_index: Mapped[int] = mapped_column(Integer)
    knowledge_entry_id: Mapped[uuid.UUID] = _fk("knowledge_entries.id", nullable=False)
    document_chunk_id: Mapped[uuid.UUID | None] = _fk("document_chunks.id")
    score: Mapped[float] = mapped_column(Float, server_default="0")


class AiFeedback(Base, TimestampMixin):
    __tablename__ = "ai_feedback"
    __table_args__ = (CheckConstraint("rating IN ('HELPFUL','NOT_HELPFUL')", name="rating"),)
    message_id: Mapped[uuid.UUID] = _fk("ai_messages.id", nullable=False, ondelete="CASCADE")
    user_id: Mapped[uuid.UUID] = _fk("users.id", nullable=False)
    rating: Mapped[str] = mapped_column(String(16))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


# Governance and cross-cutting ------------------------------------------------


class AuditLog(Base):
    """Append-only; UPDATE/DELETE rejected by trigger `audit_logs_append_only` (ADR-010)."""

    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = _uuid_pk()
    # Revision 0002: urutan insert deterministik; tidak pernah dikirim saat insert.
    seq: Mapped[int] = mapped_column(BigInteger, Identity(always=True), unique=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    actor_user_id: Mapped[uuid.UUID | None] = _fk("users.id")
    action: Mapped[str] = mapped_column(String(32), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    outcome: Mapped[str] = mapped_column(String(16), server_default="SUCCESS")
    request_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    detail: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    data_origin: Mapped[str] = mapped_column(String(32), server_default="SIMULATED_DATA")


class ApprovalRequest(Base, GovernedMixin):
    __tablename__ = "approval_requests"
    __table_args__ = (
        CheckConstraint(
            "request_type IN ('KNOWLEDGE_PUBLICATION','HERMES_WRITE_ACTION','DOCUMENT_VERSION',"
            "'ACCESS_EXCEPTION')",
            name="request_type",
        ),
        CheckConstraint(
            "status IN ('PENDING','APPROVED','REJECTED','CANCELLED','EXPIRED')", name="status"
        ),
        CheckConstraint(
            "decided_by IS NULL OR decided_by <> requested_by", name="separation_of_duties"
        ),
    )
    request_type: Mapped[str] = mapped_column(String(32))
    target_entity_type: Mapped[str] = mapped_column(String(64))
    target_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(16), server_default="PENDING", index=True)
    requested_by: Mapped[uuid.UUID] = _fk("users.id", nullable=False)
    decided_by: Mapped[uuid.UUID | None] = _fk("users.id")
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"
    recipient_user_id: Mapped[uuid.UUID] = _fk("users.id", nullable=False)
    notification_type: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    channel: Mapped[str] = mapped_column(String(16), server_default="IN_APP")
    dedupe_key: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    classification_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("data_classifications.code")
    )


class IntegrationSyncLog(Base, TimestampMixin):
    __tablename__ = "integration_sync_logs"
    provider_kind: Mapped[str] = mapped_column(String(64))
    provider_name: Mapped[str] = mapped_column(String(64))
    operation: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    records_processed: Mapped[int] = mapped_column(Integer, server_default="0")
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_production: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))


class DataQualityIssue(Base, GovernedMixin):
    __tablename__ = "data_quality_issues"
    __table_args__ = (
        CheckConstraint("severity IN ('LOW','MEDIUM','HIGH')", name="severity"),
        CheckConstraint("status IN ('OPEN','IN_PROGRESS','RESOLVED','DISMISSED')", name="status"),
    )
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    issue_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), server_default="OPEN")
