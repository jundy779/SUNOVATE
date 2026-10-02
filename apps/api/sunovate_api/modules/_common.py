"""Helpers shared by API modules."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import not_found
from ..core.responses import serialize
from ..store.records import Governed


def readable_or_404[G: Governed](
    ctx: AppContext, principal: Principal, kind: type[G], item_id: UUID, entity: str
) -> G:
    """Unreadable records are reported as 404 to avoid existence leaks (BR-20)."""
    item = ctx.store.get_governed(kind, item_id)
    if item is None or not ctx.authz.can_read(principal, item):
        raise not_found(entity)
    return item


def governed_view(ctx: AppContext, record: Governed, **extra: Any) -> dict[str, Any]:
    view = serialize(record, exclude=("deleted_at",))
    view["ownerTeamCode"] = ctx.store.team_code(record.owner_team_id)
    view.update(extra)
    return view
