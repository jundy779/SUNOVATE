"""Validate migrations and seed against a throwaway PostgreSQL + pgvector without Docker.

Validation helper only; `pgserver` is NOT a project dependency. Run from repo root:

    uv run --no-project --python 3.12 --with pgserver python scripts/validation/db_check_pgserver.py

Optional: `--autogenerate "message"` creates a new Alembic revision from the models.
Steps: start temporary server -> alembic upgrade head -> seed (twice, idempotency) ->
FTS + append-only checks -> alembic downgrade base -> stop and delete server.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pgserver  # type: ignore[import-not-found]

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "apps" / "api"
PYTHON = API / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(*args: str, env: dict[str, str]) -> str:
    print("$", " ".join(args), flush=True)
    result = subprocess.run([str(PYTHON), *args], cwd=API, env=env, capture_output=True,
                            text=True, check=False)
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output, flush=True)
    if result.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(args)}")
    return output


CHECK_SQL = """
import asyncio, os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    engine = create_async_engine(os.environ["DATABASE_URL"])
    async with engine.connect() as c:
        tables = (await c.execute(text(
            "select count(*) from information_schema.tables where table_schema='public' "
            "and table_name <> 'alembic_version'"))).scalar_one()
        print("tables:", tables)
        hits = (await c.execute(text(
            "select count(*) from document_chunks where search_vector @@ "
            "plainto_tsquery('simple', 'metadata')"))).scalar_one()
        print("fts hits for 'metadata':", hits)
        labels = (await c.execute(text(
            "select count(*) from knowledge_entries where data_origin <> 'SIMULATED_DATA'"
        ))).scalar_one()
        print("non-simulated knowledge rows:", labels)
        await c.execute(text(
            "insert into audit_logs (action, entity_type) values ('CHECK', 'validation')"))
        await c.commit()
        try:
            await c.execute(text("update audit_logs set action = 'TAMPER'"))
            print("append-only: FAILED (update allowed)")
        except Exception as exc:
            await c.rollback()
            print("append-only: OK (update rejected:", type(exc).__name__ + ")")
    await engine.dispose()
    assert tables == 30, tables
    assert hits >= 1
    assert labels == 0

asyncio.run(main())
"""


def main() -> None:
    data_dir = Path(tempfile.mkdtemp(prefix="sunovate-pg-"))
    server = pgserver.get_server(str(data_dir), cleanup_mode="stop")
    try:
        uri = server.get_uri().replace("postgresql://", "postgresql+asyncpg://", 1)
        env = {**os.environ, "DATABASE_URL": uri, "APP_ENV": "test", "PYTHONIOENCODING": "utf-8"}
        if len(sys.argv) > 2 and sys.argv[1] == "--autogenerate":
            server.psql("CREATE EXTENSION IF NOT EXISTS vector;")
            run("-m", "alembic", "revision", "--autogenerate", "-m", sys.argv[2], env=env)
            return
        run("-m", "alembic", "upgrade", "head", env=env)
        run("-m", "alembic", "check", env=env)
        run("-m", "sunovate_api.db.seed", env=env)
        run("-m", "sunovate_api.db.seed", env=env)  # idempotency: second run inserts 0 rows
        run("-c", CHECK_SQL, env=env)
        run("-m", "alembic", "downgrade", "base", env=env)
        print("DATABASE CHECK PASSED")
    finally:
        server.cleanup()
        shutil.rmtree(data_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
