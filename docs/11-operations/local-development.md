# Pengembangan Lokal

**Status:** DRAFT

**Last Updated:** 2026-10-02

## Purpose

Panduan menyiapkan dan menjalankan SUNOVATE di mesin pengembang, termasuk login pengembangan dengan pengguna simulasi.

## Prasyarat

| Alat | Versi | Keterangan |
|---|---|---|
| Node.js | 22 atau lebih baru | Versi yang dipakai pada scaffold: 24.19.0 |
| pnpm | 11.4 | Package manager workspace |
| Python | 3.12–3.14 | Versi yang dipakai pada scaffold: 3.14.4 |
| uv | Terbaru yang kompatibel | Versi yang dipakai pada scaffold: 0.11.6; mengelola environment Python di `apps/api` |
| Docker | Opsional | Hanya untuk PostgreSQL lokal lewat Docker Compose |

- **CONFIRMED**: Versi yang dipakai sesuai daftar di atas (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Docker tidak terpasang di mesin pengembangan saat ini; jalur Docker Compose belum divalidasi di mesin tersebut (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Default runtime API adalah `DATA_BACKEND=simulated`, sehingga web dan API dapat dijalankan tanpa PostgreSQL (sumber: ADR-007, `core/config.py`).
- **PROPOSED (ADR-015)**: `DATA_BACKEND=postgres` membuat runtime membaca dan menulis PostgreSQL sehingga data bertahan setelah API di-restart (lihat bagian "Menjalankan API dengan PostgreSQL").

## Langkah Menjalankan

1. Salin `.env.example` menjadi `.env` di root lalu sesuaikan nilai lokal. Jangan commit `.env` (lihat [environment-configuration.md](environment-configuration.md)).
2. Pasang dependensi JavaScript:

   ```powershell
   pnpm install
   ```

3. Siapkan environment Python backend (menjalankan `uv sync` di `apps/api`):

   ```powershell
   pnpm api:setup
   ```

4. Jalankan API di terminal pertama (port 8000):

   ```powershell
   pnpm api:dev
   ```

5. Jalankan web di terminal kedua (port 3000):

   ```powershell
   pnpm dev
   ```

6. Buka `http://localhost:3000/login` untuk aplikasi dan `http://localhost:8000/docs` untuk dokumentasi OpenAPI.

## Database Lokal (Opsional)

Database dibutuhkan untuk memvalidasi skema, migration, dan seed, serta untuk menjalankan API dengan `DATA_BACKEND=postgres`. Mode default `simulated` tidak membacanya.

```powershell
pnpm compose:check
pnpm db:up
pnpm db:migrate
pnpm db:seed
```

- Tanpa Docker: `pnpm db:check` memvalidasi migration dan seed pada PostgreSQL sementara (pgserver), dan `pnpm db:test` menjalankan seluruh suite pytest pada backend postgres (lihat [integration-testing.md](../10-testing/integration-testing.md)).
- Endpoint `GET /api/v1/health/database` dapat dipakai untuk memeriksa koneksi database.

## Menjalankan API dengan PostgreSQL

**PROPOSED (ADR-015)**. Hanya untuk `SIMULATED_DATA` di mesin pengembang.

1. Siapkan database PostgreSQL lokal (Docker Compose di atas, atau server PostgreSQL lokal lain) dan isi `DATABASE_URL` di `.env` dengan skema `postgresql+asyncpg://` atau `postgresql+psycopg://`. Skema `postgresql://` polos ditolak.
2. Jalankan migration dan seed:

   ```powershell
   pnpm db:migrate
   pnpm db:seed
   ```

3. Set `DATA_BACKEND=postgres` di `.env`, lalu jalankan `pnpm api:dev`.
4. Periksa `GET http://localhost:8000/api/v1/health`: `data.dataBackend` harus `postgres`. Data yang dibuat lewat API tetap ada setelah API di-restart.

Catatan:

- Bila database tidak terjangkau, API tetap start dan `/api/v1/health` tetap 200, tetapi endpoint data (termasuk login dev) mengembalikan 503 `DATABASE_UNAVAILABLE`.
- `pnpm db:seed` idempoten (baris yang sudah ada dilewati) dan menolak `APP_ENV=production`.
- Batasan yang diketahui (KL-24 di [known-limitations.md](../13-handover/known-limitations.md)): `sunovate_api/main.py` membuat app saat diimpor. Bila `.env` berisi `DATA_BACKEND=postgres` dengan `DATABASE_URL` yang skemanya tidak diizinkan, impor `sunovate_api.main` gagal dengan `ValueError` (tanpa URL). Hal ini juga membuat koleksi `pnpm test` gagal, karena `sunovate_api.testing` mengimpor `main`. Perbaikannya adalah memperbaiki skema `DATABASE_URL` atau mengembalikan `DATA_BACKEND=simulated`.

## Test pada PostgreSQL (`pnpm db:test`)

```powershell
pnpm api:setup
pnpm db:test
```

- Menjalankan PostgreSQL sementara lewat pgserver (tanpa Docker), `alembic upgrade head`, seed, lalu seluruh `pytest -q` (API, security, RAG golden set, integration, dan test khusus postgres) dengan `SUNOVATE_TEST_BACKEND=postgres`. Database direset (`TRUNCATE` + seed) sebelum setiap test.
- Exit code sama dengan exit code pytest. Direktori data sementara dihapus setelahnya; URL database tidak dicetak.
- Butuh beberapa menit (sekitar 4 sampai 5 menit di mesin pengembang Windows) karena reset per test. `pnpm test` tetap memakai backend simulated dan tidak butuh PostgreSQL.

## Latihan Restore dan Evaluasi Pencarian PostgreSQL

Setelah dua database uji terpisah tersedia, isi variabel yang tercantum pada
[backup-and-restore.md](backup-and-restore.md), lalu jalankan:

```powershell
pnpm db:restore-drill
pnpm search:eval:postgres
```

Perintah pertama hanya menerima sumber `SIMULATED_DATA` dan target kosong bernama restore.
Perintah kedua menggunakan `SUNOVATE_TEST_DATABASE_URL`, `APP_ENV=test`, dan
`SUNOVATE_SEARCH_EVAL_CONFIRM=SIMULATED_DATA_ONLY`. Keduanya menolak host publik yang tidak
diizinkan dan tidak mencetak URL database. Jangan menjalankannya terhadap database bersama,
database produksi, atau database yang datanya perlu dipertahankan.

## Login Pengembangan

- **PROPOSED**: Login pengembangan memakai token bertanda tangan (HMAC) yang diterbitkan oleh `POST /api/v1/auth/dev/login` untuk pengguna simulasi yang di-seed. Fitur ini nonaktif di luar development (sumber: ADR-005).
- **CONFIRMED**: Halaman `/login` menyimpan token di cookie httpOnly; server component memanggil API dengan token tersebut (sumber: implementasi scaffold sesi 2026-10-01).

Pengguna simulasi (semua fiktif, domain `@sunovate.local`):

| Email | Role | Tim | Clearance |
|---|---|---|---|
| `sim.admin@sunovate.local` | system_admin | Semua tim lewat scope | INTERNAL |
| `sim.coordinator@sunovate.local` | knowledge_coordinator | Semua tim | RESTRICTED |
| `sim.lead.psun@sunovate.local` | team_lead | PSUN | RESTRICTED |
| `sim.owner.ppsun@sunovate.local` | knowledge_owner | PPSUN | INTERNAL |
| `sim.reviewer.akpsun@sunovate.local` | reviewer | AKPSUN | INTERNAL |
| `sim.staff.pppsun@sunovate.local` | staff | PPPSUN | INTERNAL |
| `sim.auditor@sunovate.local` | auditor | Semua tim | RESTRICTED |
| `sim.readonly.dhtv@sunovate.local` | read_only | DHTV | INTERNAL |

- **PROPOSED**: Role dan matriks permission adalah usulan pengembangan; lihat [permission-matrix.md](../06-security/permission-matrix.md).
- **CONFIRMED**: Akun ini hanya untuk data `SIMULATED_DATA` dan tidak mewakili pegawai atau jabatan nyata (sumber: brief sesi 2026-10-01).

## Port dan Alamat

| Komponen | Alamat |
|---|---|
| Web (Next.js) | `http://localhost:3000` |
| API (FastAPI) | `http://localhost:8000`, prefix `/api/v1` |
| OpenAPI | `http://localhost:8000/docs` |
| PostgreSQL (opsional) | Sesuai `DATABASE_URL` |

## Pemeriksaan Sebelum Handoff

```powershell
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Atau sekaligus dengan `pnpm validate`. Untuk backend saja: `pnpm api:lint`, `pnpm api:typecheck`, `pnpm api:test`. End-to-end: `pnpm e2e` saat web dan API berjalan. Hasil terbaru: lihat laporan validasi terbaru di CHANGELOG.md.

## Related Documents

- [environment-configuration.md](environment-configuration.md)
- [troubleshooting.md](troubleshooting.md)
- [migration-guide.md](migration-guide.md)
- [developer-handover.md](../13-handover/developer-handover.md)
