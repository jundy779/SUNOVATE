"""Public database health check reuses its result instead of connecting per call (AUD-08)."""

from __future__ import annotations

import pytest

from sunovate_api.modules import health
from sunovate_api.testing import make_client

API = "/api/v1/health/database"


@pytest.fixture(autouse=True)
def _fresh_cache() -> None:
    health._database_checks.clear()


def test_repeated_anonymous_calls_open_one_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    async def fake_check(url: str) -> bool:
        calls.append(url)
        return True

    monkeypatch.setattr(health, "_database_reachable", fake_check)
    client = make_client()
    for _ in range(5):
        response = client.get(API)
        assert response.status_code == 200
        assert "postgresql" not in response.text.lower()
    assert len(calls) == 1


def test_unreachable_database_is_also_cached_and_reported_without_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    async def fake_check(url: str) -> bool:
        calls.append(url)
        return False

    monkeypatch.setattr(health, "_database_reachable", fake_check)
    client = make_client()
    first = client.get(API)
    second = client.get(API)
    assert first.status_code == second.status_code == 503
    assert first.json()["code"] == "DATABASE_UNAVAILABLE"
    assert len(calls) == 1


def test_result_expires_after_the_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    clock = [1000.0]

    async def fake_check(url: str) -> bool:
        calls.append(url)
        return True

    monkeypatch.setattr(health, "_database_reachable", fake_check)
    monkeypatch.setattr(health.time, "monotonic", lambda: clock[0])
    client = make_client()
    client.get(API)
    clock[0] += health.DATABASE_CHECK_TTL_SECONDS + 1
    client.get(API)
    assert len(calls) == 2
