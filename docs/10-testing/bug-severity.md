# Severity Bug

**Status:** NEEDS MENTOR VALIDATION

**Last Updated:** 2026-10-06

## Purpose

Menetapkan klasifikasi severity bug P0–P3, ekspektasi respons, contoh khusus SUNOVATE, dan field register bug.

## Confirmed Information

- **CONFIRMED**: Definisi severity berikut berasal dari proposal pengembang dan berstatus usulan (sumber: Proposal v2.4, slide 20; status PROPOSED):
  - P0: kebocoran atau kehilangan data; memblokir rilis.
  - P1: fungsi utama gagal atau jawaban AI menyesatkan.
  - P2: fungsi terganggu tetapi ada workaround.
  - P3: masalah visual atau minor.

## Ekspektasi Respons (PROPOSED)

Ekspektasi berikut adalah usulan untuk periode pengembangan oleh satu pengembang dan belum divalidasi mentor.

| Severity | Dampak terhadap rilis | Respons awal | Target perbaikan |
|---|---|---|---|
| P0 | Memblokir rilis; fitur terdampak dinonaktifkan bila perlu | Segera, hari kerja yang sama | Sebelum pekerjaan lain dilanjutkan |
| P1 | Memblokir rilis kecuali ada keputusan tertulis mentor | Hari kerja berikutnya | Dalam iterasi berjalan |
| P2 | Tidak memblokir; workaround didokumentasikan | Saat triase mingguan | Iterasi berikutnya |
| P3 | Tidak memblokir | Saat triase mingguan | Sesuai kapasitas |

- **PROPOSED**: P0 yang menyangkut kebocoran data juga diproses sesuai [incident-response.md](../06-security/incident-response.md).

## Contoh Khusus SUNOVATE (PROPOSED)

| Severity | Contoh |
|---|---|
| P0 | Pengguna membaca knowledge `sharing_scope` TEAM milik tim lain melalui `/search` atau Hermes |
| P0 | Hermes menyitir chunk di atas clearance pengguna atau di atas `HERMES_MAX_CLASSIFICATION` |
| P0 | `audit_logs` dapat diubah atau dihapus |
| P0 | Perubahan tertimpa diam-diam tanpa `REVISION_CONFLICT`, sehingga data hilang |
| P0 | Token, rahasia, atau isi dokumen tercatat di log aplikasi |
| P0 | Aplikasi dapat berjalan dengan `APP_ENV=production` dan dev auth aktif |
| P1 | Hermes menjawab tanpa sitasi atau dengan sitasi yang tidak mendukung jawaban |
| P1 | Jailbreak atau prompt injection berhasil mengubah perilaku Hermes |
| P1 | Permintaan aksi tulis lewat Hermes dieksekusi tanpa approval |
| P1 | Submit knowledge atau keputusan approval gagal untuk pengguna yang berhak |
| P1 | Duplikasi ingestion tidak terdeteksi |
| P2 | Deadline state salah tampil untuk satu kasus tepi, data dasar tetap benar |
| P2 | Pagination tidak konsisten, tetapi filter manual dapat dipakai |
| P2 | Pesan error tidak jelas, tetapi `requestId` tersedia |
| P3 | Warna tidak sesuai token desain, teks terpotong, ejaan |

### Contoh dari Jawaban Knowledge Owner (PROPOSED)

Contoh berikut diturunkan dari jawaban yang berlabel **CONFIRMED (knowledge owner, deck v1_ slide 24)**; pengakuan mentor tertunda (OQ-24). Definisi P0 sampai P3 tidak berubah: slide 20 tidak berubah pada deck `v1_`. Yang bertambah hanya contoh.

| Severity | Contoh | Catatan |
|---|---|---|
| P0 | Dokumen asli (bukan `SIMULATED_DATA`) masuk repository, indeks, atau RAG tanpa klasifikasi dan persetujuan eksplisit (FR-53, BR-35) | Kelas paparan data (slide 20: kebocoran data); diproses sesuai [incident-response.md](../06-security/incident-response.md) |
| P0 | Konten `CONFIDENTIAL` diambil atau dikutip Hermes karena jawaban "semua dokumen" dianggap izin | Pelanggaran plafon klasifikasi (BR-22) |
| P0 | Pengguna di luar tim membaca atau menulis data tim pilot lain karena peran berlaku global atau penunjukan salah | Pelanggaran team scope (BR-07, BR-18, T-21) |
| P0 | API atau PostgreSQL server pilot terjangkau dari jaringan tanpa kontrol, atau dev auth terbuka ke jaringan | Paparan server (NFR-42, T-23) |
| P1 | `staff` masih dapat membuat, mengubah, atau mengajukan knowledge setelah PD-1 disetujui dan dinyatakan diterapkan (FR-50, BR-33) | Sebelum PD-1 disetujui ini celah persyaratan (lihat [bug-register.md](bug-register.md), REQ-GAP-01), bukan bug fungsional; menjadi P1 bila kontrol otorisasi yang ditetapkan tidak berlaku |
| P1 | Ketua tim atau PIC yang berwenang ditolak menulis di timnya sendiri | Fungsi utama gagal untuk pengguna yang berhak |
| P1 | Perubahan katalog permission tidak sampai ke database yang sudah di-seed sehingga `/roles` berbeda dari dokumentasi | Seed hanya menambah baris (lihat logical-data-model) |
| P1 | Indikator yield atau kepemilikan SBN tampil dengan angka tanpa sumber otoritatif (FR-54, BR-36) | Angka yang menyesatkan dan melampaui batas ADR-013 |
| P2 | Teks "sumber data belum tersedia" tidak muncul, tetapi tidak ada angka | Fungsi terganggu; data tidak salah |
| P2 | Backup server pilot tidak pernah diuji restore | Risiko R-13; menjadi P1 bila backup terbukti rusak |
| P2 | Pilot tujuh tim: satu tim tidak memiliki pengguna uji sehingga isolasi tim itu tidak teruji | Lubang cakupan uji, bukan cacat produk |
| P3 | Penamaan tim pada tampilan berbeda dari nama resmi (OQ-02) | Minor sampai nama resmi dikonfirmasi |

- **PROPOSED**: Bila ragu antara dua severity, pilih yang lebih tinggi sampai triase.

## Register Bug (PROPOSED)

| Field | Keterangan |
|---|---|
| ID | Format `BUG-nnn` |
| Judul | Ringkas, menyebut fitur |
| Severity | P0, P1, P2, P3 |
| Status | Baru, Triase, Dikerjakan, Siap diuji, Selesai, Ditolak |
| Ditemukan pada | Tanggal dan lapisan (unit, integration, e2e, security, RAG, UAT) |
| Lingkungan | Lokal, UAT (OPEN QUESTION, OQ-20) |
| Versi atau commit | Hash commit |
| Langkah reproduksi | Memakai pengguna dan data SIMULATED |
| Hasil yang diharapkan dan aktual | Dua kolom terpisah |
| Request ID | Dari header `X-Request-ID` |
| Skenario wajib terkait | Akses tanpa izin, jailbreak, prompt injection, sitasi keliru, duplikasi ingestion, konflik pembaruan |
| Test regresi | Lokasi test yang ditambahkan |
| Keputusan | Catatan keputusan mentor untuk P1 yang dibiarkan terbuka |

- **PROPOSED**: Register tidak boleh memuat data asli, data pribadi, atau isi dokumen internal.
- **OPEN QUESTION**: Alat untuk menyimpan register bug belum ditetapkan.
- **PROPOSED**: Sampai alat ditetapkan, register sementara berupa dokumen: [bug-register.md](bug-register.md). Isinya hanya cacat yang dapat ditelusuri di riwayat repository dan catatan review, dengan severity usulan menurut dokumen ini.

## Related Documents

- [bug-register.md](bug-register.md)
- [test-strategy.md](test-strategy.md)
- [uat-plan.md](uat-plan.md)
- [incident-response.md](../06-security/incident-response.md)
- [risk-register.md](../12-governance/risk-register.md)
