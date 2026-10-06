# Pertanyaan Terbuka untuk Mentor

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-02

## Purpose

Dokumen ini adalah daftar otoritatif pertanyaan terbuka SUNOVATE yang memerlukan jawaban mentor atau pihak berwenang. Dokumen lain merujuk pertanyaan dengan ID `OQ-xx` dan tidak membuat daftar tandingan. OQ-03 sampai OQ-10 berasal dari delapan pertanyaan di Proposal v2.4, slide 24 (nomor slide ditulis dalam tanda kurung). Pada deck versi tetap `v1_`, judul slide 24 berubah dari "konfirmasi mentor" menjadi "konfirmasi knowledge owner" dan delapan pertanyaan tersebut sudah diberi jawaban (lihat bagian "Asal Jawaban dan Status Pengakuan").

## Prioritas

- **Tinggi**: memblokir desain inti, keamanan, atau pemakaian data asli.
- **Sedang**: memengaruhi fitur P0/P1 tetapi pengembangan dapat berlanjut dengan asumsi.
- **Rendah**: dapat dijawab menjelang fase terkait.

Prioritas di bawah adalah usulan pengembang (PROPOSED).

## Arti Status

| Status | Arti |
|---|---|
| OPEN | Belum ada jawaban. |
| PARTIAL | Ada jawaban knowledge owner, tetapi sebagian pertanyaan belum terjawab atau jawabannya perlu klarifikasi. |
| ANSWERED (knowledge owner) | Ada jawaban knowledge owner (deck `v1_` slide 24) yang menjawab pertanyaan sebagaimana diajukan. Pengakuan mentor masih tertunda (OQ-24). |

Status `ANSWERED` tanpa keterangan hanya dipakai setelah pengakuan mentor tercatat di [decision-log.md](../12-governance/decision-log.md).

## Daftar Pertanyaan

| ID | Pertanyaan | Mengapa penting | Dokumen terdampak | Prioritas | Status |
|---|---|---|---|---|---|
| OQ-01 | Apa fungsi, knowledge product, dan proses SUN Tematik? | Tanpa jawaban, tim ini tidak memiliki perilaku khusus dan tidak boleh diberi perilaku karangan. | [team-work-scope.md](../02-business/team-work-scope.md), [stakeholder-map.md](stakeholder-map.md) | Sedang | OPEN |
| OQ-02 | Deck Pengayaan 6 Mei 2026 menampilkan lebih banyak tim kerja Dit. SUN 2026 (antara lain Evaluasi Kualitas Kewajiban Panel Agen Penjual & Konsultan Hukum SUN Valas, Monev Transaksi dan Kewajiban Pihak Ketiga, Respon Cepat dan Penugasan Tertentu, Sistem Informasi Pengelolaan Transaksi SUN, DHE, Riset Pasar Keuangan & SUN) dan nama yang sedikit berbeda (mis. "Analis Pasar Keuangan dan Pasar SUN"). Apakah scope SUNOVATE tetap enam tim, dan nama resmi mana yang dipakai? | Menentukan seed tim, team scope, dashboard, dan konteks otorisasi Hermes. | [team-work-scope.md](../02-business/team-work-scope.md), [glossary.md](glossary.md), [assumptions.md](assumptions.md) | Tinggi | PARTIAL (jawaban pilot "6 tim" konsisten dengan enam tim; nama resmi dan tim tambahan masih terbuka); DEC-20261002-01 |
| OQ-03 | Tim kerja dan proses mana yang menjadi pilot pertama? (#1) | Menentukan data simulasi prioritas, skenario UAT, dan baseline adopsi. | [mvp-scope.md](../01-product/mvp-scope.md), [uat-plan.md](../10-testing/uat-plan.md) | Tinggi | ANSWERED (knowledge owner): pilot "6 tim"; bagian "proses" belum dijawab; DEC-20261002-01 |
| OQ-04 | Dokumen apa yang boleh masuk repository dan RAG? (#2) | Menentukan batas ingestion dan konten yang dapat diproses Hermes. | [ingestion-pipeline.md](../05-ai-rag/ingestion-pipeline.md), [document-lifecycle.md](../02-business/document-lifecycle.md) | Tinggi | PARTIAL (knowledge owner): cakupan "semua dokumen yang diusulkan tim kerja"; dokumen asli tetap butuh klasifikasi (OQ-05) dan persetujuan eksplisit; DEC-20261002-02 |
| OQ-05 | Bagaimana klasifikasi dan hak akses setiap jenis dokumen, dan bagaimana pemetaannya ke skema klasifikasi resmi Kemenkeu? (#3) | Dasar kontrol akses dan plafon klasifikasi Hermes. | [document-classification.md](../04-data/document-classification.md), [data-classification.md](../06-security/data-classification.md) | Tinggi | PARTIAL (knowledge owner): hanya menjawab siapa yang boleh mengubah/mengunggah data; skema klasifikasi dan pemetaan resmi masih terbuka; DEC-20261002-03 |
| OQ-06 | Apakah SharePoint menjadi sumber utama file atau hanya referensi? (#4) | Menentukan desain document provider dan sinkronisasi. | [sharepoint-proposal.md](../08-integrations/sharepoint-proposal.md), [provider-abstraction.md](../03-architecture/provider-abstraction.md) | Sedang | PARTIAL (knowledge owner): jawaban "Sandbox server" perlu klarifikasi (OQ-22); DEC-20261002-04 |
| OQ-07 | Mekanisme login dan hosting apa yang disetujui? (#5) | Menggantikan dev auth dan menentukan arsitektur deployment. | [authentication.md](../06-security/authentication.md), [deployment-architecture.md](../03-architecture/deployment-architecture.md) | Tinggi | PARTIAL (knowledge owner): hosting dijawab (komputer tersendiri sebagai server); mekanisme login belum dijawab; kebutuhan server di OQ-23; DEC-20261002-05 |
| OQ-08 | Apakah Telegram dan WhatsApp diizinkan untuk penggunaan internal? (#6) | Menentukan apakah fondasi kanal P2 dilanjutkan. | [telegram-proposal.md](../08-integrations/telegram-proposal.md), [whatsapp-proposal.md](../08-integrations/whatsapp-proposal.md) | Rendah | ANSWERED (knowledge owner): "bisa"; tetap P2 dan butuh kajian keamanan; DEC-20261002-06 |
| OQ-09 | Siapa knowledge owner dan reviewer pada masing-masing tim? (#7) | Dibutuhkan untuk alur review, publikasi, dan UAT. | [document-ownership.md](../12-governance/document-ownership.md), [review-and-approval.md](../12-governance/review-and-approval.md) | Sedang | ANSWERED (knowledge owner): ketua tim dan PIC yang ditunjuk pada setiap tim; penunjukan orang dan pemetaan ke role sistem belum ada (OQ-25); DEC-20261002-07 |
| OQ-10 | Format laporan dan indikator dashboard apa yang benar-benar dibutuhkan? (#8) | Menentukan isi dashboard dan fitur reporting P1. | [dashboard-requirements.md](../09-ui-ux/dashboard-requirements.md), [prd.md](../01-product/prd.md) | Sedang | PARTIAL (knowledge owner): indikator "yield" dan "kepemilikan SBN"; format laporan, sumber data, dan definisi belum ada (OQ-21); DEC-20261002-08 |
| OQ-11 | Model AI/LLM dan embedding apa yang diizinkan, di mana lokasi pemrosesannya, dan apakah data boleh keluar dari jaringan instansi? | Memblokir pencarian semantik dan Hermes generatif. | [rag-architecture.md](../05-ai-rag/rag-architecture.md), [technology-stack.md](../03-architecture/technology-stack.md) | Tinggi | OPEN |
| OQ-12 | Bagaimana alur persetujuan publikasi knowledge dan siapa berwenang memutuskan? | Alur saat ini hanya usulan; termasuk apakah team_lead boleh mempublikasikan. | [review-and-approval.md](../12-governance/review-and-approval.md), [permission-matrix.md](../06-security/permission-matrix.md) | Sedang | OPEN (jawaban OQ-05 dan OQ-09 menyebut peran terkait, tetapi tidak menjawab siapa memutuskan publikasi) |
| OQ-13 | Bagaimana kebijakan retensi dan penghapusan dokumen, audit log, dan percakapan AI? | Menentukan desain soft delete, arsip, dan pembersihan data. | [data-retention.md](../04-data/data-retention.md), [audit-logging.md](../06-security/audit-logging.md) | Sedang | OPEN |
| OQ-14 | Bagaimana kebijakan berbagi lintas tim (`sharing_scope`) untuk konten INTERNAL? | Memengaruhi hasil pencarian dan retrieval Hermes lintas tim. | [authorization-rbac.md](../06-security/authorization-rbac.md), [business-rules.md](../02-business/business-rules.md) | Sedang | OPEN |
| OQ-15 | Berapa ambang "jatuh tempo dekat" dan definisi status output/tugas yang dipakai tim? | Status tenggat dashboard saat ini memakai asumsi 7 hari. | [work-monitoring-flow.md](../02-business/work-monitoring-flow.md) | Rendah | OPEN |
| OQ-16 | Template document automation apa yang disetujui dan siapa pemiliknya? | Prasyarat fitur document automation P1. | [functional-requirements.md](../01-product/functional-requirements.md), [document-ownership.md](../12-governance/document-ownership.md) | Sedang | OPEN |
| OQ-17 | Bagaimana status penggunaan "PMK 128 tahun 2019" dibanding PMK 128/PMK.08/2012 pada kompilasi regulasi? | Menghindari relasi antarperaturan yang keliru di repository regulasi. | [sun-domain-overview.md](../02-business/sun-domain-overview.md) | Rendah | OPEN |
| OQ-18 | Apakah file sumber (PDF/PPTX) boleh disimpan di repository Git? | Saat ini dikecualikan lewat `.gitignore` (ADR-014). | [simulated-data-policy.md](../04-data/simulated-data-policy.md) | Rendah | OPEN |
| OQ-19 | Bagaimana hubungan dengan SUN Job Monitor; pola apa yang boleh dipakai ulang, jika ada? | Mencegah duplikasi fungsi dan kebingungan pengguna. | [scope-and-boundaries.md](scope-and-boundaries.md) | Rendah | OPEN |
| OQ-20 | Lingkungan uji (UAT) dan pengguna uji mana yang ditunjuk? | Prasyarat UAT bulan 6. | [uat-plan.md](../10-testing/uat-plan.md), [deployment-runbook.md](../11-operations/deployment-runbook.md) | Sedang | OPEN |
| OQ-21 | Apa sumber data otoritatif dan definisi untuk indikator "yield" dan "kepemilikan SBN" yang diminta, siapa yang boleh melihatnya, dan apakah indikator ini keluar dari batas SUNOVATE sebagai bukan sistem transaksi (ADR-013)? | Tanpa sumber dan definisi, tidak ada angka yang boleh ditampilkan; SUNOVATE tidak menyimpan data transaksi, yield, atau lelang. | [dashboard-requirements.md](../09-ui-ux/dashboard-requirements.md), [market-data-proposal.md](../08-integrations/market-data-proposal.md), [sun-domain-overview.md](../02-business/sun-domain-overview.md) | Sedang | OPEN |
| OQ-22 | Apa yang dimaksud "Sandbox server" pada jawaban OQ-06: apakah itu lokasi file sumber untuk pilot, dan apakah SharePoint dipakai sama sekali pada pilot? | Menentukan jenis document provider untuk pilot dan apakah integrasi SharePoint tetap relevan. | [sharepoint-proposal.md](../08-integrations/sharepoint-proposal.md), [provider-abstraction.md](../03-architecture/provider-abstraction.md) | Sedang | OPEN |
| OQ-23 | Apa persyaratan server khusus ("komputer tersendiri sebagai server"): lokasi dan akses jaringan, sistem operasi, backup, siapa yang mengadministrasi, siapa yang boleh mengaksesnya, TLS, dan mekanisme login yang dipakai di server tersebut (lanjutan OQ-07)? | Menentukan rencana deployment, backup, keamanan, dan kesiapan UAT. | [deployment-architecture.md](../03-architecture/deployment-architecture.md), [deployment-runbook.md](../11-operations/deployment-runbook.md), [backup-and-restore.md](../11-operations/backup-and-restore.md) | Tinggi | OPEN |
| OQ-24 | Apakah mentor mengakui (acknowledge) jawaban knowledge owner pada deck `v1_` slide 24 sebagai arahan resmi proyek? | Jawaban saat ini berstatus `CONFIRMED (knowledge owner)` dan belum diakui mentor; pekerjaan yang bergantung padanya berisiko berubah. | [decision-log.md](../12-governance/decision-log.md), [mentor-session-01-agenda.md](mentor-session-01-agenda.md) | Tinggi | OPEN |
| OQ-25 | Role sistem mana yang sesuai dengan "ketua tim", "kasubdit PMP", "Kasi MP", dan "PIC yang ditunjuk" untuk hak mengubah/mengunggah data; apa kepanjangan "PMP"; dan apakah staf biasa tetap boleh menyusun draf knowledge tanpa hak unggah? | Matriks izin saat ini masih memberi `staff` hak membuat dan mengubah knowledge dan dokumen. | [permission-matrix.md](../06-security/permission-matrix.md), [authorization-rbac.md](../06-security/authorization-rbac.md), [document-ownership.md](../12-governance/document-ownership.md) | Tinggi | OPEN |

## Asal Jawaban dan Status Pengakuan

**CONFIRMED (knowledge owner, deck v1_ slide 24)** Pengguna mengonfirmasi bahwa `v1_SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx` adalah versi tetap (fixed) dari deck proposal. Pada versi tersebut slide 24 berjudul "Keputusan yang memerlukan konfirmasi knowledge owner" dan setiap pertanyaan diikuti jawaban singkat. Jawaban adalah jawaban knowledge owner, bukan jawaban mentor.

**OPEN QUESTION** Pengakuan (acknowledgement) mentor atas jawaban tersebut belum ada (OQ-24). Sampai pengakuan tercatat, jawaban diperlakukan sebagai `CONFIRMED (knowledge owner, deck v1_ slide 24)`, bukan keputusan final proyek.

Pemisahan yang dipakai di seluruh dokumentasi:

- **CONFIRMED (knowledge owner)**: isi jawaban sebagaimana tertulis di deck, dikutip ringan dengan ejaan dinormalisasi.
- **PROPOSED**: tafsiran, pemetaan role, dan konsekuensi yang disusun pengembang.
- **OPEN QUESTION**: bagian pertanyaan yang tidak terjawab atau ambigu.

### Jawaban pada deck v1_ slide 24

| OQ | Pertanyaan di deck | Jawaban (CONFIRMED, knowledge owner) | Tafsiran dan celah (PROPOSED / OPEN QUESTION) |
|---|---|---|---|
| OQ-03 | Tim kerja dan proses mana yang menjadi pilot pertama? | "6 tim" | PROPOSED: enam tim pada brief sesi (PPSUN, AKPSUN, PSUN, PPPSUN, DHTV, SUN Tematik). Deck tidak menyebut nama tim. Proses pilot tidak dijawab. |
| OQ-04 | Dokumen apa yang boleh masuk repository dan RAG? | "Semua dokumen yang diusulkan tim kerja" | Cakupan ditentukan usulan tim. Tidak menyebut pengecualian, klasifikasi, atau persetujuan. Aturan AGENTS.md tetap berlaku: data asli butuh persetujuan eksplisit, CONFIDENTIAL tidak diproses Hermes. |
| OQ-05 | Bagaimana klasifikasi serta hak akses setiap jenis dokumen? | Yang dapat mengubah data atau mengunggah: ketua tim, kasubdit PMP, Kasi MP, dan PIC yang ditunjuk | Menjawab siapa yang boleh mengubah atau mengunggah. Tidak mendefinisikan skema klasifikasi atau hak baca. Pemetaan ke role sistem adalah PROPOSED (lihat [permission-matrix.md](../06-security/permission-matrix.md)). |
| OQ-06 | Apakah SharePoint sumber utama atau hanya referensi? | "Sandbox server" | Ambigu. Tampaknya sumber file untuk pilot adalah sebuah sandbox server; tidak jelas apakah SharePoint dipakai (OQ-22). |
| OQ-07 | Mekanisme login dan hosting apa yang disetujui? | "Pakai computer tersendiri sebagai server" | Hosting dijawab: komputer khusus sebagai server. Mekanisme login tidak dijawab. Persyaratan server belum ada (OQ-23). |
| OQ-08 | Apakah Telegram dan WhatsApp diizinkan untuk penggunaan internal? | "bisa" | Diizinkan untuk penggunaan internal menurut jawaban. Tetap P2; tanpa akun, token, atau persetujuan penyedia. Konten RESTRICTED ke atas tidak dikirim ke kanal eksternal secara default (PROPOSED). |
| OQ-09 | Siapa knowledge owner dan reviewer per tim? | "Masing-masing ketua tim dan PIC yang ditunjuk" | Peran dijawab. Orangnya tidak disebut dan tidak dicatat. Pemetaan ke role sistem adalah PROPOSED (OQ-25). |
| OQ-10 | Format laporan dan indikator dashboard apa yang dibutuhkan? | "Yield, kepemilikan SBN" | Dua indikator diminta. Tanpa sumber data, definisi, atau format laporan (OQ-21). Tidak ada angka yang boleh dibuat. |

Deck `v1_` juga mengubah slide 9 (kelompok pengguna "Ketua tim kerja" dan "Pengelola Knowledge / PIC") dan slide 18 ("Pengelola MP / Product Owner / Ketua Tim" dan "Knowledge Coordinator / PMP"). Lihat [stakeholder-map.md](stakeholder-map.md).

## Urutan Pembahasan yang Disarankan

**PROPOSED** Sesi mentor berikutnya dijadikan sesi konfirmasi: minta mentor mengakui jawaban knowledge owner (OQ-24), lalu bahas pertanyaan prioritas Tinggi yang masih terbuka: OQ-02 (nama resmi dan tim tambahan), OQ-05 (skema klasifikasi), OQ-07 (mekanisme login), OQ-11 (model AI dan lokasi data), OQ-23 (persyaratan server), dan OQ-25 (pemetaan peran). Agenda dan skrip demo: [mentor-session-01-agenda.md](mentor-session-01-agenda.md). Pertanyaan ini memengaruhi pekerjaan bulan 2 dan 3 pada [product-roadmap.md](../01-product/product-roadmap.md).

## Cara Mencatat Jawaban

1. Catat jawaban, tanggal, dan sumber jawaban (mis. sesi mentor, dokumen arahan, atau deck versi tetap) di [decision-log.md](../12-governance/decision-log.md) dengan merujuk ID pertanyaan.
2. Ubah kolom Status di tabel ini sesuai tabel "Arti Status" dan tambahkan rujukan entri decision log. Jangan menghapus baris.
3. Perbarui dokumen terdampak: ubah label pernyataan terkait dari OPEN QUESTION atau PROPOSED menjadi CONFIRMED dengan sumber. Jawaban knowledge owner diberi label `CONFIRMED (knowledge owner, deck v1_ slide 24)`.
4. Bila jawaban mengubah scope, ikuti [change-management.md](../12-governance/change-management.md).
5. Bila jawaban memunculkan pertanyaan baru, tambahkan baris dengan ID berikutnya (OQ-26 dan seterusnya).

Jawaban yang hanya disampaikan lisan tetap dicatat dengan keterangan "arahan lisan" dan tanggal sesi, tanpa nama orang.

## Related Documents

- [assumptions.md](assumptions.md)
- [risk-register.md](../12-governance/risk-register.md)
- [decision-log.md](../12-governance/decision-log.md)
- [mentor-session-01-agenda.md](mentor-session-01-agenda.md)

## Last Updated

2026-10-02
