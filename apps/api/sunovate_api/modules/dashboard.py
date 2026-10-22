"""Dashboard summary computed from the caller's authorized scope only.

Indicators are PROPOSED; the required set is an OPEN QUESTION (OQ-10).
"""

from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..context import AppContext
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


def _attention(
    ctx: AppContext,
    task_records: list[Task],
    tasks: list[dict[str, Any]],
    follow_up_records: list[FollowUp],
    follow_ups: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    store = ctx.store
    attention: list[dict[str, Any]] = []
    for kind, records, views in (
        ("TASK", task_records, tasks),
        ("FOLLOW_UP", follow_up_records, follow_ups),
    ):
        for record, view in zip(records, views, strict=True):
            if view["deadlineState"] not in ATTENTION_STATES:
                continue
            assignee_id = (
                record.assignee_user_id if isinstance(record, Task) else record.owner_user_id
            )
            assignee = store.user(assignee_id) if assignee_id else None
            attention.append(
                {
                    "type": kind,
                    "id": view["id"],
                    "title": view["title"],
                    "category": "Tugas" if kind == "TASK" else "Tindak lanjut",
                    "workStatus": view["status"],
                    "assigneeName": assignee.display_name if assignee else None,
                    "ownerTeamCode": view["ownerTeamCode"],
                    "dueDate": view["dueDate"],
                    "deadlineState": view["deadlineState"],
                }
            )
    attention.sort(key=lambda a: (ATTENTION_STATES.index(a["deadlineState"]), a["dueDate"]))
    return attention


def attention_items(ctx: AppContext, principal: Principal) -> list[dict[str, Any]]:
    """Every overdue or nearly due task and follow-up in the caller's scope, most urgent first."""
    task_records = ctx.authz.list_readable(principal, Task)
    follow_up_records = (
        ctx.authz.list_readable(principal, FollowUp) if principal.has("pending:read") else []
    )
    return _attention(
        ctx,
        task_records,
        [task_view(ctx, task) for task in task_records],
        follow_up_records,
        [with_deadline(ctx, f, f.due_date, f.status) for f in follow_up_records],
    )


@router.get("/dashboard/summary")
def dashboard_summary(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:read", resource="dashboard"))],
) -> dict[str, Any]:
    store, authz = ctx.store, ctx.authz
    outputs = authz.list_readable(principal, WorkOutput)
    task_records = authz.list_readable(principal, Task)
    tasks = [task_view(ctx, task) for task in task_records]
    pending = (
        authz.list_readable(principal, PendingMatter) if principal.has("pending:read") else []
    )
    follow_up_records = (
        authz.list_readable(principal, FollowUp) if principal.has("pending:read") else []
    )
    follow_ups = [
        with_deadline(ctx, follow_up, follow_up.due_date, follow_up.status)
        for follow_up in follow_up_records
    ]
    knowledge = (
        authz.list_readable(principal, KnowledgeEntry, where={"lifecycle_status": "PUBLISHED"})
        if principal.has("knowledge:read")
        else []
    )

    attention = _attention(ctx, task_records, tasks, follow_up_records, follow_ups)
    counts = Counter(t["status"] for t in tasks)
    states = Counter(t["deadlineState"] for t in tasks)
    reference_date = ctx.clock()
    week_start = reference_date - timedelta(days=reference_date.weekday())
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
                "totalActiveTasks": sum(t.status not in CLOSED_STATUSES for t in task_records),
                "attentionCount": len(attention),
                "inProgressTasks": counts["IN_PROGRESS"],
                "completedThisWeek": sum(
                    task.status == "COMPLETED"
                    and week_start <= task.updated_at.date() <= reference_date
                    for task in task_records
                ),
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
            "referenceDate": reference_date.isoformat(),
        },
        "meta": {"dataLabel": "SIMULATED_DATA", "indicatorStatus": "PROPOSED"},
    }
