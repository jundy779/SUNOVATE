# Changelog

## Unreleased - 2026-10-02 (persistence PostgreSQL, PROPOSED ADR-015)

### Ditambahkan
- Backend runtime kedua `DATA_BACKEND=postgres` di belakang interface `Repository` sinkron per request (`store/repository.py`, `store/postgres.py`): SQLAlchemy 2 sinkron + `psycopg[binary]==3.3.6` (satu-satunya dependency baru). `DATA_BACKEND=simulated` tetap default. Data bertahan setelah API di-restart.
- Revisi Alembic `0002_ordering_columns`: `audit_logs.seq` (identity, urutan insert audit) dan `knowledge_tags.position` (urutan tag). `0001_initial_schema` tidak diubah.
- `db/urls.py`: satu aturan `DATABASE_URL` (hanya `postgresql+asyncpg`/`postgresql+psycopg`) untuk runtime, Alembic, seed, dan `/health/database`; `db/testing_reset.py` (reset TRUNCATE + seed, hanya `APP_ENV=test` dan `SUNOVATE_DB_RESET_ALLOWED=1`).
- `pnpm db:test` (`scripts/validation/db_test_pgserver.py`): seluruh pytest pada PostgreSQL sementara (pgserver). Test baru: kontrak repository pada kedua backend, pemetaan constraint ke 409 `DUPLICATE_CHECKSUM` / 403 `SEPARATION_OF_DUTIES`, revision atomik dan konkuren, rollback, audit persisten dan append-only, paritas respons lintas backend, guard konfigurasi production, 503 tanpa kebocoran URL.
- Dokumentasi: ADR-015 di `architecture-decisions.md` dan `decision-log.md`; pembaruan arsitektur data, container, komponen, konfigurasi environment, pengembangan lokal, skema database, retrieval, endpoint catalog, pengujian integrasi, known limitations (KL-01, KL-02, KL-20 sampai KL-24), future development, `.env.example`, `README.md`, `tests/README.md`. Pernyataan "runtime hanya simulated / repository belum ada" juga dikoreksi di project overview, assumptions (A-06), MVP scope, data retention, RAG architecture, API overview, prototype notes, backend testing, backup-and-restore, migration guide, observability, troubleshooting, change management, risk register (R-10), dan administrator guide; rujukan ke skrip `db-check-pgserver.ps1` yang tidak ada diganti `pnpm db:check`.

### Diubah
- Semua akses data modul, `AuthorizationService`, `RetrievalService`, dan `HermesGateway` lewat `Repository`; write wajib di dalam `transaction()`.
- Urutan natural koleksi `(created_at, id)` pada kedua backend; `AuditLog` memakai satu waktu (`createdAt == updatedAt == occurredAt`).
- `tags` duplikat pada POST/PATCH knowledge dibuang (kemunculan pertama dipertahankan); `null` pada PATCH knowledge/task berarti tidak diubah.
- Production: `DATA_BACKEND=postgres` diizinkan bila `DEV_AUTH_ENABLED=false`; `simulated` dan dev auth tetap ditolak.

### Hasil validasi aktual (2026-10-02, Windows, PowerShell 7, Python 3.12.13, branch `feat/postgres-persistence`)
| Perintah | Hasil |
|---|---|
| `pnpm lint` | ESLint tanpa temuan; Ruff "All checks passed!"; exit 0 (dijalankan ulang setelah perubahan dokumentasi) |
| `pnpm typecheck` | tsc tanpa error; mypy strict "Success: no issues found in 53 source files"; exit 0 |
| `pnpm test` (simulated) | Vitest 12 passed (3 file); pytest 151 passed, 36 skipped in 22.86s; exit 0. Tidak ada regresi terhadap baseline 105 passed; 36 skipped = 3 `tests/integration` + 33 test khusus postgres |
| `pnpm build` | next build berhasil, 13 route; exit 0 |
| `pnpm db:sql` | SQL offline ter-render untuk `0001_initial_schema` lalu `0002_ordering_columns` (`ADD COLUMN seq BIGINT GENERATED ALWAYS AS IDENTITY`, `uq_audit_logs_seq`, `ADD COLUMN position INTEGER DEFAULT '0' NOT NULL`, `ck_knowledge_tags_position`); exit 0 |
| `pnpm db:check` (pgserver) | upgrade `0001` -> `0002`; `alembic check` "No new upgrade operations detected."; seed run 1 menyisipkan baris, run 2 0 baris di 21 tabel; 30 tabel; FTS `metadata` 2 hit; non-simulasi 0; `audit seq` 1; `knowledge_tags` 8 baris, `position` 0: 8; append-only OK (UPDATE ditolak); downgrade `0002` -> `0001` -> base; "DATABASE CHECK PASSED"; exit 0 |
| `pnpm db:test` (pgserver, `SUNOVATE_TEST_BACKEND=postgres`) | upgrade `0001` -> `0002` + seed, lalu pytest "187 passed in 207.92s (0:03:27)", 0 skipped, 0 failed; exit 0; wall clock 269 s |
| Smoke manual `DATA_BACKEND=postgres` (skrip sementara di `%TEMP%`, pgserver, uvicorn port 8010, dihapus setelahnya) | `alembic upgrade head` dan seed exit 0; `GET /api/v1/health` 200 dengan `dataBackend` `postgres`; login `sim.staff.pppsun` 200; `GET /api/v1/dashboard/summary` 200; `GET /api/v1/knowledge` 200 (total 3); `POST /api/v1/hermes/query` 200 dengan decision `ANSWERED`; login `sim.owner.ppsun` dan `POST /api/v1/knowledge` draft (tim PPSUN, INTERNAL, tags `["smoke","smoke"]`) 201 dengan tags `["smoke"]`; uvicorn dihentikan dan dijalankan ulang; login ulang lalu `GET /api/v1/knowledge/{id}` 200 dengan judul yang sama. "SMOKE PASSED", wall clock 21 s. URI database tidak dicetak; tidak ada skrip atau direktori sementara tersisa |
| Pencarian emoji/ikon Unicode (U+2190-U+21FF, U+2600-U+27BF, U+1F300-U+1FAFF) pada file dokumentasi yang diubah | 0 temuan |

## 0.1.0 - 2026-10-01 (fondasi, belum siap produksi)

### Ditambahkan
- Dokumentasi 108 file di `docs/00-project` sampai `docs/13-handover` (+ indeks), termasuk 20 open question (OQ-01 sampai OQ-20), decision log ADR-001 sampai ADR-014, dan risk register R-01 sampai R-12. Draf sebelumnya diarsipkan ke `docs/_archive/legacy-docs-v0/`.
- Backend FastAPI modular: 13 modul router di `/api/v1`, otorisasi permission + team scope + klasifikasi, login pengembangan (token HMAC), audit append-only, approval dengan separation of duties, pipeline Hermes (ScopeGuard, retrieval terotorisasi, rerank, filter injeksi, CitationValidator, OutputGuard).
- Skema PostgreSQL 30 tabel (SQLAlchemy 2) dan migrasi Alembic `0001_initial_schema` dengan pgvector, FTS, dan trigger append-only; seed `SIMULATED_DATA` idempoten.
- Frontend Next.js: login dev, dashboard, Knowledge Hub, detail, pencarian, monitoring kerja, Hermes chat, administrasi, halaman 403/404/error/loading.
- Paket `@sunovate/contracts`, `@sunovate/shared-types`, `@sunovate/config`.
- Test: pytest (API, security, RAG golden set, integrasi DB opsional), Vitest, Playwright smoke.

### Diubah / dihapus
- Scaffold sebelumnya diganti: migrasi tabel generik, seed SQL dengan nama tim karangan, dashboard dengan nama tim karangan, shell ganda, dan tabel SUN Business yang belum tervalidasi.

### Hasil validasi aktual (2026-10-01, Windows, Node 24.19.0, Python 3.14.4)
| Perintah | Hasil |
|---|---|
| `pnpm lint` | ESLint tanpa temuan; Ruff "All checks passed" |
| `pnpm typecheck` | tsc tanpa error; mypy strict "no issues found in 49 source files" |
| `pnpm test` | Vitest 12 passed (3 file); pytest 105 passed, 3 skipped (integrasi DB tanpa `SUNOVATE_TEST_DATABASE_URL`) |
| `pnpm build` | next build berhasil, 13 route |
| `pnpm e2e` (API + web berjalan, Chromium lokal via `PW_CHROMIUM_PATH`) | 3 passed |
| `pnpm db:check` (PostgreSQL sementara + pgvector 0.6.2) | upgrade, `alembic check`, seed dua kali, 30 tabel, FTS, trigger append-only, downgrade: PASSED |
| `pnpm db:sql` | SQL migrasi ter-render offline |
| `pnpm compose:check` | Tidak dapat dijalankan: Docker tidak terpasang. `docker-compose.yml` hanya diparse sebagai YAML |
| Tautan dokumentasi | 0 tautan relatif rusak pada 109 file; diagram Mermaid belum dirender otomatis |
