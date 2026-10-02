"""Audit log (read-only API; append-only store)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..core.responses import Pagination, envelope, paginated, serialize

router = APIRouter(tags=["audit logs"])


@router.get("/audit-logs")
def list_audit_logs(
    ctx: Ctx,
    _p: Annotated[Principal, Depends(require("audit:read", resource="audit_log"))],
    pagination: Annotated[Pagination, Depends()],
    action: Annotated[str | None, Query(max_length=32)] = None,
) -> dict[str, Any]:
    logs = ctx.store.audit_logs(action)  # newest first
    page, meta = paginated(logs, pagination)
    return envelope([serialize(entry) for entry in page], **meta)
