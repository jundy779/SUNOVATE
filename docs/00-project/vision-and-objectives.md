# Visi dan Sasaran

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini menerjemahkan delapan tujuan dari brief sesi 2026-10-01 menjadi sasaran yang dapat diukur. Tujuan berstatus CONFIRMED sebagai arahan; sasaran, indikator, dan target angka berstatus PROPOSED sampai disetujui mentor.

## Visi

**PROPOSED** SUNOVATE menjadi tempat tepercaya bagi tim kerja Dit. SUN untuk menyimpan, menemukan, dan menggunakan kembali pengetahuan institusi, dengan akses yang selalu mengikuti hak dan klasifikasi data.

## Prinsip

- **CONFIRMED** Tidak menggantikan sistem transaksi SUN resmi dan tidak mengambil keputusan keuangan (sumber: brief sesi 2026-10-01).
- **CONFIRMED** Tidak memberikan akses dokumen tanpa otorisasi (sumber: brief sesi 2026-10-01).
- **PROPOSED** Jawaban Hermes selalu bersitasi dan dapat ditelusuri ke dokumen sumber; jawaban AI bukan keputusan.
- **PROPOSED** Setiap tindakan penting tercatat di audit log.

## Pemetaan Tujuan ke Sasaran

Semua sasaran di tabel ini **PROPOSED**. Target angka adalah usulan awal untuk lingkungan pengembangan dengan data simulasi dan perlu baseline sebelum dipakai sebagai komitmen.

| No | Tujuan (CONFIRMED, brief sesi 2026-10-01) | Sasaran terukur (PROPOSED) | Indikator | Prioritas |
|---|---|---|---|---|
| T1 | Knowledge Repository web | Knowledge entry dan referensi dokumen dapat dibuat, diperbarui, diajukan, dan dipublikasikan melalui approval. | Seluruh tipe knowledge dan status lifecycle teruji di backend test. | P0 |
| T2 | AI Knowledge Assistant Hermes | Hermes menjawab hanya dari dokumen terotorisasi dan menolak di luar scope. | 100% jawaban `ANSWERED` memiliki minimal satu sitasi valid pada set evaluasi simulasi. | P0 |
| T3 | Menjaga institutional memory | Knowledge product (Close Out Note, Tacit Knowledge, Playbook, Lesson Learned) memiliki template dan pemilik. | Jumlah tipe knowledge yang memiliki template disetujui; status bergantung OQ-09 dan OQ-16. | P1 |
| T4 | Pencarian dokumen, regulasi, kajian, SOP, playbook, lesson learned, bahan rapat, arsip | Pencarian teks atas konten PUBLISHED yang dapat dibaca pengguna; pencarian semantik setelah model embedding disetujui. | Kasus uji retrieval simulasi menemukan dokumen relevan pada hasil teratas; target nilai menunggu baseline. | P0 |
| T5 | Monitoring pekerjaan dan output tim kerja | Work output, tugas, milestone, pending matter, dan follow-up dapat dipantau dengan status tenggat yang dihitung backend. | Status tenggat SAFE, DUE_SOON, DUE_TODAY, OVERDUE, COMPLETED konsisten di API dan UI. | P0 |
| T6 | Dashboard sesuai hak akses | Ringkasan dashboard hanya menghitung data yang boleh dibaca pengguna. | Tidak ada angka dashboard yang berasal dari record di luar team scope atau di atas clearance pada uji keamanan. | P0 |
| T7 | Document automation berbasis template yang disetujui | Dokumen dihasilkan dari template yang disetujui pemiliknya, dengan persetujuan manusia sebelum dipakai. | Jumlah template disetujui; bergantung OQ-16. | P1 |
| T8 | Fondasi integrasi Telegram dan WhatsApp | Abstraksi `NotificationProvider` dan `HermesClient` siap tanpa mengaktifkan kanal produksi. | Provider produksi tetap nonaktif; kanal hanya diaktifkan setelah OQ-08 dijawab. | P2 |

## Ukuran Keberhasilan

**PROPOSED** Enam ukuran keberhasilan dari Proposal v2.4, slide 23. Definisi indikator di bawah adalah usulan pengembang.

| Ukuran | Pertanyaan yang dijawab | Contoh indikator (PROPOSED) |
|---|---|---|
| Retrieval | Apakah dokumen yang relevan ditemukan? | Proporsi pertanyaan uji yang dokumen acuannya muncul di hasil teratas. |
| Citation | Apakah sitasi benar dan mendukung jawaban? | Proporsi sitasi yang menunjuk chunk terotorisasi dan relevan; target 100% valid secara struktural. |
| Access control | Apakah pengguna hanya melihat yang boleh dilihat? | Nol kebocoran pada skenario uji akses tanpa izin dan plafon klasifikasi. |
| Traceability | Apakah setiap tindakan dapat ditelusuri? | Setiap aksi LOGIN, CREATE, UPDATE, SUBMIT, APPROVE, REJECT, ACCESS_DENIED, AI_QUERY, AI_FEEDBACK, VERSION_REGISTER, SEARCH menghasilkan entri audit. |
| Adoption | Apakah tim kerja benar-benar memakai? | Jumlah pengguna aktif dan knowledge entry baru per tim selama UAT; target ditetapkan bersama mentor. |
| Quality | Apakah sistem stabil dan bebas bug kritis? | Nol bug P0 terbuka saat rilis; bug P1 memiliki rencana perbaikan (lihat [bug-severity.md](../10-testing/bug-severity.md)). |

## Hal yang Tidak Diukur pada Fase Ini

- **OUT OF SCOPE** Dampak terhadap kinerja keuangan atau transaksi SUN, karena SUNOVATE tidak terhubung dengan sistem transaksi.
- **OUT OF SCOPE** Akurasi data pasar, karena integrasi data pasar resmi termasuk P2 dan belum divalidasi.

## Open Questions

- OQ-03 Tim kerja dan proses pilot pertama, yang menentukan baseline adopsi.
- OQ-10 Format laporan dan indikator dashboard yang dibutuhkan.
- OQ-11 Model AI dan embedding yang diizinkan, yang memengaruhi target retrieval semantik.

## Risks

- R-04 Jawaban AI dianggap fakta atau keputusan.
- R-06 Scope melebihi periode enam bulan.
- R-11 Kualitas metadata rendah sehingga retrieval buruk.

## Acceptance Criteria

- Mentor menyetujui atau merevisi tabel sasaran dan ukuran keberhasilan.
- Setiap target angka memiliki baseline atau dinyatakan sebagai indikator tanpa target.

## Related Documents

- [project-overview.md](project-overview.md)
- [prd.md](../01-product/prd.md)
- [rag-evaluation.md](../05-ai-rag/rag-evaluation.md)
- [dashboard-requirements.md](../09-ui-ux/dashboard-requirements.md)

## Last Updated

2026-10-01
