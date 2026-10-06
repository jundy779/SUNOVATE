"""FastAPI dependencies for the application context and the authenticated principal."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Annotated, cast

from fastapi import Depends, Header, Request

from ..context import AppContext, AppRuntime
from ..core.errors import unauthenticated
from .principal import Principal


def get_ctx(request: Request) -> Iterator[AppContext]:
    """One repository session per request; cached by FastAPI for all dependencies.

    Exit never commits: commits happen only inside `repo.transaction()` in handlers.
    """
    runtime = cast(AppRuntime, request.app.state.runtime)
    with runtime.backend.session() as repo:
        yield runtime.request_context(repo)


Ctx = Annotated[AppContext, Depends(get_ctx)]


def current_principal(ctx: Ctx, authorization: Annotated[str | None, Header()] = None) -> Principal:
    if not ctx.settings.dev_auth_enabled:
        # No production identity provider exists yet (OQ-07): nobody is authenticated.
        raise unauthenticated("Penyedia identitas belum dikonfigurasi")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthenticated()
    user_id = ctx.signer.verify(authorization[7:].strip())
    return ctx.authz.principal_for(user_id)


CurrentPrincipal = Annotated[Principal, Depends(current_principal)]


def require(*permissions: str, resource: str) -> Callable[..., Principal]:
    """Dependency enforcing that the principal holds every listed permission."""

    def dependency(ctx: Ctx, principal: CurrentPrincipal) -> Principal:
        ctx.authz.require(principal, *permissions, resource=resource)
        return principal

    return dependency
