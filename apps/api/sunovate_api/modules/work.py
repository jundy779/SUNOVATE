"""Work outputs, tasks and milestones. Deadline state is computed here only (BR-12)."""

from __future__ import annotations

from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import Field

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..context import AppContext
from ..core.responses import ApiModel, Pagination, envelope, paginated
from ..domain import deadline_state
from ..store.records import Governed, Milestone, Task, WorkOutput
from ._common import governed_view, readable_or_404

router = APIRouter(tags=["work outputs, tasks, milestones"])

TaskStatus = Literal[
    "NOT_STARTED",
    "IN_PROGRESS",
    "WAITING_INTERNAL",
    "WAITING_EXTERNAL",
    "ON_HOLD",
    "COMPLETED",
    "CANCELLED",
]
DeadlineState = Literal["SAFE", "DUE_SOON", "DUE_TODAY", "OVERDUE", "COMPLETED"]


class TaskUpdate(ApiModel):
    revision: int = Field(ge=1)
    status: TaskStatus | None = None
    progress: int | None = Field(default=None, ge=0, le=100)


def with_deadline(ctx: AppContext, record: Governed, due: Any, status: str) -> dict[str, Any]:
    return governed_view(
        ctx,
        record,
        deadlineState=deadline_state(due, status, ctx.clock(), ctx.settings.deadline_due_soon_days),
    )


def task_view(ctx: AppContext, task: Task) -> dict[str, Any]:
    return with_deadline(ctx, task, task.due_date, task.status)


def output_view(ctx: AppContext, output: WorkOutput) -> dict[str, Any]:
    return with_deadline(ctx, output, output.target_date, output.status)


def milestone_view(ctx: AppContext, milestone: Milestone) -> dict[str, Any]:
    return with_deadline(ctx, milestone, milestone.due_date, milestone.status)


@router.get("/work-outputs")
def list_outputs(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:read", resource="work_output"))],
    pagination: Annotated[Pagination, Depends()],
    team_code: Annotated[str | None, Query(alias="teamCode", max_length=32)] = None,
) -> dict[str, Any]:
    items = ctx.authz.list_readable(principal, WorkOutput)
    if team_code:
        items = [o for o in items if ctx.store.team_code(o.owner_team_id) == team_code]
    items.sort(key=lambda o: (o.target_date is None, o.target_date))
    page, meta = paginated(items, pagination)
    return envelope([output_view(ctx, o) for o in page], **meta)


@router.get("/work-outputs/{output_id}")
def get_output(
    output_id: UUID,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:read", resource="work_output"))],
) -> dict[str, Any]:
    output = readable_or_404(ctx, principal, WorkOutput, output_id, "Output kerja")
    tasks = ctx.authz.list_readable(principal, Task, where={"work_output_id": output.id})
    milestones = ctx.authz.list_readable(
        principal, Milestone, where={"work_output_id": output.id}
    )
    return envelope(
        {
            **output_view(ctx, output),
            "tasks": [task_view(ctx, t) for t in tasks],
            "milestones": [milestone_view(ctx, m) for m in milestones],
        }
    )


@router.get("/tasks")
def list_tasks(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:read", resource="task"))],
    pagination: Annotated[Pagination, Depends()],
    status: Annotated[TaskStatus | None, Query()] = None,
    deadline: Annotated[DeadlineState | None, Query(alias="deadlineState")] = None,
    team_code: Annotated[str | None, Query(alias="teamCode", max_length=32)] = None,
) -> dict[str, Any]:
    items = ctx.authz.list_readable(principal, Task)
    if status:
        items = [t for t in items if t.status == status]
    if team_code:
        items = [t for t in items if ctx.store.team_code(t.owner_team_id) == team_code]
    items.sort(key=lambda t: (t.due_date is None, t.due_date))
    views = [task_view(ctx, t) for t in items]
    if deadline:
        views = [v for v in views if v["deadlineState"] == deadline]
    page, meta = paginated(views, pagination)
    return envelope(page, **meta)


@router.patch("/tasks/{task_id}")
def update_task(
    task_id: UUID,
    body: TaskUpdate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:update", resource="task"))],
) -> dict[str, Any]:
    with ctx.store.transaction():
        task = readable_or_404(ctx, principal, Task, task_id, "Tugas")
        if not ctx.authz.can_write(principal, task):
            ctx.authz.deny_write(principal, task, "task")
        # Explicit null means "unchanged" (ADR-015).
        changes = body.model_dump(exclude_unset=True, exclude_none=True, exclude={"revision"})
        applied: dict[str, object] = dict(changes)
        if applied.get("status", task.status) == "COMPLETED":
            applied["progress"] = 100
        updated = ctx.store.update_revisioned(
            Task,
            task.id,
            expected_revision=body.revision,
            changes=applied,
            actor_id=principal.user_id,
        )
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="UPDATE",
            entity_type="task",
            entity_id=updated.id,
            detail={"fields": sorted(changes)},
        )
    return envelope(task_view(ctx, updated))


@router.get("/milestones")
def list_milestones(
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:read", resource="milestone"))],
    pagination: Annotated[Pagination, Depends()],
) -> dict[str, Any]:
    items = sorted(
        ctx.authz.list_readable(principal, Milestone),
        key=lambda m: (m.due_date is None, m.due_date),
    )
    page, meta = paginated(items, pagination)
    return envelope([milestone_view(ctx, m) for m in page], **meta)
