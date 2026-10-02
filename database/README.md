# database/

Pointer folder. The database is owned by the API so that schema, migrations and seed stay in one
Python environment.

| Item | Location |
|---|---|
| SQLAlchemy models (30 tables) | `apps/api/sunovate_api/db/models.py` |
| Alembic migrations | `apps/api/alembic/versions/` (`0001_initial_schema`) |
| SIMULATED_DATA seed | `apps/api/sunovate_api/db/seed.py` (dataset in `sunovate_api/store/dataset.py`) |
| Throwaway DB check without Docker | `scripts/validation/db_check_pgserver.py` (`pnpm db:check`) |

`migrations/` and `seeds/` here are intentionally empty. Do not add SQL seeds with real data.

## Commands (repository root)

```bash
pnpm db:up        # docker compose up -d postgres (pgvector/pgvector:pg17)
pnpm db:migrate   # alembic upgrade head
pnpm db:seed      # idempotent SIMULATED_DATA seed; refuses APP_ENV=production
pnpm db:sql       # render migration SQL offline, no database needed
pnpm db:check     # upgrade, alembic check, seed twice, FTS + append-only checks, downgrade
```

Rules: every schema change gets a new Alembic revision; never edit an applied revision; files are
never stored as BLOBs. See `docs/04-data/database-schema.md` and `docs/11-operations/migration-guide.md`.
