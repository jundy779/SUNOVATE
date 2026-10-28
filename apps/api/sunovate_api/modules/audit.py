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
    principal: Annotated[Principal, Depends(require("audit:read", resource="audit_log"))],
    pagination: Annotated[Pagination, Depends()],
    action: Annotated[str | None, Query(max_length=32)] = None,
) -> dict[str, Any]:
    logs = ctx.store.audit_logs(action)  # newest first, read before this read is recorded
    page, meta = paginated(logs, pagination)
    # AUD-03 (partial): reading the audit trail is itself recorded, without the filter values.
    with ctx.store.transaction():
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="AUDIT_LOG_READ",
            entity_type="audit_log",
            detail={"filtered": action is not None, "returned": len(page)},
        )
    return envelope([serialize(entry) for entry in page], **meta)
