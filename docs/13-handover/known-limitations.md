# Keterbatasan yang Diketahui

**Status:** DRAFT

**Last Updated:** 2026-10-02

## Purpose

Daftar jujur keterbatasan scaffold SUNOVATE per 2026-10-01, agar tidak ada fitur yang disangka sudah tersedia.

## Ringkasan

- **CONFIRMED**: SUNOVATE belum siap produksi. Scaffold ini adalah fondasi pengembangan dengan data `SIMULATED_DATA` (sumber: implementasi scaffold sesi 2026-10-01).

## Daftar Keterbatasan

| ID | Area | Keterbatasan | Dampak | Rujukan |
|---|---|---|---|---|
| KL-01 | Data | Runtime API memakai store simulasi in-memory (`DATA_BACKEND=simulated`); data yang dibuat lewat API hilang saat API di-restart | Tidak ada persistence | ADR-007, R-10 |
| KL-02 | Data | Repository berbasis SQLAlchemy belum diimplementasikan; skema, migration, dan seed PostgreSQL sudah ada tetapi tidak dibaca runtime | Perilaku endpoint terhadap database belum teruji | ADR-007 |
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
| KL-19 | Operasional | Belum ada hosting nyata, backup produksi, metrik, tracing, atau alerting (hosting pilot dijawab knowledge owner sebagai komputer tersendiri sebagai server, belum tersedia) | Tidak ada operasi produksi | OQ-07, OQ-13, OQ-23, R-13 |
| KL-20 | Pengujian | Pengujian keamanan dan RAG berjalan terhadap store simulasi dan provider deterministik | Hasil belum mewakili kondisi produksi | [rag-testing.md](../10-testing/rag-testing.md) |

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
