"""Scoped CRUD for pending matters and follow-ups."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from pydantic import Field

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..core.errors import ApiError, permission_denied
from ..core.responses import ApiModel, Pagination, envelope, paginated
from ..store.records import FollowUp, PendingMatter
from ._common import readable_or_404
from .work import _soft_delete, _writeable, with_deadline

router = APIRouter(tags=["pending matters and follow-ups"])

ClassificationCode = Literal["PUBLIC", "INTERNAL", "RESTRICTED", "CONFIDENTIAL"]
PendingStatus = Literal["OPEN", "IN_PROGRESS", "RESOLVED", "CANCELLED"]
FollowUpStatus = Literal["OPEN", "DONE", "CANCELLED"]


class PendingCreate(ApiModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=5, max_length=4000)
    owner_team_id: UUID
    classification_code: ClassificationCode = "INTERNAL"
    due_date: date | None = None


class PendingUpdate(ApiModel):
    revision: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, min_length=5, max_length=4000)
    status: PendingStatus | None = None
    due_date: date | None = None


class FollowUpCreate(ApiModel):
    title: str = Field(min_length=3, max_length=255)
    owner_team_id: UUID
    classification_code: ClassificationCode = "INTERNAL"
    pending_matter_id: UUID | None = None
    due_date: date | None = None


class FollowUpUpdate(ApiModel):
    revision: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=3, max_length=255)
    status: FollowUpStatus | None = None
    due_date: date | None = None


def _check_target(ctx: Ctx, principal: Principal, team_id: UUID, classification: str) -> None:
    if ctx.store.team(team_id) is None:
        raise ApiError(422, "VALIDATION_ERROR", "Tim pemilik tidak dikenal")
    if not ctx.authz.team_in_scope(principal, team_id):
        raise permission_denied("Anda hanya dapat membuat pending matter untuk tim Anda")
    if not ctx.authz.classification_allowed(principal.clearance_code, classification):
        raise permission_denied("Klasifikasi melebihi clearance Anda")


@router.get("/pending-matters")
def list_pending(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:read", resource="pending_matter"))],
    pagination: Annotated[Pagination, Depends()],
) -> dict[str, Any]:
    items = sorted(
        ctx.authz.list_readable(principal, PendingMatter),
        key=lambda p: (p.due_date is None, p.due_date),
    )
    page, meta = paginated(items, pagination)
    return envelope([with_deadline(ctx, p, p.due_date, p.status) for p in page], **meta)


@router.post("/pending-matters", status_code=201)
def create_pending(
    body: PendingCreate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:manage", resource="pending_matter"))],
) -> dict[str, Any]:
    _check_target(ctx, principal, body.owner_team_id, body.classification_code)
    item = PendingMatter(
        title=body.title,
        description=body.description,
        due_date=body.due_date,
        owner_team_id=body.owner_team_id,
        owner_user_id=principal.user_id,
        classification_code=body.classification_code,
        created_by=principal.user_id,
        updated_by=principal.user_id,
        data_origin="USER_ENTERED",
    )
    with ctx.store.transaction():
        ctx.store.insert(item)
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="CREATE",
            entity_type="pending_matter",
            entity_id=item.id,
        )
    return envelope(with_deadline(ctx, item, item.due_date, item.status))


@router.patch("/pending-matters/{item_id}")
def update_pending(
    item_id: UUID,
    body: PendingUpdate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:manage", resource="pending_matter"))],
) -> dict[str, Any]:
    with ctx.store.transaction():
        item = _writeable(ctx, principal, PendingMatter, item_id, "Pending matter")
        changes = body.model_dump(exclude_unset=True, exclude_none=True, exclude={"revision"})
        updated = ctx.store.update_revisioned(
            PendingMatter,
            item.id,
            expected_revision=body.revision,
            changes=changes,
            actor_id=principal.user_id,
        )
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="UPDATE",
            entity_type="pending_matter",
            entity_id=updated.id,
            detail={"fields": sorted(changes)},
        )
    return envelope(with_deadline(ctx, updated, updated.due_date, updated.status))


@router.delete("/pending-matters/{item_id}", status_code=204)
def delete_pending(
    item_id: UUID,
    revision: Annotated[int, Query(ge=1)],
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:manage", resource="pending_matter"))],
) -> Response:
    _soft_delete(ctx, principal, PendingMatter, item_id, revision, "Pending matter")
    return Response(status_code=204)


@router.get("/follow-ups")
def list_follow_ups(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:read", resource="follow_up"))],
    pagination: Annotated[Pagination, Depends()],
) -> dict[str, Any]:
    items = sorted(
        ctx.authz.list_readable(principal, FollowUp),
        key=lambda f: (f.due_date is None, f.due_date),
    )
    page, meta = paginated(items, pagination)
    return envelope([with_deadline(ctx, f, f.due_date, f.status) for f in page], **meta)


@router.post("/follow-ups", status_code=201)
def create_follow_up(
    body: FollowUpCreate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:manage", resource="follow_up"))],
) -> dict[str, Any]:
    _check_target(ctx, principal, body.owner_team_id, body.classification_code)
    if body.pending_matter_id is not None:
        parent = readable_or_404(
            ctx, principal, PendingMatter, body.pending_matter_id, "Pending matter"
        )
        if parent.owner_team_id != body.owner_team_id:
            raise ApiError(
                422,
                "VALIDATION_ERROR",
                "Tindak lanjut dan pending matter harus berada pada tim yang sama",
            )
    item = FollowUp(
        pending_matter_id=body.pending_matter_id,
        title=body.title,
        due_date=body.due_date,
        owner_team_id=body.owner_team_id,
        owner_user_id=principal.user_id,
        classification_code=body.classification_code,
        created_by=principal.user_id,
        updated_by=principal.user_id,
        data_origin="USER_ENTERED",
    )
    with ctx.store.transaction():
        ctx.store.insert(item)
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="CREATE",
            entity_type="follow_up",
            entity_id=item.id,
        )
    return envelope(with_deadline(ctx, item, item.due_date, item.status))


@router.patch("/follow-ups/{item_id}")
def update_follow_up(
    item_id: UUID,
    body: FollowUpUpdate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:manage", resource="follow_up"))],
) -> dict[str, Any]:
    with ctx.store.transaction():
        item = _writeable(ctx, principal, FollowUp, item_id, "Tindak lanjut")
        changes = body.model_dump(exclude_unset=True, exclude_none=True, exclude={"revision"})
        updated = ctx.store.update_revisioned(
            FollowUp,
            item.id,
            expected_revision=body.revision,
            changes=changes,
            actor_id=principal.user_id,
        )
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="UPDATE",
            entity_type="follow_up",
            entity_id=updated.id,
            detail={"fields": sorted(changes)},
        )
    return envelope(with_deadline(ctx, updated, updated.due_date, updated.status))


@router.delete("/follow-ups/{item_id}", status_code=204)
def delete_follow_up(
    item_id: UUID,
    revision: Annotated[int, Query(ge=1)],
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:manage", resource="follow_up"))],
) -> Response:
    _soft_delete(ctx, principal, FollowUp, item_id, revision, "Tindak lanjut")
    return Response(status_code=204)
