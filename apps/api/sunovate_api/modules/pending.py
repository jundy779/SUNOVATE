"""Pending matters and follow-ups (read-only in this scaffold)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..core.responses import Pagination, envelope, paginated
from .work import with_deadline

router = APIRouter(tags=["pending matters and follow-ups"])


@router.get("/pending-matters")
def list_pending(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:read", resource="pending_matter"))],
    pagination: Annotated[Pagination, Depends()],
) -> dict[str, Any]:
    items = sorted(
        ctx.authz.readable(principal, ctx.store.pending_matters.values()),
        key=lambda p: (p.due_date is None, p.due_date),
    )
    page, meta = paginated(items, pagination)
    return envelope([with_deadline(ctx, p, p.due_date, p.status) for p in page], **meta)


@router.get("/follow-ups")
def list_follow_ups(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("pending:read", resource="follow_up"))],
    pagination: Annotated[Pagination, Depends()],
) -> dict[str, Any]:
    items = sorted(
        ctx.authz.readable(principal, ctx.store.follow_ups.values()),
        key=lambda f: (f.due_date is None, f.due_date),
    )
    page, meta = paginated(items, pagination)
    return envelope([with_deadline(ctx, f, f.due_date, f.status) for f in page], **meta)
