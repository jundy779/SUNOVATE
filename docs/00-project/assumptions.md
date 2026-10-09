# Asumsi

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-09

## Purpose

Dokumen ini mencatat asumsi kerja yang dipakai untuk membangun scaffold SUNOVATE. Asumsi berbeda dengan keputusan: asumsi dipakai agar pengembangan dapat berjalan, tetapi harus divalidasi. Setiap asumsi memiliki dampak bila salah dan pemilik validasi. Pemilik validasi seluruh asumsi adalah mentor, kecuali dinyatakan lain. Pada 2026-10-02 sebagian asumsi diperbarui setelah deck proposal versi tetap `v1_` (slide 24) memuat jawaban knowledge owner; jawaban tersebut berlabel `CONFIRMED (knowledge owner, deck v1_ slide 24)` dan pengakuan mentor masih tertunda (OQ-24), sehingga status asumsi terkait belum menjadi `VALIDATED`.

## Cara Membaca

- Status `OPEN` berarti belum divalidasi. Status `PARTIAL` berarti ada jawaban knowledge owner yang menyentuh asumsi tetapi belum lengkap atau belum diakui mentor. Status `VALIDATED` atau `REJECTED` hanya diubah setelah keputusan dicatat di [decision-log.md](../12-governance/decision-log.md) dan diakui mentor (OQ-24).
- Kolom "Terkait" menunjuk pertanyaan terbuka (OQ), risiko (R), atau ADR.

## Daftar Asumsi

| ID | Asumsi | Dampak bila salah | Pemilik validasi | Terkait | Status |
|---|---|---|---|---|---|
| A-01 | Seluruh data selama pengembangan adalah `SIMULATED_DATA`; tidak ada data internal, data keuangan, atau data pribadi asli yang dimasukkan. | Risiko kebocoran data; perlu kontrol klasifikasi, retensi, dan lokasi hosting sebelum data asli masuk. | Mentor | R-03, [simulated-data-policy.md](../04-data/simulated-data-policy.md) | OPEN |
| A-02 | Scope awal adalah enam tim kerja: PPSUN, AKPSUN, PSUN, PPPSUN, DHTV, SUN Tematik. Jawaban knowledge owner untuk pilot ("6 tim", deck `v1_` slide 24) konsisten dengan asumsi ini, tetapi tidak menyebut nama tim (tafsiran PROPOSED). | Seed data, team scope, dan dashboard harus disesuaikan bila daftar tim berubah. | Mentor | OQ-02, OQ-03, DEC-20261002-01, R-12 | PARTIAL |
| A-03 | Fungsi SUN Tematik belum diketahui sehingga tim ini hanya ada sebagai entitas tim tanpa perilaku khusus. | Bila ada proses khusus, perlu tambahan knowledge type, alur kerja, atau dashboard. | Mentor | OQ-01 | OPEN |
| A-04 | Identitas pengembangan memakai token HMAC dari `POST /api/v1/auth/dev/login` untuk pengguna simulasi; dimatikan di luar development, dan aplikasi menolak start bila `APP_ENV=production` dengan dev auth aktif. | Bila mekanisme login organisasi berbeda jauh, modul identitas dan alur sesi frontend perlu diganti. | Mentor | OQ-07, ADR-005 | OPEN |
| A-05 | Tidak ada integrasi produksi (SharePoint, SSO, Power BI, Telegram, WhatsApp, Kemenkeu Satu, data pasar) selama MVP; semua provider produksi berupa placeholder nonaktif. Knowledge owner menjawab "bisa" untuk Telegram dan WhatsApp pada penggunaan internal (OQ-08), tetapi itu belum menjadi akun, token, atau persetujuan penyedia; keduanya tetap P2 dan tidak diaktifkan. | Bila integrasi wajib untuk MVP, jadwal bulan 5 dan kesiapan akses harus dihitung ulang. | Mentor | OQ-06, OQ-08, OQ-22, DEC-20261002-06, R-05 | PARTIAL |
| A-06 | Runtime scaffold memakai `DATA_BACKEND=simulated`, yaitu penyimpanan in-memory yang dimuat dari dataset yang sama dengan seed database. Data hilang saat API restart. | Bila dianggap persistence produksi, perubahan pengguna hilang; mode persisten `DATA_BACKEND=postgres` tersedia sebagai PROPOSED (ADR-015). | Mentor | ADR-007, ADR-015, R-10 | OPEN |
| A-07 | Provider AI pengembangan bersifat deterministik dan ekstraktif (`development_extractive`): jawaban disusun hanya dari chunk terotorisasi, tanpa model eksternal dan tanpa jaringan. | Kualitas jawaban di demo tidak mewakili model generatif; evaluasi ulang diperlukan setelah model disetujui. | Mentor | OQ-11, ADR-008 | OPEN |
| A-08 | Provider embedding nonaktif; pencarian semantik belum berjalan, dan kolom vektor tidak bertipe tetap serta tanpa indeks ANN sampai model dan dimensi disetujui. | Target retrieval semantik pada bulan 3 bergeser bila model tidak segera disetujui. | Mentor | OQ-11, ADR-009 | OPEN |
| A-09 | Klasifikasi data memakai usulan empat tingkat PUBLIC, INTERNAL, RESTRICTED, CONFIDENTIAL, dengan `HERMES_MAX_CLASSIFICATION=RESTRICTED` di development. | Bila skema resmi Kemenkeu berbeda, tabel `data_classifications`, matriks akses, dan uji keamanan harus diubah. | Mentor | OQ-05, R-09 | OPEN |
| A-10 | Matriks peran dan izin delapan peran pengembangan (system_admin sampai read_only) cukup untuk MVP. | Peran tambahan atau kewenangan berbeda memerlukan perubahan seed dan uji otorisasi. | Mentor | OQ-09, OQ-12 | OPEN |
| A-11 | Publikasi knowledge hanya melalui approval request bertipe `KNOWLEDGE_PUBLICATION` yang disetujui, dan pengaju tidak dapat memutuskan permintaannya sendiri. | Alur publikasi dan audit perlu diubah bila kewenangan berbeda. | Mentor | OQ-12 | OPEN |
| A-12 | Ambang "jatuh tempo dekat" adalah 7 hari (`DEADLINE_DUE_SOON_DAYS`). | Status tenggat di dashboard tidak sesuai praktik tim. | Mentor | OQ-15 | OPEN |
| A-13 | Docker tidak terpasang di mesin pengembang saat ini; migrasi divalidasi memakai PostgreSQL sementara melalui paket Python `pgserver` sebagai alat bantu validasi, bukan dependensi proyek. | `docker-compose.yml` belum diuji langsung di mesin ini; perlu verifikasi di lingkungan yang memiliki Docker. | Pengembang, dikonfirmasi mentor untuk lingkungan uji | OQ-20 | OPEN |
| A-14 | File sumber PDF dan PPTX di root tidak dimasukkan ke Git sampai klasifikasinya dikonfirmasi. | Bila boleh disimpan, struktur `references/source` perlu diperbarui. | Mentor | OQ-18, ADR-014 | OPEN |
| A-15 | Tabel bisnis SUN (instrumen, lelang, transaksi, yield, setelmen) tidak diperlukan pada fase ini. Knowledge owner menyebut "yield" dan "kepemilikan SBN" sebagai indikator dashboard (OQ-10); itu tercatat sebagai indikator yang diminta tanpa data, bukan alasan menambah tabel bisnis SUN. | Bila diperlukan, perlu desain domain baru dan validasi sumber data (OQ-21). | Mentor | ADR-013, OQ-10, OQ-21 | OPEN |
| A-16 | Lokasi pemrosesan AI dan residensi data akan ditentukan instansi sebelum ada data asli. Hosting sudah dijawab sebagian (lihat A-17). | Pilihan model dan arsitektur deployment dapat berubah. | Mentor | OQ-07, OQ-11 | OPEN |
| A-17 | Hosting untuk pilot adalah satu komputer tersendiri yang berperan sebagai server (jawaban knowledge owner atas OQ-07, deck `v1_` slide 24). Asumsi pengembang (PROPOSED): satu host untuk web, API, dan PostgreSQL di jaringan internal, tanpa redundansi, dengan backup dan administrator yang belum ditetapkan. | Bila server berbeda (mis. tidak ada akses jaringan, OS berbeda, atau harus ada redundansi), rencana deployment, backup, dan patching harus dirancang ulang; satu host juga berarti satu titik kegagalan (R-13). | Mentor | OQ-07, OQ-23, DEC-20261002-05, R-13 | PARTIAL |
| A-18 | Jawaban knowledge owner pada deck `v1_` slide 24 dipakai sebagai dasar kerja sambil menunggu pengakuan mentor. | Bila mentor tidak mengakui atau mengubah jawaban, dokumen dan rencana yang bergantung padanya harus direvisi (R-16). | Mentor | OQ-24, DEC-20261002-09, R-16 | OPEN |
| A-19 | Hak mengubah/mengunggah data pada pilot dibatasi untuk ketua tim, kasubdit PMP, Kasi MP, dan PIC yang ditunjuk; staf biasa tidak termasuk (jawaban knowledge owner atas OQ-05). Matriks izin saat ini belum mengikutinya (role `staff` masih dapat membuat dan mengubah knowledge dan dokumen). | Bila tidak diubah, perilaku sistem tidak sesuai jawaban; bila diubah tanpa konfirmasi peran, akses yang sah bisa tertutup. Perubahan diusulkan di [permission-matrix.md](../06-security/permission-matrix.md) dan belum diimplementasikan. | Mentor | OQ-05, OQ-25, DEC-20261002-03 | PARTIAL |
| A-20 | Target teknis demo adalah sekitar 25 pengguna dengan satu komputer kantor khusus; Docker Compose dan Nginx menjadi baseline paket. Cloudflare Tunnel/Access hanya opsi akses (arahan project lead, 2026-10-09). | Kapasitas belum terbukti dan jalur pihak ketiga dapat menambah risiko akses/data. | Mentor dan TIK/keamanan | OQ-20, OQ-23, OQ-34, ADR-016, R-19, R-20 | OPEN / NEEDS APPROVAL |
| A-21 | Python/FastAPI tetap backend inti. Go, Rust, PWA, Android, dan iOS bukan syarat MVP serta hanya masuk setelah kebutuhan terukur. | Penambahan prematur menaikkan biaya operasi, pengujian, dan handover. | Project lead, Mentor | ADR-016, TASK-015 sampai TASK-017 | PROPOSED |

## Asumsi yang Sengaja Tidak Dibuat

- Tidak ada asumsi tentang jabatan, rantai persetujuan, atau kewenangan staf di luar peran pengembangan yang tercatat.
- Tidak ada asumsi tentang angka SUN, pembiayaan, yield, atau hasil lelang.
- Tidak ada asumsi bahwa pola SUN Job Monitor dapat dipakai ulang (OQ-19).

## Risks

- R-01 Asumsi proses bisnis tanpa validasi.
- R-10 Simulated store disangka persistence produksi.
- R-13 Server tunggal khusus (A-17).
- R-16 Ketergantungan pada jawaban knowledge owner yang belum diakui mentor (A-18).
- R-17 Matriks izin belum selaras dengan jawaban hak unggah (A-19).

## Acceptance Criteria

- Setiap asumsi memiliki status yang diperbarui setelah sesi dengan mentor.
- Asumsi yang ditolak memicu pembaruan dokumen terdampak dan entri di decision log.

## Related Documents

- [open-questions.md](open-questions.md)
- [architecture-decisions.md](../03-architecture/architecture-decisions.md)
- [known-limitations.md](../13-handover/known-limitations.md)

## Last Updated

2026-10-09
