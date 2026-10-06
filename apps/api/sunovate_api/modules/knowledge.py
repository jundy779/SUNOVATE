"""Knowledge entries: list, detail, create draft, update draft, submit for review."""

from __future__ import annotations

from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import Field, field_validator

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import ApiError, invalid_state, permission_denied
from ..core.responses import ApiModel, Pagination, envelope, paginated, serialize
from ..store.records import ApprovalRequest, DocumentReference, KnowledgeEntry
from ._common import governed_view, readable_or_404

router = APIRouter(prefix="/knowledge", tags=["knowledge entries"])

KnowledgeType = Literal[
    "REGULATION",
    "POLICY",
    "STUDY",
    "SOP",
    "PLAYBOOK",
    "REPORT",
    "MEETING_MATERIAL",
    "CLOSE_OUT_NOTE",
    "LESSON_LEARNED",
    "TACIT_KNOWLEDGE",
    "DECISION_RECORD",
    "ARCHIVE",
    "REFERENCE",
    "OTHER",
]
LifecycleStatus = Literal["DRAFT", "IN_REVIEW", "PUBLISHED", "SUPERSEDED", "ARCHIVED"]
ClassificationCode = Literal["PUBLIC", "INTERNAL", "RESTRICTED", "CONFIDENTIAL"]
SharingScope = Literal["TEAM", "DIRECTORATE"]


class KnowledgeCreate(ApiModel):
    title: str = Field(min_length=5, max_length=255)
    knowledge_type: KnowledgeType
    summary: str = Field(min_length=10, max_length=2000)
    classification_code: ClassificationCode
    sharing_scope: SharingScope = "TEAM"
    owner_team_id: UUID
    tags: list[Annotated[str, Field(min_length=1, max_length=48)]] = Field(
        default_factory=list, max_length=20
    )

    @field_validator("tags", mode="after")
    @classmethod
    def _dedupe_tags(cls, value: list[str]) -> list[str]:
        return _dedupe(value)


def _dedupe(value: list[str]) -> list[str]:
    """Duplicate tags are dropped; first occurrence wins, case-sensitive (ADR-015)."""
    return list(dict.fromkeys(value))


class KnowledgeUpdate(ApiModel):
    revision: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=5, max_length=255)
    summary: str | None = Field(default=None, min_length=10, max_length=2000)
    classification_code: ClassificationCode | None = None
    sharing_scope: SharingScope | None = None
    tags: list[Annotated[str, Field(min_length=1, max_length=48)]] | None = Field(
        default=None, max_length=20
    )

    @field_validator("tags", mode="after")
    @classmethod
    def _dedupe_tags(cls, value: list[str] | None) -> list[str] | None:
        return None if value is None else _dedupe(value)


class KnowledgeSubmit(ApiModel):
    revision: int = Field(ge=1)
    note: str | None = Field(default=None, max_length=1000)


def _view(ctx: AppContext, entry: KnowledgeEntry, *, detail: bool = False) -> dict[str, Any]:
    view = governed_view(ctx, entry)
    if detail:
        docs = ctx.store.list_governed(
            DocumentReference, where={"knowledge_entry_id": entry.id, "deleted_at": None}
        )
        view["documents"] = [serialize(d, exclude=("deleted_at",)) for d in docs]
        view["sections"] = [
            {"index": c.chunk_index, "sectionLabel": c.section_label, "content": c.content}
            for c in ctx.store.chunks_of_entry(entry.id)
        ]
    return view


def _check_target(
    ctx: AppContext, principal: Principal, team_id: UUID, classification: str
) -> None:
    if ctx.store.team(team_id) is None:
        raise ApiError(422, "VALIDATION_ERROR", "Tim pemilik tidak dikenal")
    if not ctx.authz.team_in_scope(principal, team_id):
        raise permission_denied("Anda hanya dapat membuat knowledge untuk tim Anda")
    if not ctx.authz.classification_allowed(principal.clearance_code, classification):
        raise permission_denied("Klasifikasi melebihi clearance Anda")


@router.get("")
def list_knowledge(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("knowledge:read", resource="knowledge"))],
    pagination: Annotated[Pagination, Depends()],
    q: Annotated[str | None, Query(max_length=200)] = None,
    status: Annotated[LifecycleStatus | None, Query()] = None,
    knowledge_type: Annotated[KnowledgeType | None, Query(alias="type")] = None,
    team_code: Annotated[str | None, Query(alias="teamCode", max_length=32)] = None,
) -> dict[str, Any]:
    items = ctx.authz.list_readable(principal, KnowledgeEntry)
    if q:
        needle = q.lower()
        items = [e for e in items if needle in f"{e.title} {e.summary}".lower()]
    if status:
        items = [e for e in items if e.lifecycle_status == status]
    if knowledge_type:
        items = [e for e in items if e.knowledge_type == knowledge_type]
    if team_code:
        items = [e for e in items if ctx.store.team_code(e.owner_team_id) == team_code]
    items.sort(key=lambda e: e.updated_at, reverse=True)
    page, meta = paginated(items, pagination)
    return envelope([_view(ctx, e) for e in page], **meta)


@router.get("/{entry_id}")
def get_knowledge(
    entry_id: UUID,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("knowledge:read", resource="knowledge"))],
) -> dict[str, Any]:
    entry = readable_or_404(ctx, principal, KnowledgeEntry, entry_id, "Knowledge")
    return envelope(_view(ctx, entry, detail=True))


@router.post("", status_code=201)
def create_knowledge(
    body: KnowledgeCreate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("knowledge:create", resource="knowledge"))],
) -> dict[str, Any]:
    _check_target(ctx, principal, body.owner_team_id, body.classification_code)
    entry = KnowledgeEntry(
        title=body.title,
        knowledge_type=body.knowledge_type,
        summary=body.summary,
        classification_code=body.classification_code,
        sharing_scope=body.sharing_scope,
        owner_team_id=body.owner_team_id,
        owner_user_id=principal.user_id,
        created_by=principal.user_id,
        updated_by=principal.user_id,
        tags=body.tags,
        data_origin="USER_ENTERED",
    )
    with ctx.store.transaction():
        ctx.store.insert(entry)
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="CREATE",
            entity_type="knowledge_entry",
            entity_id=entry.id,
        )
    return envelope(_view(ctx, entry))


@router.patch("/{entry_id}")
def update_knowledge(
    entry_id: UUID,
    body: KnowledgeUpdate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("knowledge:update", resource="knowledge"))],
) -> dict[str, Any]:
    with ctx.store.transaction():
        entry = readable_or_404(ctx, principal, KnowledgeEntry, entry_id, "Knowledge")
        if not ctx.authz.can_write(principal, entry):
            ctx.authz.deny_write(principal, entry, "knowledge_entry")
        if entry.lifecycle_status != "DRAFT":
            raise invalid_state("Hanya knowledge berstatus DRAFT yang dapat diubah")
        if body.classification_code:
            _check_target(ctx, principal, entry.owner_team_id, body.classification_code)
        # Explicit null means "unchanged" (ADR-015).
        changes = body.model_dump(exclude_unset=True, exclude_none=True, exclude={"revision"})
        updated = ctx.store.update_revisioned(
            KnowledgeEntry,
            entry.id,
            expected_revision=body.revision,
            changes=changes,
            actor_id=principal.user_id,
            expected_state={"lifecycle_status": "DRAFT"},
        )
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="UPDATE",
            entity_type="knowledge_entry",
            entity_id=updated.id,
            detail={"fields": sorted(changes)},
        )
    return envelope(_view(ctx, updated))


@router.post("/{entry_id}/submit")
def submit_knowledge(
    entry_id: UUID,
    body: KnowledgeSubmit,
    ctx: Ctx,
    principal: Annotated[
        Principal,
        Depends(require("knowledge:submit", "approval:request", resource="knowledge")),
    ],
) -> dict[str, Any]:
    with ctx.store.transaction():
        entry = readable_or_404(ctx, principal, KnowledgeEntry, entry_id, "Knowledge")
        if not ctx.authz.can_write(principal, entry):
            ctx.authz.deny_write(principal, entry, "knowledge_entry")
        if entry.lifecycle_status != "DRAFT":
            raise invalid_state("Hanya knowledge berstatus DRAFT yang dapat diajukan")
        updated = ctx.store.update_revisioned(
            KnowledgeEntry,
            entry.id,
            expected_revision=body.revision,
            changes={"lifecycle_status": "IN_REVIEW"},
            actor_id=principal.user_id,
            expected_state={"lifecycle_status": "DRAFT"},
        )
        request = ApprovalRequest(
            request_type="KNOWLEDGE_PUBLICATION",
            target_entity_type="knowledge_entry",
            target_entity_id=updated.id,
            requested_by=principal.user_id,
            owner_team_id=updated.owner_team_id,
            owner_user_id=principal.user_id,
            classification_code=updated.classification_code,
            created_by=principal.user_id,
            payload={"knowledgeRevision": updated.revision, "note": body.note},
            data_origin="USER_ENTERED",
        )
        ctx.store.insert(request)
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="SUBMIT",
            entity_type="knowledge_entry",
            entity_id=updated.id,
            detail={"approvalRequestId": str(request.id)},
        )
    return envelope({"knowledge": _view(ctx, updated), "approvalRequestId": request.id})
