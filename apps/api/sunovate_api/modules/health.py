"""Health endpoints (public). Never expose credentials or connection strings."""

from __future__ import annotations

import asyncio
import hashlib
import time
from typing import Any

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ..authz.dependencies import Ctx
from ..core.errors import ApiError
from ..core.responses import envelope
from ..db.urls import async_database_url

router = APIRouter(tags=["system"])


@router.get("/health", summary="Liveness check")
def health(ctx: Ctx) -> dict[str, Any]:
    return envelope(
        {
            "status": "ok",
            "service": "sunovate-api",
            "version": ctx.settings.app_version,
            "environment": ctx.settings.app_env,
            "dataBackend": ctx.data_backend,
        }
    )


# AUD-08: the endpoint is public, so each anonymous call must not open a new database
# connection. A result is reused for a short time; the cache key never contains the URL itself.
DATABASE_CHECK_TTL_SECONDS = 10.0
_database_checks: dict[str, tuple[float, bool]] = {}


async def _database_reachable(database_url: str) -> bool:
    engine: AsyncEngine | None = None
    try:
        # Invalid DATABASE_URL raises ValueError here -> unavailable like any failure.
        engine = create_async_engine(async_database_url(database_url), pool_pre_ping=False)
        async with asyncio.timeout(3):
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 - report unavailability without details
        return False
    finally:
        if engine is not None:
            await engine.dispose()


@router.get("/health/database", summary="PostgreSQL connectivity check")
async def health_database(ctx: Ctx) -> dict[str, Any]:
    key = hashlib.sha256(ctx.settings.database_url.encode()).hexdigest()
    now = time.monotonic()
    cached = _database_checks.get(key)
    if cached is not None and now - cached[0] < DATABASE_CHECK_TTL_SECONDS:
        reachable = cached[1]
    else:
        reachable = await _database_reachable(ctx.settings.database_url)
        _database_checks[key] = (time.monotonic(), reachable)
    if not reachable:
        raise ApiError(503, "DATABASE_UNAVAILABLE", "Database tidak dapat dijangkau")
    return envelope(
        {
            "status": "ok",
            "note": "Konektivitas saja; runtime memakai DATA_BACKEND=" + ctx.data_backend,
        }
    )
