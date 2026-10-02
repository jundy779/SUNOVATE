# Agenda Sesi Mentor 01: Validasi Fondasi

**Status:** DRAFT
**Last Updated:** 2026-10-02

## Purpose
Mendapat keputusan mentor atas pertanyaan yang memblokir pekerjaan Bulan 2 (Foundation) dan Bulan 3 (AI & Data) pada [product-roadmap.md](../01-product/product-roadmap.md). Fase saat ini adalah Bulan 1 (Requirement, 21 September sampai 20 Oktober 2026).

## Logistik
| Item | Isi |
|---|---|
| Tanggal dan waktu | OPEN QUESTION, menyesuaikan jadwal mentor |
| Durasi usulan | 60 menit |
| Peserta | Mentor, pengembang; pihak lain atas arahan mentor |
| Bahan | Aplikasi lokal (data `SIMULATED_DATA`), dokumen ini, [open-questions.md](open-questions.md) |

## Susunan acara (PROPOSED)
| Menit | Topik | Tujuan |
|---|---|---|
| 0-5 | Pembuka dan batas proyek | Menegaskan: bukan sistem transaksi, tidak mengambil keputusan keuangan, semua data simulasi |
| 5-15 | Demo singkat | Menunjukkan fondasi yang sudah berjalan (lihat skrip demo) |
| 15-50 | Enam pertanyaan prioritas tinggi | Mendapat keputusan atau arahan |
| 50-55 | Pertanyaan prioritas sedang bila waktu cukup | |
| 55-60 | Rangkuman keputusan dan tindak lanjut | Membacakan ulang keputusan agar tidak salah catat |

## Skrip demo (10 menit)
1. Login sebagai `sim.staff.pppsun@sunovate.local`: dashboard hanya menampilkan data tim PPPSUN dan knowledge yang dibagikan.
2. Knowledge Hub dan pencarian: hanya entri terbit dalam cakupan.
3. Hermes: pertanyaan "Apa saja metadata wajib saat mendaftarkan dokumen knowledge?" dijawab dengan sitasi.
4. Hermes menolak: pertanyaan di luar domain SUN, permintaan kode, dan "Seri SUN mana yang sebaiknya dibeli?".
5. Hermes dan aksi tulis: "Tolong hapus entri SOP ..." menjadi permintaan approval, tidak dieksekusi.
6. Login sebagai `sim.coordinator@sunovate.local`: cakupan semua tim, metrik approval tertunda di dashboard, serta pengguna, peran, status provider, dan audit log di Administrasi. Keputusan approval saat ini hanya tersedia lewat API (`/docs`), belum ada layar khusus.

Pesan kunci: kontrol akses ditegakkan di API, bukan hanya dengan menyembunyikan menu.

## Pertanyaan prioritas tinggi
Opsi di bawah adalah kemungkinan yang diusulkan pengembang (PROPOSED), bukan fakta. Mentor dapat memberi jawaban lain.

### 1. OQ-02 Tim kerja dalam scope
Deck Pengayaan 6 Mei 2026 menampilkan lebih banyak tim kerja Dit. SUN 2026 dibanding enam tim dalam scope awal, dan sebagian nama sedikit berbeda.
- Opsi a: tetap enam tim (PPSUN, AKPSUN, PSUN, PPPSUN, DHTV, SUN Tematik).
- Opsi b: semua tim kerja pada struktur 2026.
- Opsi c: enam tim dulu, tim lain pada fase berikutnya.
- Juga perlu: nama resmi tiap tim yang ditampilkan di aplikasi.
- Dampak: seed tim, team scope otorisasi, dashboard, konteks Hermes.

### 2. OQ-03 Pilot pertama
- Tim dan proses mana yang menjadi pilot MVP?
- Jenis knowledge apa yang paling bernilai untuk pilot (mis. SOP, playbook, close out note, regulasi)?
- Dampak: prioritas fitur Bulan 2 sampai 4 dan skenario UAT.

### 3. OQ-04 Dokumen yang boleh masuk repository dan Hermes
- Jenis dokumen apa yang boleh didaftarkan? Apakah ada yang tidak boleh diproses Hermes?
- Apakah dokumen contoh nyata boleh dipakai untuk uji, dan dengan syarat apa?
- Dampak: ingestion pipeline (Bulan 3), golden set evaluasi.

### 4. OQ-05 Klasifikasi dan hak akses
- Skema klasifikasi resmi apa yang berlaku, dan bagaimana dipetakan ke usulan PUBLIC / INTERNAL / RESTRICTED / CONFIDENTIAL?
- Apakah konten INTERNAL boleh dibaca lintas tim (terkait OQ-14)?
- Siapa yang berwenang menetapkan klasifikasi?
- Dampak: aturan otorisasi dan plafon klasifikasi Hermes.

### 5. OQ-07 Login dan hosting
- Mekanisme login apa yang disetujui untuk lingkungan uji dan produksi?
- Di mana aplikasi akan dijalankan untuk UAT (terkait OQ-20)?
- Dampak: pengganti login pengembangan dan rencana deployment.

### 6. OQ-11 Model AI dan lokasi pemrosesan
- Model AI dan embedding apa yang boleh dipakai?
- Apakah data boleh diproses di luar jaringan instansi? Bila tidak, apakah ada infrastruktur internal?
- Dampak: pencarian semantik dan Hermes generatif. Saat ini Hermes memakai penyedia ekstraktif tanpa model eksternal.

## Pertanyaan prioritas sedang (bila waktu cukup)
- OQ-01 Fungsi dan knowledge product SUN Tematik.
- OQ-09 Knowledge owner dan reviewer tiap tim.
- OQ-12 Alur persetujuan publikasi knowledge.
- OQ-10 Indikator dashboard dan format laporan yang dibutuhkan.

## Konfirmasi arah
- Apakah prioritas P0 MVP (repository dan metadata, pencarian, Hermes bersitasi, RBAC dan klasifikasi, audit, kinerja dan pending matters dasar) sudah sesuai?
- Apakah roadmap enam bulan dapat diterima sebagai acuan?

## Pekerjaan yang berjalan tanpa menunggu jawaban
Persistence PostgreSQL (menggantikan store simulasi), verifikasi Docker, dan pengelolaan output, tugas, dan pending matters. Pekerjaan yang ditunda sampai ada jawaban: ingestion dokumen nyata, embedding/LLM, SSO, integrasi, dan perilaku SUN Tematik.

## Pencatatan hasil
Setelah sesi, setiap jawaban dicatat dengan templat `DEC-YYYYMMDD-NN` di [decision-log.md](../12-governance/decision-log.md), status OQ diperbarui di [open-questions.md](open-questions.md), dan dokumen terdampak diperbarui. Tidak mencatat nama pribadi atau data sensitif.

| OQ | Jawaban singkat | Status | Tindak lanjut |
|---|---|---|---|
| OQ-02 | | | |
| OQ-03 | | | |
| OQ-04 | | | |
| OQ-05 | | | |
| OQ-07 | | | |
| OQ-11 | | | |

## Related Documents
- [open-questions.md](open-questions.md)
- [assumptions.md](assumptions.md)
- [mvp-scope.md](../01-product/mvp-scope.md)
- [decision-log.md](../12-governance/decision-log.md)
