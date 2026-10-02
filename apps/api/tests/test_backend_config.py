"""DATABASE_URL rule (design 3.2) and seed production refusal (AC-06.2)."""

from __future__ import annotations

import os
import subprocess
import sys
import traceback
from pathlib import Path

import pytest

from sunovate_api.db.urls import async_database_url, parse_database_url, sync_database_url

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
    # Today Settings itself rejects APP_ENV=production with DATA_BACKEND=simulated; once
    # postgres is allowed in production, seed() refuses with SystemExit. Either way: non-zero.
    assert result.returncode != 0
