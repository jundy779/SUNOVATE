"""PostgreSQL integration checks. Skipped unless SUNOVATE_TEST_DATABASE_URL is set.

The URL must point to a disposable database that already ran `alembic upgrade head`
and the SIMULATED_DATA seed. For a throwaway server without Docker use
`scripts/validation/db_check_pgserver.py`.
"""

from __future__ import annotations

import asyncio
import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

URL = os.environ.get("SUNOVATE_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="SUNOVATE_TEST_DATABASE_URL not set")


async def _scalar(sql: str) -> object:
    assert URL
    engine = create_async_engine(URL)
    try:
        async with engine.connect() as conn:
            return (await conn.execute(text(sql))).scalar_one()
    finally:
        await engine.dispose()


def test_schema_has_thirty_tables() -> None:
    count = asyncio.run(_scalar(
        "select count(*) from information_schema.tables where table_schema='public' "
        "and table_name <> 'alembic_version'"))
    assert count == 30


def test_seed_is_simulated_only() -> None:
    assert asyncio.run(_scalar(
        "select count(*) from teams where data_origin <> 'SIMULATED_DATA'")) == 0


def test_full_text_search_index_works() -> None:
    hits = asyncio.run(_scalar(
        "select count(*) from document_chunks "
        "where search_vector @@ plainto_tsquery('simple', 'metadata')"))
    assert isinstance(hits, int) and hits >= 1
