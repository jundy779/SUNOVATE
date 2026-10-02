"""Helpers shared by API modules."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import not_found, revision_conflict
from ..core.responses import serialize
from ..store.records import Governed, utcnow


def readable_or_404[G: Governed](
    ctx: AppContext, principal: Principal, items: Mapping[UUID, G], item_id: UUID, entity: str
) -> G:
    """Unreadable records are reported as 404 to avoid existence leaks (BR-20)."""
    item = items.get(item_id)
    if item is None or not ctx.authz.can_read(principal, item):
        raise not_found(entity)
    return item


def governed_view(ctx: AppContext, record: Governed, **extra: Any) -> dict[str, Any]:
    view = serialize(record, exclude=("deleted_at",))
    view["ownerTeamCode"] = ctx.store.team_code(record.owner_team_id)
    view.update(extra)
    return view


def touch(record: Governed, actor: Principal, expected_revision: int) -> None:
    """Optimistic concurrency (ADR-011): bump revision or raise 409."""
    if record.revision != expected_revision:
        raise revision_conflict(record.revision)
    record.revision += 1
    record.updated_at = utcnow()
    record.updated_by = actor.user_id
