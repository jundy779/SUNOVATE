# Deployment Runbook

**Status:** PROPOSED

**Last Updated:** 2026-10-01

## Purpose

Mencatat langkah deployment yang sudah dapat dijalankan (lokal) dan kerangka usulan untuk lingkungan lain. Dokumen ini tidak mengklaim adanya hosting, SSO, atau integrasi produksi.

## Status

- **CONFIRMED**: Hanya deployment lokal yang diimplementasikan (sumber: implementasi scaffold sesi 2026-10-01).
- **OPEN QUESTION**: Mekanisme login dan hosting yang disetujui (OQ-07).
- **OPEN QUESTION**: Lingkungan UAT (OQ-20).
- **CONFIRMED**: SUNOVATE belum siap produksi; lihat [known-limitations.md](../13-handover/known-limitations.md).

## Bagian A: Deployment Lokal (Diimplementasikan)

| Langkah | Perintah | Hasil |
|---|---|---|
| 1. Konfigurasi | Salin `.env.example` menjadi `.env` | Variabel lokal tersedia |
| 2. Dependensi web | `pnpm install` | Workspace JavaScript terpasang |
| 3. Dependensi API | `pnpm api:setup` | Environment Python `apps/api` tersinkron |
| 4. Validasi | `pnpm validate` | Lint, typecheck, test, build |
| 5. Database (opsional) | `pnpm compose:check`, `pnpm db:up`, `pnpm db:migrate`, `pnpm db:seed` | PostgreSQL lokal dengan skema dan seed |
| 6. API | `pnpm api:dev` | API di port 8000 |
| 7. Web | `pnpm dev` | Web di port 3000 |
| 8. Verifikasi | Buka `GET /api/v1/health` dan `http://localhost:3000/login` | Aplikasi dapat diakses |
| 9. E2E (opsional) | `pnpm e2e` | Alur utama terverifikasi |

- **CONFIRMED**: Docker Compose hanya berisi service `postgres` (image `pgvector/pgvector:pg17`); web dan API dijalankan langsung di host (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Jalur Docker belum divalidasi di mesin pengembangan saat ini karena Docker tidak terpasang.

## Bagian B: Kerangka Deployment Lingkungan Lain (PROPOSED)

Kerangka berikut hanya struktur. Isinya baru dapat dilengkapi setelah OQ-07 dan OQ-20 terjawab.

```mermaid
flowchart LR
    A["Checklist pra-deployment"] --> B["Backup database"]
    B --> C["Deploy API"]
    C --> D["Migration"]
    D --> E["Deploy web"]
    E --> F["Smoke test"]
    F --> G["Catat di CHANGELOG"]
```

### Checklist Pra-Deployment

- [ ] Hosting, jaringan, dan mekanisme login sudah disetujui (OQ-07).
- [ ] `APP_ENV` diset sesuai lingkungan dan `DEV_AUTH_ENABLED=false` di luar development.
- [ ] Semua rahasia disimpan di luar repository dan berbeda dari nilai `.env.example`.
- [ ] `IDENTITY_PROVIDER`, `DOCUMENT_PROVIDER`, `NOTIFICATION_PROVIDER`, `AI_PROVIDER`, dan `EMBEDDING_PROVIDER` hanya memakai provider yang sudah divalidasi; provider lain tetap nonaktif.
- [ ] `HERMES_MAX_CLASSIFICATION` sesuai keputusan klasifikasi (OQ-05).
- [ ] `pnpm validate` dan `pnpm api:test` selesai tanpa kegagalan pada commit yang akan dirilis.
- [ ] Gate kebocoran RAG bernilai nol (lihat [rag-testing.md](../10-testing/rag-testing.md)).
- [ ] Tidak ada bug P0 terbuka; P1 terbuka memiliki keputusan tertulis mentor.
- [ ] `pnpm audit` dan audit dependensi Python sudah ditinjau.
- [ ] Migration baru sudah direview dan diuji upgrade/downgrade di database uji.
- [ ] Backup database terbaru tersedia dan pernah diuji restore.
- [ ] `security-checklist.md` sudah diisi (lihat [security-checklist.md](../06-security/security-checklist.md)).
- [ ] Data yang dimuat sudah dipastikan boleh berada di lingkungan tersebut (OQ-04, OQ-05).

### Langkah Deployment (kerangka)

1. Umumkan jendela deployment kepada pihak terkait (OPEN QUESTION: siapa).
2. Buat backup database.
3. Deploy API versi baru.
4. Jalankan migration.
5. Deploy web versi baru dengan `SUNOVATE_API_URL` yang benar.
6. Jalankan smoke test.
7. Catat versi, waktu, dan hasil di CHANGELOG.md.

### Smoke Test (kerangka)

- `GET /api/v1/health` dan `GET /api/v1/health/database` merespons.
- Login dengan mekanisme yang disetujui berhasil; `POST /api/v1/auth/dev/login` mengembalikan 404 `DEV_AUTH_DISABLED`.
- Satu pencarian dan satu pertanyaan Hermes dengan akun uji menghasilkan respons dengan `X-Request-ID`.
- Akses tanpa token mengembalikan 401.

### Rollback (kerangka)

- Web dan API dikembalikan ke versi sebelumnya.
- Database dipulihkan dengan revision perbaikan maju atau restore dari backup (lihat [migration-guide.md](migration-guide.md) dan [backup-and-restore.md](backup-and-restore.md)).
- Insiden dicatat sesuai [incident-response.md](../06-security/incident-response.md).

## Related Documents

- [deployment-architecture.md](../03-architecture/deployment-architecture.md)
- [environment-configuration.md](environment-configuration.md)
- [integration-readiness-checklist.md](../08-integrations/integration-readiness-checklist.md)
