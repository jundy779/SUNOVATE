"""Async engine/session factory for PostgreSQL (used by migrations tooling and the seed).

DATABASE_URL is validated and normalised to asyncpg by `db.urls.async_database_url`.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .urls import async_database_url


def make_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(async_database_url(database_url), pool_pre_ping=True)


def make_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
