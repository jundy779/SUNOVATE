# Changelog
## Docs 2026-10-02 - Jawaban knowledge owner dari deck proposal versi tetap (hanya dokumentasi)
### Diubah
- Dokumentasi memasukkan deck `v1_SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx`, versi tetap (fixed) dari deck proposal yang dikonfirmasi pengguna. Slide 24 kini berjudul "konfirmasi knowledge owner" dan delapan pertanyaannya dijawab. Jawaban diberi label `CONFIRMED (knowledge owner, deck v1_ slide 24)`; pengakuan mentor masih tertunda (OQ-24). Tafsiran, pemetaan role, dan konsekuensi tetap `PROPOSED`.
- Status open question: OQ-03, OQ-08, OQ-09 ANSWERED (knowledge owner); OQ-02, OQ-04, OQ-05, OQ-06, OQ-07, OQ-10 PARTIAL; OQ-01, OQ-11 sampai OQ-20 tidak berubah.
- Slide 9 dan 18 deck `v1_` ("Ketua tim kerja", "Pengelola Knowledge / PIC", "Ketua Tim", "PMP") tercermin di stakeholder map, persona, dan tata kelola. "PMP" tidak dijelaskan di deck dan ditulis sebagai kemungkinan Program dan Manajemen Pengetahuan, perlu konfirmasi (OQ-25).
- Dokumen hosting (deployment, runbook, backup, batas integrasi, identity provider), SharePoint, Telegram, WhatsApp, dan dashboard diselaraskan dengan jawaban (komputer tersendiri sebagai server, "Sandbox server", "bisa", indikator "yield" dan "kepemilikan SBN" tanpa data).
- Agenda sesi mentor 01 diubah menjadi sesi konfirmasi.
### Ditambahkan
- Open question OQ-21 sampai OQ-25 (sumber data yield dan kepemilikan SBN, makna "Sandbox server", persyaratan server dan login, pengakuan mentor, pemetaan peran).
- Entri decision log DEC-20261002-01 sampai DEC-20261002-09 (di bagian jawaban, bukan di tabel ADR).
- Risiko R-13 sampai R-17 (server tunggal, cakupan "semua dokumen", indikator tanpa sumber data, jawaban belum diakui mentor, matriks izin belum selaras).
- Asumsi A-17 sampai A-19 dan usulan perubahan izin `staff` (PROPOSED, belum diimplementasikan) di `docs/06-security/permission-matrix.md`, `docs/06-security/authorization-rbac.md`, dan `docs/13-handover/future-development.md` (PD-1 sampai PD-6).
- `references/README.md` mencatat deck `v1_` sebagai versi tetap dan slide yang berubah.
### Tidak diubah
- Kode, test, migrasi, file paket, katalog role, dan dokumen sumber di root. Tidak ada integrasi yang diaktifkan atau diklaim tersedia.
### Hasil validasi aktual (2026-10-02, Windows, Python 3.14)
| Pemeriksaan | Hasil |
|---|---|
| Pemeriksa tautan dokumentasi (skrip sementara, `docs/**/*.md` tanpa `_archive`) | 110 file, 0 tautan relatif rusak, semua file memiliki baris `**Status:**` dan `Last Updated` |
| Karakter emoji/ikon | 0 ditemukan |
| `git diff --stat main..HEAD` | Hanya `docs/`, `references/README.md`, dan `CHANGELOG.md` |
| `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, `pnpm db:sql` | Tidak dijalankan: tidak ada perubahan kode, test, migrasi, atau paket |


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
