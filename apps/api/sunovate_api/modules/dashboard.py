"""Dashboard summary computed from the caller's authorized scope only.

Indicators are PROPOSED; the required set is an OPEN QUESTION (OQ-10).
"""

from __future__ import annotations

from collections import Counter
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..domain import CLOSED_STATUSES, TASK_STATUSES
from ..store.records import (
    ApprovalRequest,
    FollowUp,
    KnowledgeEntry,
    PendingMatter,
    Task,
    WorkOutput,
)
from .work import task_view, with_deadline

router = APIRouter(tags=["dashboard"])

ATTENTION_STATES = ("OVERDUE", "DUE_TODAY", "DUE_SOON")


@router.get("/dashboard/summary")
def dashboard_summary(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:read", resource="dashboard"))],
) -> dict[str, Any]:
    store, authz = ctx.store, ctx.authz
    outputs = authz.list_readable(principal, WorkOutput)
    tasks = [task_view(ctx, t) for t in authz.list_readable(principal, Task)]
    pending = (
        authz.list_readable(principal, PendingMatter) if principal.has("pending:read") else []
    )
    follow_ups = (
        [
            with_deadline(ctx, f, f.due_date, f.status)
            for f in authz.list_readable(principal, FollowUp)
        ]
        if principal.has("pending:read")
        else []
    )
    knowledge = (
        authz.list_readable(principal, KnowledgeEntry, where={"lifecycle_status": "PUBLISHED"})
        if principal.has("knowledge:read")
        else []
    )

    attention = [
        {
            "type": kind,
            "id": v["id"],
            "title": v["title"],
            "ownerTeamCode": v["ownerTeamCode"],
            "dueDate": v["dueDate"],
            "deadlineState": v["deadlineState"],
        }
        for kind, views in (("TASK", tasks), ("FOLLOW_UP", follow_ups))
        for v in views
        if v["deadlineState"] in ATTENTION_STATES
    ]
    attention.sort(key=lambda a: (ATTENTION_STATES.index(a["deadlineState"]), a["dueDate"]))
    counts = Counter(t["status"] for t in tasks)
    states = Counter(t["deadlineState"] for t in tasks)
    pending_approvals = (
        authz.list_readable(principal, ApprovalRequest, where={"status": "PENDING"})
        if principal.has("approval:decide")
        else []
    )

    return {
        "data": {
            "scope": {
                "allTeams": principal.all_teams,
                "teamCodes": sorted(filter(None, (store.team_code(t) for t in principal.team_ids))),
                "clearanceCode": principal.clearance_code,
            },
            "metrics": {
                "activeOutputs": sum(o.status not in CLOSED_STATUSES for o in outputs),
                "tasksDueSoon": states["DUE_SOON"] + states["DUE_TODAY"],
                "tasksOverdue": states["OVERDUE"],
                "openPendingMatters": sum(p.status not in CLOSED_STATUSES for p in pending),
                "openFollowUps": sum(f["status"] not in CLOSED_STATUSES for f in follow_ups),
                "pendingApprovals": len(pending_approvals),
            },
            "tasksByStatus": [{"status": s, "count": counts.get(s, 0)} for s in TASK_STATUSES],
            "attention": attention[:10],
            "recentKnowledge": [
                {
                    "id": str(k.id),
                    "title": k.title,
                    "knowledgeType": k.knowledge_type,
                    "ownerTeamCode": store.team_code(k.owner_team_id),
                    "updatedAt": k.updated_at.isoformat(),
                }
                for k in sorted(knowledge, key=lambda k: k.updated_at, reverse=True)[:5]
            ],
            "referenceDate": ctx.clock().isoformat(),
        },
        "meta": {"dataLabel": "SIMULATED_DATA", "indicatorStatus": "PROPOSED"},
    }
