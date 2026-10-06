# Pengujian Integrasi Database

**Status:** DRAFT

**Last Updated:** 2026-10-02

## Purpose

Menjelaskan pengujian yang membutuhkan PostgreSQL nyata: migration upgrade dan downgrade, seed SIMULATED_DATA, pemeriksaan full-text search, dan seluruh suite API pada backend `postgres`.

## Confirmed Information

- **CONFIRMED**: Skema fisik 30 tabel didefinisikan pada revision Alembic `0001_initial_schema`, ditambah kolom urutan pada `0002_ordering_columns` (sumber: fact sheet bagian 6, `apps/api/alembic/versions/`; status skema PROPOSED).
- **CONFIRMED**: PostgreSQL adalah satu-satunya store: relasional, full-text search (tsvector, GIN), dan pgvector (sumber: ADR-003).
- **CONFIRMED**: Suite berlokasi di `tests/integration/` dan hanya berjalan bila `SUNOVATE_TEST_DATABASE_URL` diisi; jika tidak, test dilewati (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Docker tidak terpasang di mesin pengembangan saat ini. Migration divalidasi memakai PostgreSQL lokal sementara melalui paket Python `pgserver`, yang hanya alat bantu validasi dan bukan dependensi proyek (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED (implementasi)**: Runtime API dapat membaca dan menulis database dengan `DATA_BACKEND=postgres` (ADR-015, PROPOSED). Perilaku endpoint terhadap database diuji lewat `pnpm db:test` (Jalur C); `tests/integration/` tetap memvalidasi skema.
- **CONFIRMED**: Hasil eksekusi tidak dicatat di sini; lihat laporan validasi terbaru di CHANGELOG.md.

## Cakupan

| Pemeriksaan | Yang dibuktikan | Status |
|---|---|---|
| Upgrade ke head | Semua tabel, constraint, indeks, dan ekstensi pgvector terbentuk | PROPOSED |
| Seed | Dataset SIMULATED_DATA termuat; `data_origin` bernilai `SIMULATED_DATA` | PROPOSED |
| Full-text search | Query tsvector pada knowledge/chunk mengembalikan record yang sesuai | PROPOSED |
| Audit append-only | UPDATE dan DELETE pada `audit_logs` ditolak oleh trigger | PROPOSED |
| Unique checksum | Duplikasi (`document_reference_id`, `checksum_sha256`) ditolak | PROPOSED |
| Downgrade ke base | Semua objek terhapus bersih tanpa sisa | PROPOSED |

## Jalur A: Docker Compose

Prasyarat: Docker terpasang (belum divalidasi di mesin pengembangan saat ini).

```powershell
pnpm compose:check
pnpm db:up
pnpm db:migrate
pnpm db:seed
```

- **CONFIRMED**: `pnpm db:up` menjalankan service `postgres` dengan image `pgvector/pgvector:pg17` dan healthcheck (sumber: implementasi scaffold sesi 2026-10-01).
- **PROPOSED**: Setelah database siap, isi `SUNOVATE_TEST_DATABASE_URL` dengan connection string database uji lalu jalankan pytest untuk `tests/integration/`.
- **PROPOSED**: Gunakan database terpisah untuk pengujian agar data pengembangan tidak tertimpa.

## Jalur B: Tanpa Docker (opsional)

```powershell
pnpm db:check
```

- **CONFIRMED**: `scripts/validation/db_check_pgserver.py` menjalankan migrate (termasuk `0002_ordering_columns`), `alembic check`, seed dua kali, pemeriksaan FTS dan trigger append-only, lalu downgrade terhadap PostgreSQL sementara tanpa Docker (sumber: `scripts/validation/db_check_pgserver.py`).
- **PROPOSED**: Jalur ini hanya untuk validasi skema lokal. Paket `pgserver` tidak boleh ditambahkan sebagai dependensi proyek.

## Jalur C: Seluruh suite pada backend postgres (`pnpm db:test`)

```powershell
pnpm api:setup
pnpm db:test
```

- **CONFIRMED (implementasi)**: `scripts/validation/db_test_pgserver.py` menjalankan pgserver sementara, `alembic upgrade head`, seed, lalu `pytest -q` di `apps/api` (testpaths `tests` dan `../../tests`) dengan `SUNOVATE_TEST_BACKEND=postgres`, `SUNOVATE_TEST_DATABASE_URL`, `SUNOVATE_DB_RESET_ALLOWED=1`, dan `APP_ENV=test`. Exit code sama dengan pytest; direktori sementara dihapus; URL tidak dicetak (sumber: skrip tersebut, ADR-015).
- **CONFIRMED (implementasi)**: Fixture autouse `_reset_backend_state` di `apps/api/tests/conftest.py` dan `tests/conftest.py` mereset database (`TRUNCATE ... RESTART IDENTITY CASCADE` + seed) sebelum setiap test. Reset menolak berjalan kecuali `APP_ENV=test` dan `SUNOVATE_DB_RESET_ALLOWED=1`.
- **CONFIRMED (implementasi)**: Pada jalur ini test `tests/integration/` ikut berjalan (tidak di-skip), begitu pula test khusus postgres di `apps/api/tests/postgres/` dan instance postgres dari `apps/api/tests/test_repository_contract.py`: pemetaan constraint ke 409 `DUPLICATE_CHECKSUM` / 403 `SEPARATION_OF_DUTIES`, revision atomik dan konkuren, rollback multi-langkah, audit persisten dan append-only, paritas respons dengan backend simulated per persona, persistence lintas instance backend, dan jumlah statement yang tidak bertambah dengan data. Pada `pnpm test` (simulated) test tersebut di-skip.
- **PROPOSED**: Jalur ini hanya untuk database sementara. Jangan menjalankan reset terhadap database yang berisi data yang ingin disimpan.

## Render SQL Offline

```powershell
pnpm db:sql
```

- **CONFIRMED**: Merender SQL migration secara offline tanpa koneksi database (sumber: implementasi scaffold sesi 2026-10-01).
- **PROPOSED**: Hasil render dipakai untuk review perubahan skema; lihat [migration-guide.md](../11-operations/migration-guide.md).

## Alur Validasi

```mermaid
flowchart LR
    A["Database kosong"] --> B["Upgrade ke head"]
    B --> C["Seed SIMULATED_DATA"]
    C --> D["Cek FTS, trigger, constraint"]
    D --> E["Downgrade ke base"]
    E --> F["Database kosong kembali"]
```

## Aturan

- **PROPOSED**: Database uji tidak pernah diarahkan ke database bersama atau produksi.
- **PROPOSED**: Connection string uji tidak di-commit; gunakan variabel lingkungan lokal.
- **PROPOSED**: Kolom vektor belum bertipe dan belum ada indeks ANN sampai model embedding disetujui (sumber: ADR-009); test tidak boleh mengasumsikan dimensi vektor tertentu.

## Open Questions

- OQ-11 Model embedding dan dimensinya; menentukan kapan pengujian pgvector dapat ditambahkan.
- OQ-20 Lingkungan uji bersama, jika ada.

## Related Documents

- [database-schema.md](../04-data/database-schema.md)
- [migration-guide.md](../11-operations/migration-guide.md)
- [local-development.md](../11-operations/local-development.md)
- [backend-testing.md](backend-testing.md)
