# Register Bug

**Status:** PROPOSED
**Last Updated:** 2026-10-06

## Purpose

Register sementara cacat SUNOVATE yang dapat ditelusuri di riwayat Git dan catatan review, dengan field dari [bug-severity.md](bug-severity.md). Alat register bug belum ditetapkan (OPEN QUESTION di bug-severity.md), sehingga register berupa dokumen ini.

## Sumber dan Aturan

- **CONFIRMED (riwayat repository)**: Hanya cacat yang dapat dirujuk ke commit, `CHANGELOG.md`, `docs/13-handover/known-limitations.md`, atau catatan review yang dicatat di sini. Setiap SHA diperiksa dengan `git cat-file -e <sha>^{commit}` pada 2026-10-06.
- **Catatan review (tidak masuk Git)**: `.agents/tasks/postgres-persistence/review.md` dan `review.json` (review implementasi, 2026-10-02, verdict APPROVED dengan empat temuan NIT) serta `design-review.md` (review desain sebelum kode). Berkas tersebut adalah catatan kerja lokal yang tidak di-commit; dirujuk sebagai catatan, bukan sumber yang dapat diverifikasi dari repository. Temuan `design-review.md` adalah temuan desain sebelum ada kode (satu MEDIUM dan dua belas NIT, seluruhnya diselesaikan di desain atau kode sebelum review implementasi) dan tidak dihitung sebagai cacat kode.
- **PROPOSED**: Severity adalah usulan menurut [bug-severity.md](bug-severity.md); definisi P0 sampai P3 berasal dari Proposal v2.4 slide 20 (tidak berubah pada deck `v1_`). "NIT" pada kolom deskripsi adalah skala reviewer, bukan P0 sampai P3.
- Hanya `SIMULATED_DATA`. Tidak ada data asli, data pribadi, atau isi dokumen di register ini.
- Repository hanya memiliki satu commit sebelum fitur PostgreSQL (`357df94`), sehingga perbaikan atas masalah yang ditemukan sebelum commit itu tercatat pada SHA tersebut.

## Cacat yang Sudah Diperbaiki

| ID | Ditemukan | Area | Deskripsi | Severity (PROPOSED) | Ditemukan lewat | Status | Rujukan perbaikan | Uji yang mencakup |
|---|---|---|---|---|---|---|---|---|
| BUG-001 | Sebelum 2026-10-02; CHANGELOG 0.1.0 bertanggal 2026-10-01 | Database | Migrasi scaffold awal berisi tabel generik dan tabel SUN Business (instrumen, lelang, transaksi, yield, setelmen) yang belum tervalidasi. Diganti skema 30 tabel; tabel bisnis SUN dikeluarkan (ADR-013) | P2 | Inspeksi scaffold (dicatat di CHANGELOG 0.1.0, bagian "Diubah / dihapus"); mekanisme penemuan tidak dicatat terpisah | Selesai | `357df94` | `tests/integration/test_database_integration.py::test_schema_has_thirty_tables` (hanya saat `SUNOVATE_TEST_DATABASE_URL` diisi atau lewat `pnpm db:test`); `pnpm db:check` |
| BUG-002 | Sama dengan BUG-001 | Data simulasi, dashboard | Seed SQL dan dashboard memakai nama tim karangan, bertentangan dengan aturan tidak mengarang data SUN (AGENTS.md). Diganti enam tim dari brief dengan `validation_status` | P2 | Inspeksi scaffold (CHANGELOG 0.1.0) | Selesai | `357df94` | `apps/api/tests/test_admin_endpoints.py::test_teams_are_the_six_confirmed_codes` |
| BUG-003 | Sama dengan BUG-001 | Frontend | Shell aplikasi ganda pada scaffold awal. Diganti satu `AppShell` (`apps/web/src/components/app-shell.tsx`) | P3 | Inspeksi scaffold (CHANGELOG 0.1.0) | Selesai | `357df94` | Tidak ada uji khusus yang teridentifikasi |
| BUG-004 | Sebelum 2026-10-02 (tanggal pasti tidak tercatat) | Hermes, retrieval | Ambang bukti menerima kecocokan yang hanya pada judul atau label bagian dari SOP lain (kasus RAG-16), sehingga Hermes dapat menjawab tanpa bukti isi. Ditambah `MIN_SCORE = 0.45` pada `hermes/gateway.py` (dicatat di [retrieval-strategy.md](../05-ai-rag/retrieval-strategy.md)) | P1 (jawaban AI menyesatkan) | Evaluasi golden set RAG | Selesai | `357df94` | `tests/rag-evaluation/test_rag_golden_set.py::test_golden_case[RAG-16]` (pengguna `sim.owner.ppsun`, keputusan `INSUFFICIENT_EVIDENCE`, sitasi K7 terlarang) |
| BUG-005 | 2026-10-02 | Logging, PostgreSQL | Kesalahan database yang tidak terpetakan dapat menulis teks `DETAIL` driver (termasuk nilai baris) ke log lewat handler 500 generik. Log kini hanya memuat `errorType`, `sqlstate`, `stack`, dan `requestId`. Review: NIT, dengan catatan tidak ada URL atau kredensial dan hanya `SIMULATED_DATA` | P2 (naik ke P0 bila data asli, menurut contoh "isi dokumen tercatat di log") | Code review (`review.md`, temuan 4) | Selesai | `3fba69f`; dokumentasi `6ed05bb` | `apps/api/tests/test_runtime_hardening.py::test_unmapped_db_error_is_not_logged_with_row_values`, `::test_log_unhandled_error_omits_message_and_chained_causes` |
| BUG-006 | 2026-10-02 | API, health | `GET /api/v1/health` melaporkan `settings.data_backend` (yang dikonfigurasi), bukan backend yang sebenarnya terpasang. Kini melaporkan `AppRuntime.backend.name` | P3 | Code review (`review.md`, temuan 1) | Selesai | `3fba69f`; dokumentasi `6ed05bb` | `test_runtime_hardening.py::test_health_reports_wired_backend_not_configured_one`, `::test_health_reports_simulated_for_simulated_backend`; `tests/postgres/test_postgres_backend.py::test_health_reports_postgres_when_postgres_is_wired` |
| BUG-007 | 2026-10-02 | API, PostgreSQL | Semua `OperationalError` (termasuk statement timeout, deadlock, kegagalan serialisasi) menjadi 503 `DATABASE_UNAVAILABLE` sehingga kondisi sibuk terbaca sebagai database tidak terjangkau. Kini SQLSTATE 57014, 55P03, 40P01, 40001 menjadi 503 `DATABASE_BUSY` dengan `Retry-After: 5`; kegagalan koneksi tetap `DATABASE_UNAVAILABLE` | P2 | Code review (`review.md`, temuan 2) | Selesai | `3fba69f`; dokumentasi `6ed05bb` | `test_runtime_hardening.py::test_transient_sqlstates_map_to_database_busy`, `::test_connection_failures_stay_database_unavailable`, `::test_interface_error_with_busy_sqlstate_is_still_unavailable`, `::test_busy_error_response_carries_retry_after_header`; `tests/postgres/test_postgres_backend.py::test_real_statement_timeout_maps_to_database_busy` |
| BUG-008 | 2026-10-02 | Operasional | Engine PostgreSQL tidak di-dispose saat aplikasi shutdown. Kini lifespan FastAPI memanggil `DataBackend.close()` (no-op pada backend simulasi) dan kegagalan close tidak menggagalkan shutdown | P3 | Code review (`review.md`, temuan 3) | Selesai | `3fba69f`; dokumentasi `6ed05bb` | `test_runtime_hardening.py::test_shutdown_closes_the_backend`, `::test_shutdown_survives_a_failing_close`, `::test_simulated_backend_close_is_a_noop`; `tests/postgres/test_postgres_backend.py::test_application_shutdown_disposes_the_engine` |
| BUG-009 | 2026-10-02 | Dokumentasi | Drift dokumentasi saat konvergensi: rujukan ke skrip `scripts/validation/db-check-pgserver.ps1` yang tidak ada (seharusnya `pnpm db:check`) dan pernyataan "repository SQLAlchemy belum diimplementasikan" atau "runtime hanya simulated" di 15 berkas dokumentasi yang bertentangan dengan kode (16 berkas diubah, termasuk `CHANGELOG.md`) | P3 | Pemeriksaan konvergensi atas dokumentasi (`verification.md`, bagian "Seams found and fixed") | Selesai | `a084a53` | Tidak ada uji otomatis; pemeriksa tautan sementara dijalankan manual |

## Terbuka: Keterbatasan yang Diketahui

Bukan bug yang diperbaiki. Keterbatasan dicatat di [known-limitations.md](../13-handover/known-limitations.md) dan diterima pada skala `SIMULATED_DATA`; severity di bawah adalah usulan untuk keputusan triase, bukan penilaian yang disetujui mentor.

| ID | Ditemukan | Area | Deskripsi | Severity (PROPOSED) | Ditemukan lewat | Status | Rujukan perbaikan | Uji yang mencakup |
|---|---|---|---|---|---|---|---|---|
| BUG-010 | 2026-10-02 (KL-21) | Audit | Trigger `audit_logs_append_only` menolak UPDATE/DELETE per baris tetapi tidak `TRUNCATE`. Butuh hak TRUNCATE pada database, bukan jalur API | P1 (usulan): contoh P0 "audit_logs dapat diubah atau dihapus" tidak terpenuhi lewat aplikasi, tetapi relevan pada server tunggal (T-24) | Dicatat sebagai keterbatasan (KL-21, ADR-015) | OPEN (penutupan OUT OF SCOPE, ADR-015) | Belum ada | Uji trigger menguji UPDATE/DELETE saja (`tests/postgres/test_postgres_backend.py::test_audit_rows_are_persisted_stable_and_append_only`); tidak ada uji TRUNCATE |
| BUG-011 | 2026-10-02 (KL-22) | PostgreSQL, audit penolakan | Audit penolakan memakai koneksi kedua dari pool yang sama; bila database mati, permintaan yang seharusnya 403 menjadi 503, dan bila pool habis permintaan menunggu sampai 10 detik lalu 503 | P2 | Dicatat sebagai keterbatasan (KL-22, ADR-015) | OPEN (engine terpisah ada di backlog) | Belum ada | `apps/api/tests/test_backend_config.py::test_unreachable_database_returns_503_without_leaking_url` mencakup sisi 503 tanpa kebocoran URL saja |
| BUG-012 | 2026-10-02 (KL-23) | Hermes, PostgreSQL | Koneksi request Hermes berstatus idle in transaction (tanpa row lock) selama generasi jawaban. Diterima karena generasi lokal dan cepat; perlu ditinjau sebelum provider AI remote | P3 | Dicatat sebagai keterbatasan (KL-23, ADR-015) | OPEN | Belum ada | Belum ada |
| BUG-013 | 2026-10-02 (KL-24) | Konfigurasi | `sunovate_api/main.py` membuat app saat impor; `.env` dengan `DATA_BACKEND=postgres` dan skema `DATABASE_URL` yang tidak diizinkan membuat impor gagal, termasuk koleksi `pnpm test`. Workaround: perbaiki `.env` | P2 | Review desain (`design-review.md`, temuan 9); dicatat sebagai KL-24 | OPEN (validasi lazy ada di backlog) | Belum ada | `test_backend_config.py::test_rejected_urls_do_not_leak_password` menguji penolakan URL, bukan perilaku impor |

## Terbuka: Celah Persyaratan (bukan bug fungsional)

Celah antara jawaban knowledge owner (deck `v1_` slide 24, **CONFIRMED (knowledge owner)**; pengakuan mentor tertunda, OQ-24) dan keadaan kode per 2026-10-06. Tidak ada yang dinyatakan diperbaiki; kebutuhan dan rencananya ada di dokumen yang dirujuk.

| ID | Ditemukan | Area | Deskripsi | Severity (PROPOSED) | Ditemukan lewat | Status | Rujukan perbaikan | Uji yang mencakup |
|---|---|---|---|---|---|---|---|---|
| REQ-GAP-01 | 2026-10-06 | Otorisasi | Role `staff` masih memiliki `knowledge:create`, `knowledge:update`, `knowledge:submit`, dan `document:create`, sedangkan hak mengubah/mengunggah hanya untuk ketua tim, kasubdit PMP, Kasi MP, dan PIC (FR-50, BR-33). Pengecekan manual: `sim.staff.pppsun` memperoleh 201, 200, 200 pada create, patch, submit knowledge | P2 (usulan) selama hanya `SIMULATED_DATA` dan PD-1 belum disetujui; menjadi P1 bila PD-1 disetujui tetapi belum diterapkan | Inspeksi kode dan pengecekan manual dengan pengguna simulasi | OPEN (PD-1, R-17, OQ-25) | Belum ada | Belum ada; SEC-40 dan AC-17 PLANNED |
| REQ-GAP-02 | 2026-10-06 | Otorisasi, data | Peran `knowledge_owner` (representasi PIC) tidak memiliki `knowledge:review` maupun `approval:decide`, dan penunjukan ketua tim dan PIC per tim tidak tercatat; role berlaku global karena `user_roles.team_id` tidak diperiksa (FR-51, BR-34) | P2 (usulan) | Inspeksi kode (`authz/catalog.py`, `principal_facts`) | OPEN (OQ-25) | Belum ada | Belum ada; SEC-43 PLANNED |
| REQ-GAP-03 | 2026-10-06 | Deployment | `APP_ENV=production` mewajibkan dev auth nonaktif, sedangkan `IdentityProvider` hanya `development`; server pilot pada mode production belum punya cara login (NFR-43) | P2 (usulan) | Inspeksi kode (`core/config.py`, `modules/auth.py`) | OPEN (OQ-07, PD-3) | Belum ada | Belum ada; SEC-76 belum dapat ditulis |

## Kandidat yang Tidak Dicatat

Kandidat berikut diminta untuk diperiksa tetapi **tidak dapat ditelusuri** di riwayat Git, `CHANGELOG.md`, known-limitations, atau catatan review yang tersedia (riwayat sebelum fitur PostgreSQL hanya satu commit, `357df94`). Tidak dicatat sebagai cacat sampai ada bukti; bila ada tangkapan layar atau catatan review asli, tambahkan dengan ID berikutnya.

- Uji API yang gagal dan plugin mypy yang hilang pada scaffold awal. Berkas `apps/api/pyproject.toml` kini memuat `plugins = ["pydantic.mypy"]` dan suite lulus pada `357df94`, tetapi tidak ada catatan bahwa keduanya pernah menjadi cacat yang ditemukan.
- Label sumbu x grafik dashboard yang tumpang tindih, indeks sitasi Hermes yang tidak terlihat, dan sidebar yang tidak setinggi layar penuh. Kode CSS saat ini memuat `.sidebar { min-height: 100vh }` dan `.sidebar-inner { position: sticky }`, tetapi tidak ada catatan review visual atau commit yang menyebut temuan tersebut.

## Related Documents

- [bug-severity.md](bug-severity.md)
- [test-strategy.md](test-strategy.md)
- [security-testing.md](security-testing.md)
- [known-limitations.md](../13-handover/known-limitations.md)
- [risk-register.md](../12-governance/risk-register.md)
- [future-development.md](../13-handover/future-development.md)
