"""FastAPI application factory."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from .context import AppRuntime, build_runtime
from .core.config import Settings, get_settings
from .core.errors import error_body, log_unhandled_error, register_error_handlers
from .core.logging import configure_logging, request_id_var
from .modules import build_api_router

_REQUEST_ID_MAX = 128
_PRIVATE_RESPONSE_HEADERS = {
    "Cache-Control": "no-store, private, max-age=0, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
    "X-Robots-Tag": "noindex, nofollow, noarchive, nosnippet, noimageindex",
    "Content-Security-Policy": (
        "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), browsing-topics=()",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
}


def create_app(settings: Settings | None = None, runtime: AppRuntime | None = None) -> FastAPI:
    settings = settings or get_settings()
    logger = configure_logging(settings.log_level)
    runtime = runtime or build_runtime(settings)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            # Release the backend (connection pool) when the application shuts down.
            try:
                await run_in_threadpool(runtime.backend.close)
            except Exception as exc:  # noqa: BLE001 - shutdown must not raise
                logger.warning("backend close gagal", extra={"errorType": type(exc).__name__})

    expose_development_docs = settings.app_env in {"development", "test"}
    app = FastAPI(
        lifespan=lifespan,
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if expose_development_docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if expose_development_docs else None,
        description=(
            "SUNOVATE modular-monolith API scaffold. Development only; all data is "
            "SIMULATED_DATA and production integrations are disabled."
        ),
    )
    app.state.runtime = runtime

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
            except Exception as exc:  # noqa: BLE001 - last resort: sanitized log + generic 500
                log_unhandled_error(exc)
                response = JSONResponse(
                    error_body("INTERNAL_ERROR", "Terjadi kesalahan internal"), 500
                )
            response.headers["X-Request-ID"] = request_id
            for name, value in _PRIVATE_RESPONSE_HEADERS.items():
                response.headers[name] = value
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
