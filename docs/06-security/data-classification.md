# Data Classification

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-21

## Purpose

Menetapkan tingkat klasifikasi data yang dipakai SUNOVATE pada pengembangan dan aturan penanganan per tingkat untuk penyimpanan, pencarian, Hermes, ekspor, logging, dan kanal eksternal. Skema ini adalah usulan pengembangan dan belum dipetakan ke skema klasifikasi resmi Kemenkeu.

## Confirmed Information

- **CONFIRMED** Otorisasi mencakup data classification sebagai syarat ketiga di samping permission dan team scope (sumber: brief sesi 2026-10-01; ADR-006).
- **CONFIRMED** File tidak disimpan sebagai BLOB; yang disimpan adalah referensi, metadata, checksum SHA-256, versi, klasifikasi, dan lokasi provider (sumber: ADR-003).
- **CONFIRMED** `HERMES_MAX_CLASSIFICATION=RESTRICTED` pada development (sumber: fact sheet bagian 4; `.env.example`).
- **CONFIRMED** Klasifikasi yang tidak dikenal selalu ditolak (sumber: implementasi scaffold sesi 2026-10-01).
- **PROPOSED** Tabel klasifikasi di bawah (sumber: fact sheet bagian 4).

## Tingkat klasifikasi (PROPOSED)

| Code | Rank | Meaning (proposal) |
|---|---|---|
| PUBLIC | 0 | Boleh dibuka publik (mis. regulasi yang sudah diundangkan). |
| INTERNAL | 1 | Internal Dit. SUN/DJPPR. |
| RESTRICTED | 2 | Terbatas pada tim pemilik atau penerima yang ditunjuk. |
| CONFIDENTIAL | 3 | Sangat terbatas; tidak diproses Hermes pada pengembangan. |

Aturan dasar:

- Setiap pengguna memiliki `clearance_code`. Akses mensyaratkan rank(clearance) >= rank(klasifikasi rekaman).
- Knowledge entry dan document reference memiliki `sharing_scope`: `TEAM` (hanya tim pemilik) atau `DIRECTORATE` (semua tim, hanya saat `PUBLISHED`).
- Klasifikasi tidak menggantikan team scope. Rekaman INTERNAL milik tim lain tetap tidak terbaca kecuali dibagikan `DIRECTORATE` dan `PUBLISHED`, atau principal memiliki `scope:all_teams`.

## Aturan penanganan per tingkat (PROPOSED)

| Aspek | PUBLIC | INTERNAL | RESTRICTED | CONFIDENTIAL |
|---|---|---|---|---|
| Penyimpanan | Metadata dan referensi file; file di provider dokumen | Sama | Sama; lokasi provider harus terbatas aksesnya | Sama; pada pengembangan tidak ada rekaman CONFIDENTIAL selain contoh `SIMULATED_DATA` |
| Pencarian | Tampil sesuai team scope | Tampil jika clearance >= INTERNAL dan team scope terpenuhi | Tampil jika clearance >= RESTRICTED dan team scope terpenuhi | Tampil hanya untuk clearance CONFIDENTIAL dan team scope terpenuhi |
| Hermes | Boleh menjadi konteks | Boleh menjadi konteks jika principal berhak | Boleh menjadi konteks jika principal berhak; batas atas development | Tidak diproses Hermes |
| Ekspor | Boleh | Hanya pengguna berhak; menyertakan label klasifikasi | Hanya pengguna berhak; menyertakan label klasifikasi dan tercatat di audit | Tidak tersedia pada pengembangan |
| Logging | Hanya id, kode klasifikasi, dan action; tanpa isi | Sama | Sama; prompt lengkap dengan konteks RESTRICTED tidak dicatat | Sama |
| Kanal eksternal (Telegram, WhatsApp, notifikasi) | Belum tersedia; kandidat pertama jika disetujui | Tidak dikirim sampai kajian keamanan selesai (OQ-08 dijawab "bisa" oleh knowledge owner) | Tidak dikirim | Tidak dikirim |

Catatan:

- **CONFIRMED** Ekspor dan reporting termasuk prioritas P1 dan belum diimplementasikan pada scaffold (sumber: Proposal v2.4, slide 11; fact sheet bagian 9).
- **CONFIRMED** Telegram dan WhatsApp belum tersedia; termasuk P2 dan bukan janji (sumber: Proposal v2.4, slide 11).
- **CONFIRMED** `OutputGuard` memeriksa batas klasifikasi pada jawaban Hermes (sumber: fact sheet bagian 9).

## Penetapan klasifikasi

- **PROPOSED** Klasifikasi ditetapkan oleh knowledge owner saat membuat rekaman dan diperiksa reviewer saat review.
- **PROPOSED** Bila ragu, gunakan tingkat yang lebih tinggi.
- **PROPOSED** Penurunan klasifikasi (downgrade) diperlakukan sebagai perubahan yang tercatat di audit log.
- **CONFIRMED** Skema memiliki `extraction_status` `QUARANTINED` (sumber: fact sheet bagian 6). **PROPOSED** Status ini dipakai untuk menahan dokumen yang klasifikasinya belum jelas agar tidak masuk retrieval.

## Open Questions

- **OPEN QUESTION** OQ-05 Klasifikasi dan hak akses setiap jenis dokumen; pemetaan ke skema klasifikasi resmi Kemenkeu.
- **OPEN QUESTION** OQ-04 Dokumen apa yang boleh masuk repository dan RAG.
- **CONFIRMED (knowledge owner, deck v1_ slide 24)** OQ-08 Telegram dan WhatsApp dijawab "bisa" untuk penggunaan internal. **PROPOSED** Konten RESTRICTED dan CONFIDENTIAL tetap tidak dikirim ke kanal eksternal secara default; kanal belum tersedia.
- **OPEN QUESTION** OQ-11 Apakah data boleh diproses model di luar jaringan instansi, dan sampai tingkat klasifikasi berapa.
- **OPEN QUESTION** OQ-14 Kebijakan berbagi lintas tim untuk konten INTERNAL.

## Risks

- R-09 Klasifikasi tidak sesuai skema resmi.
- R-02 Kebocoran data melalui pencarian atau Hermes.
- R-11 Metadata klasifikasi yang salah menyebabkan rekaman terbuka terlalu luas atau terlalu sempit.

## Acceptance Criteria

- Rekaman tanpa klasifikasi yang dikenal tidak dapat dibaca siapa pun.
- Hermes tidak pernah menerima chunk di atas `HERMES_MAX_CLASSIFICATION`.
- Uji otorisasi mencakup kombinasi clearance INTERNAL dan RESTRICTED terhadap rekaman tiap tingkat.

## Pemetaan istilah rancangan dan kode (2026-10-21)

Dokumen rancangan di luar repository (blueprint SUNOVATE v0.5, deck v2.5) memakai istilah usulan yang belum menjadi kode. Pemetaan berikut berlaku sampai mentor memutuskan; kode tidak diganti nama berdasarkan usulan tersebut.

| Istilah rancangan (PROPOSED) | Padanan di kode | Status |
|---|---|---|
| INTERNAL | `INTERNAL` | sama |
| TEAM | `sharing_scope = TEAM` (bukan tingkat klasifikasi) | sudah ada |
| RESTRICTED | `RESTRICTED` | sama |
| RAHASIA | perlakuan penampil hanya-baca di vault terpisah (ADR-020), dengan klasifikasi biasa pada dokumen | simulasi |
| METADATA_ONLY | belum ada | belum diimplementasikan |
| (tidak dipakai rancangan) | `PUBLIC`, `CONFIDENTIAL` | sudah ada |

## Unduhan Excel monitoring kerja (2026-10-21)

- `GET /api/v1/exports/attention` mengunduh seluruh daftar "Perlu ditindaklanjuti" dari Ringkasan dengan perhitungan yang sama seperti ringkasan.
- `GET /api/v1/exports/work?kind=outputs|tasks|milestones|pending|followUps` memakai filter otorisasi dan klasifikasi yang sama dengan endpoint daftar, sehingga isi berkas sama dengan yang dapat dilihat pengguna di layar. Maksimal 5.000 baris per berkas.
- Setiap unduhan dicatat di audit (`WORK_EXPORT`) dengan jenis data dan jumlah baris saja, tanpa isi baris.
- Teks dari pengguna yang diawali `=`, `+`, `-`, `@`, tab, atau carriage return disimpan sebagai teks sehingga tidak dieksekusi sebagai formula saat berkas dibuka (perlindungan formula injection).
- Berkas memuat catatan bahwa isinya data contoh dan hanya untuk pengunduh. Respons memakai `no-store`. Dokumen RAHASIA tidak memiliki jalur unduhan dan tidak termasuk.
- Batas yang diketahui: setelah diunduh, berkas berada di luar kendali aplikasi; pengendaliannya mengikuti kebijakan penanganan dokumen kantor.

## Related Documents

- [document-classification](../04-data/document-classification.md)
- [authorization-rbac](authorization-rbac.md)
- [audit-logging](audit-logging.md)
- [integration-readiness-checklist](../08-integrations/integration-readiness-checklist.md)
