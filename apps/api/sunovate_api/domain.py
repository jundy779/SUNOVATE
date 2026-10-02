"""Shared domain rules computed only by the backend (BR-12)."""

from __future__ import annotations

from datetime import date

TASK_STATUSES = (
    "NOT_STARTED",
    "IN_PROGRESS",
    "WAITING_INTERNAL",
    "WAITING_EXTERNAL",
    "ON_HOLD",
    "COMPLETED",
    "CANCELLED",
)
CLOSED_STATUSES = frozenset({"COMPLETED", "CANCELLED", "RESOLVED", "DONE", "ACHIEVED"})


def deadline_state(due: date | None, status: str, today: date, due_soon_days: int) -> str | None:
    """SAFE | DUE_SOON | DUE_TODAY | OVERDUE | COMPLETED, or None without a due date."""
    if status in CLOSED_STATUSES:
        return "COMPLETED"
    if due is None:
        return None
    remaining = (due - today).days
    if remaining < 0:
        return "OVERDUE"
    if remaining == 0:
        return "DUE_TODAY"
    if remaining <= due_soon_days:
        return "DUE_SOON"
    return "SAFE"
