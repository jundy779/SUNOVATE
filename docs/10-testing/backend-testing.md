# Pengujian Backend

**Status:** DRAFT

**Last Updated:** 2026-10-02

## Purpose

Menjelaskan cara menguji API `apps/api` (FastAPI), termasuk pengujian negatif otorisasi, lint, dan pemeriksaan tipe.

## Confirmed Information

- **CONFIRMED**: Backend memakai Python 3.12–3.14, FastAPI, Pydantic v2, SQLAlchemy 2, dan Alembic (sumber: brief sesi 2026-10-01).
- **CONFIRMED**: Alat uji: pytest dengan FastAPI TestClient; lint dengan Ruff; pemeriksaan tipe dengan mypy mode strict (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Pengujian berlokasi di `apps/api/tests/` (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Default runtime dan default test memakai `DATA_BACKEND=simulated` (store in-memory dari dataset SIMULATED_DATA yang sama dengan seed database) (sumber: ADR-007).
- **CONFIRMED (implementasi)**: Backend `postgres` (repository SQLAlchemy sinkron di `store/postgres.py`) sudah diimplementasikan; `pnpm db:test` menjalankan seluruh suite pytest dengan `SUNOVATE_TEST_BACKEND=postgres` pada PostgreSQL sementara (ADR-015, PROPOSED; lihat [integration-testing.md](integration-testing.md)).
- **CONFIRMED**: Hasil eksekusi tidak dicatat di sini; lihat laporan validasi terbaru di CHANGELOG.md.

## Perintah

| Tujuan | Perintah |
|---|---|
| Menyiapkan environment Python | `pnpm api:setup` |
| Lint (Ruff) | `pnpm api:lint` |
| Typecheck (mypy strict) | `pnpm api:typecheck` |
| Unit dan API test (pytest) | `pnpm api:test` |
| Seluruh gate frontend dan backend | `pnpm validate` |

## Pola Pengujian API

- **PROPOSED**: Setiap test membuat aplikasi dan store simulasi yang segar agar tidak ada status yang bocor antar test.
- **PROPOSED**: Token diperoleh lewat `POST /api/v1/auth/dev/login` untuk pengguna simulasi yang di-seed, lalu dikirim sebagai header otorisasi pada request berikutnya.
- **PROPOSED**: Assertion memeriksa status HTTP, `code` error, envelope `{ "data", "meta" }`, `meta.dataLabel` bernilai `SIMULATED_DATA`, dan keberadaan header `X-Request-ID`.

## Pengujian Negatif Otorisasi

Otorisasi = permission DAN team scope DAN klasifikasi data, deny by default (sumber: ADR-006). Setiap endpoint terlindungi minimal memiliki kasus berikut (PROPOSED):

| Kasus | Contoh pengguna simulasi | Hasil yang diharapkan |
|---|---|---|
| Tanpa token | - | 401 `UNAUTHENTICATED` |
| Token tidak valid atau kedaluwarsa | - | 401 `UNAUTHENTICATED` |
| Permission tidak dimiliki | `sim.readonly.dhtv` memanggil `POST /knowledge` | 403 `PERMISSION_DENIED` |
| Record tim lain dengan `sharing_scope` TEAM | `sim.staff.pppsun` membaca knowledge milik PSUN | 404 `NOT_FOUND` |
| Klasifikasi di atas clearance | `sim.owner.ppsun` (INTERNAL) membaca record RESTRICTED | 404 `NOT_FOUND` |
| Data tidak terbaca di daftar dan pencarian | `GET /knowledge`, `GET /search?q=` | Record terlarang tidak muncul dan tidak terhitung dalam `meta.total` |
| Separation of duties | Pengaju memutuskan approval miliknya sendiri | Ditolak |
| Audit | Setiap penolakan akses | Tercatat dengan aksi `ACCESS_DENIED` |

- **CONFIRMED**: Record yang tidak boleh dibaca mengembalikan 404, bukan 403, untuk mencegah kebocoran keberadaan record (sumber: implementasi scaffold sesi 2026-10-01).
- **PROPOSED**: Kasus pada kolom "Contoh pengguna" mengikuti matriks pada [permission-matrix.md](../06-security/permission-matrix.md); jika matriks berubah, test diperbarui bersamaan.

## Pengujian Aturan Bisnis

| Aturan | Hasil yang diharapkan | Sumber |
|---|---|---|
| `revision` usang pada `PATCH /knowledge/{id}` atau `PATCH /tasks/{id}` | 409 `REVISION_CONFLICT` | ADR-011 |
| Versi dokumen dengan checksum SHA-256 yang sama | 409 `DUPLICATE_CHECKSUM` | Fact sheet bagian 6 |
| Submit knowledge | Status `DRAFT` menjadi `IN_REVIEW`, audit `SUBMIT` | Fact sheet bagian 6 |
| Publikasi | Hanya melalui approval `KNOWLEDGE_PUBLICATION` yang disetujui | Fact sheet bagian 5 |
| Deadline state | Dihitung backend: SAFE, DUE_SOON, DUE_TODAY, OVERDUE, COMPLETED dengan `DEADLINE_DUE_SOON_DAYS` | Fact sheet bagian 6 |
| Validasi input | 422 `VALIDATION_ERROR`; `pageSize` di luar 1–100 ditolak | Fact sheet bagian 9 |
| Dev auth dimatikan | `POST /auth/dev/login` mengembalikan 404 `DEV_AUTH_DISABLED` | ADR-005 |

## Pengujian Pipeline Hermes

- **PROPOSED**: Setiap komponen (ScopeGuard, RetrievalService, Reranker, injection filter, CitationValidator, OutputGuard, HermesGateway) memiliki unit test terpisah dan satu test alur penuh melalui `POST /hermes/query`.
- **PROPOSED**: Test memastikan filter otorisasi diterapkan sebelum scoring retrieval, bukan setelahnya.
- **PROPOSED**: Permintaan dengan niat menulis menghasilkan `REQUIRES_HUMAN_APPROVAL` dan approval `PENDING`, tanpa eksekusi aksi.
- Detail skenario ada di [security-testing.md](security-testing.md) dan [rag-testing.md](rag-testing.md).

## Aturan Kode Uji

- **PROPOSED**: Kode test ikut diperiksa Ruff dan bertipe; hindari `type: ignore` tanpa alasan tertulis.
- **PROPOSED**: Tidak ada akses jaringan dalam test; provider AI pengembangan bersifat deterministik dan ekstraktif (sumber: ADR-008).
- **PROPOSED**: Tidak ada data asli; fixture memakai `SIMULATED_DATA`.

## Related Documents

- [test-strategy.md](test-strategy.md)
- [integration-testing.md](integration-testing.md)
- [authorization-rbac.md](../06-security/authorization-rbac.md)
- [error-format.md](../07-api/error-format.md)
- [endpoint-catalog.md](../07-api/endpoint-catalog.md)
