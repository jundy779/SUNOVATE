# Panduan Administrator

**Status:** DRAFT

**Last Updated:** 2026-10-02

## Purpose

Menjelaskan tugas administrasi yang dapat dilakukan pada scaffold pengembangan dan mengusulkan tugas administrator untuk lingkungan produksi.

## Status

- **CONFIRMED**: Hanya tugas administrasi pengembangan yang tersedia (sumber: implementasi scaffold sesi 2026-10-01).
- **PROPOSED**: Tugas administrasi produksi pada bagian B adalah usulan dan menunggu keputusan hosting dan login (OQ-07) serta tata kelola (OQ-09, OQ-12).
- **OPEN QUESTION**: Apakah administrator sistem boleh membaca isi konten knowledge.

## Bagian A: Tugas Administrasi Pengembangan

### Melihat pengguna, tim, role, dan klasifikasi

- Login sebagai `sim.admin@sunovate.local` (role `system_admin`) lalu buka `/admin`.
- Endpoint terkait: `GET /api/v1/users`, `GET /api/v1/teams`, `GET /api/v1/roles`, `GET /api/v1/permissions`, `GET /api/v1/classifications`.
- **CONFIRMED**: Belum ada endpoint untuk membuat atau mengubah pengguna, tim, atau role; permission `user:manage`, `team:manage`, dan `role:manage` belum memiliki endpoint (sumber: implementasi scaffold sesi 2026-10-01).

### Mengubah pengguna atau role simulasi

- Pengguna dan role berasal dari dataset SIMULATED_DATA yang sama untuk store simulasi dan seed database (ADR-007).
- Perubahan dilakukan di dataset tersebut melalui perubahan kode yang direview, lalu API di-restart.
- **PROPOSED**: Pengguna baru tetap fiktif, memakai domain `@sunovate.local`, dan tidak mewakili pegawai atau jabatan nyata.

### Memeriksa status provider

- Endpoint `GET /api/v1/providers` (permission `provider:read`) menunjukkan provider aktif.
- **CONFIRMED**: Provider produksi berupa placeholder nonaktif; provider yang aktif adalah implementasi pengembangan (sumber: implementasi scaffold sesi 2026-10-01).

### Membaca audit log dan isu kualitas data

- `GET /api/v1/audit-logs` (permission `audit:read`) dan `GET /api/v1/data-quality-issues` (permission `data_quality:read`).
- Role `system_admin` dan `auditor` memiliki `audit:read`; pengelolaan isu kualitas data (`data_quality:manage`) ada pada `knowledge_coordinator` (sumber: fact sheet bagian 5; status PROPOSED).

### Mengatur ulang data runtime

- `DATA_BACKEND=simulated` (default): store simulasi berada di memori; restart `pnpm api:dev` mengembalikan data ke dataset awal. Semua perubahan yang dibuat lewat API ikut hilang.
- `DATA_BACKEND=postgres` (ADR-015, PROPOSED): data bertahan setelah restart. Untuk kembali ke dataset awal, bentuk ulang database lokal (`uv run alembic downgrade base` dari `apps/api`, lalu `pnpm db:migrate` dan `pnpm db:seed`); seed saja tidak menghapus perubahan yang sudah ada.

### Database lokal

- Membentuk skema dan seed: `pnpm db:up`, `pnpm db:migrate`, `pnpm db:seed`. Lihat [migration-guide.md](../11-operations/migration-guide.md).
- Memeriksa koneksi: `GET /api/v1/health/database`.

### Mengganti rahasia lokal

- Ganti `DEV_AUTH_SECRET` di `.env` lokal lalu restart API. Semua token lama menjadi tidak valid dan pengguna harus login ulang.

### Mengaktifkan atau menonaktifkan login pengembangan

- `DEV_AUTH_ENABLED=true` hanya untuk `APP_ENV=development`. Lihat [environment-configuration.md](../11-operations/environment-configuration.md).

## Bagian B: Tugas Administrasi Produksi (PROPOSED)

| Tugas | Usulan | Ketergantungan |
|---|---|---|
| Siklus hidup akun | Provisioning dan deprovisioning lewat identity provider yang disetujui | OQ-07 |
| Penugasan role dan tim | Lewat endpoint `user:manage` dan `team:manage` yang belum dibuat, dengan audit | OQ-09 |
| Penetapan knowledge owner dan reviewer | Berdasarkan penunjukan resmi, bukan inisiatif administrator | OQ-09, OQ-12 |
| Review akses berkala | Membandingkan role aktif dengan penugasan; frekuensi belum ditetapkan | OPEN QUESTION |
| Pengelolaan klasifikasi | Mengikuti pemetaan ke skema resmi Kemenkeu | OQ-05 |
| Pengelolaan provider | Mengaktifkan provider hanya setelah checklist kesiapan integrasi terpenuhi | Lihat [integration-readiness-checklist.md](../08-integrations/integration-readiness-checklist.md) |
| Backup dan restore | Sesuai kebijakan produksi | OQ-07, OQ-13 |
| Rotasi rahasia | Sesuai mekanisme hosting | OQ-07 |
| Penanganan insiden | Sesuai [incident-response.md](../06-security/incident-response.md) | - |

- **PROPOSED**: Administrator sistem tidak memutuskan approval konten; `system_admin` tidak memiliki `approval:decide` pada matriks usulan.
- **PROPOSED**: Setiap tindakan administrasi tercatat di audit log.

## Related Documents

- [developer-handover.md](developer-handover.md)
- [permission-matrix.md](../06-security/permission-matrix.md)
- [authorization-rbac.md](../06-security/authorization-rbac.md)
- [knowledge-governance.md](../12-governance/knowledge-governance.md)
