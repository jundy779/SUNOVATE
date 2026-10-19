"""Config and guards without a database: DATABASE_URL rule (design 3.2), production guard
(AC-01.2, AC-06.1), seed and reset refusal (AC-06.2, AC-06.3), unreachable DB (NFR-02)."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import traceback
from pathlib import Path
from typing import NoReturn, cast

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import Engine

from sunovate_api.context import build_runtime
from sunovate_api.core.config import Settings
from sunovate_api.core.logging import JsonFormatter
from sunovate_api.db.testing_reset import reset_database
from sunovate_api.db.urls import async_database_url, parse_database_url, sync_database_url
from sunovate_api.main import create_app
from sunovate_api.store.dataset import sid
from sunovate_api.store.postgres import PostgresBackend
from sunovate_api.testing import make_settings

PLACEHOLDER_PASSWORD = "SIMULATED-placeholder"
API_DIR = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("scheme", ["postgresql+asyncpg", "postgresql+psycopg"])
def test_allowed_schemes_are_accepted(scheme: str) -> None:
    url = parse_database_url(f"{scheme}://sim:{PLACEHOLDER_PASSWORD}@127.0.0.1:5432/sim")
    assert url.drivername == scheme
    assert url.database == "sim"


@pytest.mark.parametrize(
    "raw",
    [
        f"postgresql://sim:{PLACEHOLDER_PASSWORD}@127.0.0.1:5432/sim",
        f"mysql://sim:{PLACEHOLDER_PASSWORD}@127.0.0.1:3306/sim",
        f"not a url {PLACEHOLDER_PASSWORD}",
    ],
)
def test_rejected_urls_do_not_leak_password(raw: str) -> None:
    with pytest.raises(ValueError, match="DATABASE_URL") as info:
        parse_database_url(raw)
    exc = info.value
    assert PLACEHOLDER_PASSWORD not in str(exc)
    assert PLACEHOLDER_PASSWORD not in "".join(traceback.format_exception(exc))
    assert exc.__cause__ is None
    assert exc.__suppress_context__ is True


@pytest.mark.parametrize("scheme", ["postgresql+asyncpg", "postgresql+psycopg"])
def test_sync_and_async_drivernames(scheme: str) -> None:
    raw = f"{scheme}://sim:{PLACEHOLDER_PASSWORD}@127.0.0.1:5432/sim"
    assert sync_database_url(raw).drivername == "postgresql+psycopg"
    assert async_database_url(raw).drivername == "postgresql+asyncpg"
    assert sync_database_url(raw).password == PLACEHOLDER_PASSWORD


def test_seed_refuses_production() -> None:
    env = {
        **os.environ,
        "APP_ENV": "production",
        "DATABASE_URL": f"postgresql+asyncpg://sim:{PLACEHOLDER_PASSWORD}@127.0.0.1:1/sim",
    }
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "sunovate_api.db.seed"],
        cwd=API_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    # Settings itself rejects APP_ENV=production with DATA_BACKEND=simulated: non-zero.
    assert result.returncode != 0


def test_seed_refuses_production_with_valid_production_settings() -> None:
    """Valid production settings (postgres, dev auth off) reach seed()'s own refusal."""
    env = {
        **os.environ,
        "APP_ENV": "production",
        "DATA_BACKEND": "postgres",
        "DEV_AUTH_ENABLED": "false",
        "DATABASE_URL": f"postgresql+asyncpg://sim:{PLACEHOLDER_PASSWORD}@127.0.0.1:1/sim",
    }
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "sunovate_api.db.seed"],
        cwd=API_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode != 0
    assert "Refusing to seed SIMULATED_DATA when APP_ENV=production" in result.stderr
    assert PLACEHOLDER_PASSWORD not in result.stdout + result.stderr


# Settings and production guard (AC-01.2, AC-06.1) ------------------------------------


def test_production_with_postgres_and_dev_auth_disabled_is_valid() -> None:
    settings = Settings(
        _env_file=None, app_env="production", dev_auth_enabled=False, data_backend="postgres"
    )
    assert (settings.app_env, settings.data_backend) == ("production", "postgres")


def test_production_refuses_simulated_backend() -> None:
    with pytest.raises(ValidationError, match="DATA_BACKEND=simulated"):
        Settings(
            _env_file=None, app_env="production", dev_auth_enabled=False, data_backend="simulated"
        )


def test_production_refuses_dev_auth() -> None:
    with pytest.raises(ValidationError, match="DEV_AUTH_ENABLED"):
        Settings(
            _env_file=None, app_env="production", dev_auth_enabled=True, data_backend="postgres"
        )


def test_unknown_data_backend_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, data_backend="mysql")  # type: ignore[arg-type]


def test_default_data_backend_is_simulated() -> None:
    assert Settings(_env_file=None).data_backend == "simulated"


def test_private_data_boundary_accepts_secure_dotenv_strings(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            (
                "PRIVATE_DATA_MODE=true",
                "PUBLIC_INDEXING_ENABLED=false",
                "EXTERNAL_AI_DATA_EGRESS_ENABLED=false",
                "EXTERNAL_AGENT_ACCESS_ENABLED=false",
                "TELEMETRY_DATA_EGRESS_ENABLED=false",
            )
        ),
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.private_data_mode is True
    assert settings.public_indexing_enabled is False
    assert settings.external_ai_data_egress_enabled is False
    assert settings.external_agent_access_enabled is False
    assert settings.telemetry_data_egress_enabled is False


@pytest.mark.parametrize(
    ("field", "unsafe_value"),
    [
        ("private_data_mode", False),
        ("public_indexing_enabled", True),
        ("external_ai_data_egress_enabled", True),
        ("external_agent_access_enabled", True),
        ("telemetry_data_egress_enabled", True),
    ],
)
def test_private_data_boundary_cannot_be_disabled(field: str, unsafe_value: bool) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{field: unsafe_value})


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("PRIVATE_DATA_MODE", "false"),
        ("PUBLIC_INDEXING_ENABLED", "true"),
        ("EXTERNAL_AI_DATA_EGRESS_ENABLED", "true"),
        ("EXTERNAL_AGENT_ACCESS_ENABLED", "true"),
        ("TELEMETRY_DATA_EGRESS_ENABLED", "true"),
    ],
)
def test_private_data_boundary_rejects_unsafe_dotenv_strings(
    tmp_path: Path, key: str, value: str
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(f"{key}={value}\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        Settings(_env_file=env_file)


def test_private_response_headers_are_applied_to_every_api_response() -> None:
    client = TestClient(create_app(make_settings()))
    response = client.get("/api/v1/health")
    assert response.headers["cache-control"] == "no-store, private, max-age=0, must-revalidate"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["expires"] == "0"
    assert response.headers["x-robots-tag"] == (
        "noindex, nofollow, noarchive, nosnippet, noimageindex"
    )
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cross-origin-resource-policy"] == "same-origin"


def test_api_schema_and_interactive_docs_are_hidden_outside_development() -> None:
    client = TestClient(create_app(make_settings(app_env="staging")))
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


# Reset guard (AC-06.3) ---------------------------------------------------------------


class _UntouchableEngine:
    """Any use of the engine fails the test: the guard must run first."""

    def begin(self) -> NoReturn:
        pytest.fail("reset_database touched the engine before its guard")

    def connect(self) -> NoReturn:
        pytest.fail("reset_database touched the engine before its guard")


def test_reset_database_refuses_production_before_using_engine() -> None:
    settings = make_settings(app_env="production", dev_auth_enabled=False, data_backend="postgres")
    with pytest.raises(RuntimeError, match="APP_ENV=test"):
        reset_database(cast(Engine, _UntouchableEngine()), settings)


# Unreachable database (NFR-02, AC-01.6) ------------------------------------------------


class _Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.setFormatter(JsonFormatter())
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(self.format(record) + repr(record.__dict__))


def test_unreachable_database_returns_503_without_leaking_url() -> None:
    unreachable = f"postgresql+asyncpg://sim:{PLACEHOLDER_PASSWORD}@127.0.0.1:1/sim"
    settings = make_settings(data_backend="postgres", database_url=unreachable)
    runtime = build_runtime(settings)
    app = create_app(settings, runtime)  # no connection at startup
    capture = _Capture()
    logger = logging.getLogger("sunovate")
    logger.addHandler(capture)
    try:
        client = TestClient(app)
        login_response = client.post(
            "/api/v1/auth/dev/login", json={"email": "sim.admin@sunovate.local"}
        )
        token, _ = runtime.signer.issue(sid("user:sim.admin"))
        list_response = client.get(
            "/api/v1/knowledge", headers={"Authorization": f"Bearer {token}"}
        )
    finally:
        logger.removeHandler(capture)
        assert isinstance(runtime.backend, PostgresBackend)
        runtime.backend.dispose()

    for response in (login_response, list_response):
        assert response.status_code == 503, response.text
        body = response.json()
        assert body["code"] == "DATABASE_UNAVAILABLE"
        assert body["requestId"]
        assert PLACEHOLDER_PASSWORD not in response.text
        assert "DATABASE_URL" not in response.text
    assert capture.lines, "the 503 must be logged"
    logged = "\n".join(capture.lines)
    assert PLACEHOLDER_PASSWORD not in logged
    assert "DATABASE_URL" not in logged
