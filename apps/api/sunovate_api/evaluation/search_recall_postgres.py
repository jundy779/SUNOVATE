"""Run the search relevance evaluator against an explicit test PostgreSQL database."""

from __future__ import annotations

import json
import os
from typing import Final

from ..db.backup_restore_drill import DrillError, parse_target

DATABASE_ENV: Final = "SUNOVATE_TEST_DATABASE_URL"
CONFIRM_ENV: Final = "SUNOVATE_SEARCH_EVAL_CONFIRM"
CONFIRM_VALUE: Final = "SIMULATED_DATA_ONLY"


def prepare_environment(raw_url: str) -> None:
    if os.environ.get("APP_ENV") != "test":
        raise DrillError("Evaluasi PostgreSQL hanya boleh berjalan dengan APP_ENV=test")
    if os.environ.get(CONFIRM_ENV) != CONFIRM_VALUE:
        raise DrillError(f"{CONFIRM_ENV} harus bernilai {CONFIRM_VALUE}")
    parse_target(raw_url, role="source")
    os.environ["SUNOVATE_TEST_BACKEND"] = "postgres"


def main() -> int:
    raw_url = os.environ.get(DATABASE_ENV, "").strip()
    try:
        if not raw_url:
            raise DrillError(f"{DATABASE_ENV} wajib diisi")
        prepare_environment(raw_url)
        # Import only after the backend environment has been locked to postgres.
        from .search_recall import main as run_evaluator

        return run_evaluator()
    except DrillError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
