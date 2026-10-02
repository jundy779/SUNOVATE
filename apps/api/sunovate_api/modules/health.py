"""Health endpoints (public). Never expose credentials or connection strings."""

from __future__ import annotations

import asyncio
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
            "dataBackend": ctx.settings.data_backend,
        }
    )


@router.get("/health/database", summary="PostgreSQL connectivity check")
async def health_database(ctx: Ctx) -> dict[str, Any]:
    engine: AsyncEngine | None = None
    try:
        # Invalid DATABASE_URL raises ValueError here -> 503 like any connectivity failure.
        engine = create_async_engine(
            async_database_url(ctx.settings.database_url), pool_pre_ping=False
        )
        async with asyncio.timeout(3):
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - report unavailability without details
        raise ApiError(503, "DATABASE_UNAVAILABLE", "Database tidak dapat dijangkau") from exc
    finally:
        if engine is not None:
            await engine.dispose()
    return envelope(
        {
            "status": "ok",
            "note": "Konektivitas saja; runtime memakai DATA_BACKEND=" + ctx.settings.data_backend,
        }
    )
