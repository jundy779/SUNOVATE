# Pertanyaan Terbuka untuk Mentor

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini adalah daftar otoritatif pertanyaan terbuka SUNOVATE yang memerlukan jawaban mentor atau pihak berwenang. Dokumen lain merujuk pertanyaan dengan ID `OQ-xx` dan tidak membuat daftar tandingan. OQ-03 sampai OQ-10 berasal dari delapan pertanyaan mentor di Proposal v2.4, slide 24 (nomor slide ditulis dalam tanda kurung).

## Prioritas

- **Tinggi**: memblokir desain inti, keamanan, atau pemakaian data asli.
- **Sedang**: memengaruhi fitur P0/P1 tetapi pengembangan dapat berlanjut dengan asumsi.
- **Rendah**: dapat dijawab menjelang fase terkait.

Prioritas di bawah adalah usulan pengembang (PROPOSED).

## Daftar Pertanyaan

| ID | Pertanyaan | Mengapa penting | Dokumen terdampak | Prioritas | Status |
|---|---|---|---|---|---|
| OQ-01 | Apa fungsi, knowledge product, dan proses SUN Tematik? | Tanpa jawaban, tim ini tidak memiliki perilaku khusus dan tidak boleh diberi perilaku karangan. | [team-work-scope.md](../02-business/team-work-scope.md), [stakeholder-map.md](stakeholder-map.md) | Sedang | OPEN |
| OQ-02 | Deck Pengayaan 6 Mei 2026 menampilkan lebih banyak tim kerja Dit. SUN 2026 (antara lain Evaluasi Kualitas Kewajiban Panel Agen Penjual & Konsultan Hukum SUN Valas, Monev Transaksi dan Kewajiban Pihak Ketiga, Respon Cepat dan Penugasan Tertentu, Sistem Informasi Pengelolaan Transaksi SUN, DHE, Riset Pasar Keuangan & SUN) dan nama yang sedikit berbeda (mis. "Analis Pasar Keuangan dan Pasar SUN"). Apakah scope SUNOVATE tetap enam tim, dan nama resmi mana yang dipakai? | Menentukan seed tim, team scope, dashboard, dan konteks otorisasi Hermes. | [team-work-scope.md](../02-business/team-work-scope.md), [glossary.md](glossary.md), [assumptions.md](assumptions.md) | Tinggi | OPEN |
| OQ-03 | Tim kerja dan proses mana yang menjadi pilot pertama? (#1) | Menentukan data simulasi prioritas, skenario UAT, dan baseline adopsi. | [mvp-scope.md](../01-product/mvp-scope.md), [uat-plan.md](../10-testing/uat-plan.md) | Tinggi | OPEN |
| OQ-04 | Dokumen apa yang boleh masuk repository dan RAG? (#2) | Menentukan batas ingestion dan konten yang dapat diproses Hermes. | [ingestion-pipeline.md](../05-ai-rag/ingestion-pipeline.md), [document-lifecycle.md](../02-business/document-lifecycle.md) | Tinggi | OPEN |
| OQ-05 | Bagaimana klasifikasi dan hak akses setiap jenis dokumen, dan bagaimana pemetaannya ke skema klasifikasi resmi Kemenkeu? (#3) | Dasar kontrol akses dan plafon klasifikasi Hermes. | [document-classification.md](../04-data/document-classification.md), [data-classification.md](../06-security/data-classification.md) | Tinggi | OPEN |
| OQ-06 | Apakah SharePoint menjadi sumber utama file atau hanya referensi? (#4) | Menentukan desain document provider dan sinkronisasi. | [sharepoint-proposal.md](../08-integrations/sharepoint-proposal.md), [provider-abstraction.md](../03-architecture/provider-abstraction.md) | Sedang | OPEN |
| OQ-07 | Mekanisme login dan hosting apa yang disetujui? (#5) | Menggantikan dev auth dan menentukan arsitektur deployment. | [authentication.md](../06-security/authentication.md), [deployment-architecture.md](../03-architecture/deployment-architecture.md) | Tinggi | OPEN |
| OQ-08 | Apakah Telegram dan WhatsApp diizinkan untuk penggunaan internal? (#6) | Menentukan apakah fondasi kanal P2 dilanjutkan. | [telegram-proposal.md](../08-integrations/telegram-proposal.md), [whatsapp-proposal.md](../08-integrations/whatsapp-proposal.md) | Rendah | OPEN |
| OQ-09 | Siapa knowledge owner dan reviewer pada masing-masing tim? (#7) | Dibutuhkan untuk alur review, publikasi, dan UAT. | [document-ownership.md](../12-governance/document-ownership.md), [review-and-approval.md](../12-governance/review-and-approval.md) | Sedang | OPEN |
| OQ-10 | Format laporan dan indikator dashboard apa yang benar-benar dibutuhkan? (#8) | Menentukan isi dashboard dan fitur reporting P1. | [dashboard-requirements.md](../09-ui-ux/dashboard-requirements.md), [prd.md](../01-product/prd.md) | Sedang | OPEN |
| OQ-11 | Model AI/LLM dan embedding apa yang diizinkan, di mana lokasi pemrosesannya, dan apakah data boleh keluar dari jaringan instansi? | Memblokir pencarian semantik dan Hermes generatif. | [rag-architecture.md](../05-ai-rag/rag-architecture.md), [technology-stack.md](../03-architecture/technology-stack.md) | Tinggi | OPEN |
| OQ-12 | Bagaimana alur persetujuan publikasi knowledge dan siapa berwenang memutuskan? | Alur saat ini hanya usulan; termasuk apakah team_lead boleh mempublikasikan. | [review-and-approval.md](../12-governance/review-and-approval.md), [permission-matrix.md](../06-security/permission-matrix.md) | Sedang | OPEN |
| OQ-13 | Bagaimana kebijakan retensi dan penghapusan dokumen, audit log, dan percakapan AI? | Menentukan desain soft delete, arsip, dan pembersihan data. | [data-retention.md](../04-data/data-retention.md), [audit-logging.md](../06-security/audit-logging.md) | Sedang | OPEN |
| OQ-14 | Bagaimana kebijakan berbagi lintas tim (`sharing_scope`) untuk konten INTERNAL? | Memengaruhi hasil pencarian dan retrieval Hermes lintas tim. | [authorization-rbac.md](../06-security/authorization-rbac.md), [business-rules.md](../02-business/business-rules.md) | Sedang | OPEN |
| OQ-15 | Berapa ambang "jatuh tempo dekat" dan definisi status output/tugas yang dipakai tim? | Status tenggat dashboard saat ini memakai asumsi 7 hari. | [work-monitoring-flow.md](../02-business/work-monitoring-flow.md) | Rendah | OPEN |
| OQ-16 | Template document automation apa yang disetujui dan siapa pemiliknya? | Prasyarat fitur document automation P1. | [functional-requirements.md](../01-product/functional-requirements.md), [document-ownership.md](../12-governance/document-ownership.md) | Sedang | OPEN |
| OQ-17 | Bagaimana status penggunaan "PMK 128 tahun 2019" dibanding PMK 128/PMK.08/2012 pada kompilasi regulasi? | Menghindari relasi antarperaturan yang keliru di repository regulasi. | [sun-domain-overview.md](../02-business/sun-domain-overview.md) | Rendah | OPEN |
| OQ-18 | Apakah file sumber (PDF/PPTX) boleh disimpan di repository Git? | Saat ini dikecualikan lewat `.gitignore` (ADR-014). | [simulated-data-policy.md](../04-data/simulated-data-policy.md) | Rendah | OPEN |
| OQ-19 | Bagaimana hubungan dengan SUN Job Monitor; pola apa yang boleh dipakai ulang, jika ada? | Mencegah duplikasi fungsi dan kebingungan pengguna. | [scope-and-boundaries.md](scope-and-boundaries.md) | Rendah | OPEN |
| OQ-20 | Lingkungan uji (UAT) dan pengguna uji mana yang ditunjuk? | Prasyarat UAT bulan 6. | [uat-plan.md](../10-testing/uat-plan.md), [deployment-runbook.md](../11-operations/deployment-runbook.md) | Sedang | OPEN |

## Urutan Pembahasan yang Disarankan

**PROPOSED** Bahas pertanyaan prioritas Tinggi terlebih dahulu pada sesi mentor berikutnya: OQ-02, OQ-03, OQ-04, OQ-05, OQ-07, OQ-11. Agenda dan skrip demo: [mentor-session-01-agenda.md](mentor-session-01-agenda.md). Pertanyaan ini memengaruhi pekerjaan bulan 2 dan 3 pada [product-roadmap.md](../01-product/product-roadmap.md).

## Cara Mencatat Jawaban

1. Catat jawaban, tanggal, dan sumber jawaban (mis. sesi mentor atau dokumen arahan) di [decision-log.md](../12-governance/decision-log.md) dengan merujuk ID pertanyaan.
2. Ubah kolom Status di tabel ini menjadi `ANSWERED` dan tambahkan rujukan entri decision log. Jangan menghapus baris.
3. Perbarui dokumen terdampak: ubah label pernyataan terkait dari OPEN QUESTION atau PROPOSED menjadi CONFIRMED dengan sumber.
4. Bila jawaban mengubah scope, ikuti [change-management.md](../12-governance/change-management.md).
5. Bila jawaban memunculkan pertanyaan baru, tambahkan baris dengan ID berikutnya (OQ-21 dan seterusnya).

Jawaban yang hanya disampaikan lisan tetap dicatat dengan keterangan "arahan lisan" dan tanggal sesi, tanpa nama orang.

## Related Documents

- [assumptions.md](assumptions.md)
- [risk-register.md](../12-governance/risk-register.md)
- [decision-log.md](../12-governance/decision-log.md)

## Last Updated

2026-10-01
