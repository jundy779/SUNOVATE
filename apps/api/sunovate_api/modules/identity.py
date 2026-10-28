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
    principal: Annotated[Principal, Depends(require("user:read", resource="user"))],
    pagination: Annotated[Pagination, Depends()],
) -> dict[str, Any]:
    store = ctx.store
    # AUD-21: clearance levels are visible only to user administrators, not to every reader.
    show_clearance = principal.has("user:manage")
    roles_by_user = store.role_codes_by_user()
    teams_by_user = store.team_ids_by_user()
    rows = []
    for user in sorted(store.users(), key=lambda u: u.email):
        rows.append(
            {
                **serialize(user),
                "clearanceCode": user.clearance_code if show_clearance else None,
                "roles": sorted(roles_by_user.get(user.id, frozenset())),
                "teamCodes": sorted(
                    filter(
                        None,
                        (store.team_code(t) for t in teams_by_user.get(user.id, frozenset())),
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
    teams = sorted(ctx.store.teams(), key=lambda t: t.code)
    return envelope([serialize(t) for t in teams], total=len(teams))


@router.get("/roles")
def list_roles(
    ctx: Ctx, _p: Annotated[Principal, Depends(require("role:read", resource="role"))]
) -> dict[str, Any]:
    store = ctx.store
    codes_by_role = store.permission_codes_by_role()
    rows = [
        {**serialize(role), "permissions": sorted(codes_by_role.get(role.id, frozenset()))}
        for role in store.roles()
    ]
    return envelope(rows, total=len(rows), status="PROPOSED")


@router.get("/permissions")
def list_permissions(
    ctx: Ctx, _p: Annotated[Principal, Depends(require("role:read", resource="permission"))]
) -> dict[str, Any]:
    rows = [serialize(p) for p in sorted(ctx.store.permissions(), key=lambda p: p.code)]
    return envelope(rows, total=len(rows), status="PROPOSED")


@router.get("/classifications")
def list_classifications(ctx: Ctx, _principal: CurrentPrincipal) -> dict[str, Any]:
    rows = [serialize(c) for c in sorted(ctx.store.classifications(), key=lambda c: c.rank)]
    return envelope(rows, total=len(rows), status="NEEDS_MENTOR_VALIDATION")
