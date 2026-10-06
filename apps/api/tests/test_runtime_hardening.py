"""Review NIT fixes: log hygiene, wired /health backend, DB error classes, shutdown.

Backend-neutral and DB-free; runs in `pnpm test` and `pnpm db:test`. PostgreSQL-only
counterparts live in postgres/test_postgres_backend.py.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import AbstractContextManager

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, InterfaceError, OperationalError

from sunovate_api.context import build_runtime
from sunovate_api.core.errors import ApiError, log_unhandled_error, sqlstate_of
from sunovate_api.core.logging import JsonFormatter
from sunovate_api.main import create_app
from sunovate_api.store.postgres import database_error_to_api
from sunovate_api.store.repository import Repository
from sunovate_api.store.simulated import SimulatedBackend, SimulatedStore
from sunovate_api.testing import make_client, make_settings

FAKE_VALUE = "SIMULATED_SECRET_VALUE_123"  # SIMULATED_DATA marker, not a real secret
API = "/api/v1"


class _Capture(logging.Handler):
    """Collects everything a handler could emit: formatted JSON plus the raw record."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.setFormatter(JsonFormatter())
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(self.format(record) + repr(record.__dict__))

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


@pytest.fixture
def captured() -> Iterator[_Capture]:
    capture = _Capture()
    logger = logging.getLogger("sunovate")
    logger.addHandler(capture)
    previous = logger.level
    logger.setLevel(logging.DEBUG)
    try:
        yield capture
    finally:
        logger.removeHandler(capture)
        logger.setLevel(previous)


def _unique_violation() -> IntegrityError:
    orig = psycopg.errors.UniqueViolation(
        f'duplicate key value violates unique constraint "x"\nDETAIL:  Key (title)=({FAKE_VALUE}) '
        "already exists."
    )
    return IntegrityError("INSERT INTO knowledge_entries ...", {"title": FAKE_VALUE}, orig)


# 1. Log hygiene ------------------------------------------------------------------------


def test_unmapped_db_error_is_not_logged_with_row_values(captured: _Capture) -> None:
    client = make_client(raise_server_exceptions=False)

    def boom() -> None:
        raise _unique_violation()

    client.app.add_api_route(f"{API}/__boom", boom)  # type: ignore[attr-defined]
    response = client.get(f"{API}/__boom", headers={"X-Request-ID": "req-nit-1"})

    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "INTERNAL_ERROR"
    assert body["message"] == "Terjadi kesalahan internal"
    assert body["details"] is None
    assert body["requestId"] == "req-nit-1"
    assert FAKE_VALUE not in response.text

    assert captured.lines, "the unhandled error must still be logged"
    assert FAKE_VALUE not in captured.text
    assert "DETAIL" not in captured.text
    assert "INSERT INTO" not in captured.text
    assert '"errorType": "IntegrityError"' in captured.text
    assert '"sqlstate": "23505"' in captured.text
    assert "req-nit-1" in captured.text
    assert "boom" in captured.text  # stack location is kept


def test_log_unhandled_error_omits_message_and_chained_causes(captured: _Capture) -> None:
    try:
        try:
            raise ValueError(f"inner {FAKE_VALUE}")
        except ValueError as inner:
            raise RuntimeError(f"outer {FAKE_VALUE}") from inner
    except RuntimeError as exc:
        log_unhandled_error(exc)

    assert FAKE_VALUE not in captured.text
    assert "RuntimeError" in captured.text
    assert "sqlstate" not in captured.text


# 2. /health reports the wired backend ---------------------------------------------------


def test_health_reports_wired_backend_not_configured_one() -> None:
    settings = make_settings(
        data_backend="postgres",
        database_url="postgresql+asyncpg://sim:placeholder@127.0.0.1:1/sim",
    )
    runtime = build_runtime(settings, backend=SimulatedBackend(SimulatedStore()))
    client = TestClient(create_app(settings, runtime))

    response = client.get(f"{API}/health")

    assert response.status_code == 200
    assert response.json()["data"]["dataBackend"] == "simulated"


def test_health_reports_simulated_for_simulated_backend() -> None:
    client = make_client(backend="simulated")
    assert client.get(f"{API}/health").json()["data"]["dataBackend"] == "simulated"


# 3. OperationalError classification ----------------------------------------------------


class _FakeDriverError(Exception):
    def __init__(self, sqlstate: str | None) -> None:
        super().__init__(f"driver message with {FAKE_VALUE}")
        self.sqlstate = sqlstate


def _operational(sqlstate: str | None) -> OperationalError:
    return OperationalError("SELECT 1", {"p": FAKE_VALUE}, _FakeDriverError(sqlstate))


@pytest.mark.parametrize("sqlstate", ["57014", "40P01", "40001", "55P03"])
def test_transient_sqlstates_map_to_database_busy(sqlstate: str) -> None:
    error = database_error_to_api(_operational(sqlstate))
    assert (error.status_code, error.code) == (503, "DATABASE_BUSY")
    assert error.headers == {"Retry-After": "5"}
    assert "sibuk" in error.message
    assert "dijangkau" not in error.message
    assert FAKE_VALUE not in error.message


@pytest.mark.parametrize("sqlstate", [None, "08006", "08001", "57P01", "53300", "XX000"])
def test_connection_failures_stay_database_unavailable(sqlstate: str | None) -> None:
    error = database_error_to_api(_operational(sqlstate))
    assert (error.status_code, error.code) == (503, "DATABASE_UNAVAILABLE")
    assert error.message == "Database tidak dapat dijangkau"
    assert error.headers is None


def test_interface_error_with_busy_sqlstate_is_still_unavailable() -> None:
    error = database_error_to_api(InterfaceError("SELECT 1", None, _FakeDriverError("40P01")))
    assert error.code == "DATABASE_UNAVAILABLE"


def test_sqlstate_of_only_returns_well_formed_codes() -> None:
    assert sqlstate_of(_operational("40P01")) == "40P01"
    assert sqlstate_of(_operational("not a sqlstate with text")) is None
    assert sqlstate_of(ValueError("x")) is None


def test_busy_error_response_carries_retry_after_header() -> None:
    client = make_client()
    error = database_error_to_api(_operational("57014"))

    def busy() -> None:
        raise error

    client.app.add_api_route(f"{API}/__busy", busy)  # type: ignore[attr-defined]
    response = client.get(f"{API}/__busy")

    assert response.status_code == 503
    assert response.headers["Retry-After"] == "5"
    assert response.json()["code"] == "DATABASE_BUSY"
    assert set(response.json()) == {"code", "message", "details", "requestId"}
    assert isinstance(error, ApiError)


# 4. Backend is closed at shutdown ------------------------------------------------------


class _CountingBackend:
    name = "simulated"

    def __init__(self) -> None:
        self._inner = SimulatedBackend(SimulatedStore())
        self.closed = 0

    def session(self) -> AbstractContextManager[Repository]:
        return self._inner.session()

    def close(self) -> None:
        self.closed += 1


def test_shutdown_closes_the_backend() -> None:
    backend = _CountingBackend()
    settings = make_settings(data_backend="simulated")
    app = create_app(settings, build_runtime(settings, backend=backend))  # type: ignore[arg-type]

    with TestClient(app) as client:
        assert client.get(f"{API}/health").status_code == 200
        assert backend.closed == 0
    assert backend.closed == 1


def test_shutdown_survives_a_failing_close(captured: _Capture) -> None:
    class _Failing(_CountingBackend):
        def close(self) -> None:
            raise RuntimeError(f"close failed {FAKE_VALUE}")

    settings = make_settings(data_backend="simulated")
    app = create_app(settings, build_runtime(settings, backend=_Failing()))  # type: ignore[arg-type]

    with TestClient(app) as client:
        assert client.get(f"{API}/health").status_code == 200
    assert FAKE_VALUE not in captured.text


def test_simulated_backend_close_is_a_noop() -> None:
    backend = SimulatedBackend(SimulatedStore())
    backend.close()
    with backend.session() as repo:
        assert repo.classifications()
