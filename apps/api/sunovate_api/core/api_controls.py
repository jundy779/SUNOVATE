"""In-process API controls for the single-host demo baseline.

This module deliberately has no external dependency. It limits request volume and
body size before route handlers run, and keeps only aggregate counters in memory.
It is not a replacement for reverse-proxy limits or a distributed rate limiter.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock

from fastapi import Request


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int = 0


class InMemoryRateLimiter:
    """Sliding-window limiter using monotonic timestamps and bounded keys."""

    def __init__(
        self,
        *,
        max_keys: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._max_keys = max_keys
        self._clock = clock
        self._events: dict[str, deque[float]] = {}
        self._lock = Lock()

    def check(self, key: str, *, limit: int, window_seconds: int) -> RateLimitDecision:
        now = self._clock()
        cutoff = now - window_seconds
        with self._lock:
            events = self._events.get(key)
            if events is None:
                self._discard_expired_keys(cutoff)
                if len(self._events) >= self._max_keys:
                    return RateLimitDecision(False, window_seconds)
                events = deque()
                self._events[key] = events
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                retry_after = max(1, math.ceil(events[0] + window_seconds - now))
                return RateLimitDecision(False, retry_after)
            events.append(now)
            return RateLimitDecision(True)

    def _discard_expired_keys(self, cutoff: float) -> None:
        expired = [
            key for key, events in self._events.items() if not events or events[-1] <= cutoff
        ]
        for key in expired:
            del self._events[key]


@dataclass(frozen=True)
class RequestBodyDecision:
    body_bytes: int
    status_code: int | None = None
    error_code: str | None = None
    message: str | None = None


async def buffer_request_body(
    request: Request,
    *,
    max_bytes: int,
    timeout_seconds: int,
) -> RequestBodyDecision:
    """Read at most ``max_bytes`` and preserve the body for downstream parsing."""
    raw_length = request.headers.get("content-length")
    if raw_length is not None:
        try:
            declared_length = int(raw_length)
        except ValueError:
            return RequestBodyDecision(
                0, 400, "INVALID_CONTENT_LENGTH", "Ukuran permintaan tidak valid"
            )
        if declared_length < 0:
            return RequestBodyDecision(
                0, 400, "INVALID_CONTENT_LENGTH", "Ukuran permintaan tidak valid"
            )
        if declared_length > max_bytes:
            return RequestBodyDecision(
                declared_length,
                413,
                "REQUEST_TOO_LARGE",
                "Ukuran permintaan melebihi batas yang diizinkan",
            )
    chunks: list[bytes] = []
    total = 0
    try:
        async with asyncio.timeout(timeout_seconds):
            async for chunk in request.stream():
                total += len(chunk)
                if total > max_bytes:
                    return RequestBodyDecision(
                        total,
                        413,
                        "REQUEST_TOO_LARGE",
                        "Ukuran permintaan melebihi batas yang diizinkan",
                    )
                chunks.append(chunk)
    except TimeoutError:
        return RequestBodyDecision(
            total,
            408,
            "REQUEST_BODY_TIMEOUT",
            "Waktu penerimaan permintaan telah habis",
        )

    body = b"".join(chunks)
    # Starlette's wrapped receive replays `_body` to the downstream request.
    # The attribute is internal but avoids an unbounded second read or dependency.
    request._body = body  # noqa: SLF001 - Starlette replays this buffered body downstream
    return RequestBodyDecision(total)


def client_rate_identity(request: Request) -> str:
    """Return a non-secret identity; raw authorization values are never retained."""
    client_host = request.client.host if request.client is not None else "unknown"
    authorization = request.headers.get("authorization")
    if not authorization:
        return f"ip:{client_host}"
    token_digest = hashlib.sha256(authorization.encode("utf-8")).hexdigest()[:24]
    return f"ip:{client_host}:token:{token_digest}"


class ApiControlMetrics:
    """Private, process-local counters. No public metrics endpoint is exposed."""

    def __init__(self) -> None:
        self._counts: defaultdict[str, int] = defaultdict(int)
        self._duration_ms = 0.0
        self._lock = Lock()

    def record(self, *, status_code: int, duration_ms: float, rejection: str | None) -> None:
        with self._lock:
            self._counts["requests_total"] += 1
            self._counts[f"responses_{status_code // 100}xx"] += 1
            if rejection is not None:
                self._counts[f"rejected_{rejection}"] += 1
            self._duration_ms += duration_ms

    def snapshot(self) -> dict[str, int | float]:
        with self._lock:
            return {**self._counts, "duration_ms_total": round(self._duration_ms, 2)}
