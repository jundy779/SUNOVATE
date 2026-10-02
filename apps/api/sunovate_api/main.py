"""FastAPI application factory."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .context import AppContext, build_context
from .core.config import Settings, get_settings
from .core.errors import error_body, register_error_handlers
from .core.logging import configure_logging, request_id_var
from .modules import build_api_router

_REQUEST_ID_MAX = 128


def create_app(settings: Settings | None = None, context: AppContext | None = None) -> FastAPI:
    settings = settings or get_settings()
    logger = configure_logging(settings.log_level)
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "SUNOVATE modular-monolith API scaffold. Development only; all data is "
            "SIMULATED_DATA and production integrations are disabled."
        ),
    )
    app.state.ctx = context or build_context(settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        incoming = request.headers.get("x-request-id", "")
        request_id = incoming if 0 < len(incoming) <= _REQUEST_ID_MAX else str(uuid4())
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception:
                logger.exception("Unhandled application error")
                response = JSONResponse(
                    error_body("INTERNAL_ERROR", "Terjadi kesalahan internal"), 500
                )
            response.headers["X-Request-ID"] = request_id
            logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "durationMs": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            return response
        finally:
            request_id_var.reset(token)

    register_error_handlers(app)
    app.include_router(build_api_router(), prefix=settings.api_prefix)
    return app


app = create_app()
