"""Users, teams, roles, permissions and data classifications (read-only)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from ..authz.dependencies import Ctx, CurrentPrincipal, require
from ..authz.principal import Principal
from ..core.responses import Pagination, envelope, paginated, serialize

router = APIRouter(tags=["users, teams, roles"])


@router.get("/users")
def list_users(
    ctx: Ctx,
    _p: Annotated[Principal, Depends(require("user:read", resource="user"))],
    pagination: Annotated[Pagination, Depends()],
) -> dict[str, Any]:
    store = ctx.store
    rows = []
    for user in sorted(store.users.values(), key=lambda u: u.email):
        role_ids = {ur.role_id for ur in store.user_roles if ur.user_id == user.id}
        rows.append(
            {
                **serialize(user),
                "roles": sorted(store.roles[r].code for r in role_ids),
                "teamCodes": sorted(
                    filter(
                        None,
                        (
                            store.team_code(m.team_id)
                            for m in store.memberships
                            if m.user_id == user.id
                        ),
                    )
                ),
            }
        )
    page, meta = paginated(rows, pagination)
    return envelope(page, **meta)


@router.get("/teams")
def list_teams(
    ctx: Ctx, _p: Annotated[Principal, Depends(require("team:read", resource="team"))]
) -> dict[str, Any]:
    teams = sorted(ctx.store.teams.values(), key=lambda t: t.code)
    return envelope([serialize(t) for t in teams], total=len(teams))


@router.get("/roles")
def list_roles(
    ctx: Ctx, _p: Annotated[Principal, Depends(require("role:read", resource="role"))]
) -> dict[str, Any]:
    store = ctx.store
    rows = [
        {
            **serialize(role),
            "permissions": sorted(
                store.permissions[p].code for p in store.role_permissions.get(role.id, set())
            ),
        }
        for role in store.roles.values()
    ]
    return envelope(rows, total=len(rows), status="PROPOSED")


@router.get("/permissions")
def list_permissions(
    ctx: Ctx, _p: Annotated[Principal, Depends(require("role:read", resource="permission"))]
) -> dict[str, Any]:
    rows = [serialize(p) for p in sorted(ctx.store.permissions.values(), key=lambda p: p.code)]
    return envelope(rows, total=len(rows), status="PROPOSED")


@router.get("/classifications")
def list_classifications(ctx: Ctx, _principal: CurrentPrincipal) -> dict[str, Any]:
    rows = [serialize(c) for c in sorted(ctx.store.classifications.values(), key=lambda c: c.rank)]
    return envelope(rows, total=len(rows), status="NEEDS_MENTOR_VALIDATION")
