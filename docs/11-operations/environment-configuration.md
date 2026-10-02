# Konfigurasi Environment

**Status:** DRAFT

**Last Updated:** 2026-10-01

## Purpose

Mendokumentasikan setiap variabel environment SUNOVATE beserta nilai default, arti, dan nilai yang diizinkan, serta aturan keamanan konfigurasi.

## Confirmed Information

- **CONFIRMED**: Daftar variabel berikut tercantum di `.env.example` (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: `.env` di-ignore git; hanya `.env.example` yang di-commit (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Integrasi produksi untuk identitas, dokumen, notifikasi, dan AI tetap nonaktif sampai divalidasi (sumber: brief sesi 2026-10-01, AGENTS.md).

## Daftar Variabel

Kolom "Default" berisi nilai pengembangan. Bila tertulis "lihat `.env.example`", nilai contoh lokal ada di file tersebut dan tidak boleh dipakai di luar mesin pengembang.

### Aplikasi

| Variabel | Default | Arti | Nilai yang diizinkan |
|---|---|---|---|
| `APP_ENV` | `development` | Lingkungan aplikasi | `development`, `production`; nilai lain mengikuti `config` backend |
| `LOG_LEVEL` | `INFO` | Level log JSON | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CORS_ORIGINS` | Lihat `.env.example` | Origin yang boleh memanggil API dari browser | Daftar origin; lokal `http://localhost:3000` |
| `SUNOVATE_API_URL` | Lihat `.env.example` | Alamat API yang dipanggil server Next.js (sisi server) | URL; lokal `http://localhost:8000` |

### Data

| Variabel | Default | Arti | Nilai yang diizinkan |
|---|---|---|---|
| `DATA_BACKEND` | `simulated` | Sumber data runtime API | `simulated` (satu-satunya yang diimplementasikan; backend database PROPOSED) |
| `DATABASE_URL` | Lihat `.env.example` | Connection string PostgreSQL untuk Alembic, seed, dan health database | URL PostgreSQL |
| `POSTGRES_DB` | Lihat `.env.example` | Nama database service `postgres` di Docker Compose | Teks |
| `POSTGRES_USER` | Lihat `.env.example` | User database Docker Compose | Teks |
| `POSTGRES_PASSWORD` | Lihat `.env.example` | Password database Docker Compose; hanya untuk lokal | Rahasia, tidak di-commit selain nilai contoh lokal |

### Autentikasi Pengembangan

| Variabel | Default | Arti | Nilai yang diizinkan |
|---|---|---|---|
| `DEV_AUTH_ENABLED` | `true` di development | Mengaktifkan `POST /api/v1/auth/dev/login` | `true`, `false`; wajib `false` di luar development |
| `DEV_AUTH_SECRET` | Lihat `.env.example` | Kunci HMAC untuk menandatangani token pengembangan | Rahasia acak; ganti dari nilai contoh |
| `DEV_AUTH_TOKEN_TTL_MINUTES` | Lihat `.env.example` | Masa berlaku token pengembangan dalam menit | Bilangan bulat positif |

### Provider

| Variabel | Default | Arti | Nilai yang diizinkan |
|---|---|---|---|
| `DOCUMENT_PROVIDER` | `local` | Provider referensi dokumen | `local` (provider produksi nonaktif) |
| `LOCAL_STORAGE_PATH` | Lihat `.env.example` | Folder lokal untuk provider dokumen `local` | Path lokal di luar folder yang di-commit |
| `IDENTITY_PROVIDER` | `development` | Provider identitas | `development` (SSO organisasi belum tersedia, OQ-07) |
| `NOTIFICATION_PROVIDER` | `disabled` | Provider notifikasi | `disabled` |
| `AI_PROVIDER` | `development_extractive` | Provider jawaban Hermes | `development_extractive` (deterministik, tanpa jaringan) |
| `EMBEDDING_PROVIDER` | `disabled` | Provider embedding | `disabled` sampai model disetujui (OQ-11) |

### Hermes dan Monitoring

| Variabel | Default | Arti | Nilai yang diizinkan |
|---|---|---|---|
| `HERMES_MODE` | `development` | Mode runtime Hermes | `development` |
| `HERMES_MAX_CLASSIFICATION` | `RESTRICTED` | Batas atas klasifikasi chunk yang boleh masuk konteks Hermes | `PUBLIC`, `INTERNAL`, `RESTRICTED`; `CONFIDENTIAL` tidak diproses Hermes pada pengembangan |
| `DEADLINE_DUE_SOON_DAYS` | `7` | Ambang hari untuk deadline state `DUE_SOON` | Bilangan bulat; ambang final OPEN QUESTION (OQ-15) |

- **PROPOSED**: Nilai provider di luar daftar "Nilai yang diizinkan" belum didukung. Provider produksi hanya berupa placeholder nonaktif (lihat [provider-abstraction.md](../03-architecture/provider-abstraction.md)).

## Aturan Keamanan Konfigurasi

1. **Diimplementasikan**: Settings menolak start bila `APP_ENV=production` dengan `DEV_AUTH_ENABLED=true` atau `DATA_BACKEND=simulated` (ADR-005, ADR-007); diuji di `apps/api/tests/test_health_auth.py`. Skenario terkait: SEC-12 di [security-testing.md](../10-testing/security-testing.md).
2. **PROPOSED**: `DEV_AUTH_ENABLED` wajib `false` di semua lingkungan selain development, termasuk UAT.
3. **PROPOSED**: Rahasia (`DEV_AUTH_SECRET`, `POSTGRES_PASSWORD`, kredensial di `DATABASE_URL`) tidak pernah di-commit, tidak dicetak ke log, dan tidak ditempel di issue atau chat.
4. **PROPOSED**: `.env` tetap di-ignore git. Periksa `git status` sebelum commit.
5. **PROPOSED**: Nilai contoh di `.env.example` hanya untuk mesin lokal dan harus diganti di lingkungan lain.
6. **PROPOSED**: Penambahan variabel baru wajib diikuti pembaruan `.env.example` dan dokumen ini pada perubahan yang sama.
7. **OPEN QUESTION**: Mekanisme penyimpanan rahasia di lingkungan produksi bergantung pada hosting yang disetujui (OQ-07); lihat [secrets-management.md](../06-security/secrets-management.md).

## Related Documents

- [local-development.md](local-development.md)
- [secrets-management.md](../06-security/secrets-management.md)
- [authentication.md](../06-security/authentication.md)
- [deployment-runbook.md](deployment-runbook.md)
