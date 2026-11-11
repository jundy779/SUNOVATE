"""SAVI administrative tasks: SAVI prepares a draft, the employee reviews it (DEC-20261111-02).

The first task, a work report, is assembled from Monitoring Kerja data the caller may already
read; it needs no language model, so it runs today. Nothing is stored or sent: the draft is
returned to the employee, who edits and then accepts or rejects it. Only the decision is audited,
never the text, so the audit trail cannot leak report content.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Annotated, Any, Final, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import Field

from ..authz.dependencies import Ctx, require
from ..authz.principal import Principal
from ..core.responses import ApiModel, envelope
from ..domain import CLOSED_STATUSES
from ..store.records import Task
from .dashboard import attention_items
from .exports import _DEADLINE
from .work import task_view

router = APIRouter(tags=["savi-tasks"])

MAX_ATTENTION_LINES: Final = 15
TaskKind = Literal["WORK_REPORT"]


def _format_date(value: object) -> str:
    if not value:
        return "tanpa tenggat"
    text = str(value)[:10]  # ISO date, as in the work views
    year, month, day = text.split("-")
    return f"{day}-{month}-{year}"


def build_work_report(ctx: Ctx, principal: Principal) -> dict[str, Any]:
    """Draft weekly work report from records the caller is already allowed to read."""
    store = ctx.store
    tasks = ctx.authz.list_readable(principal, Task)
    views = [task_view(ctx, task) for task in tasks]
    attention = attention_items(ctx, principal)
    today = ctx.clock()
    week_start = today - timedelta(days=today.weekday())
    completed = [
        task
        for task in tasks
        if task.status == "COMPLETED" and week_start <= task.updated_at.date() <= today
    ]
    active = [
        view for view, task in zip(views, tasks, strict=True) if task.status not in CLOSED_STATUSES
    ]
    overdue = sum(view["deadlineState"] == "OVERDUE" for view in views)
    due_soon = sum(view["deadlineState"] in ("DUE_SOON", "DUE_TODAY") for view in views)
    follow_ups_due = sum(item["type"] == "FOLLOW_UP" for item in attention)
    teams = (
        "Seluruh tim Direktorat SUN"
        if principal.all_teams
        else ", ".join(sorted(filter(None, (store.team_code(t) for t in principal.team_ids))))
    )

    lines = [
        f"Draf laporan pekerjaan per {today:%d-%m-%Y}",
        f"Cakupan: {teams}",
        "",
        "Ringkasan",
        f"- Tugas aktif: {len(active)}",
        f"- Tugas terlambat: {overdue}",
        f"- Tugas jatuh tempo dalam waktu dekat: {due_soon}",
        f"- Tindak lanjut terlambat atau jatuh tempo dekat: {follow_ups_due}",
        f"- Tugas selesai minggu ini: {len(completed)}",
        "",
        "Perlu ditindaklanjuti",
    ]
    shown = attention[:MAX_ATTENTION_LINES]
    if shown:
        for item in shown:
            owner = item["assigneeName"] or "belum ditentukan"
            lines.append(
                f"- {item['title']} ({item['ownerTeamCode']}, {item['category'].lower()}): "
                f"{_DEADLINE.get(item['deadlineState'], item['deadlineState']).lower()}, "
                f"tenggat {_format_date(item['dueDate'])}, penanggung jawab {owner}"
            )
        if len(attention) > len(shown):
            lines.append(f"- dan {len(attention) - len(shown)} butir lain di Monitoring Kerja")
    else:
        lines.append("- Tidak ada tugas atau tindak lanjut yang terlambat atau jatuh tempo dekat.")
    if completed:
        lines += ["", "Selesai minggu ini"]
        lines += [f"- {task.title}" for task in completed[:MAX_ATTENTION_LINES]]
    lines += [
        "",
        "Catatan: draf disusun SAVI dari data Monitoring Kerja yang boleh Anda akses. "
        "Periksa dan lengkapi sebelum digunakan.",
    ]
    sources = [{"type": item["type"], "id": item["id"], "title": item["title"]} for item in shown]
    return {
        "draftId": str(uuid4()),
        "kind": "WORK_REPORT",
        "title": "Draf laporan pekerjaan",
        "text": "\n".join(lines),
        "sources": sources,
        "counts": {
            "activeTasks": len(active),
            "overdue": overdue,
            "dueSoon": due_soon,
            "followUpsDue": follow_ups_due,
            "completedThisWeek": len(completed),
            "attentionItems": len(attention),
        },
        "status": "AWAITING_REVIEW",
    }


@router.post("/savi/tasks/work-report", status_code=201, summary="Draft a work report for review")
def create_work_report(
    ctx: Ctx,
    principal: Annotated[
        Principal, Depends(require("hermes:query", "work:read", resource="savi_task"))
    ],
) -> dict[str, Any]:
    draft = build_work_report(ctx, principal)
    with ctx.store.transaction():
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="SAVI_TASK_DRAFTED",
            entity_type="savi_task",
            detail={"kind": draft["kind"], "draftId": draft["draftId"], **draft["counts"]},
        )
    return envelope(draft)


class TaskReview(ApiModel):
    draft_id: str = Field(pattern=r"^[0-9a-f-]{36}$")
    kind: TaskKind
    decision: Literal["ACCEPTED", "REJECTED"]
    edited: bool = False
    note: str | None = Field(default=None, max_length=500)


@router.post("/savi/tasks/reviews", status_code=201, summary="Record the employee's review")
def review_task(
    body: TaskReview,
    ctx: Ctx,
    principal: Annotated[
        Principal, Depends(require("hermes:query", "work:read", resource="savi_task"))
    ],
) -> dict[str, Any]:
    """The employee decides; SAVI never finalises a draft by itself."""
    with ctx.store.transaction():
        ctx.store.audit(
            actor_user_id=principal.user_id,
            action="SAVI_TASK_REVIEWED",
            entity_type="savi_task",
            detail={
                "kind": body.kind,
                "draftId": body.draft_id,
                "decision": body.decision,
                "edited": body.edited,
                "hasNote": bool(body.note),
            },
        )
    return envelope(
        {"draftId": body.draft_id, "decision": body.decision, "recordedBy": str(principal.user_id)}
    )
