"""Approval requests and human decisions.

Separation of duties: a requester can never decide their own request (BR-06).
HERMES_WRITE_ACTION approval records the decision only; execution is NOT implemented.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import Field

from ..authz.dependencies import Ctx, CurrentPrincipal
from ..context import AppContext
from ..core.errors import ApiError, invalid_state, not_found, permission_denied
from ..core.responses import ApiModel, Pagination, envelope, paginated
from ..store.records import ApprovalRequest, utcnow
from ._common import governed_view, touch

router = APIRouter(prefix="/approvals", tags=["approvals"])


class DecisionRequest(ApiModel):
    decision: Literal["APPROVE", "REJECT"]
    revision: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=1000)


def _view(ctx: AppContext, request: ApprovalRequest) -> dict[str, Any]:
    return governed_view(ctx, request, executionImplemented=False)


@router.get("")
def list_approvals(
    ctx: Ctx, principal: CurrentPrincipal, pagination: Annotated[Pagination, Depends()]
) -> dict[str, Any]:
    if not (principal.has("approval:decide") or principal.has("approval:request")):
        ctx.authz.require(principal, "approval:request", resource="approval_request")
    items = [
        a
        for a in ctx.store.approvals.values()
        if a.requested_by == principal.user_id
        or (principal.has("approval:decide") and ctx.authz.can_read(principal, a))
    ]
    items.sort(key=lambda a: a.created_at, reverse=True)
    page, meta = paginated(items, pagination)
    return envelope([_view(ctx, a) for a in page], **meta)


@router.post("/{approval_id}/decision")
def decide(
    approval_id: UUID, body: DecisionRequest, ctx: Ctx, principal: CurrentPrincipal
) -> dict[str, Any]:
    ctx.authz.require(principal, "approval:decide", resource="approval_request")
    with ctx.store.lock:
        request = ctx.store.approvals.get(approval_id)
        if request is None or not ctx.authz.can_read(principal, request):
            raise not_found("Approval")
        if request.requested_by == principal.user_id:
            ctx.store.audit(
                actor_user_id=principal.user_id,
                action="ACCESS_DENIED",
                entity_type="approval_request",
                entity_id=request.id,
                outcome="DENIED",
                detail={"reason": "separation_of_duties"},
            )
            raise ApiError(
                403, "SEPARATION_OF_DUTIES", "Pengaju tidak dapat memutuskan permintaannya sendiri"
            )
        if request.status != "PENDING":
            raise invalid_state("Approval sudah diputuskan atau tidak aktif")
        approve = body.decision == "APPROVE"
        entry = None
        if request.request_type == "KNOWLEDGE_PUBLICATION":
            if approve and not principal.has("knowledge:publish"):
                ctx.authz.require(principal, "knowledge:publish", resource="knowledge_entry")
            entry = (
                ctx.store.knowledge.get(request.target_entity_id)
                if request.target_entity_id
                else None
            )
            if entry is None or entry.lifecycle_status != "IN_REVIEW":
                raise invalid_state("Knowledge target tidak dalam status IN_REVIEW")
            if not ctx.authz.can_write(principal, entry):
                raise permission_denied("Knowledge target di luar cakupan Anda")
        touch(request, principal, body.revision)
        request.status = "APPROVED" if approve else "REJECTED"
        request.decided_by = principal.user_id
        request.decided_at = utcnow()
        request.decision_reason = body.reason
        if entry is not None:
            entry.lifecycle_status = "PUBLISHED" if approve else "DRAFT"
            entry.revision += 1
            entry.updated_at = utcnow()
            entry.updated_by = principal.user_id
            entry.published_at = utcnow() if approve else entry.published_at
    ctx.store.audit(
        actor_user_id=principal.user_id,
        action="APPROVE" if approve else "REJECT",
        entity_type="approval_request",
        entity_id=request.id,
        detail={"requestType": request.request_type},
    )
    return envelope(_view(ctx, request))
