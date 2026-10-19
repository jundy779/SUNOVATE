# Pengujian Backend

**Status:** DRAFT

**Last Updated:** 2026-10-19

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
| Evaluasi kualitas ekstraksi simulasi | `pnpm extraction:eval` |
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

## Pengujian Ekstraksi Dokumen Simulasi

Pengujian ekstraksi memakai fixture sintetis yang dibuat di memori. Tidak ada dokumen internal
atau berkas sumber yang disimpan di repository.

| Format | Struktur yang diuji | Gerbang keamanan yang diuji |
|---|---|---|
| PDF | Dua halaman teks dan jumlah halaman | Header/struktur PDF tidak valid ditolak |
| DOCX | Judul Word, paragraf, tabel di tengah dokumen, dan urutan setelah tabel | Makro dikarantina; hasil dapat dibagi menurut judul |
| XLSX | Beberapa lembar, termasuk lembar tersembunyi, nilai teks/angka, dan rumus | Rumus tidak dijalankan; instruksi mencurigakan pada lembar tersembunyi dikarantina |
| XLS | Beberapa lembar dan nilai tabel | Struktur OLE palsu ditolak; makro dideteksi sebelum pembacaan |
| TXT/MD | UTF-8 dan penanda struktur | Data biner, ukuran berlebih, dan instruksi mencurigakan dikarantina |

Lembar tersembunyi tidak dianggap sebagai batas keamanan. Isinya tetap masuk pemeriksaan agar
instruksi yang disisipkan tidak lolos hanya karena tidak terlihat pada tampilan awal Excel.

Evaluator `pnpm extraction:eval` memakai tujuh kasus berlabel `SIMULATED_DATA`. Gate awalnya
menetapkan keberhasilan ekstraksi, ketercakupan fragmen, ketepatan struktur, dan akurasi
klasifikasi instruksi masing-masing 1,00, dengan kemunculan fragmen terlarang wajib 0. Output
hanya menampilkan metrik agregat dan ID kasus, tanpa nama berkas, checksum, atau isi dokumen.

## Kasus Terencana dari Jawaban Knowledge Owner (PLANNED)

Semua baris **PLANNED** kecuali bila kolom Status menyebut uji yang ada. Rujukan ID dan skenario rinci: [security-testing.md](security-testing.md) dan [acceptance-criteria.md](../01-product/acceptance-criteria.md) (AC-16 sampai AC-25).

| Kasus | Contoh pengguna simulasi | Hasil yang diharapkan | Status |
|---|---|---|---|
| `staff` membuat, mengubah, mengajukan knowledge (setelah PD-1) | `sim.staff.pppsun` | 403 `PERMISSION_DENIED`, audit `ACCESS_DENIED` (SEC-40, AC-17) | PLANNED; hari ini 201/200/200 |
| Ketua tim, PIC, tingkat PMP menulis dalam scope | `sim.lead.psun`, `sim.owner.ppsun`, `sim.coordinator` | 201/200 (SEC-41, AC-16) | Ada sebagian di `test_knowledge_workflow.py` |
| `staff` mendaftarkan versi dokumen | `sim.staff.pppsun` | 403 (SEC-44, AC-18) | PLANNED |
| Penunjukan per tim dan kedaluwarsa | Pengguna tambahan (usulan) | 403 di luar tim atau setelah berakhir (SEC-42, SEC-43) | SEC-42 ada; SEC-43 PLANNED |
| Dashboard tanpa yield dan kepemilikan SBN | Semua pengguna simulasi | Tidak ada field atau angka (SEC-60) | PLANNED |
| Route kanal pesan tidak ada | `sim.admin` | 404 untuk webhook kanal (SEC-80) | PLANNED |
| Konfigurasi production | Tanpa login | Ditolak bila dev auth aktif atau `simulated` (SEC-70) | Ada |

- **PLANNED**: Uji otorisasi tulis dijalankan pada kedua backend (`pnpm test` dan `pnpm db:test`) karena pilot memakai `DATA_BACKEND=postgres`; uji penerapan PD-1 pada database yang sudah di-seed (SEC-45) hanya bermakna pada PostgreSQL.
- **PROPOSED**: Bila matriks izin berubah (PD-1), uji dan dokumentasi diperbarui bersamaan, dan uji yang ada yang terdampak tercatat di bagian "Uji yang Ada dan Hubungannya dengan PD-1" pada [security-testing.md](security-testing.md).

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
