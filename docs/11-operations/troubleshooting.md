# Troubleshooting

**Status:** DRAFT

**Last Updated:** 2026-10-02

## Purpose

Kumpulan masalah umum pada pengembangan lokal SUNOVATE beserta penyebab dan langkah penanganan. Semua contoh memakai lingkungan lokal dan data SIMULATED.

## Ringkasan

| Gejala | Kemungkinan penyebab | Bagian |
|---|---|---|
| Web atau API gagal start karena port | Port 3000 atau 8000 sudah dipakai | 1 |
| Halaman web error saat memuat data | `SUNOVATE_API_URL` salah atau API mati | 2 |
| Login pengembangan 404 | `DEV_AUTH_ENABLED=false` | 3 |
| 401 setelah beberapa waktu | Token pengembangan kedaluwarsa | 4 |
| Migration gagal di ekstensi vector | pgvector tidak tersedia | 5 |
| `pnpm db:up` gagal di Windows | Docker belum terpasang | 6 |
| `pnpm install` menolak paket | Aturan `minimumReleaseAge` pnpm | 7 |
| `pnpm api:setup` gagal | Versi Python tidak didukung | 8 |

## 1. Port Sudah Dipakai

- Gejala: proses berhenti dengan pesan alamat sudah dipakai untuk port 3000 (web) atau 8000 (API).
- Penanganan: hentikan proses lama yang memakai port tersebut. Di PowerShell, `Get-NetTCPConnection -LocalPort 8000` menunjukkan `OwningProcess`, lalu hentikan proses itu dengan `Stop-Process` bila memang proses SUNOVATE yang tertinggal.
- Bila port dipindah, sesuaikan `SUNOVATE_API_URL` dan `CORS_ORIGINS`.

## 2. API Tidak Terjangkau dari Web

- Gejala: halaman server component menampilkan state error; log web menunjukkan kegagalan koneksi.
- Penyebab: API belum berjalan, atau `SUNOVATE_API_URL` tidak menunjuk ke `http://localhost:8000`.
- Penanganan:
  1. Pastikan `pnpm api:dev` berjalan dan `http://localhost:8000/api/v1/health` merespons.
  2. Periksa `SUNOVATE_API_URL`. Variabel ini dibaca sisi server Next.js; restart `pnpm dev` setelah mengubahnya.
  3. Bila panggilan dari browser ditolak, periksa `CORS_ORIGINS`.

## 3. Login Pengembangan Mengembalikan 404

- Gejala: `POST /api/v1/auth/dev/login` mengembalikan 404 dengan code `DEV_AUTH_DISABLED`.
- Penyebab: `DEV_AUTH_ENABLED=false`, atau `APP_ENV` bukan `development`.
- Penanganan: di mesin lokal saja, set `APP_ENV=development` dan `DEV_AUTH_ENABLED=true`, lalu restart API. Jangan mengaktifkan dev auth di lingkungan lain (ADR-005).

## 4. 401 karena Token Kedaluwarsa

- Gejala: setelah beberapa waktu, request mengembalikan 401 `UNAUTHENTICATED`.
- Penyebab: masa berlaku token melewati `DEV_AUTH_TOKEN_TTL_MINUTES`, atau `DEV_AUTH_SECRET` berubah sejak token dibuat.
- Penanganan: login ulang di `/login`. Bila sering terjadi saat pengembangan, naikkan `DEV_AUTH_TOKEN_TTL_MINUTES` di `.env` lokal.

## 5. Migration Gagal: Ekstensi pgvector Tidak Ada

- Gejala: `pnpm db:migrate` gagal saat membuat ekstensi `vector`.
- Penyebab: PostgreSQL yang dipakai tidak memiliki pgvector.
- Penanganan: gunakan service `postgres` dari Docker Compose (image `pgvector/pgvector:pg17`) melalui `pnpm db:up`, atau jalankan `pnpm db:check` untuk validasi tanpa Docker. Pastikan `DATABASE_URL` menunjuk ke database tersebut.

## 6. Docker Tidak Terpasang di Windows

- Gejala: `pnpm db:up` atau `pnpm compose:check` gagal karena perintah `docker` tidak dikenali.
- Konteks: Docker belum terpasang di mesin pengembangan saat ini (sumber: implementasi scaffold sesi 2026-10-01).
- Penanganan:
  - Database tidak wajib untuk menjalankan web dan API karena default runtime memakai `DATA_BACKEND=simulated`. Mode `DATA_BACKEND=postgres` memerlukan database (ADR-015, PROPOSED).
  - Untuk validasi skema tanpa Docker, gunakan `pnpm db:check`; untuk seluruh suite test pada PostgreSQL sementara, gunakan `pnpm db:test`.
  - Memasang Docker di perangkat instansi memerlukan izin pengelola perangkat (OPEN QUESTION).

## 7. `pnpm install` Diblokir oleh `minimumReleaseAge`

- Gejala: pnpm menolak memasang versi paket yang baru dirilis.
- Penyebab: konfigurasi workspace menahan paket yang umurnya belum melewati batas minimum; pengecualian dicatat di `minimumReleaseAgeExclude` pada `pnpm-workspace.yaml`.
- Penanganan: tunggu sampai batas umur terlewati atau pakai versi yang sudah dikunci di lockfile. Menambah pengecualian hanya untuk versi tertentu yang dipin dan dengan alasan yang dicatat di CHANGELOG.md. Jangan menonaktifkan aturan ini secara global.

## 8. Versi Python Tidak Sesuai

- Gejala: `pnpm api:setup` gagal atau uv memilih interpreter yang tidak didukung.
- Penyebab: Python di luar rentang 3.12–3.14.
- Penanganan: pasang Python dalam rentang yang didukung, atau biarkan uv menyediakan interpreter yang sesuai, lalu jalankan ulang `pnpm api:setup`. Periksa versi dengan `uv run python --version` dari folder `apps/api`.

## Melaporkan Masalah Baru

Sertakan langkah reproduksi, perintah yang dijalankan, potongan pesan error tanpa rahasia, dan `X-Request-ID` bila ada. Lihat [bug-severity.md](../10-testing/bug-severity.md) untuk field register bug.

## Related Documents

- [local-development.md](local-development.md)
- [environment-configuration.md](environment-configuration.md)
- [observability.md](observability.md)
