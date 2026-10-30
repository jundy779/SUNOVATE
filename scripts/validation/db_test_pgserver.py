"""Run the full pytest suite on DATA_BACKEND=postgres against a throwaway PostgreSQL.

Validation helper only; `pgserver` is NOT a project dependency. Prerequisite: `pnpm api:setup`.
Run from repo root:

    uv run --no-project --python 3.12 --with pgserver python scripts/validation/db_test_pgserver.py

Steps: start temporary server -> alembic upgrade head -> seed -> pytest with
SUNOVATE_TEST_BACKEND=postgres (reset TRUNCATE + seed per test) -> stop and delete server.
Exit code = pytest exit code. The database URI is passed via env only and never printed.
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


def prepare(*args: str, env: dict[str, str]) -> None:
    print("$", " ".join(args), flush=True)
    result = subprocess.run([str(PYTHON), *args], cwd=API, env=env, capture_output=True,
                            text=True, check=False)
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output, flush=True)
    if result.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(args)}")


# The throwaway server holds SIMULATED_DATA only and is deleted after the run, so durability can be
# traded for speed. Hundreds of TRUNCATE + reseed cycles otherwise leave a large final checkpoint;
# on Windows the shutdown took about 38 s, close to pg_ctl's default 60 s wait (PGCTLTIMEOUT), and
# an occasional timeout made pgserver kill the server instead of stopping it. pgserver's own
# `pg_ctl -w stop` honours PGCTLTIMEOUT, so the longer wait below needs no custom stop logic.
TEST_ONLY_SETTINGS = (
    "ALTER SYSTEM SET fsync = off;",
    "ALTER SYSTEM SET synchronous_commit = off;",
    "ALTER SYSTEM SET full_page_writes = off;",
    "SELECT pg_reload_conf();",
)
STOP_TIMEOUT_SECONDS = "180"


def tune_for_tests(server: object) -> None:
    for statement in TEST_ONLY_SETTINGS:
        server.psql(statement)  # type: ignore[attr-defined]


def main() -> int:
    os.environ["PGCTLTIMEOUT"] = STOP_TIMEOUT_SECONDS
    data_dir = Path(tempfile.mkdtemp(prefix="sunovate-pg-test-"))
    try:
        server = pgserver.get_server(str(data_dir), cleanup_mode="stop")
    except Exception as exc:  # noqa: BLE001 - third-party bootstrap has no stable error type
        shutil.rmtree(data_dir, ignore_errors=True)
        print(
            "DATABASE TEST BLOCKED: pgserver tidak dapat dimulai pada lingkungan ini "
            f"({type(exc).__name__}); gunakan Docker atau host PostgreSQL uji yang disetujui.",
            flush=True,
        )
        return 2
    try:
        uri = server.get_uri().replace("postgresql://", "postgresql+asyncpg://", 1)
        env = {
            **os.environ,
            "DATABASE_URL": uri,
            "SUNOVATE_TEST_DATABASE_URL": uri,
            "SUNOVATE_TEST_BACKEND": "postgres",
            "SUNOVATE_DB_RESET_ALLOWED": "1",
            "APP_ENV": "test",
            "PYTHONIOENCODING": "utf-8",
        }
        env.pop("DATA_BACKEND", None)
        tune_for_tests(server)
        prepare("-m", "alembic", "upgrade", "head", env=env)
        prepare("-m", "sunovate_api.db.seed", env=env)
        print("$ -m pytest -q (SUNOVATE_TEST_BACKEND=postgres)", flush=True)
        # Output streams directly (not captured).
        return subprocess.run([str(PYTHON), "-m", "pytest", "-q"], cwd=API, env=env,
                              check=False).returncode
    finally:
        server.cleanup()
        shutil.rmtree(data_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
