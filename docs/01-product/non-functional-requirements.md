# Kebutuhan Non-Fungsional

**Status:** PROPOSED
**Last Updated:** 2026-10-02

## Purpose

Dokumen ini mendefinisikan kebutuhan non-fungsional SUNOVATE dengan ID `NFR-xx`. Target angka adalah usulan untuk lingkungan pengembangan dan harus dikalibrasi dengan baseline sebelum menjadi komitmen. Kebutuhan yang bergantung pada keputusan instansi ditandai OPEN QUESTION.

## Keamanan

| ID | Kebutuhan | Label |
|---|---|---|
| NFR-01 | Otorisasi ditegakkan di API untuk setiap endpoint terproteksi: permission, team scope, dan klasifikasi; deny by default. Penyembunyian menu di frontend bukan kontrol keamanan. | CONFIRMED prinsip (sumber: brief sesi 2026-10-01, ADR-006) |
| NFR-02 | Hermes tidak memiliki akses atau kredensial database; hanya menerima konteks terotorisasi dari HermesGateway. | CONFIRMED (sumber: brief sesi 2026-10-01, ADR-004) |
| NFR-03 | Token pengembangan tidak dapat dipakai di produksi; aplikasi menolak start bila `APP_ENV=production` dan dev auth aktif. | PROPOSED (ADR-005) |
| NFR-04 | Secret (mis. `DEV_AUTH_SECRET`, `POSTGRES_PASSWORD`) hanya dari environment, tidak di-commit, dan tidak ditulis ke log. | PROPOSED |
| NFR-05 | Token sesi web disimpan di cookie httpOnly; panggilan API dari server component. | PROPOSED |
| NFR-06 | Skenario uji wajib: akses tanpa izin, jailbreak, prompt injection, sitasi keliru, duplikasi ingestion, konflik pembaruan. | PROPOSED (sumber: Proposal v2.4, slide 20) |
| NFR-07 | Integrasi produksi tetap nonaktif sampai divalidasi. | PROPOSED |

## Privasi dan Data

| ID | Kebutuhan | Label |
|---|---|---|
| NFR-08 | Hanya `SIMULATED_DATA` selama pengembangan; setiap respons API membawa `meta.dataLabel`. | CONFIRMED aturan proyek |
| NFR-09 | Data pribadi, jumlah anggota tim, dan nomor surat tugas dari dokumen sumber tidak disalin ke sistem atau dokumentasi. | CONFIRMED aturan proyek |
| NFR-10 | Konten berklasifikasi CONFIDENTIAL tidak diproses Hermes pada pengembangan (`HERMES_MAX_CLASSIFICATION=RESTRICTED`). | PROPOSED |
| NFR-11 | Retensi dokumen, audit log, dan percakapan AI mengikuti kebijakan instansi. | OPEN QUESTION (OQ-13) |
| NFR-12 | Residensi data dan lokasi pemrosesan AI, termasuk apakah data boleh keluar dari jaringan instansi. | OPEN QUESTION (OQ-11) |

## Aksesibilitas

| ID | Kebutuhan | Label |
|---|---|---|
| NFR-13 | Target WCAG 2.2 level AA untuk seluruh halaman web. | PROPOSED |
| NFR-14 | Seluruh fungsi dapat dioperasikan dengan keyboard; fokus terlihat dengan outline 3px warna gold sesuai design token. | PROPOSED |
| NFR-15 | Status tidak hanya disampaikan melalui warna; label teks selalu menyertai indikator success dan risk. | PROPOSED |
| NFR-16 | Formulir memiliki label, pesan error yang terhubung ke field, dan bahasa yang jelas. | PROPOSED |

Pemeriksaan otomatis (lint, Testing Library, Playwright) hanya menangkap sebagian masalah. Validasi penuh kepatuhan WCAG memerlukan pengujian manual dengan teknologi asistif (mis. pembaca layar) dan tinjauan ahli aksesibilitas. Lihat [accessibility.md](../09-ui-ux/accessibility.md).

## Kinerja

**PROPOSED** Target berikut perlu baseline pada lingkungan uji yang ditunjuk (OQ-20) sebelum dipakai sebagai komitmen.

| ID | Kebutuhan | Target usulan |
|---|---|---|
| NFR-17 | Waktu respons endpoint baca (daftar dan detail) pada data simulasi. | p95 di bawah 500 ms di lingkungan lokal. |
| NFR-18 | Waktu respons pencarian teks. | p95 di bawah 1 detik di lingkungan lokal. |
| NFR-19 | Waktu respons Hermes dengan provider pengembangan. | p95 di bawah 3 detik; target untuk model generatif ditetapkan setelah OQ-11. |
| NFR-20 | Pagination wajib untuk daftar; `pageSize` 1 sampai 100, default 20. | Sudah diterapkan di API. |

## Keandalan

| ID | Kebutuhan | Label |
|---|---|---|
| NFR-21 | Pembaruan konkuren tidak saling menimpa; revision basi menghasilkan 409 `REVISION_CONFLICT`. | PROPOSED (ADR-011) |
| NFR-22 | Ingestion ganda ditolak melalui keunikan checksum. | PROPOSED |
| NFR-23 | Data bisnis memakai soft delete; audit log append-only. | PROPOSED (ADR-010) |
| NFR-24 | Endpoint `GET /health` dan `GET /health/database` tersedia untuk pemeriksaan kesehatan. | PROPOSED |
| NFR-25 | Backup dan restore database didefinisikan sebelum ada data non-simulasi. | PROPOSED (lihat [backup-and-restore.md](../11-operations/backup-and-restore.md)) |

Catatan: dengan `DATA_BACKEND=simulated`, data runtime hilang saat API restart (ADR-007, R-10).

## Observability

| ID | Kebutuhan | Label |
|---|---|---|
| NFR-26 | Log terstruktur JSON dengan `request_id`; setiap respons membawa header `X-Request-ID`. | PROPOSED |
| NFR-27 | Respons error memuat `requestId` agar dapat ditelusuri ke log. | PROPOSED |
| NFR-28 | Log tidak memuat isi dokumen, token, atau secret. | PROPOSED |

## Maintainability

| ID | Kebutuhan | Label |
|---|---|---|
| NFR-29 | Modular monolith dengan modul per domain; tanpa microservices, Redis, atau message broker. | CONFIRMED (sumber: brief sesi 2026-10-01) |
| NFR-30 | TypeScript strict, Python bertipe (mypy), lint (ESLint, Ruff) bersih sebelum serah terima. | PROPOSED |
| NFR-31 | Integrasi eksternal hanya melalui interface provider. | PROPOSED |
| NFR-32 | Dependensi baru hanya dengan kebutuhan konkret dan versi terkunci. | CONFIRMED aturan proyek |
| NFR-33 | Dokumentasi diperbarui bersama perubahan perilaku; serah terima di [developer-handover.md](../13-handover/developer-handover.md). | PROPOSED |

## Portabilitas

| ID | Kebutuhan | Label |
|---|---|---|
| NFR-34 | Pengembangan lokal dengan Docker Compose (`pgvector/pgvector:pg17`); alternatif validasi tanpa Docker tersedia melalui skrip `pgserver`. | PROPOSED |
| NFR-35 | Konfigurasi sepenuhnya melalui environment variable (lihat `.env.example`). | PROPOSED |
| NFR-36 | Target hosting produksi. | PARTIAL: komputer tersendiri sebagai server (CONFIRMED, knowledge owner, deck v1_ slide 24); persyaratan server OPEN QUESTION (OQ-07, OQ-23) |

## Antarmuka

| ID | Kebutuhan | Label |
|---|---|---|
| NFR-37 | Hanya design token SUNOVATE yang terkunci; tanpa gradien, ungu, ikon Unicode, atau grid kartu besar generik. | CONFIRMED aturan proyek |
| NFR-38 | Tampilan responsif untuk desktop dan layar lebih kecil. | PROPOSED |

## Related Documents

- [security-overview.md](../06-security/security-overview.md)
- [observability.md](../11-operations/observability.md)
- [design-system.md](../09-ui-ux/design-system.md)
- [functional-requirements.md](functional-requirements.md)

## Last Updated

2026-10-02
