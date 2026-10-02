# Changelog

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
