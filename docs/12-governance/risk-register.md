# Register Risiko

**Status:** PROPOSED
**Last Updated:** 2026-10-19

## Purpose

Dokumen ini mencatat risiko awal SUNOVATE beserta penilaian, mitigasi, pemilik, dan status. Penilaian kemungkinan dan dampak adalah usulan pengembang dan perlu ditinjau mentor.

## Skala

| Nilai | Kemungkinan | Dampak |
|---|---|---|
| Rendah | Jarang terjadi pada periode magang | Gangguan kecil, mudah dipulihkan |
| Sedang | Mungkin terjadi | Menghambat fitur atau jadwal |
| Tinggi | Cenderung terjadi tanpa mitigasi | Kebocoran data, kehilangan kepercayaan, atau kegagalan tujuan |

Seluruh penilaian di bawah PROPOSED. Pemilik "Pengembang" berarti peserta magang pengembang SUNOVATE; pemilik "Mentor" berarti mentor yang ditunjuk Dit. SUN. Pemilik selain itu adalah OPEN QUESTION.

## Register

| ID | Kondisi | Dampak | Kemungkinan | Tingkat dampak | Mitigasi | Pemilik | Status |
|---|---|---|---|---|---|---|---|
| R-01 | Proses bisnis diasumsikan tanpa validasi | Fitur tidak sesuai kebutuhan tim | Tinggi | Sedang | Label bukti pada setiap pernyataan; daftar OQ; validasi mentor sebelum implementasi detail | Pengembang, Mentor | Terbuka |
| R-02 | Kebocoran data melalui pencarian atau Hermes | Akses tidak sah ke konten terbatas | Sedang | Tinggi | Filter otorisasi sebelum scoring; ceiling klasifikasi Hermes; 404 untuk record tak berizin; uji akses tanpa izin | Pengembang | Termitigasi sebagian |
| R-03 | Data asli atau sensitif masuk repository atau log | Pelanggaran kerahasiaan | Sedang | Tinggi | Hanya `SIMULATED_DATA`; file sumber dikecualikan dari Git (ADR-014); OutputGuard; log tanpa isi dokumen | Pengembang | Termitigasi sebagian |
| R-04 | Jawaban AI dianggap fakta atau keputusan | Keputusan keliru berbasis jawaban AI | Sedang | Tinggi | Sitasi wajib; `INSUFFICIENT_EVIDENCE`; penolakan di luar cakupan; penjelasan di UI bahwa Hermes adalah alat bantu | Pengembang, Mentor | Termitigasi sebagian |
| R-05 | Akses integrasi produksi tidak tersedia | Fitur P2 tidak dapat direalisasikan | Tinggi | Sedang | Abstraksi provider; implementasi pengembangan; P2 tidak dijanjikan | Mentor | Diterima |
| R-06 | Cakupan melebihi periode enam bulan | Fitur inti tidak selesai | Sedang | Tinggi | Prioritas P0/P1/P2; target feature-complete akhir bulan 5; kontrol perubahan cakupan | Pengembang, Mentor | Terbuka |
| R-07 | Prompt injection dari isi dokumen | Hermes menjalankan instruksi tersembunyi atau membocorkan data | Sedang | Tinggi | Filter injeksi pada chunk; karantina; CitationValidator; Hermes tanpa akses DB dan tanpa aksi tulis otomatis | Pengembang | Termitigasi sebagian |
| R-08 | Ketergantungan pada satu pengembang | Sistem sulit dilanjutkan setelah magang | Tinggi | Tinggi | Dokumentasi, ADR, decision log, uji otomatis, panduan handover | Pengembang; penerima handover OPEN QUESTION | Terbuka |
| R-09 | Klasifikasi tidak sesuai skema resmi | Kontrol akses tidak selaras kebijakan instansi | Sedang | Tinggi | Klasifikasi sebagai data konfigurasi; validasi OQ-05 sebelum data riil | Mentor | Terbuka |
| R-10 | Simulated store disangka persistence produksi | Data hilang saat restart; ekspektasi keliru | Sedang | Sedang | `DATA_BACKEND=simulated` terdokumentasi; `meta.dataLabel`; backend persisten `DATA_BACKEND=postgres` tersedia (ADR-007, ADR-015 PROPOSED) | Pengembang | Terbuka |
| R-11 | Kualitas metadata rendah | Retrieval dan sitasi buruk | Tinggi | Sedang | Standar metadata minimum; review sebelum publikasi; `data_quality_issues`; evaluasi RAG | Pengembang; knowledge owner per tim OPEN QUESTION (OQ-09) | Terbuka |
| R-12 | Perbedaan daftar tim kerja | Lingkup akses dan dashboard keliru | Sedang | Sedang | Seed hanya enam tim brief; tabel `teams` dapat diperluas; OQ-02 diajukan. Jawaban pilot "6 tim" (knowledge owner, OQ-03) konsisten tetapi tidak menyebut nama tim | Mentor | Terbuka |
| R-13 | Server tunggal khusus ("computer tersendiri sebagai server", jawaban OQ-07): satu titik kegagalan tanpa redundansi | Layanan dan data hilang atau tidak tersedia bila perangkat keras rusak; backup di host yang sama ikut hilang; patching dan akses fisik atau jaringan tidak terkelola; penyerang yang menguasai host menguasai web, API, dan database sekaligus | Sedang | Tinggi | Backup di luar host dan uji restore ([backup-and-restore](../11-operations/backup-and-restore.md)); tetapkan administrator, jadwal patching, daftar yang boleh mengakses, dan TLS (OQ-23); tidak memuat data asli sebelum kontrol tersebut ada; pemulihan dapat dibangun ulang dari migrasi dan seed | Pengembang; administrator server OPEN QUESTION (OQ-23) | Terbuka |
| R-14 | Cakupan "semua dokumen yang diusulkan tim kerja" (OQ-04) berjalan tanpa klasifikasi resmi dan persetujuan per dokumen | Dokumen RESTRICTED atau CONFIDENTIAL atau data pribadi masuk repository dan RAG; paparan data melalui pencarian atau Hermes | Sedang | Tinggi | Tetap `SIMULATED_DATA` sampai klasifikasi (OQ-05) dan persetujuan eksplisit ada; CONFIDENTIAL dikecualikan dari Hermes; karantina dan review manusia sebelum publikasi; ceiling klasifikasi Hermes | Pengembang, Mentor | Terbuka |
| R-15 | Indikator "yield" dan "kepemilikan SBN" diminta tanpa sumber data otoritatif (OQ-10, OQ-21) | Angka tidak akurat atau dianggap resmi; SUNOVATE melampaui batas sebagai bukan sistem transaksi; data sensitif terbuka ke pengguna yang tidak berwenang | Sedang | Tinggi | Tidak menampilkan angka dan tidak membuat tabel bisnis SUN (ADR-013) sebelum sumber, definisi, dan hak lihat jelas; placeholder berlabel `SIMULATED_DATA` saja | Mentor; pemilik data OPEN QUESTION (OQ-21) | Terbuka |
| R-16 | Pekerjaan bergantung pada jawaban knowledge owner yang belum diakui mentor (OQ-24) | Dokumen dan rencana harus direvisi bila mentor mengubah atau menolak jawaban | Sedang | Sedang | Label `CONFIRMED (knowledge owner, deck v1_ slide 24)` dan `PROPOSED` dipisahkan; perubahan kode yang bergantung padanya ditunda sampai pengakuan (termasuk perubahan izin `staff`); agenda sesi mentor dijadikan sesi konfirmasi | Mentor, Pengembang | Terbuka |
| R-17 | Matriks izin saat ini (role `staff` dapat membuat dan mengubah knowledge dan dokumen) tidak selaras dengan jawaban hak ubah/unggah (OQ-05) | Perilaku sistem berbeda dari ketentuan knowledge owner; bila diperbaiki tanpa konfirmasi peran, pengguna yang berwenang bisa kehilangan akses | Sedang | Sedang | Usulan perubahan terdokumentasi di [permission-matrix](../06-security/permission-matrix.md) dan [future-development](../13-handover/future-development.md) (PD-1); konfirmasi peran (OQ-25) sebelum menerapkan; selama data hanya `SIMULATED_DATA` paparan terbatas | Pengembang, Mentor | Terbuka |
| R-18 | Status berlaku terkini regulasi tidak dapat diturunkan dari Kompilasi Peraturan SUN, sedangkan tampilan "Berlaku" dan ketiadaan relasi pencabutan dapat dibaca sebagai bukti berlaku (OQ-26, OQ-29) | Pengguna atau Hermes mengutip regulasi yang sudah dicabut atau diubah sebagai berlaku; pencabutan sebagian atau ketentuan peralihan dibaca sebagai pencabutan penuh atau sebagai bukti berlaku; contoh: PMK 128/PMK.08/2012 tidak punya relasi di kompilasi tetapi statusnya tidak diketahui (OQ-17) | Sedang | Tinggi | Status hukum diisi pemilik konten setelah validasi, tidak diturunkan otomatis (BR-40); sitasi menyertakan "status berlaku belum diverifikasi" sampai divalidasi dan menampilkan pencabutan sebagian dengan cakupan ([citation-policy](../05-ai-rag/citation-policy.md), PROPOSED, belum diimplementasikan); validasi terhadap sumber resmi seperti Berita Negara atau JDIH oleh pemilik konten | Mentor; pemilik konten OPEN QUESTION (OQ-09, OQ-26) | Terbuka |
| R-19 | Cloudflare Tunnel/Access diaktifkan tanpa persetujuan, konfigurasi least privilege, atau kill switch | Aplikasi demo terekspos tidak semestinya; akun atau metadata akses berada pada layanan pihak ketiga | Sedang | Tinggi | Jangan aktifkan sebelum OQ-34 disetujui; akun/domain instansi, MFA, allowlist pengguna, log review, expiry, egress policy, dan prosedur penghentian wajib | Mentor, TIK/keamanan; administrator OPEN QUESTION | Terbuka |
| R-20 | Target 25 pengguna dianggap kapasitas terjamin tanpa load test pada host aktual | Demo lambat/gagal, database kehabisan koneksi, atau data rusak saat beban | Sedang | Sedang | Tetapkan skenario dan SLA; uji ramp-up, steady state, spike, koneksi DB, CPU/RAM/disk; uji backup/restore; jangan gunakan data asli | Pengembang; administrator OPEN QUESTION | Terbuka |
| R-21 | Go/Rust/mobile ditambahkan sebelum boundary dan kebutuhan stabil | Kompleksitas deployment, keamanan, test, dan handover meningkat; MVP terlambat | Sedang | Sedang | Modular monolith tetap baseline; butuh metrik, ADR baru, owner operasional, dan acceptance criteria sebelum ekstraksi service/klien | Project lead, Mentor | Diterima untuk roadmap; dicegah pada MVP |
| R-22 | Akun utama memiliki override konten atau file terbit dapat ditimpa/dihapus | Hilangnya bukti kerja, manipulasi rekaman, versi RAG tidak dapat ditelusuri, dan audit tidak dapat dipercaya | Sedang | Tinggi | Pisahkan administrasi akses dari kepemilikan konten; PUBLISHED immutable; koreksi lewat versi baru; withdrawal mempertahankan bukti; grant terbatas scope/waktu; separation of duties dan audit wajib | Mentor, knowledge owner, TIK/keamanan | Terbuka (OQ-35) |
| R-23 | Framework pemrosesan multimodal pihak ketiga membaca path lokal, mengikuti referensi tidak tepercaya, mengirim konten ke provider eksternal, atau menghabiskan resource host | Kebocoran dokumen/kredensial, hasil ingestion salah, denial of service, dan pelanggaran lokasi pemrosesan | Sedang | Tinggi | Adapter terisolasi tanpa DB/egress; input/output volume terbatas; tolak symlink/path/URL eksternal; pin minimal 1.4.2 dan blokir 1.4.1; SBOM/dependency scan; batas CPU/RAM/waktu/disk; fallback parser Python; hanya data simulasi sampai OQ-11 dan review keamanan selesai | Pengembang; TIK/keamanan dan pemilik data OPEN QUESTION | Terbuka |
| R-24 | Aplikasi, respons, dokumen, atau hasil SAVI terekspos ke internet, cache, crawler, AI Search, SEO/GEO/AIO, agent/model eksternal, telemetry, atau exfiltration melalui jailbreak | Kebocoran data sensitif, penyebaran tidak terkendali, pelanggaran tata kelola, dan hilangnya kepercayaan | Sedang | Tinggi | Private-data lock fail-closed; no-store; anti-index; robots deny-all; CSP same-origin; docs API nonpublik; RBAC dan klasifikasi sebelum retrieval; pola exfiltration ditolak; data asli dilarang; sebelum data asli wajib jaringan privat, firewall egress deny-by-default, SSO/MFA, TLS, audit, dan pentest | Project lead, Pengembang; TIK/keamanan dan pemilik data OPEN QUESTION | Termitigasi sebagian; infrastruktur belum diverifikasi |
| R-25 | Limiter memori dianggap perlindungan produksi atau alamat proxy dianggap IP pengguna | Batas dapat terpecah antarworker, hilang saat restart, atau seluruh pengguna berbagi satu identitas; abuse dan denial of service tetap mungkin | Sedang | Sedang | Label satu proses; forwarded address hanya dari CIDR proxy eksplisit dan fail-closed; batas key; paket Nginx localhost-only; limit global/per kelompok; load test dan observability host tetap wajib | Pengembang; administrator dan TIK/keamanan OPEN QUESTION | Termitigasi sebagian |

## Status Risiko

| Status | Arti |
|---|---|
| Terbuka | Belum ada mitigasi memadai |
| Termitigasi sebagian | Kontrol ada di scaffold, belum diuji pada data atau lingkungan riil |
| Diterima | Risiko disadari dan diterima untuk fase ini |
| Ditutup | Tidak relevan lagi atau mitigasi tervalidasi |

## Aturan Tinjauan

- **PROPOSED**: Register ditinjau minimal setiap akhir bulan sesuai roadmap enam bulan dan setiap kali ada jawaban mentor atas OQ terkait.
- **PROPOSED**: Risiko baru diberi ID berikutnya (R-13 dan seterusnya); ID tidak dipakai ulang.
- **PROPOSED**: Risiko yang ditutup tetap tercatat dengan tanggal dan alasan.
- **PROPOSED**: Insiden yang mewujudkan risiko dicatat sesuai [incident-response](../06-security/incident-response.md) dan dikaitkan ke ID risiko.
- **PROPOSED**: Kebocoran atau kehilangan data diperlakukan sebagai bug P0 yang memblokir rilis (sumber: Proposal v2.4, slide 20; lihat [bug-severity](../10-testing/bug-severity.md)).

## Related Documents

- [threat-model](../06-security/threat-model.md)
- [open-questions](../00-project/open-questions.md)
- [assumptions](../00-project/assumptions.md)
- [decision-log](decision-log.md)
- [known-limitations](../13-handover/known-limitations.md)
