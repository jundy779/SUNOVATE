"""Approval requests and human decisions.

Separation of duties: a requester can never decide their own request (BR-06).
HERMES_WRITE_ACTION approval records the decision only; execution is NOT implemented.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import Field

from ..authz.dependencies import Ctx, CurrentPrincipal
from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import ApiError, invalid_state, not_found, permission_denied
from ..core.responses import ApiModel, Pagination, envelope, paginated
from ..store.records import ApprovalRequest, KnowledgeEntry, utcnow
from ._common import governed_view

router = APIRouter(prefix="/approvals", tags=["approvals"])


class DecisionRequest(ApiModel):
    decision: Literal["APPROVE", "REJECT"]
    revision: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=1000)


def _view(ctx: AppContext, request: ApprovalRequest, principal: Principal) -> dict[str, Any]:
    requester = ctx.store.user(request.requested_by)
    target = (
        ctx.store.get_governed(KnowledgeEntry, request.target_entity_id)
        if request.request_type == "KNOWLEDGE_PUBLICATION" and request.target_entity_id
        else None
    )
    target_title = None
    target_status = None
    if target is not None and ctx.authz.can_read(principal, target):
        target_title = target.title
        target_status = target.lifecycle_status
    return governed_view(
        ctx,
        request,
        executionImplemented=False,
        requestedByName=requester.display_name if requester else None,
        targetTitle=target_title,
        targetLifecycleStatus=target_status,
    )


@router.get("")
def list_approvals(
    ctx: Ctx,
    principal: CurrentPrincipal,
    pagination: Annotated[Pagination, Depends()],
    status: Annotated[str | None, Query(pattern="^(PENDING|APPROVED|REJECTED|CANCELLED)$")] = None,
    request_type: Annotated[str | None, Query(alias="requestType", max_length=64)] = None,
    team_code: Annotated[str | None, Query(alias="teamCode", max_length=32)] = None,
) -> dict[str, Any]:
    if not (principal.has("approval:decide") or principal.has("approval:request")):
        ctx.authz.require(principal, "approval:request", resource="approval_request")
    # No read scope: requesters see their own requests without can_read (design 6.3).
    items = [
        a
        for a in ctx.store.list_governed(ApprovalRequest)
        if a.requested_by == principal.user_id
        or (principal.has("approval:decide") and ctx.authz.can_read(principal, a))
    ]
    if status:
        items = [item for item in items if item.status == status]
    if request_type:
        items = [item for item in items if item.request_type == request_type]
    if team_code:
        items = [item for item in items if ctx.store.team_code(item.owner_team_id) == team_code]
    items.sort(key=lambda a: a.created_at, reverse=True)
    page, meta = paginated(items, pagination)
    return envelope([_view(ctx, a, principal) for a in page], **meta)


@router.post("/{approval_id}/decision")
def decide(
    approval_id: UUID, body: DecisionRequest, ctx: Ctx, principal: CurrentPrincipal
) -> dict[str, Any]:
    ctx.authz.require(principal, "approval:decide", resource="approval_request")
    with ctx.store.transaction():
        request = ctx.store.get_governed(ApprovalRequest, approval_id)
        if request is None or not ctx.authz.can_read(principal, request):
            raise not_found("Approval")
        if request.requested_by == principal.user_id:
            ctx.store.audit_denial(
                actor_user_id=principal.user_id,
                action="ACCESS_DENIED",
                entity_type="approval_request",
                entity_id=request.id,
                detail={"reason": "separation_of_duties"},
            )
            raise ApiError(
                403, "SEPARATION_OF_DUTIES", "Pengaju tidak dapat memutuskan permintaannya sendiri"
            )
        if request.status != "PENDING":
            raise invalid_state("Permintaan persetujuan sudah diputuskan atau tidak aktif")
        approve = body.decision == "APPROVE"
        entry: KnowledgeEntry | None = None
        if request.request_type == "KNOWLEDGE_PUBLICATION":
            if approve and not principal.has("knowledge:publish"):
                ctx.authz.require(principal, "knowledge:publish", resource="knowledge_entry")
            entry = (
                ctx.store.get_governed(KnowledgeEntry, request.target_entity_id)
                if request.target_entity_id
                else None
            )
            if entry is None or entry.lifecycle_status != "IN_REVIEW":
                raise invalid_state("Pengetahuan yang dituju tidak sedang diperiksa")
            if not ctx.authz.can_write(principal, entry):
                raise permission_denied("Pengetahuan yang dituju berada di luar cakupan akses Anda")
        # (1) The decision itself, guarded by the client's approval revision.
        decided = ctx.store.update_revisioned(
            ApprovalRequest,
            request.id,
            expected_revision=body.revision,
            changes={
                "status": "APPROVED" if approve else "REJECTED",
                "decided_by": principal.user_id,
                "decided_at": utcnow(),
                "decision_reason": body.reason,
            },
            actor_id=principal.user_id,
            expected_state={"status": "PENDING"},
        )
        # (2) The knowledge target, in the same transaction.
        if entry is not None:
            try:
                ctx.store.update_revisioned(
                    KnowledgeEntry,
                    entry.id,
                    expected_revision=entry.revision,
                    changes={
                        "lifecycle_status": "PUBLISHED" if approve else "DRAFT",
                        "published_at": utcnow() if approve else entry.published_at,
                    },
                    actor_id=principal.user_id,
                    expected_state={"lifecycle_status": "IN_REVIEW"},
                )
            except ApiError as exc:
                if exc.code != "REVISION_CONFLICT":
                    raise
                # Never leak the knowledge revision as if it were the approval revision.
                raise invalid_state("Pengetahuan yang dituju tidak sedang diperiksa") from exc
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="APPROVE" if approve else "REJECT",
            entity_type="approval_request",
            entity_id=decided.id,
            detail={"requestType": decided.request_type},
        )
    return envelope(_view(ctx, decided, principal))
