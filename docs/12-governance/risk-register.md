# Register Risiko

**Status:** PROPOSED
**Last Updated:** 2026-10-02

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
| R-12 | Perbedaan daftar tim kerja | Lingkup akses dan dashboard keliru | Sedang | Sedang | Seed hanya enam tim brief; tabel `teams` dapat diperluas; OQ-02 diajukan | Mentor | Terbuka |

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
