"""Single DATABASE_URL rule for runtime, health, Alembic, and seed (design 3.2).

The URL is never rendered to a string, printed, or logged; errors never include it.
"""

from __future__ import annotations

from typing import Final

from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError

ALLOWED_DRIVERNAMES: Final = frozenset({"postgresql+asyncpg", "postgresql+psycopg"})


def parse_database_url(raw: str) -> URL:
    try:
        url = make_url(raw)
    except (ArgumentError, ValueError):
        # from None: the URL (with password) must not appear in the traceback.
        raise ValueError("DATABASE_URL tidak dapat di-parse") from None
    if url.drivername not in ALLOWED_DRIVERNAMES:
        raise ValueError(
            "DATABASE_URL harus memakai skema postgresql+asyncpg atau postgresql+psycopg"
        ) from None
    return url


def sync_database_url(raw: str) -> URL:
    """Runtime PostgresBackend (psycopg 3, sync)."""
    return parse_database_url(raw).set(drivername="postgresql+psycopg")


def async_database_url(raw: str) -> URL:
    """Alembic, seed (make_engine), and /health/database (asyncpg)."""
    return parse_database_url(raw).set(drivername="postgresql+asyncpg")
