"""Test helpers shared by `apps/api/tests` and the root `tests/` suites.

Backend selection (design 15.2): SUNOVATE_TEST_BACKEND=simulated (default) or postgres.
`postgres` requires SUNOVATE_TEST_DATABASE_URL pointing at a throwaway database
(`pnpm db:test` sets both).
"""

from __future__ import annotations

import functools
import os
from datetime import date
from typing import TYPE_CHECKING, Any, cast

import pytest
from fastapi.testclient import TestClient

from .context import build_runtime
from .core.config import DataBackendName, Settings
from .main import create_app
from .store.dataset import REFERENCE_DATE
from .store.repository import DataBackend
from .store.simulated import SimulatedBackend, SimulatedStore

if TYPE_CHECKING:
    from .store.postgres import PostgresBackend

TEST_SECRET = "test-only-secret-not-for-production"  # noqa: S105 - test fixture value

_backend = os.environ.get("SUNOVATE_TEST_BACKEND", "simulated")
if _backend not in ("simulated", "postgres"):
    raise RuntimeError("SUNOVATE_TEST_BACKEND harus 'simulated' atau 'postgres'")
TEST_BACKEND = cast(DataBackendName, _backend)
TEST_DATABASE_URL = os.environ.get("SUNOVATE_TEST_DATABASE_URL")
if TEST_BACKEND == "postgres" and not TEST_DATABASE_URL:
    raise RuntimeError("SUNOVATE_TEST_BACKEND=postgres membutuhkan SUNOVATE_TEST_DATABASE_URL")

requires_postgres = pytest.mark.skipif(
    TEST_BACKEND != "postgres", reason="postgres backend not selected"
)


def make_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "app_env": "test",
        "dev_auth_secret": TEST_SECRET,
        "log_level": "WARNING",
        # Always explicit so a developer's DATA_BACKEND does not leak into tests.
        "data_backend": TEST_BACKEND,
    }
    values.update(overrides)
    if values["data_backend"] == "postgres" and TEST_DATABASE_URL:
        values.setdefault("database_url", TEST_DATABASE_URL)
    return Settings(_env_file=None, **values)


@functools.cache
def shared_postgres_backend() -> PostgresBackend:
    """One engine/pool for the whole pytest session (no connection leak across apps)."""
    if not TEST_DATABASE_URL:
        raise RuntimeError("SUNOVATE_TEST_DATABASE_URL belum diisi")
    from .store.postgres import PostgresBackend

    return PostgresBackend(TEST_DATABASE_URL)


def make_client(
    today: date = REFERENCE_DATE,
    *,
    backend: DataBackendName | None = None,
    raise_server_exceptions: bool = True,
    **overrides: Any,
) -> TestClient:
    data_backend: DataBackendName = backend or TEST_BACKEND
    settings = make_settings(data_backend=data_backend, **overrides)
    selected: DataBackend = (
        shared_postgres_backend()
        if data_backend == "postgres"
        else SimulatedBackend(SimulatedStore())
    )
    runtime = build_runtime(settings, backend=selected, clock=lambda: today)
    app = create_app(settings, runtime)
    return TestClient(app, raise_server_exceptions=raise_server_exceptions)


def reset_backend_state() -> None:
    """Called before every test: no-op on simulated; TRUNCATE + seed on postgres."""
    if TEST_BACKEND != "postgres":
        return
    from .db.testing_reset import reset_database

    reset_database(shared_postgres_backend().engine, make_settings())


def login(client: TestClient, local_part: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/dev/login", json={"email": f"{local_part}@sunovate.local"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['data']['accessToken']}"}
