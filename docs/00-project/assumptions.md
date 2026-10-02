# Asumsi

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose

Dokumen ini mencatat asumsi kerja yang dipakai untuk membangun scaffold SUNOVATE. Asumsi berbeda dengan keputusan: asumsi dipakai agar pengembangan dapat berjalan, tetapi harus divalidasi. Setiap asumsi memiliki dampak bila salah dan pemilik validasi. Pemilik validasi seluruh asumsi adalah mentor, kecuali dinyatakan lain.

## Cara Membaca

- Status `OPEN` berarti belum divalidasi. Status `VALIDATED` atau `REJECTED` hanya diubah setelah keputusan dicatat di [decision-log.md](../12-governance/decision-log.md).
- Kolom "Terkait" menunjuk pertanyaan terbuka (OQ), risiko (R), atau ADR.

## Daftar Asumsi

| ID | Asumsi | Dampak bila salah | Pemilik validasi | Terkait | Status |
|---|---|---|---|---|---|
| A-01 | Seluruh data selama pengembangan adalah `SIMULATED_DATA`; tidak ada data internal, data keuangan, atau data pribadi asli yang dimasukkan. | Risiko kebocoran data; perlu kontrol klasifikasi, retensi, dan lokasi hosting sebelum data asli masuk. | Mentor | R-03, [simulated-data-policy.md](../04-data/simulated-data-policy.md) | OPEN |
| A-02 | Scope awal adalah enam tim kerja: PPSUN, AKPSUN, PSUN, PPPSUN, DHTV, SUN Tematik. | Seed data, team scope, dan dashboard harus disesuaikan bila daftar tim berubah. | Mentor | OQ-02, R-12 | OPEN |
| A-03 | Fungsi SUN Tematik belum diketahui sehingga tim ini hanya ada sebagai entitas tim tanpa perilaku khusus. | Bila ada proses khusus, perlu tambahan knowledge type, alur kerja, atau dashboard. | Mentor | OQ-01 | OPEN |
| A-04 | Identitas pengembangan memakai token HMAC dari `POST /api/v1/auth/dev/login` untuk pengguna simulasi; dimatikan di luar development, dan aplikasi menolak start bila `APP_ENV=production` dengan dev auth aktif. | Bila mekanisme login organisasi berbeda jauh, modul identitas dan alur sesi frontend perlu diganti. | Mentor | OQ-07, ADR-005 | OPEN |
| A-05 | Tidak ada integrasi produksi (SharePoint, SSO, Power BI, Telegram, WhatsApp, Kemenkeu Satu, data pasar) selama MVP; semua provider produksi berupa placeholder nonaktif. | Bila integrasi wajib untuk MVP, jadwal bulan 5 dan kesiapan akses harus dihitung ulang. | Mentor | OQ-06, OQ-08, R-05 | OPEN |
| A-06 | Runtime scaffold memakai `DATA_BACKEND=simulated`, yaitu penyimpanan in-memory yang dimuat dari dataset yang sama dengan seed database. Data hilang saat API restart. | Bila dianggap persistence produksi, perubahan pengguna hilang; repository SQLAlchemy harus diprioritaskan. | Mentor | ADR-007, R-10 | OPEN |
| A-07 | Provider AI pengembangan bersifat deterministik dan ekstraktif (`development_extractive`): jawaban disusun hanya dari chunk terotorisasi, tanpa model eksternal dan tanpa jaringan. | Kualitas jawaban di demo tidak mewakili model generatif; evaluasi ulang diperlukan setelah model disetujui. | Mentor | OQ-11, ADR-008 | OPEN |
| A-08 | Provider embedding nonaktif; pencarian semantik belum berjalan, dan kolom vektor tidak bertipe tetap serta tanpa indeks ANN sampai model dan dimensi disetujui. | Target retrieval semantik pada bulan 3 bergeser bila model tidak segera disetujui. | Mentor | OQ-11, ADR-009 | OPEN |
| A-09 | Klasifikasi data memakai usulan empat tingkat PUBLIC, INTERNAL, RESTRICTED, CONFIDENTIAL, dengan `HERMES_MAX_CLASSIFICATION=RESTRICTED` di development. | Bila skema resmi Kemenkeu berbeda, tabel `data_classifications`, matriks akses, dan uji keamanan harus diubah. | Mentor | OQ-05, R-09 | OPEN |
| A-10 | Matriks peran dan izin delapan peran pengembangan (system_admin sampai read_only) cukup untuk MVP. | Peran tambahan atau kewenangan berbeda memerlukan perubahan seed dan uji otorisasi. | Mentor | OQ-09, OQ-12 | OPEN |
| A-11 | Publikasi knowledge hanya melalui approval request bertipe `KNOWLEDGE_PUBLICATION` yang disetujui, dan pengaju tidak dapat memutuskan permintaannya sendiri. | Alur publikasi dan audit perlu diubah bila kewenangan berbeda. | Mentor | OQ-12 | OPEN |
| A-12 | Ambang "jatuh tempo dekat" adalah 7 hari (`DEADLINE_DUE_SOON_DAYS`). | Status tenggat di dashboard tidak sesuai praktik tim. | Mentor | OQ-15 | OPEN |
| A-13 | Docker tidak terpasang di mesin pengembang saat ini; migrasi divalidasi memakai PostgreSQL sementara melalui paket Python `pgserver` sebagai alat bantu validasi, bukan dependensi proyek. | `docker-compose.yml` belum diuji langsung di mesin ini; perlu verifikasi di lingkungan yang memiliki Docker. | Pengembang, dikonfirmasi mentor untuk lingkungan uji | OQ-20 | OPEN |
| A-14 | File sumber PDF dan PPTX di root tidak dimasukkan ke Git sampai klasifikasinya dikonfirmasi. | Bila boleh disimpan, struktur `references/source` perlu diperbarui. | Mentor | OQ-18, ADR-014 | OPEN |
| A-15 | Tabel bisnis SUN (instrumen, lelang, transaksi, yield, setelmen) tidak diperlukan pada fase ini. | Bila diperlukan, perlu desain domain baru dan validasi sumber data. | Mentor | ADR-013 | OPEN |
| A-16 | Hosting, lokasi pemrosesan AI, dan residensi data akan ditentukan instansi sebelum ada data asli. | Arsitektur deployment dan pilihan model dapat berubah. | Mentor | OQ-07, OQ-11 | OPEN |

## Asumsi yang Sengaja Tidak Dibuat

- Tidak ada asumsi tentang jabatan, rantai persetujuan, atau kewenangan staf di luar peran pengembangan yang tercatat.
- Tidak ada asumsi tentang angka SUN, pembiayaan, yield, atau hasil lelang.
- Tidak ada asumsi bahwa pola SUN Job Monitor dapat dipakai ulang (OQ-19).

## Risks

- R-01 Asumsi proses bisnis tanpa validasi.
- R-10 Simulated store disangka persistence produksi.

## Acceptance Criteria

- Setiap asumsi memiliki status yang diperbarui setelah sesi dengan mentor.
- Asumsi yang ditolak memicu pembaruan dokumen terdampak dan entri di decision log.

## Related Documents

- [open-questions.md](open-questions.md)
- [architecture-decisions.md](../03-architecture/architecture-decisions.md)
- [known-limitations.md](../13-handover/known-limitations.md)

## Last Updated

2026-10-01
