from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest
from starlette.requests import Request

from sunovate_api.core.api_controls import (
    InMemoryRateLimiter,
    buffer_request_body,
    client_rate_identity,
)
from sunovate_api.testing import make_client


def test_login_rate_limit_returns_standard_error_before_handler() -> None:
    client = make_client(api_login_rate_limit=2)
    payload = {"email": "sim.admin@sunovate.local"}

    assert client.post("/api/v1/auth/dev/login", json=payload).status_code == 200
    assert client.post("/api/v1/auth/dev/login", json=payload).status_code == 200
    response = client.post(
        "/api/v1/auth/dev/login",
        json=payload,
        headers={"X-Request-ID": "req-rate-limit"},
    )

    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"
    assert response.headers["x-request-id"] == "req-rate-limit"
    assert response.json() == {
        "code": "RATE_LIMITED",
        "message": "Terlalu banyak permintaan. Silakan coba kembali beberapa saat lagi.",
        "details": None,
        "requestId": "req-rate-limit",
    }
    metrics = client.app.state.api_control_metrics.snapshot()  # type: ignore[attr-defined]
    assert metrics["requests_total"] == 3
    assert metrics["rejected_rate_limit"] == 1


def test_oversized_request_is_rejected_without_route_parsing() -> None:
    client = make_client(api_max_request_bytes=65_536)
    response = client.post(
        "/api/v1/auth/dev/login",
        content=b"x" * 65_537,
        headers={"Content-Type": "application/json", "X-Request-ID": "req-too-large"},
    )

    assert response.status_code == 413
    assert response.json()["code"] == "REQUEST_TOO_LARGE"
    assert response.json()["requestId"] == "req-too-large"
    assert response.headers["cache-control"].startswith("no-store")
    metrics = client.app.state.api_control_metrics.snapshot()  # type: ignore[attr-defined]
    assert metrics["rejected_request_too_large"] == 1


def test_normal_request_body_is_preserved_for_downstream_validation() -> None:
    client = make_client(api_max_request_bytes=65_536)
    response = client.post(
        "/api/v1/auth/dev/login", json={"email": "sim.admin@sunovate.local"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["accessToken"]


@pytest.mark.asyncio
async def test_chunked_body_stops_when_actual_size_exceeds_limit() -> None:
    messages: AsyncIterator[dict[str, object]]

    async def chunks() -> AsyncIterator[dict[str, object]]:
        yield {"type": "http.request", "body": b"1234", "more_body": True}
        yield {"type": "http.request", "body": b"5", "more_body": False}

    messages = chunks()

    async def receive() -> dict[str, object]:
        return await anext(messages)

    request = Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/upload",
            "raw_path": b"/upload",
            "query_string": b"",
            "headers": [(b"content-length", b"0")],
            "client": ("127.0.0.1", 1234),
            "server": ("testserver", 80),
        },
        receive,
    )

    decision = await buffer_request_body(request, max_bytes=4, timeout_seconds=1)
    assert decision.status_code == 413
    assert decision.error_code == "REQUEST_TOO_LARGE"
    assert decision.body_bytes == 5


@pytest.mark.asyncio
async def test_body_read_timeout_is_a_sanitized_408_decision() -> None:
    async def receive() -> dict[str, object]:
        await asyncio.sleep(1)
        return {"type": "http.request", "body": b"late", "more_body": False}

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/upload",
            "headers": [],
            "client": ("127.0.0.1", 1234),
        },
        receive,
    )
    decision = await buffer_request_body(request, max_bytes=100, timeout_seconds=0)
    assert decision.status_code == 408
    assert decision.error_code == "REQUEST_BODY_TIMEOUT"
    assert decision.body_bytes == 0


@pytest.mark.asyncio
async def test_invalid_content_length_is_rejected() -> None:
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/upload",
            "headers": [(b"content-length", b"not-a-number")],
            "client": ("127.0.0.1", 1234),
        }
    )
    decision = await buffer_request_body(request, max_bytes=100, timeout_seconds=1)
    assert decision.status_code == 400
    assert decision.error_code == "INVALID_CONTENT_LENGTH"


def test_limiter_uses_retry_after_and_recovers_after_window() -> None:
    now = 100.0
    limiter = InMemoryRateLimiter(max_keys=100, clock=lambda: now)
    assert limiter.check("user", limit=1, window_seconds=10).allowed
    blocked = limiter.check("user", limit=1, window_seconds=10)
    assert not blocked.allowed
    assert blocked.retry_after_seconds == 10

    now = 111.0
    assert limiter.check("user", limit=1, window_seconds=10).allowed


def test_rate_identity_never_contains_raw_authorization_value() -> None:
    secret = "Bearer SIMULATED_SECRET_TOKEN"
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/health",
            "headers": [(b"authorization", secret.encode("ascii"))],
            "client": ("127.0.0.1", 1234),
        }
    )
    identity = client_rate_identity(request)
    assert secret not in identity
    assert "127.0.0.1" in identity
