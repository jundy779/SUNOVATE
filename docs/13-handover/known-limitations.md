# Keterbatasan yang Diketahui

**Status:** DRAFT

**Last Updated:** 2026-10-02

## Purpose

Daftar jujur keterbatasan scaffold SUNOVATE per 2026-10-02, agar tidak ada fitur yang disangka sudah tersedia.

## Ringkasan

- **CONFIRMED**: SUNOVATE belum siap produksi. Scaffold ini adalah fondasi pengembangan dengan data `SIMULATED_DATA` (sumber: implementasi scaffold sesi 2026-10-01).

## Daftar Keterbatasan

| ID | Area | Keterbatasan | Dampak | Rujukan |
|---|---|---|---|---|
| KL-01 | Data | Default runtime tetap store simulasi in-memory (`DATA_BACKEND=simulated`); pada mode ini data yang dibuat lewat API hilang saat API di-restart. Persistence hanya tersedia bila `DATA_BACKEND=postgres` dengan database yang sudah di-migrate dan di-seed | Mode default tidak persisten | ADR-007, ADR-015, R-10 |
| KL-02 | Data | Backend `postgres` (repository SQLAlchemy sinkron + psycopg 3) sudah diimplementasikan dan seluruh suite lulus padanya lewat `pnpm db:test`, tetapi hanya diuji pada PostgreSQL sementara (pgserver) di satu mesin Windows dengan `SIMULATED_DATA`; belum diuji pada Docker Compose, beban multi-pengguna, atau lingkungan hosting. FTS dan pgvector belum dipakai runtime | Perilaku pada skala dan lingkungan lain belum terbukti | ADR-015 |
| KL-03 | Identitas | Hanya login pengembangan (token HMAC untuk pengguna simulasi); tidak ada SSO organisasi | Tidak dapat dipakai pengguna nyata | ADR-005, OQ-07 |
| KL-04 | Pencarian | Retrieval hanya leksikal; tidak ada retrieval semantik | Kualitas pencarian terbatas pada kecocokan kata | ADR-008 |
| KL-05 | AI | Provider AI pengembangan deterministik dan ekstraktif; tidak ada model bahasa | Jawaban Hermes berupa kutipan tersusun, bukan sintesis | ADR-008, OQ-11 |
| KL-06 | AI | Embedding provider nonaktif; kolom vektor tanpa tipe dimensi dan tanpa indeks ANN | Tidak ada embedding | ADR-009, OQ-11 |
| KL-07 | Dokumen | Belum ada unggah dokumen, ekstraksi teks, atau pipeline ingestion; dokumen hanya referensi dan versi dari dataset simulasi | Konten baru tidak dapat diolah otomatis | OQ-04, OQ-06 |
| KL-08 | Dokumen | Document automation berbasis template belum diimplementasikan | Tujuan (7) brief belum terpenuhi | OQ-16 |
| KL-09 | Notifikasi | Tabel `notifications` ada, tetapi pengiriman notifikasi belum ada; `NOTIFICATION_PROVIDER=disabled` | Pengguna tidak menerima pemberitahuan | Prioritas P1 |
| KL-10 | Integrasi | Tidak ada integrasi SharePoint, Power BI, Telegram, WhatsApp, Kemenkeu Satu, atau data pasar; provider produksi hanya placeholder nonaktif | Tidak ada pertukaran data dengan sistem lain | Prioritas P2, OQ-06, OQ-08 |
| KL-11 | Approval | Keputusan approval tercatat, tetapi eksekusi aksi setelah disetujui (mis. aksi tulis dari Hermes) belum diimplementasikan | Approval belum memicu perubahan | OQ-12 |
| KL-12 | Hermes | ScopeGuard dan filter prompt injection berbasis aturan | Variasi bahasa baru dapat lolos atau tertolak keliru | R-07 |
| KL-13 | Infrastruktur | Docker tidak terpasang di mesin pengembangan saat ini; jalur Docker Compose belum divalidasi di mesin tersebut. Migration divalidasi lewat `pgserver` | Jalur Docker perlu diuji di mesin lain | ADR-003 |
| KL-14 | UI | shadcn/ui tidak dipasang karena belum ada kebutuhan konkret | Komponen UI dibangun manual | AGENTS.md |
| KL-15 | Aksesibilitas | Belum ada audit aksesibilitas; validasi penuh memerlukan pengujian manual dengan teknologi asistif dan review ahli | Kepatuhan aksesibilitas belum diketahui | [accessibility.md](../09-ui-ux/accessibility.md) |
| KL-16 | Kebijakan | Klasifikasi data, matriks permission, role, dan aturan berbagi lintas tim masih usulan | Hak akses dapat berubah setelah validasi | OQ-05, OQ-14 |
| KL-17 | Domain | Fungsi SUN Tematik belum dikonfirmasi; daftar tim kerja dapat berbeda dari bagan organisasi | Cakupan tim dapat berubah | OQ-01, OQ-02 |
| KL-18 | Domain | Data bisnis SUN (instrumen, lelang, transaksi, yield, settlement) tidak dimodelkan | Tidak ada fitur SUN Business | ADR-013 |
| KL-19 | Operasional | Belum ada hosting, backup produksi, metrik, tracing, atau alerting | Tidak ada operasi produksi | OQ-07, OQ-13 |
| KL-20 | Pengujian | Pengujian keamanan dan RAG berjalan terhadap data simulasi (store in-memory pada `pnpm test`, PostgreSQL sementara pada `pnpm db:test`) dan provider deterministik | Hasil belum mewakili kondisi produksi | [rag-testing.md](../10-testing/rag-testing.md) |
| KL-21 | Audit | Trigger `audit_logs_append_only` menolak UPDATE/DELETE per baris, tetapi tidak mencegah `TRUNCATE`. Reset test `pnpm db:test` memakai `TRUNCATE` dengan sengaja, hanya pada database pgserver sementara dan hanya bila `APP_ENV=test` dan `SUNOVATE_DB_RESET_ALLOWED=1` | Pengguna database dengan hak TRUNCATE dapat menghapus audit; penutupan celah OUT OF SCOPE | ADR-010, ADR-015 |
| KL-22 | Data | Pada mode postgres, audit penolakan (`audit_denial`) ditulis lewat koneksi kedua dari pool yang sama. Bila database mati, permintaan yang seharusnya 403 menjadi 503 `DATABASE_UNAVAILABLE`; bila pool habis, permintaan menunggu sampai 10 detik lalu 503 | Risiko diterima pada skala `SIMULATED_DATA`; mitigasi (engine terpisah) ada di backlog | ADR-015 |
| KL-23 | Hermes | Pada mode postgres, koneksi request Hermes berstatus idle in transaction (tanpa row lock) selama generasi jawaban, karena fase baca dan fase tulis dipisah tetapi query baca melakukan autobegin | Diterima karena generasi saat ini lokal dan cepat; perlu ditinjau sebelum provider AI remote | ADR-015 |
| KL-24 | Konfigurasi | `sunovate_api/main.py` membuat app saat diimpor. `.env` dengan `DATA_BACKEND=postgres` dan skema `DATABASE_URL` yang tidak diizinkan membuat impor `sunovate_api.main` gagal (`ValueError` tanpa URL), termasuk koleksi `pnpm test` | Pengembang harus memperbaiki `.env`; validasi lazy ada di backlog | ADR-015, [local-development.md](../11-operations/local-development.md) |

Hasil validasi terbaru (lint, typecheck, test, build): lihat laporan validasi terbaru di CHANGELOG.md.

## Hal yang Bukan Keterbatasan Tetapi Batas Desain

- **CONFIRMED**: SUNOVATE tidak menggantikan sistem transaksi SUN resmi, tidak mengambil keputusan keuangan, dan tidak memberikan akses dokumen tanpa otorisasi (sumber: brief sesi 2026-10-01).
- **CONFIRMED**: Hermes tidak mengakses database secara langsung (sumber: ADR-004).
- **CONFIRMED**: File tidak disimpan sebagai BLOB di database (sumber: ADR-003).
- **OUT OF SCOPE**: Turborepo, Kubernetes, microservices, Redis, dan message broker (sumber: brief sesi 2026-10-01).

## Related Documents

- [future-development.md](future-development.md)
- [risk-register.md](../12-governance/risk-register.md)
- [open-questions.md](../00-project/open-questions.md)
- [mvp-scope.md](../01-product/mvp-scope.md)
