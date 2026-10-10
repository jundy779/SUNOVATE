"""Work outputs, tasks and milestones. Deadline state is computed here only (BR-12)."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from pydantic import Field

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import ApiError, permission_denied
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
Priority = Literal["LOW", "NORMAL", "HIGH", "URGENT"]
ClassificationCode = Literal["PUBLIC", "INTERNAL", "RESTRICTED", "CONFIDENTIAL"]
MilestoneStatus = Literal["PLANNED", "ACHIEVED", "MISSED", "CANCELLED"]


class WorkOutputCreate(ApiModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=5, max_length=4000)
    owner_team_id: UUID
    classification_code: ClassificationCode = "INTERNAL"
    priority: Priority = "NORMAL"
    target_date: date | None = None


class WorkOutputUpdate(ApiModel):
    revision: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, min_length=5, max_length=4000)
    status: TaskStatus | None = None
    priority: Priority | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    target_date: date | None = None


class TaskCreate(ApiModel):
    title: str = Field(min_length=3, max_length=255)
    owner_team_id: UUID
    classification_code: ClassificationCode = "INTERNAL"
    work_output_id: UUID | None = None
    priority: Priority = "NORMAL"
    due_date: date | None = None


class MilestoneCreate(ApiModel):
    work_output_id: UUID
    title: str = Field(min_length=3, max_length=255)
    owner_team_id: UUID
    classification_code: ClassificationCode = "INTERNAL"
    due_date: date | None = None


class MilestoneUpdate(ApiModel):
    revision: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=3, max_length=255)
    status: MilestoneStatus | None = None
    due_date: date | None = None


class TaskUpdate(ApiModel):
    revision: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=3, max_length=255)
    status: TaskStatus | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    priority: Priority | None = None
    due_date: date | None = None


def _check_target(
    ctx: AppContext, principal: Principal, team_id: UUID, classification: str
) -> None:
    if ctx.store.team(team_id) is None:
        raise ApiError(422, "VALIDATION_ERROR", "Tim pemilik tidak dikenal")
    if not ctx.authz.team_in_scope(principal, team_id):
        raise permission_denied("Anda hanya dapat membuat data kerja untuk tim Anda")
    if not ctx.authz.classification_allowed(principal.clearance_code, classification):
        raise permission_denied("Klasifikasi melebihi clearance Anda")


def _writeable[G: Governed](
    ctx: AppContext, principal: Principal, kind: type[G], record_id: UUID, label: str
) -> G:
    record = readable_or_404(ctx, principal, kind, record_id, label)
    if not ctx.authz.can_write(principal, record):
        ctx.authz.deny_write(principal, record, kind.__name__.lower())
    return record


def _soft_delete[G: Governed](
    ctx: AppContext,
    principal: Principal,
    kind: type[G],
    record_id: UUID,
    revision: int,
    label: str,
) -> None:
    with ctx.store.transaction():
        record = _writeable(ctx, principal, kind, record_id, label)
        ctx.store.update_revisioned(
            kind,
            record.id,
            expected_revision=revision,
            changes={"deleted_at": ctx.clock()},
            actor_id=principal.user_id,
        )
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="DELETE",
            entity_type=kind.__name__.lower(),
            entity_id=record.id,
        )


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


@router.post("/work-outputs", status_code=201)
def create_output(
    body: WorkOutputCreate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:create", resource="work_output"))],
) -> dict[str, Any]:
    _check_target(ctx, principal, body.owner_team_id, body.classification_code)
    output = WorkOutput(
        title=body.title,
        description=body.description,
        priority=body.priority,
        target_date=body.target_date,
        owner_team_id=body.owner_team_id,
        owner_user_id=principal.user_id,
        classification_code=body.classification_code,
        created_by=principal.user_id,
        updated_by=principal.user_id,
        data_origin="USER_ENTERED",
    )
    with ctx.store.transaction():
        ctx.store.insert(output)
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="CREATE",
            entity_type="work_output",
            entity_id=output.id,
        )
    return envelope(output_view(ctx, output))


@router.get("/work-outputs/{output_id}")
def get_output(
    output_id: UUID,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:read", resource="work_output"))],
) -> dict[str, Any]:
    output = readable_or_404(ctx, principal, WorkOutput, output_id, "Output kerja")
    tasks = ctx.authz.list_readable(principal, Task, where={"work_output_id": output.id})
    milestones = ctx.authz.list_readable(principal, Milestone, where={"work_output_id": output.id})
    return envelope(
        {
            **output_view(ctx, output),
            "tasks": [task_view(ctx, t) for t in tasks],
            "milestones": [milestone_view(ctx, m) for m in milestones],
        }
    )


@router.patch("/work-outputs/{output_id}")
def update_output(
    output_id: UUID,
    body: WorkOutputUpdate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:update", resource="work_output"))],
) -> dict[str, Any]:
    with ctx.store.transaction():
        output = _writeable(ctx, principal, WorkOutput, output_id, "Output kerja")
        changes = body.model_dump(exclude_unset=True, exclude_none=True, exclude={"revision"})
        if changes.get("status", output.status) == "COMPLETED":
            changes["progress"] = 100
        updated = ctx.store.update_revisioned(
            WorkOutput,
            output.id,
            expected_revision=body.revision,
            changes=changes,
            actor_id=principal.user_id,
        )
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="UPDATE",
            entity_type="work_output",
            entity_id=updated.id,
            detail={"fields": sorted(changes)},
        )
    return envelope(output_view(ctx, updated))


@router.delete("/work-outputs/{output_id}", status_code=204)
def delete_output(
    output_id: UUID,
    revision: Annotated[int, Query(ge=1)],
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:update", resource="work_output"))],
) -> Response:
    _soft_delete(ctx, principal, WorkOutput, output_id, revision, "Output kerja")
    return Response(status_code=204)


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


@router.post("/tasks", status_code=201)
def create_task(
    body: TaskCreate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:create", resource="task"))],
) -> dict[str, Any]:
    _check_target(ctx, principal, body.owner_team_id, body.classification_code)
    if body.work_output_id is not None:
        parent = readable_or_404(ctx, principal, WorkOutput, body.work_output_id, "Output kerja")
        if parent.owner_team_id != body.owner_team_id:
            raise ApiError(
                422, "VALIDATION_ERROR", "Tugas dan output harus berada pada tim yang sama"
            )
    task = Task(
        work_output_id=body.work_output_id,
        title=body.title,
        priority=body.priority,
        due_date=body.due_date,
        owner_team_id=body.owner_team_id,
        owner_user_id=principal.user_id,
        classification_code=body.classification_code,
        created_by=principal.user_id,
        updated_by=principal.user_id,
        data_origin="USER_ENTERED",
    )
    with ctx.store.transaction():
        ctx.store.insert(task)
        ctx.store.audit(
            actor_user_id=principal.user_id, action="CREATE", entity_type="task", entity_id=task.id
        )
    return envelope(task_view(ctx, task))


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


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: UUID,
    revision: Annotated[int, Query(ge=1)],
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:update", resource="task"))],
) -> Response:
    _soft_delete(ctx, principal, Task, task_id, revision, "Tugas")
    return Response(status_code=204)


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


@router.post("/milestones", status_code=201)
def create_milestone(
    body: MilestoneCreate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:create", resource="milestone"))],
) -> dict[str, Any]:
    _check_target(ctx, principal, body.owner_team_id, body.classification_code)
    parent = readable_or_404(ctx, principal, WorkOutput, body.work_output_id, "Output kerja")
    if parent.owner_team_id != body.owner_team_id:
        raise ApiError(
            422, "VALIDATION_ERROR", "Milestone dan output harus berada pada tim yang sama"
        )
    milestone = Milestone(
        work_output_id=body.work_output_id,
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
        ctx.store.insert(milestone)
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="CREATE",
            entity_type="milestone",
            entity_id=milestone.id,
        )
    return envelope(milestone_view(ctx, milestone))


@router.patch("/milestones/{milestone_id}")
def update_milestone(
    milestone_id: UUID,
    body: MilestoneUpdate,
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:update", resource="milestone"))],
) -> dict[str, Any]:
    with ctx.store.transaction():
        milestone = _writeable(ctx, principal, Milestone, milestone_id, "Milestone")
        changes = body.model_dump(exclude_unset=True, exclude_none=True, exclude={"revision"})
        updated = ctx.store.update_revisioned(
            Milestone,
            milestone.id,
            expected_revision=body.revision,
            changes=changes,
            actor_id=principal.user_id,
        )
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="UPDATE",
            entity_type="milestone",
            entity_id=updated.id,
            detail={"fields": sorted(changes)},
        )
    return envelope(milestone_view(ctx, updated))


@router.delete("/milestones/{milestone_id}", status_code=204)
def delete_milestone(
    milestone_id: UUID,
    revision: Annotated[int, Query(ge=1)],
    ctx: Ctx,
    principal: Annotated[Principal, Depends(require("work:update", resource="milestone"))],
) -> Response:
    _soft_delete(ctx, principal, Milestone, milestone_id, revision, "Milestone")
    return Response(status_code=204)
