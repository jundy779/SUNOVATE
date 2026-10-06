# Agenda Sesi Mentor 01: Konfirmasi Jawaban dan Validasi Fondasi

**Status:** DRAFT
**Last Updated:** 2026-10-02

## Purpose
Sesi ini menjadi **sesi konfirmasi**. Pada deck proposal versi tetap `v1_` (slide 24, kini berjudul "Keputusan yang memerlukan konfirmasi knowledge owner"), knowledge owner sudah menjawab delapan pertanyaan. Tujuan sesi: (1) meminta mentor mengakui (acknowledge) jawaban tersebut, (2) membahas sisa pertanyaan yang benar-benar masih terbuka, dan (3) mengonfirmasi perubahan izin yang diusulkan. Hasilnya memengaruhi pekerjaan Bulan 2 (Foundation) dan Bulan 3 (AI & Data) pada [product-roadmap.md](../01-product/product-roadmap.md). Fase saat ini adalah Bulan 1 (Requirement, 21 September sampai 20 Oktober 2026).

## Logistik
| Item | Isi |
|---|---|
| Tanggal dan waktu | OPEN QUESTION, menyesuaikan jadwal mentor |
| Durasi usulan | 60 menit |
| Peserta | Mentor, pengembang; pihak lain atas arahan mentor |
| Bahan | Aplikasi lokal (data `SIMULATED_DATA`), dokumen ini, [open-questions.md](open-questions.md), [decision-log.md](../12-governance/decision-log.md) |

## Susunan acara (PROPOSED)
| Menit | Topik | Tujuan |
|---|---|---|
| 0-5 | Pembuka dan batas proyek | Menegaskan: bukan sistem transaksi, tidak mengambil keputusan keuangan, semua data simulasi |
| 5-15 | Demo singkat | Menunjukkan fondasi yang sudah berjalan (lihat skrip demo) |
| 15-25 | Pengakuan jawaban knowledge owner | Mentor mengakui, mengoreksi, atau menolak setiap jawaban pada tabel di bawah (OQ-24) |
| 25-50 | Pertanyaan yang masih terbuka | Mendapat keputusan atau arahan |
| 50-55 | Keputusan izin yang diusulkan | Mengonfirmasi peran dan perubahan hak `staff` (OQ-25) |
| 55-60 | Rangkuman keputusan dan tindak lanjut | Membacakan ulang keputusan agar tidak salah catat |

## Skrip demo (10 menit)
1. Login sebagai `sim.staff.pppsun@sunovate.local`: dashboard hanya menampilkan data tim PPPSUN dan knowledge yang dibagikan.
2. Knowledge Hub dan pencarian: hanya entri terbit dalam cakupan.
3. Hermes: pertanyaan "Apa saja metadata wajib saat mendaftarkan dokumen knowledge?" dijawab dengan sitasi.
4. Hermes menolak: pertanyaan di luar domain SUN, permintaan kode, dan "Seri SUN mana yang sebaiknya dibeli?".
5. Hermes dan aksi tulis: "Tolong hapus entri SOP ..." menjadi permintaan approval, tidak dieksekusi.
6. Login sebagai `sim.coordinator@sunovate.local`: cakupan semua tim, metrik approval tertunda di dashboard, serta pengguna, peran, status provider, dan audit log di Administrasi. Keputusan approval saat ini hanya tersedia lewat API (`/docs`), belum ada layar khusus.

Pesan kunci: kontrol akses ditegakkan di API, bukan hanya dengan menyembunyikan menu.

## A. Jawaban knowledge owner yang dimintakan pengakuan mentor (OQ-24)

**CONFIRMED (knowledge owner, deck v1_ slide 24)** Jawaban berikut berasal dari knowledge owner, bukan dari mentor. Kolom "Tafsiran pengembang" adalah PROPOSED. Catatan keputusan: [decision-log.md](../12-governance/decision-log.md).

| OQ | Pertanyaan | Jawaban knowledge owner | Tafsiran pengembang (PROPOSED) | Status setelah jawaban | Keputusan mentor |
|---|---|---|---|---|---|
| OQ-03 | Pilot pertama (tim kerja dan proses) | "6 tim" | Enam tim pada brief; proses pilot belum dijawab | ANSWERED (knowledge owner), DEC-20261002-01 | |
| OQ-04 | Dokumen yang boleh masuk repository dan RAG | "Semua dokumen yang diusulkan tim kerja" | Data asli tetap butuh klasifikasi dan persetujuan eksplisit; CONFIDENTIAL tidak diproses Hermes | PARTIAL, DEC-20261002-02 | |
| OQ-05 | Klasifikasi dan hak akses tiap jenis dokumen | Yang dapat mengubah/mengunggah: ketua tim, kasubdit PMP, Kasi MP, dan PIC yang ditunjuk | Hanya menjawab siapa yang boleh mengubah/mengunggah; skema klasifikasi belum | PARTIAL, DEC-20261002-03 | |
| OQ-06 | SharePoint sumber utama atau referensi | "Sandbox server" | Ambigu; perlu klarifikasi (bagian B.5) | PARTIAL, DEC-20261002-04 | |
| OQ-07 | Mekanisme login dan hosting | "Pakai computer tersendiri sebagai server" | Hosting dijawab; login belum | PARTIAL, DEC-20261002-05 | |
| OQ-08 | Telegram dan WhatsApp untuk penggunaan internal | "bisa" | Tetap P2; butuh kajian keamanan; RESTRICTED ke atas tidak dikirim ke kanal eksternal secara default | ANSWERED (knowledge owner), DEC-20261002-06 | |
| OQ-09 | Knowledge owner dan reviewer per tim | Masing-masing ketua tim dan PIC yang ditunjuk | Ketua tim = `team_lead`, PIC = `knowledge_owner`; orangnya belum ditunjuk | ANSWERED (knowledge owner), DEC-20261002-07 | |
| OQ-10 | Format laporan dan indikator dashboard | "Yield, kepemilikan SBN" | Indikator diminta tanpa data; format laporan belum | PARTIAL, DEC-20261002-08 | |

Yang diminta dari mentor: untuk setiap baris, nyatakan diakui, diubah, atau ditolak. Bila diakui, OQ terkait diubah menjadi `ANSWERED` penuh (bila tidak ada sisa) dan label jawaban diperbarui. Bila diubah atau ditolak, dokumen yang bergantung direvisi (R-16).

## B. Pertanyaan yang masih terbuka
Opsi di bawah adalah kemungkinan yang diusulkan pengembang (PROPOSED), bukan fakta. Mentor dapat memberi jawaban lain.

### 1. OQ-02 Nama resmi tim dan tim tambahan
Jawaban pilot "6 tim" konsisten dengan enam tim pada brief, tetapi deck Pengayaan 6 Mei 2026 menampilkan lebih banyak tim kerja Dit. SUN 2026 dan sebagian nama sedikit berbeda.
- Opsi a: tetap enam tim (PPSUN, AKPSUN, PSUN, PPPSUN, DHTV, SUN Tematik).
- Opsi b: semua tim kerja pada struktur 2026.
- Opsi c: enam tim dulu, tim lain pada fase berikutnya.
- Juga perlu: nama resmi tiap tim yang ditampilkan di aplikasi dan proses pilot yang dipilih.
- Dampak: seed tim, team scope otorisasi, dashboard, konteks Hermes.

### 2. OQ-05 Skema klasifikasi
- Skema klasifikasi resmi apa yang berlaku, dan bagaimana dipetakan ke usulan PUBLIC / INTERNAL / RESTRICTED / CONFIDENTIAL?
- Apakah konten INTERNAL boleh dibaca lintas tim (terkait OQ-14)?
- Siapa yang berwenang menetapkan klasifikasi (jawaban saat ini hanya menyebut siapa yang boleh mengubah/mengunggah)?
- Dampak: aturan otorisasi dan plafon klasifikasi Hermes; risiko R-14 untuk cakupan "semua dokumen".

### 3. OQ-07 dan OQ-23 Login dan persyaratan server khusus
- Mekanisme login apa yang dipakai di server khusus (SSO organisasi, akun lokal, lainnya)?
- Persyaratan "komputer tersendiri sebagai server": lokasi dan akses jaringan, sistem operasi, apakah Docker boleh dipasang, backup di luar host, siapa yang mengadministrasi, siapa yang boleh mengaksesnya, dan TLS.
- Di mana UAT dijalankan (terkait OQ-20)?
- Dampak: pengganti login pengembangan, rencana deployment, risiko R-13.

### 4. OQ-11 Model AI dan lokasi pemrosesan
- Model AI dan embedding apa yang boleh dipakai?
- Apakah data boleh diproses di luar jaringan instansi? Bila tidak, apakah ada infrastruktur internal (mungkin terkait server khusus)?
- Dampak: pencarian semantik dan Hermes generatif. Saat ini Hermes memakai penyedia ekstraktif tanpa model eksternal.

### 5. OQ-06 dan OQ-22 Klarifikasi "Sandbox server"
- Apa yang dimaksud "Sandbox server"? Apakah itu lokasi file sumber pilot, dan apakah sama dengan komputer server khusus?
- Apakah SharePoint dipakai pada pilot?
- Dampak: jenis document provider untuk pilot.

### 6. OQ-21 Sumber data "yield" dan "kepemilikan SBN"
- Apa sumber data otoritatif, definisi, periode, dan siapa yang boleh melihat kedua indikator?
- Apakah indikator ini tetap di luar SUNOVATE (SUNOVATE bukan sistem transaksi, ADR-013)?
- Dampak: dashboard; tanpa jawaban tidak ada angka yang ditampilkan.

### 7. OQ-01 Fungsi SUN Tematik
- Fungsi, knowledge product, dan proses SUN Tematik. Tanpa jawaban, tim ini tidak diberi perilaku khusus.

## C. Keputusan izin yang diusulkan (OQ-25)
**CONFIRMED (knowledge owner, deck v1_ slide 24)** Yang dapat mengubah data atau mengunggah adalah ketua tim, kasubdit PMP, Kasi MP, dan PIC yang ditunjuk. Matriks izin saat ini masih memberi role `staff` hak `knowledge:create`, `knowledge:update`, `knowledge:submit`, dan `document:create`.

**PROPOSED** `team_lead` = ketua tim; `knowledge_owner` = PIC; `knowledge_coordinator` = peran tingkat PMP; cabut keempat permission di atas dari `staff`. Belum diimplementasikan. Rincian: [permission-matrix.md](../06-security/permission-matrix.md).

Yang perlu dikonfirmasi mentor:
- Role sistem yang tepat untuk ketua tim, kasubdit PMP, Kasi MP, dan PIC, serta kepanjangan "PMP" (deck tidak menjelaskan; kemungkinan Program dan Manajemen Pengetahuan).
- Apakah kasubdit PMP dan Kasi MP bekerja lintas tim atau hanya pada tim tertentu.
- Apakah staf biasa tetap boleh menyusun draf knowledge tanpa hak unggah.
- Apakah perubahan boleh diterapkan sekarang atau menunggu pengakuan penuh.

## Pertanyaan prioritas sedang (bila waktu cukup)
- OQ-12 Alur persetujuan publikasi knowledge (jawaban OQ-05 dan OQ-09 tidak menjawab siapa yang memutuskan publikasi).
- OQ-10 Format laporan dan indikator dashboard selain yield dan kepemilikan SBN.

## Konfirmasi arah
- Apakah prioritas P0 MVP (repository dan metadata, pencarian, Hermes bersitasi, RBAC dan klasifikasi, audit, kinerja dan pending matters dasar) sudah sesuai?
- Apakah roadmap enam bulan dapat diterima sebagai acuan?

## Pekerjaan yang berjalan tanpa menunggu jawaban
Persistence PostgreSQL (menggantikan store simulasi), verifikasi Docker, dan pengelolaan output, tugas, dan pending matters. Pekerjaan yang ditunda sampai ada jawaban: ingestion dokumen nyata, embedding/LLM, login produksi, integrasi, perubahan izin `staff`, indikator yield dan kepemilikan SBN, dan perilaku SUN Tematik.

## Pencatatan hasil
Setelah sesi, setiap jawaban dicatat dengan templat `DEC-YYYYMMDD-NN` di [decision-log.md](../12-governance/decision-log.md), status OQ diperbarui di [open-questions.md](open-questions.md), dan dokumen terdampak diperbarui. Tidak mencatat nama pribadi atau data sensitif.

| OQ | Jawaban singkat | Status | Tindak lanjut |
|---|---|---|---|
| OQ-24 (pengakuan atas OQ-03 sampai OQ-10) | | | |
| OQ-02 | | | |
| OQ-05 | | | |
| OQ-07 dan OQ-23 | | | |
| OQ-11 | | | |
| OQ-06 dan OQ-22 | | | |
| OQ-21 | | | |
| OQ-25 | | | |
| OQ-01 | | | |

## Related Documents
- [open-questions.md](open-questions.md)
- [assumptions.md](assumptions.md)
- [mvp-scope.md](../01-product/mvp-scope.md)
- [decision-log.md](../12-governance/decision-log.md)
- [permission-matrix.md](../06-security/permission-matrix.md)
