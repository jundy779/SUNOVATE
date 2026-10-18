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
from .core.api_controls import (
    ApiControlMetrics,
    InMemoryRateLimiter,
    buffer_request_body,
    client_rate_identity,
    resolve_client_ip,
)
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


def _rate_bucket(request: Request, settings: Settings) -> tuple[str, int]:
    path = request.url.path
    if path.endswith("/auth/dev/login"):
        return "login", settings.api_login_rate_limit
    if path.endswith("/hermes/query"):
        return "savi", settings.api_savi_rate_limit
    if "/search" in path:
        return "search", settings.api_search_rate_limit
    if path.endswith("/knowledge/extract-preview"):
        return "ingestion", settings.api_ingestion_rate_limit
    return "default", settings.api_default_rate_limit


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
    limiter = InMemoryRateLimiter(max_keys=settings.api_rate_limit_max_keys)
    control_metrics = ApiControlMetrics()
    trusted_proxy_networks = settings.api_trusted_proxy_networks
    app.state.api_control_metrics = control_metrics

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
        rejection: str | None = None
        response: Response
        try:
            try:
                client_ip = resolve_client_ip(
                    request, trusted_proxy_networks=trusted_proxy_networks
                )
                identity = client_rate_identity(request, client_ip=client_ip)
                global_decision = limiter.check(
                    f"global:{client_ip}",
                    limit=settings.api_global_rate_limit,
                    window_seconds=settings.api_rate_limit_window_seconds,
                )
                bucket, bucket_limit = _rate_bucket(request, settings)
                rate_decision = global_decision
                if global_decision.allowed:
                    rate_decision = limiter.check(
                        f"{bucket}:{identity}",
                        limit=bucket_limit,
                        window_seconds=settings.api_rate_limit_window_seconds,
                    )
                if not rate_decision.allowed:
                    rejection = "rate_limit"
                    response = JSONResponse(
                        error_body(
                            "RATE_LIMITED",
                            "Terlalu banyak permintaan. Silakan coba kembali beberapa saat lagi.",
                        ),
                        429,
                        headers={"Retry-After": str(rate_decision.retry_after_seconds)},
                    )
                else:
                    body_decision = await buffer_request_body(
                        request,
                        max_bytes=settings.api_max_request_bytes,
                        timeout_seconds=settings.api_body_read_timeout_seconds,
                    )
                    if body_decision.status_code is not None:
                        rejection = (body_decision.error_code or "request_body").lower()
                        response = JSONResponse(
                            error_body(
                                body_decision.error_code or "BAD_REQUEST",
                                body_decision.message or "Permintaan tidak dapat diproses",
                            ),
                            body_decision.status_code,
                            headers={"Connection": "close"},
                        )
                    else:
                        response = await call_next(request)
            except Exception as exc:  # noqa: BLE001 - last resort: sanitized log + generic 500
                log_unhandled_error(exc)
                response = JSONResponse(
                    error_body("INTERNAL_ERROR", "Terjadi kesalahan internal"), 500
                )
            response.headers["X-Request-ID"] = request_id
            for name, value in _PRIVATE_RESPONSE_HEADERS.items():
                response.headers[name] = value
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            control_metrics.record(
                status_code=response.status_code,
                duration_ms=duration_ms,
                rejection=rejection,
            )
            log_extra: dict[str, object] = {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "durationMs": duration_ms,
            }
            if rejection is not None:
                log_extra["controlRejection"] = rejection
            logger.info(
                "request",
                extra=log_extra,
            )
            return response
        finally:
            request_id_var.reset(token)

    register_error_handlers(app)
    app.include_router(build_api_router(), prefix=settings.api_prefix)
    return app


app = create_app()
