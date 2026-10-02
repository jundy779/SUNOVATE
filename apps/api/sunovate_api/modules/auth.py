"""Development authentication stub. Disabled outside development (ADR-005)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import Field

from ..authz.dependencies import Ctx, CurrentPrincipal
from ..authz.principal import Principal
from ..context import AppContext
from ..core.errors import ApiError, unauthenticated
from ..core.responses import ApiModel, envelope

router = APIRouter(prefix="/auth", tags=["auth (development stub)"])


class DevLoginRequest(ApiModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+$")


def principal_view(ctx: AppContext, principal: Principal) -> dict[str, Any]:
    return {
        "id": str(principal.user_id),
        "email": principal.email,
        "displayName": principal.display_name,
        "roles": sorted(principal.role_codes),
        "permissions": sorted(principal.permissions),
        "teams": sorted(
            ({"id": str(t), "code": ctx.store.team_code(t)} for t in principal.team_ids),
            key=lambda t: str(t["code"]),
        ),
        "allTeams": principal.all_teams,
        "clearanceCode": principal.clearance_code,
    }


@router.post("/dev/login", summary="Issue a development token for a SIMULATED user")
def dev_login(body: DevLoginRequest, ctx: Ctx) -> dict[str, Any]:
    if not ctx.settings.dev_auth_enabled or ctx.settings.app_env == "production":
        raise ApiError(404, "DEV_AUTH_DISABLED", "Login pengembangan tidak tersedia")
    user_id = ctx.providers.identity.resolve_login(body.email)
    if user_id is None:
        ctx.store.audit(
            actor_user_id=None,
            action="LOGIN",
            entity_type="user",
            outcome="DENIED",
            detail={"reason": "unknown_simulated_user"},
        )
        raise unauthenticated("Pengguna simulasi tidak dikenal")
    token, expires_at = ctx.signer.issue(user_id)
    principal = ctx.authz.principal_for(user_id)
    ctx.store.audit(actor_user_id=user_id, action="LOGIN", entity_type="user", entity_id=user_id)
    return envelope(
        {
            "accessToken": token,
            "tokenType": "Bearer",
            "expiresAt": expires_at,
            "user": principal_view(ctx, principal),
        }
    )


@router.get("/me", summary="Current principal")
def me(ctx: Ctx, principal: CurrentPrincipal) -> dict[str, Any]:
    return envelope(principal_view(ctx, principal))
