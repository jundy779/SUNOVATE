"""Per-test reset of a throwaway PostgreSQL database (design 15.3).

TRUNCATE + SIMULATED_DATA seed, used only by `pnpm db:test` on a temporary pgserver.
Guarded twice: APP_ENV=test and SUNOVATE_DB_RESET_ALLOWED=1 (set only by
scripts/validation/db_test_pgserver.py). The append-only trigger is not touched.
"""

from __future__ import annotations

import os

from sqlalchemy import Engine, text

from ..core.config import Settings
from .models import Base
from .seed import apply_plan


def reset_database(engine: Engine, settings: Settings) -> None:
    # Checked before the engine is touched.
    if settings.app_env != "test" or os.environ.get("SUNOVATE_DB_RESET_ALLOWED") != "1":
        raise RuntimeError("Reset database hanya untuk APP_ENV=test pada database sementara")
    tables = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)  # static model names
    with engine.begin() as conn:
        conn.execute(text("SET LOCAL lock_timeout = '5s'"))  # never wait without a limit
        # The application's 15 s statement_timeout is too tight for TRUNCATE + reseed when the
        # machine is busy (BUG-036); this applies only to the throwaway test database reset.
        conn.execute(text("SET LOCAL statement_timeout = '120s'"))
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
        apply_plan(conn)  # seed SIMULATED_DATA
