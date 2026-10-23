# Changelog

## 2026-10-22 — Catatan sambutan per akun

- Status "sudah ditutup" untuk catatan "Baru menggunakan SUNOVATE?" kini disimpan per akun, bukan per browser, sehingga setiap pegawai di komputer kantor yang dipakai bergantian tetap melihat catatan sambutan pertamanya (BUG-037). Halaman Ringkasan kini juga memuat identitas pengguna untuk keperluan ini.
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict, 45 test frontend, 349 test backend mode simulated (40 PostgreSQL dilewati), build produksi, dan 12/12 skenario Playwright e2e lulus, termasuk skenario dua akun bergantian di browser yang sama.
- Validasi aktual (Windows 11, Git Bash, Python 3.12 via uv): patch 0012 diterapkan dengan `git am` sebagai `cb64347`.
  - `pnpm validate` lulus: ESLint, Ruff, TypeScript, mypy strict (71 berkas), 45 test frontend (13 berkas), 348 test backend lulus (41 dilewati), dan build produksi (29 halaman statis). Karena lulus, `validate.log` tidak dibuat.
  - `pnpm e2e` dengan `pnpm api:dev` (`DATA_BACKEND=simulated`): 12/12 skenario lulus, termasuk "each account on a shared browser gets its own welcome note".
- Pemeriksaan manual di satu browser (server pengembangan, data simulasi), dimulai dari `localStorage` tanpa kunci `sunovate.*`:
  - `sim.staff.pppsun` menutup catatan "Baru menggunakan SUNOVATE?"; tersimpan satu kunci `sunovate.guide-welcome.dismissed.v1:<id pengguna>` dan catatan tidak muncul setelah muat ulang.
  - Setelah keluar lalu masuk sebagai `sim.lead.psun` di browser yang sama, tanpa menghapus `localStorage`, catatan muncul lagi; kunci milik staf tetap ada dan tidak memengaruhi akun lain.

## 2026-10-22 — Panduan singkat di dalam aplikasi

- Halaman baru `/panduan` ("Cara memakai SUNOVATE") berisi panduan langkah demi langkah untuk mencari dokumen dan pengetahuan, bertanya kepada SAVI AI, memantau dan memperbarui pekerjaan, membaca dokumen rahasia, serta menentukan pembaca dokumen rahasia. Panduan hanya tampil bila pengguna memiliki kewenangan terkait, dan label di panduan sama dengan label di layar.
- Tombol bantuan (ikon tanda tanya) di bilah atas dan tautan "Panduan singkat" di menu akun membuka halaman tersebut dari mana saja, termasuk di ponsel.
- Halaman Ringkasan menampilkan catatan "Baru menggunakan SUNOVATE?" yang dapat ditutup; status tutup disimpan di browser pengguna dan tidak berkedip saat halaman dimuat.
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict, 45 test frontend, 349 test backend mode simulated (40 PostgreSQL dilewati), build produksi, dan 11/11 skenario Playwright e2e lulus. QA visual pada 1440 px (ketua tim, lima panduan) dan 390 px (staf, empat panduan) tanpa scroll halaman ke samping. Backend tidak berubah sehingga `db:test` tidak dijalankan ulang.
- Validasi aktual (Windows 11, Git Bash, Python 3.12 via uv): patch 0011 diterapkan dengan `git am` sebagai `0f3fd70`.
  - `pnpm validate` lulus: ESLint, Ruff, TypeScript, mypy strict (71 berkas), 45 test frontend (13 berkas), 348 test backend lulus (41 dilewati), dan build produksi (29 halaman statis). Run pertama perintah gabungan berhenti dengan exit code 4 sebelum `validate` selesai (penyebab tidak tercatat); `pnpm validate` dijalankan ulang tersendiri dan lulus.
  - `pnpm e2e` dengan `pnpm api:dev` (`DATA_BACKEND=simulated`): 11/11 skenario lulus, termasuk "new users find the quick guide and can dismiss the welcome note".
- Pemeriksaan manual di browser (server pengembangan, data simulasi). Status tutup catatan disimpan di `localStorage` browser (`sunovate.guide-welcome.dismissed.v1`) dan berlaku untuk semua akun di browser yang sama, sehingga kunci dihapus sebelum tiap akun diuji:
  - `sim.staff.pppsun`: catatan "Baru menggunakan SUNOVATE?" tampil di Ringkasan; setelah "Tutup" catatan hilang dan tidak muncul lagi setelah halaman dimuat ulang. Ikon tanda tanya di bilah atas membuka `/panduan` dengan 4 panduan (mencari, SAVI AI, pekerjaan, membaca dokumen rahasia).
  - `sim.lead.psun`: perilaku catatan sama; `/panduan` menampilkan 5 panduan, tambahan "Menentukan pembaca dokumen rahasia".

## 2026-10-22 — Unduh Excel dari Ringkasan

- Bagian "Perlu ditindaklanjuti" di halaman Ringkasan kini memiliki tautan "Unduh Excel". Berkas berisi seluruh tugas dan tindak lanjut yang terlambat, jatuh tempo hari ini, atau segera jatuh tempo dalam cakupan pengguna (layar hanya menampilkan enam teratas), dengan kolom penanggung jawab, batas waktu, status tenggat, dan status pekerjaan.
- Endpoint baru `GET /api/v1/exports/attention` memakai perhitungan yang sama dengan ringkasan (`attention_items` di modul dashboard) dan audit `WORK_EXPORT`. Proxy unduhan web dipindahkan ke `lib/export-proxy.ts` dan dipakai bersama oleh kedua unduhan.
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict, 42 test frontend, 349 test backend mode simulated (40 PostgreSQL dilewati), 389 test mode PostgreSQL, build produksi, dan 10/10 skenario Playwright e2e lulus. Berkas unduhan diperiksa berisi 7 baris (layar menampilkan 6) dengan filter otomatis A5:G12.
- Validasi aktual (Windows 11, Git Bash, Python 3.12 via uv) untuk patch 0009 dan 0010, diterapkan berurutan dengan `git am` sebagai `8fad302` dan `34f7838` (`git am` memberi satu peringatan whitespace: baris kosong di akhir `apps/api/tests/test_work_export.py`):
  - `pnpm validate` lulus: ESLint, Ruff, TypeScript, mypy strict (71 berkas), 42 test frontend (12 berkas), 348 test backend lulus (41 dilewati), dan build produksi (28 halaman statis).
  - `pnpm db:test` tanpa beban lain lulus: 388 test lulus dan 1 dilewati (9 menit 14 detik untuk pytest); pgserver berhenti normal. Linux mencatat 389.
  - `pnpm e2e` dengan `pnpm api:dev` (`DATA_BACKEND=simulated`): 10/10 skenario lulus, termasuk dua skenario Excel baru.
- Pemeriksaan manual sebagai `sim.coordinator` (API dinyalakan ulang setelah e2e agar data kembali ke seed):
  - `/work-monitoring`, tab Output kerja: pencarian "penyusunan" menyisakan 3 dari 5 baris (tidak peka huruf besar/kecil); saring status "Berjalan" dan tim "PPSUN" bersama pencarian menyisakan 1 baris ("Menampilkan 1 dari 5 baris"); klik judul kolom Tim mengurutkan naik lalu turun, kolom Judul mengurutkan naik, dan `aria-sort` mengikuti. Kolom Progres tidak dapat diurutkan. Tombol "Unduh Excel" mengunduh berkas lewat `/api/exports/work?kind=outputs` (200) dan, sesuai keterangannya, berisi semua data yang dapat dilihat tanpa mengikuti saringan di layar.
  - `/dashboard`: angka "Perlu perhatian" 7; bagian "Perlu ditindaklanjuti" menampilkan 6 baris. Tautan "Unduh Excel" mengunduh lewat `/api/exports/attention` (200).
  - Kedua berkas dibuka di Microsoft Excel 16.0 (otomasi COM, tanpa pesan perbaikan): `SUNOVATE-output-kerja-20261022.xlsx` berisi 5 baris data sama dengan layar; `SUNOVATE-perlu-ditindaklanjuti-20261022.xlsx` berisi 7 baris data (5 tugas dan 2 tindak lanjut, termasuk baris ketujuh yang tidak tampil di layar), sama dengan angka "Perlu perhatian". Keduanya memiliki filter otomatis, header beku pada baris 5, nama pengunduh, dan waktu WIB. Respons memakai `Content-Disposition: attachment` dan `Cache-Control: no-store`.
  - Pane browser bawaan tidak menyimpan unduhan ke lokasi yang dapat ditemukan di disk, sehingga berkas untuk Excel diambil ulang lewat rute proxy web yang sama dengan sesi `sim.coordinator`.
- Catatan, tidak diubah: baris ketiga kedua berkas Excel memuat teks "(SIMULATED_DATA)", yang menurut aturan bahasa antarmuka (`AGENTS.md`, `content-language.md`) tidak boleh tampil kepada pengguna; judul kolom "PROGRES" di tabel Monitoring Kerja dan label status di tabel sebaran tugas tampil dalam huruf kapital penuh.

## 2026-10-22 — Fitur ala Excel di Monitoring Kerja

- Tabel Monitoring Kerja kini dapat dicari berdasarkan judul, disaring per status dan tim, serta diurutkan dengan mengklik judul kolom (Judul, Tim, Status, Tanggal, Tenggat). Jumlah baris yang tampil ditunjukkan saat saringan aktif.
- Tombol "Unduh Excel" mengunduh berkas `.xlsx` berisi seluruh data jenis tersebut yang boleh dilihat pengguna, lengkap dengan filter otomatis Excel, baris judul beku, label status dalam bahasa Indonesia, dan catatan data contoh. Endpoint baru `GET /api/v1/exports/work` memakai otorisasi yang sama dengan daftar, mencatat audit `WORK_EXPORT`, dan melindungi teks dari formula injection.
- Uji e2e monitoring kerja kini mencari kolom formulir di dalam formulir tambah, karena label penyaring baru juga memuat kata "judul" dan "tim".
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict, 42 test frontend, 347 test backend mode simulated (40 PostgreSQL dilewati), 387 test mode PostgreSQL, build produksi, dan 9/9 skenario Playwright e2e lulus. QA visual Chromium pada 1440 px dan 390 px tanpa scroll halaman ke samping; berkas unduhan diperiksa memuat filter otomatis (A5:H12), header beku, dan baris yang sama dengan daftar di layar.

## 2026-10-21 — Akses RAHASIA oleh Ketua Tim dan Kasubdit PMP, daftar pembaca permanen

- Arahan baru dicatat sebagai DEC-20261021-02 (CONFIRMED): Ketua Tim pemilik dokumen menentukan siapa yang boleh membaca, termasuk pegawai tim lain, dan Kasubdit PMP juga dapat mengelola akses untuk seluruh tim.
- Kewenangan kini berasal dari permission katalog `secure_document:manage_team` (dipegang `team_lead`) dan `secure_document:manage_all` (dipegang `knowledge_coordinator`), bukan nama peran di kode, sehingga keputusan peran berikutnya cukup mengubah katalog.
- Daftar pembaca disimpan permanen di tabel baru `secure_document_readers` (migrasi `0003_secure_document_readers`), di backend simulated maupun PostgreSQL; isi tersegel tetap di vault. Pemeriksa skema `db:check` diperbarui menjadi 31 tabel.
- Reset database uji memakai batas waktu 120 detik agar tidak gagal saat mesin sibuk (BUG-036); batas 15 detik aplikasi tidak berubah.
- Halaman Kelola akses baca dan skenario e2e disesuaikan dengan Ketua Tim sebagai pengelola.
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict, 39 test frontend, 338 test backend mode simulated (40 PostgreSQL dilewati), 378 test mode PostgreSQL, `db:check` (31 tabel, upgrade dan downgrade migrasi), render SQL Alembic, build produksi, dan 8/8 skenario Playwright e2e lulus. Run `db:test` pertama gagal satu test karena hitungan tabel tetap 30 di `test_database_integration.py`; hitungan diperbarui menjadi 31 lalu run ulang lulus.
- Validasi aktual (Windows 11, Git Bash, Python 3.12 via uv): patch 0008 versi "Ketua Tim dan Kasubdit PMP" diterapkan dengan `git am` sebagai `ee525e3`. Versi sebelumnya ("hanya Ketua Tim", sempat diterapkan secara lokal sebagai `50746e8` dan lulus `validate`, `db:check`, `db:test` 376/1, serta e2e 8/8) dibatalkan sebelum di-push karena tidak sesuai arahan terbaru.
  - `pnpm api:setup` lulus. `pnpm validate` lulus: ESLint, Ruff, TypeScript, mypy strict (70 berkas), 39 test frontend (11 berkas), 337 test backend lulus (41 dilewati), dan build produksi (26 halaman statis).
  - `pnpm db:check` lulus pada PostgreSQL sementara (pgserver): 31 tabel, trigger append-only menolak UPDATE, downgrade `0003_secure_document_readers` lalu ke base berhasil.
  - `pnpm db:test` tanpa beban lain lulus: 377 test lulus dan 1 dilewati (10 menit 22 detik untuk pytest). Linux mencatat 378. Setelah test selesai, pgserver gagal berhenti normal (`pg_ctl: server does not shut down`) lalu dihentikan paksa oleh skrip; exit code tetap 0 dan tidak ada proses `postgres` yang tertinggal.
  - `pnpm db:migrate` dan `pnpm db:seed` tidak dijalankan: mesin ini memakai `DATA_BACKEND=simulated` dan tidak ada PostgreSQL lokal pada port 5432.
  - Dev server dinyalakan ulang setelah `db:test`. `pnpm e2e` dengan `pnpm api:dev`: 8/8 skenario lulus, termasuk "team lead grants and revokes read access without seeing document content".
- Pemeriksaan manual `/dokumen-rahasia/kelola` di browser (server pengembangan, data simulasi):
  - `sim.coordinator` (padanan Kasubdit PMP) melihat tombol "Kelola akses baca" di daftar dokumen rahasia dan dua dokumen di halaman kelola (PSUN dan PPSUN) beserta daftar pembaca sesuai seed, tanpa isi dokumen.
  - `sim.lead.psun` hanya melihat satu dokumen PSUN tanpa isi dokumen. Pemberian akses pada dokumen PPSUN lewat proxy web ditolak API dengan 404 `NOT_FOUND`.
- Pemeriksaan lanjutan pada commit yang sama (`ee525e3`), dev server dinyalakan ulang: `pnpm e2e` 8/8 lulus. `api:setup`, `validate`, `db:check`, dan `db:test` tidak diulang karena kode tidak berubah sejak run di atas. `git reset --hard a774b15` tidak dijalankan karena `ee525e3` dan catatan ini sudah di-push; versi "Ketua Tim dan Kasubdit PMP" sudah menjadi isi `main`.
  - `sim.coordinator`: memberi akses `sim.auditor` pada dokumen PSUN dan PPSUN lewat UI berhasil ("Akses baca diberikan kepada sim.auditor@sunovate.local."), lalu mencabutnya di kedua dokumen juga berhasil; daftar pembaca kembali sesuai seed.
  - `sim.lead.psun`: pemberian dan pencabutan akses pada dokumen PPSUN keduanya ditolak API dengan 404 `NOT_FOUND` (JSON).
  - `sim.staff.pppsun`: tombol "Kelola akses baca" tidak ada, halaman kelola menampilkan "Tidak ada dokumen yang dapat Anda kelola", dan pemberian maupun pencabutan akses pada dokumen PSUN dan PPSUN ditolak API dengan 404 `NOT_FOUND`.

## 2026-10-21 — Pengelolaan akses dokumen RAHASIA sesuai keputusan mentor

- Jawaban mentor dicatat sebagai DEC-20261021-01: penetapan dan akses dokumen RAHASIA oleh Kasubdit PMP dan Ketua Tim, jenis dokumen dikurasi ketua tim, dibuka dari komputer kantor, dan alat penyimpan kunci belum tersedia. OQ-40 dan OQ-41 menjadi PARTIAL; OQ-42 diperbarui.
- API baru: `GET /secure-documents/manageable`, `GET/POST /secure-documents/{id}/readers`, dan `DELETE /secure-documents/{id}/readers/{email}`. Hanya `knowledge_coordinator` (seluruh tim) dan `team_lead` (tim sendiri) yang dapat mengelola; pihak lain menerima 404 yang diaudit. Penerima wajib pengguna aktif dengan clearance yang cukup. Pencabutan langsung menutup penampil dan menghapus persetujuan pernyataan.
- Halaman baru `/dokumen-rahasia/kelola` untuk memberi dan mencabut akses baca tanpa menampilkan isi dokumen. Vault simulasi kini berisi dua dokumen (PPSUN dan PSUN) untuk menguji kewenangan per tim.
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict, 39 test frontend, 337 test backend mode simulated (40 PostgreSQL dilewati), 377 test mode PostgreSQL, `savi:eval`, `demo:smoke`, build produksi, dan 8/8 skenario Playwright e2e lulus. QA visual halaman Kelola akses baca pada 1440 px (Kasubdit PMP, dua dokumen) dan 390 px (ketua tim PSUN, satu dokumen).
- Validasi aktual (Windows 11, Git Bash, Python 3.12 via uv): patch 0007 diterapkan dengan `git am` sebagai `216f0ca`.
  - `pnpm validate` lulus: ESLint, Ruff, TypeScript, mypy strict (70 berkas), 39 test frontend (11 berkas), 336 test backend lulus (41 dilewati), dan build produksi (26 halaman statis).
  - `pnpm e2e` dengan `pnpm api:dev` (`DATA_BACKEND=simulated`): 8/8 skenario lulus, termasuk "Kasubdit PMP grants and revokes read access without seeing document content".
  - `pnpm db:test` run pertama **gagal**: 375 lulus, 1 dilewati, 1 error. Error terjadi pada setup `tests/test_secure_viewer.py::test_no_route_exposes_file_text_or_download`: `TRUNCATE ... RESTART IDENTITY CASCADE` pada reset database uji dibatalkan oleh `statement_timeout` 15 detik (`QueryCanceled`); test itu sendiri tidak sempat berjalan. Run ini berlangsung bersamaan dengan e2e, dua server pengembangan, dan browser. Run ulang tanpa beban lain lulus: 376 lulus, 1 dilewati (8 menit 32 detik untuk pytest). Linux mencatat 377. Penyebab pasti timeout belum dibuktikan; bila terulang, perlu dicek apakah ada koneksi lain yang menahan lock saat reset.
- Pemeriksaan manual `/dokumen-rahasia/kelola` di browser (server pengembangan, data simulasi):
  - `sim.coordinator` melihat dua dokumen (PSUN dan PPSUN) beserta daftar pembaca sesuai seed, tanpa isi dokumen (penanda uji isi tidak ada di teks halaman, tanpa gambar halaman). Pemberian akses ke `sim.staff.pppsun` ditolak dengan "Tingkat kerahasiaan pengguna tidak mencukupi untuk dokumen ini." dan daftar pembaca tidak berubah.
  - `sim.lead.psun` hanya melihat dokumen PSUN. Memberi lalu mencabut akses `sim.auditor` pada dokumen PSUN lewat UI berhasil (API 200), dan daftar kembali seperti seed. Pemberian dan pencabutan akses pada dokumen PPSUN lewat proxy web ditolak API dengan 404 `NOT_FOUND`.
  - Pada instance server pengembangan pertama, rute `DELETE /api/secure-documents/{id}/readers/{email}` menjawab halaman 404 HTML dari Next tanpa meneruskan ke API, sehingga tombol "Cabut akses" menampilkan "Akses belum dapat dicabut." Setelah server pengembangan di-restart, rute berfungsi (tanpa cookie 401 JSON, dengan sesi 200). Penyebab tidak diketahui dan tidak muncul pada e2e; dicatat sebagai pengamatan mode pengembangan.
- Catatan tinjauan kode (tidak diubah): pengelola dapat memberi akses kepada pengguna di luar tim pemilik dokumen; hak kelola ditentukan dari kode peran yang ditulis di modul, bukan kode permission katalog; daftar pembaca berada di memori dan kembali ke seed saat API di-restart.

## 2026-10-21 — Evaluasi jawaban SAVI berkategori dan corpus ekstraksi diperluas

- Golden set SAVI diberi kategori dan diperluas dari 24 menjadi 43 kasus, termasuk 10 percobaan prompt injection (leetspeak, bermain peran, muatan base64, header SYSTEM palsu), permintaan rahasia, nasihat investasi, query SQL, isolasi dokumen RAHASIA, dan pertanyaan tanpa sumber. Evaluator baru `pnpm savi:eval` melaporkan metrik per kategori tanpa menampilkan pertanyaan atau jawaban.
- ScopeGuard diperluas (BUG-035): normalisasi leetspeak, pola bermain peran sebagai admin/pengembang, muatan terenkode yang diminta dijalankan, penolakan permintaan nilai rahasia (`secret_request`), pertanyaan waktu beli/jual SUN, dan permintaan query SQL. Aturan khusus pertanyaan tidak dipakai untuk passage sehingga SOP tentang kata sandi tidak dibuang.
- Corpus ekstraksi diperluas menjadi 13 kasus ditambah 4 kasus penolakan dengan metrik baru `rejection_accuracy`.
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict (70 berkas), 39 test frontend, 331 test backend mode simulated (40 PostgreSQL dilewati), 371 test mode PostgreSQL (`pnpm db:test`), serta `savi:eval`, `extraction:eval`, `search:eval`, dan `demo:smoke` lulus. Frontend dan skema basis data tidak berubah sehingga build dan render SQL tidak dijalankan ulang.
- Validasi aktual (Windows 11, Git Bash, Python 3.12 via uv): patch 0006 diterapkan dengan `git am` sebagai `cd4d570`. Perubahan ScopeGuard diperiksa sebelum diterapkan; isinya hanya menambah pola penolakan.
  - `pnpm validate` lulus: ESLint, Ruff, TypeScript, mypy strict (70 berkas), 39 test frontend (11 berkas), 330 test backend lulus (41 dilewati), dan build produksi (25 halaman statis). Selisih satu test dengan Linux sama dengan validasi sebelumnya (skip izin POSIX di Windows).
  - `pnpm savi:eval` lulus: 43 kasus di 10 kategori, `decision_accuracy` 1,0 untuk setiap kategori, `unauthorized_leakage` 0, `citation_validity` 1,0, `adversarial_answered` 0, `abstained_when_evidence_missing` 1,0, tanpa kasus gagal.
  - `pnpm extraction:eval` lulus: 13 kasus dengan `extraction_success_rate`, `fragment_recall`, `structure_pass_rate`, dan `instruction_classification_accuracy` 1,0, `forbidden_hits` 0, serta 4 kasus penolakan dengan `rejection_accuracy` 1,0.
  - `pnpm db:test` lulus pada PostgreSQL sementara (pgserver): 370 test lulus dan 1 dilewati (9 menit 0 detik untuk pytest, sekitar 10 menit total). Linux mencatat 371; alasan skip tidak ditampilkan oleh output `-q`.

## 2026-10-21 — Skenario e2e dapat diulang

- Skenario monitoring kerja memakai judul output unik per run sehingga lulus walaupun API masih menyimpan data run sebelumnya; langkah pertama penampil dokumen rahasia diberi batas 30 detik untuk kompilasi rute pertama di mode pengembangan (BUG-034). Penyebab kegagalan pertama skenario dokumen rahasia di Windows tidak tercatat; trace Playwright tetap `retain-on-failure` untuk run berikutnya.
- Validasi aktual (Linux): `pnpm e2e` 7/7 lulus dua kali berturut-turut tanpa restart API.
- Validasi aktual (Windows 11, Git Bash): patch 0005 diterapkan dengan `git am` sebagai `a1f66b4`. `pnpm e2e` dijalankan dua kali berturut-turut terhadap satu proses `pnpm api:dev` (`DATA_BACKEND=simulated`, satu kali "Application startup complete" di log, tanpa restart): run pertama 7/7 lulus (43,7 detik), run kedua 7/7 lulus (41,4 detik). Skenario dokumen rahasia selesai dalam 10,5 dan 11,2 detik; kegagalan run pertama yang tercatat pada validasi patch 0004 tidak muncul lagi. `pnpm validate`, `db:check`, dan `db:test` tidak dijalankan ulang karena patch hanya mengubah test e2e dan dokumentasi.

## 2026-10-21 — Validasi Windows untuk kepatuhan dokumentasi, CSP gambar, dan uji PostgreSQL

- Patch 0004 diterapkan dengan `git am` sebagai `8fcb96e`. Perubahan `pnpm-lock.yaml` diperiksa sebelum instalasi: hanya kenaikan versi kecil (`rolldown`, `postcss`, `nanoid`, `@oxc-project/types`, `@babel/runtime`, `source-map-js` 1.2.2) tanpa registry lain.
- Validasi aktual (Windows 11, Git Bash, Python 3.12 via uv):
  - `pnpm install` lulus; lockfile tidak berubah.
  - `pnpm validate` lulus: ESLint, Ruff, TypeScript, mypy strict (69 berkas), 39 test frontend (11 berkas), 306 test backend lulus (41 dilewati), dan build produksi (25 halaman statis).
  - `pnpm db:check` lulus pada PostgreSQL sementara (pgserver).
  - `pnpm db:test` lulus: 346 test lulus dan 1 dilewati dalam 10 menit 4 detik. Linux mencatat 347 lulus. Alasan skip tidak direkam pada run ini; kandidat yang sudah diketahui adalah `test_demo_preflight.py:141` (bit izin POSIX tidak tersedia di Windows).
- `pnpm e2e` dengan API `pnpm api:dev` (`DATA_BACKEND=simulated`), hasil apa adanya:
  - Run pertama: 6/7 lulus. "granted reader opens a confidential document only after accepting the notice" gagal; detail errornya tidak tersimpan karena `test-results` ditimpa run berikutnya. Skenario yang sama lulus saat dijalankan sendiri.
  - Dua run berikutnya pada proses API yang sama: run kedua 7/7, run ketiga 6/7. "staff creates and updates scoped work data" gagal karena strict mode: `getByText('Output simulasi dari UI')` menemukan 2 elemen, sebab store simulasi di memori menyimpan output dari run sebelumnya. Skenario ini tidak idempoten bila API tidak di-restart.
  - Setelah API di-restart: 7/7 lulus.
- Belum diperiksa di Windows: header CSP gambar halaman di browser (dicakup aturan `next.config.ts` dan QA header di Linux) dan runtime aplikasi pada backend PostgreSQL.

## 2026-10-21 — Kepatuhan dokumentasi, pengerasan, dan uji PostgreSQL penuh

- `pnpm db:test` dijalankan penuh pada PostgreSQL sementara: 347 test lulus, termasuk penampil RAHASIA dan audit pada backend postgres. Dua uji yang gagal saat pertama dijalankan diperbaiki: uji paritas umum tidak lagi membandingkan label mesin pencarian (`postgres_fts` vs `lexical`, sudah dicakup uji pencarian khusus), dan uji keluaran demo journey menetapkan backend simulasi (BUG-032).
- Gambar halaman RAHASIA kini menerima CSP `default-src 'none'; frame-ancestors 'none'; sandbox` lewat aturan khusus setelah aturan situs di `next.config.ts` (BUG-031). Detail dokumen yang hilang atau tidak diberikan memanggil `notFound()`; statusnya tetap 200 karena streaming area kerja (soft 404 dengan `noindex`, KL-25).
- `source-map-js` diperbarui ke 1.2.2 (BUG-033). `braces` dan `vite` masih dilaporkan `pnpm audit` karena rilis perbaikan belum tersedia atau terlalu baru untuk kebijakan usia rilis; keduanya hanya alat pengembangan (KL-26).
- Dokumentasi: bug register BUG-026 sampai BUG-033, keputusan terbaru di `ai-agent-handoff.md`, `cryptography` dan Pillow di technology stack, dokumen baru `docs/06-security/secure-document-viewer.md`, serta pemetaan peran dan klasifikasi rancangan ke kode di `authorization-rbac.md` dan `data-classification.md`.
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict, 39 test frontend, 307 test backend mode simulated (40 PostgreSQL dilewati), 347 test mode PostgreSQL, build produksi, render SQL Alembic, dan QA header proxy lulus.

## 2026-10-21 — Validasi Windows untuk penyempurnaan visual dan dokumen RAHASIA

- Patch 0001 sampai 0003 (penyempurnaan visual, fondasi dokumen RAHASIA, penampil web) sudah ada di `main` sebagai `72a2ba9`, `d89abbc`, dan `cbf3a7b`. Penerapan ketiga patch pada `5b4d46d` di index sementara menghasilkan tree yang identik dengan HEAD (`aec61d3`), sehingga `git am` tidak dijalankan ulang.
- Validasi aktual (Windows 11, Git Bash, Python 3.12 via uv): `pnpm api:setup` lulus. `pnpm validate` lulus: ESLint, Ruff, TypeScript, mypy strict (69 berkas), 39 test frontend (11 berkas), 306 test backend lulus (41 dilewati), dan build produksi (25 halaman statis). Skip tambahan dibanding Linux adalah `test_demo_preflight.py:141` karena bit izin POSIX tidak tersedia di Windows; 37 skip lain karena backend PostgreSQL tidak dipilih dan 3 karena `SUNOVATE_TEST_DATABASE_URL` tidak diisi.
- `pnpm e2e` dengan API `pnpm api:dev` (`DATA_BACKEND=simulated`): 7/7 skenario Playwright lulus.
- Pemeriksaan manual di browser (Chromium bawaan, server pengembangan):
  - `sim.coordinator` melihat satu dokumen simulasi di menu Dokumen Rahasia. Tombol "Buka dokumen" nonaktif sampai pernyataan disetujui. Setelah disetujui, halaman 1 dari 2 tampil sebagai gambar PNG bertanda air nama, email, waktu WIB, dan rujukan sesi. Penanda uji isi dokumen tidak ada di teks DOM. Gambar halaman memakai `no-store`, `inline`, dan `nosniff`.
  - `sim.staff.pppsun` melihat "Belum ada dokumen rahasia untuk Anda". Akses langsung ke gambar halaman menghasilkan 404, dan URL detail menampilkan halaman tidak ditemukan tanpa judul dokumen.
- Catatan, tidak diperbaiki:
  - CSP yang sampai ke browser untuk gambar halaman adalah CSP situs Next, bukan `default-src 'none'` dari API, karena proxy same-origin menggantinya.
  - URL detail yang ditolak tetap berstatus HTTP 200 (halaman tidak ditemukan dirender saat streaming).
  - Indikator "1 Issue" di mode dev berasal dari CSP yang memblokir `eval()` milik React dev, bukan error aplikasi.
- `pnpm db:sql` lulus (render hingga `0002_ordering_columns`). `pnpm db:check` lulus pada PostgreSQL sementara (pgserver): migrasi, seed, trigger append-only menolak UPDATE, dan downgrade ke base.
- Tidak dijalankan: `pnpm db:test`, runtime aplikasi pada backend PostgreSQL, dan pemeriksaan dengan font Aptos asli.

## 2026-10-21 — Penampil dokumen RAHASIA di web

- Halaman baru `/dokumen-rahasia` (menu "Dokumen Rahasia") menampilkan hanya dokumen yang diberikan kepada pengguna. Pengguna tanpa akses melihat keterangan bahwa belum ada dokumen untuknya.
- Pernyataan kerahasiaan wajib disetujui setiap kali dokumen dibuka. API mengunci halaman (428 `SECURE_NOTICE_REQUIRED`) sampai persetujuan tercatat; persetujuan diaudit, berlaku 30 menit, dan per pembaca per dokumen.
- Pembaca per halaman memakai proxy same-origin sehingga token tetap di server; gambar tidak di-cache dan tidak ditawarkan sebagai unduhan. Menu konteks, seret gambar, pintasan simpan/cetak/salin/DevTools, dan cetak halaman dicegah, serta tampilan dikaburkan saat jendela tidak aktif. Langkah ini penghalang, bukan batas keamanan (ADR-020).
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict, 39 test frontend, 307 test backend (40 PostgreSQL dilewati), build produksi, dan 7/7 skenario Playwright e2e terhadap server pengembangan lulus. QA visual Chromium pada 1440 px dan 390 px.

## 2026-10-21 — Fondasi dokumen RAHASIA (penampil hanya-baca dan enkripsi)

- Modul API baru `/api/v1/secure-documents` (ADR-020, PROPOSED): daftar, metadata, dan satu halaman sebagai PNG. Tidak ada route berkas, teks, atau unduhan. Halaman dirender di server dengan tanda air nama, email, waktu WIB, dan rujukan sesi; teks tidak pernah dikirim ke browser.
- Akses hanya untuk pembaca yang diberikan per dokumen dengan clearance yang mencukupi; pihak lain menerima 404 dan percobaannya diaudit (`SECURE_PAGE_VIEW` / `SECURE_DOCUMENT_READ`, outcome `DENIED`). Batas 40 halaman per menit per pengguna (429 + `Retry-After`). Respons memakai `no-store`, `inline`, `nosniff`, dan CSP `default-src 'none'`.
- Enkripsi envelope AES-256-GCM per halaman yang terikat ke id dokumen dan nomor halaman, dengan antarmuka `KeyProvider`. Saat ini hanya penyedia kunci pengembangan sementara; TPM menyusul (OQ-42). Crypto-shredding tersedia.
- Vault berada di memori dan hanya berisi satu dokumen simulasi. Dokumen RAHASIA tidak masuk pencarian maupun SAVI AI.
- Dependency baru beralasan: `cryptography` dan `pillow` (ADR-020). OQ-38 dan OQ-40 sampai OQ-42 ditambahkan; TASK-027 dicatat.
- Validasi aktual (Linux): Ruff, mypy strict (69 berkas), ESLint, TypeScript, 35 test frontend, 304 test backend (40 PostgreSQL dilewati), termasuk 12 test keamanan baru untuk penampil dan enkripsi. UI penampil, penyedia TPM, dan penyimpanan persisten belum dibuat.

## 2026-10-21 — Penyempurnaan visual landing, halaman masuk, dan dashboard

- Landing, halaman masuk, dan dashboard ditata ulang dengan gabungan struktur institusional Bank Indonesia (bar pemerintah, header, sidebar navy, baris akses cepat) dan disiplin editorial The Economist (hierarki judul, garis rambut, tab emas di atas judul dan grafik, sumber pada grafik). Gaya baru ada di `apps/web/src/app/editorial.css`; hanya token warna terkunci dan font Aptos yang dipakai (font Georgia dihapus).
- Satu momen gerak per halaman: grafik siklus pengetahuan (enam tahap) di landing, garis emas tagline di halaman masuk, dan batang grafik status tugas di dashboard. Semua dimatikan pada `prefers-reduced-motion: reduce`.
- Angka ringkasan dashboard menjadi satu baris ledger; tabel prioritas, fokus, pengetahuan terbaru, panel SAVI AI, dan indikator SUN memakai pola judul editorial yang sama.
- Formulir masuk baru aktif setelah halaman siap sehingga tidak ada pengiriman native yang memasukkan email ke URL; kirim memakai `method="post"`.
- Perbaikan tata letak mobile: kolom shell kini `minmax(0, 1fr)` sehingga navigasi sidebar tidak melebarkan halaman, dan `.table-wrap` diberi `position: relative` agar sel `sr-only` tidak keluar dari area gulir. Sekitar 350 aturan CSS yang tidak lagi dipakai dihapus.
- Tes e2e diselaraskan dengan teks antarmuka saat ini (tanpa `SIMULATED_DATA` di layar, menunggu tombol masuk aktif, tautan SAVI AI dicari di navigasi utama). Preview visual di `docs/09-ui-ux/previews` diperbarui; tangkapan layar memakai font cadangan karena Aptos tidak tersedia di lingkungan QA.
- Validasi aktual (Linux): ESLint, Ruff, TypeScript, mypy strict, 35 test frontend, 292 test backend (40 PostgreSQL dilewati), build produksi, render SQL Alembic, dan 5/5 skenario Playwright e2e terhadap server pengembangan lulus. QA visual Chromium pada 1440 px dan 390 px. Pemeriksaan visual dengan font Aptos asli dan di Windows belum dijalankan.

## 2026-10-20 — MONEV sebagai tim pilot ketujuh dan nama resmi

- Menambahkan MONEV (Monitoring dan Evaluasi) ke `TEAM_CODES` dan seed `SIMULATED_DATA` dengan status `NEEDS_MENTOR_VALIDATION`. Tidak ada record simulasi MONEV yang dikarang.
- Menutup OQ-02 melalui DEC-20261020-01: tujuh tim pilot dan nama resmi AKPSUN "TK Analisis Keuangan dan Pasar SUN". Dokumen cakupan tim dan task tracker (TASK-025) diperbarui.
- README memakai nama resmi "SUN Organizational Values and Transformation through Experience", tagline mentor, nama publik SAVI AI, tujuh tim, target MVP sekitar 3 bulan, serta status rencana klasifikasi RAHASIA.
- Memberi id pendek pada parameter `test_rejects_unsafe_or_mislabelled_files` agar `PYTEST_CURRENT_TEST` tidak melampaui batas 32767 karakter variabel lingkungan Windows (sebelumnya 2 error teardown di Windows).
- Validasi aktual (`pnpm validate`, Windows): ESLint, Ruff, TypeScript, mypy strict (64 source files), 35 test frontend, 291 test backend lulus (41 dilewati), dan build produksi lulus. Setelahnya, di Windows yang sama: `db:sql` (render SQL Alembic hingga `0002_ordering_columns`), `search:eval` (10 kasus, hit@5 1,00, MRR 1,00, kebocoran 0), `extraction:eval` (7 kasus, tingkat keberhasilan 1,00), dan `demo:smoke` (PASSED, tanpa koneksi eksternal dan tanpa penulisan persisten) lulus. Di lingkungan Linux penulis patch tercatat 292 test backend lulus (40 dilewati). QA visual dan PostgreSQL aktual belum dijalankan.

## 2026-10-20 — Konsistensi bahasa antarmuka dan status layanan

- Memperbaiki BUG-025: hasil pencarian tidak lagi menampilkan kode jenis pengetahuan mentah,
  sedangkan halaman administrasi kini membedakan tujuh layanan pendukung dengan nama serta
  penjelasan yang mudah dipahami.
- Mengganti sisa nama Hermes dan istilah pengembang pada keterangan kewenangan, nama pengguna
  simulasi, isi pengetahuan contoh, serta pesan kegagalan dengan nama SAVI AI dan bahasa kerja
  yang jelas. Kode kewenangan, alamat layanan, dan nama kelas internal tidak diubah.
- Menambahkan pengujian pemetaan nama layanan, status layanan, label aman untuk kode yang tidak
  dikenal, dan katalog kewenangan yang tidak membocorkan nama internal ke pengguna.
- Perubahan hanya menyentuh bahasa dan penyajian data contoh. Aturan akses, batas data privat,
  alur persetujuan, serta status integrasi eksternal tetap sama.
- Validasi aktual: ESLint, Ruff, TypeScript, mypy strict (64 source files), 35 tes frontend,
  292 tes backend lulus dengan 40 tes PostgreSQL dilewati, build produksi, render SQL Alembic,
  sembilan langkah demo API, serta render HTTP terautentikasi untuk halaman administrasi dan
  pencarian lulus. Tidak ada koneksi AI eksternal atau data asli yang digunakan.

## 2026-10-20 — Penyempurnaan percakapan dan sumber SAVI AI

- Memperbaiki BUG-024: contoh pertanyaan awal kini selalu membawa konteks SUN yang dapat dikenali
  pengaman domain dan telah diuji terhadap data contoh, sehingga pengguna tidak diarahkan ke
  pertanyaan yang langsung ditolak karena konteksnya terlalu umum.
- Menambahkan pilihan contoh pertanyaan, penghitung karakter, tombol memulai percakapan baru,
  ringkasan jumlah rujukan, serta susunan sumber yang lebih mudah dibaca tanpa menampilkan istilah
  teknis internal.
- Membedakan tindak lanjut saat bahan terbit sama sekali belum ditemukan dan saat bahan ditemukan
  tetapi belum cukup kuat untuk mendukung jawaban. SAVI tetap tidak menebak, tidak membuka sumber
  di luar hak akses, dan tidak mengirim permintaan otomatis kepada pegawai.
- Mengganti sisa nama internal Hermes dan istilah `approval` pada pesan yang dapat dibaca pengguna
  dengan nama SAVI AI serta bahasa Indonesia yang lebih jelas. Nama internal pada kode tetap
  dipertahankan untuk kompatibilitas.
- Tidak ada model atau koneksi AI eksternal yang diaktifkan. Mode pengembangan tetap ekstraktif,
  lokal, dan menggunakan data contoh.
- Validasi aktual: ESLint, Ruff, TypeScript, mypy strict (64 source files), 35 tes frontend,
  292 tes backend lulus dengan 40 tes PostgreSQL dilewati, build produksi, render SQL Alembic,
  sembilan langkah demo API, serta render HTTP halaman SAVI terautentikasi lulus. Pengujian
  browser otomatis belum berjalan karena binari Chromium Playwright tidak tersedia pada
  lingkungan eksekusi.

## 2026-10-19 — Dashboard editorial dan penjelasan SAVI AI

- Menata ulang dashboard menjadi pusat kerja institusional dengan hierarki editorial: ringkasan,
  konteks akses, prioritas tenggat, fokus kerja, status tugas, pengetahuan terbaru, akses SAVI,
  serta kesiapan sumber indikator SUN.
- Memperbaiki BUG-023 dengan menghapus grafik aktivitas dan persentase kualitas yang sebelumnya
  memakai angka statis. Semua jumlah operasional yang tampil kini berasal dari
  `GET /api/v1/dashboard/summary` sesuai tim, klasifikasi, dan kewenangan pengguna.
- Menambahkan fokus tugas terlambat, jatuh tempo dekat, persetujuan menunggu, tindak lanjut
  terbuka, daftar pengetahuan terbaru, serta tindakan cepat ke Monitoring Kerja dan SAVI AI.
- Memperjelas batas SAVI AI dengan bahasa awam: hanya memakai pengetahuan terbit yang dapat
  diakses, tetap pada lingkup SUN, menyertakan sumber, dan tidak menggantikan keputusan manusia.
- Status teknis tetap jujur: runtime pengembangan masih ekstraktif tanpa model AI eksternal;
  LLM produksi, embedding, dan lokasi pemrosesan menunggu OQ-11.
- Validasi aktual: Ruff, ESLint, mypy strict (64 source files), TypeScript, 33 tes frontend,
  290 tes backend lulus dengan 40 tes PostgreSQL dilewati, build produksi, render SQL Alembic,
  serta render HTTP terautentikasi lulus. Screenshot desktop/mobile belum dijalankan karena
  browser Playwright tidak tersedia dan unduhan binari diblokir oleh jaringan lingkungan eksekusi.

## 2026-10-19 — Perbaikan startup API dari `.env` Windows

- Memperbaiki BUG-022: API gagal start ketika `.env` berisi lima nilai pengaman `true`/`false`
  yang benar karena tipe literal boolean tidak menerima teks environment pada Pydantic 2.13.
- Pengaman kini diparsing sebagai boolean, lalu model validator tetap mewajibkan private mode
  aktif serta public indexing, AI egress, agent eksternal, dan telemetry egress nonaktif.
- Menambahkan regresi untuk `.env` aman serta lima variasi konfigurasi yang mencoba melonggarkan
  pengaman. Perubahan tidak mengaktifkan koneksi eksternal atau data asli.
- Validasi aktual: `.env.example` berhasil membentuk konfigurasi startup; lint, TypeScript, mypy
  strict (64 source files), 33 tes frontend, 290 tes backend lulus dengan 40 tes PostgreSQL
  dilewati, build produksi bersih, dan SQL Alembic ter-render.

## 2026-10-19 — Skenario dan pemeriksaan perjalanan demo bulan pertama

- Menambahkan naskah demo 8 sampai 10 menit untuk halaman utama, login, dashboard, Monitoring
  Kerja, Knowledge Hub, pencarian, jawaban SAVI bersumber, dan dua contoh penolakan aman.
- Menambahkan `pnpm demo:smoke` yang menjalankan sembilan langkah API pada backend baru
  `SIMULATED_DATA` di memori dan menolak mode PostgreSQL.
- Laporan hanya memuat nama langkah dan jumlah agregat. Pertanyaan, jawaban, sitasi, token, ID,
  dan isi dokumen tidak dicetak; tidak ada koneksi eksternal atau penulisan persisten.
- Hasil tidak dianggap sebagai bukti browser, PostgreSQL, Nginx, jaringan, atau komputer kantor.
  Skenario masih memerlukan review mentor dan pengujian lingkungan demo yang disetujui.
- Validasi aktual: lint, TypeScript, mypy strict (64 source files), 33 tes frontend, 284 tes
  backend lulus dengan 40 tes PostgreSQL dilewati, sembilan langkah demo lulus, build produksi
  bersih, dan SQL Alembic ter-render.

## 2026-10-19 — Build produksi frontend yang deterministik

- Memperbaiki BUG-021: build produksi berulang dengan Turbopack dua kali gagal membaca database
  cache persisten lokal (`invalid digit found in string`) walaupun lint, typecheck, dan test lulus.
- Perintah `pnpm build` kini memakai `next build --webpack`. Mode pengembangan tetap memakai
  `next dev`; tidak ada dependency atau perubahan perilaku aplikasi yang ditambahkan.
- Validasi aktual: Ruff, ESLint, mypy strict (63 source files), TypeScript, 33 tes frontend,
  280 tes backend lulus dengan 40 tes PostgreSQL dilewati, evaluator ekstraksi tujuh kasus lulus,
  dua build produksi Webpack berturut-turut lulus, dan SQL Alembic ter-render.

## 2026-10-19 — Baseline kualitas ekstraksi dokumen simulasi

- Menambahkan corpus evaluasi `SIMULATED_DATA` berisi tujuh kasus untuk TXT, Markdown, PDF,
  DOCX, XLSX, dan XLS. Kasus mencakup dokumen multi-halaman, judul dan tabel berurutan,
  beberapa lembar, rumus, lembar tersembunyi, serta instruksi mencurigakan tersisip.
- Menambahkan `pnpm extraction:eval` dengan gate keberhasilan ekstraksi, ketercakupan fragmen,
  konten yang tidak boleh muncul, ketepatan struktur, dan klasifikasi indikasi instruksi.
- Output evaluator hanya memuat metrik dan ID kasus. Nama berkas, checksum, teks sumber, dan
  hasil ekstraksi tidak dicetak.
- Baseline tujuh kasus lulus: extraction success 1,00; fragment recall 1,00; forbidden hits 0;
  structure pass 1,00; instruction classification accuracy 1,00.

## 2026-10-19 — Penguatan ekstraksi dokumen simulasi representatif

- Memperbaiki BUG-020: ekstraksi DOCX kini mempertahankan urutan paragraf dan tabel sesuai
  dokumen, bukan memindahkan seluruh tabel ke akhir hasil pembacaan.
- Gaya judul Word tingkat 1 sampai 6 dipertahankan sebagai penanda bagian agar pembagian isi
  laporan dapat mengikuti struktur dokumen.
- Menambahkan pengujian PDF teks dua halaman, DOCX dengan judul dan tabel di tengah dokumen,
  XLSX serta XLS multi-lembar, dan verifikasi rumus XLSX tetap tidak dijalankan.
- Lembar XLSX tersembunyi tetap dibaca untuk pemeriksaan keamanan. Uji integrasi membuktikan
  instruksi mencurigakan pada lembar tersembunyi menghasilkan `QUARANTINED`, tidak membuat
  bagian, serta tidak menyalin nama atau isi berkas ke audit.
- Seluruh fixture dibuat di memori dan hanya memuat `SIMULATED_DATA`; tidak ada berkas internal,
  dependency runtime baru, penyimpanan sumber, atau koneksi eksternal.
- Validasi aktual: Ruff, ESLint, mypy strict (62 source files), TypeScript, 33 tes frontend,
  277 tes backend lulus dengan 40 tes PostgreSQL dilewati, build produksi bersih setelah cache
  `.next` lama dipindahkan keluar workspace, dan SQL Alembic ter-render.

## 2026-10-19 — Preflight keamanan paket demo privat

- Menambahkan `pnpm demo:preflight` untuk memeriksa bind loopback, network internal, lock data
  privat, container non-root/read-only, header keamanan, contoh tunnel nonaktif, dan status
  `demo.env` tanpa menjalankan container atau tunnel.
- Validasi environment menolak placeholder, secret pendek atau sama, izin file terlalu luas,
  origin non-loopback, URL database eksternal/tidak cocok, database sistem, debug logging, dan
  variabel tambahan yang tidak diizinkan. Nilai environment tidak dicetak.
- Memperbaiki BUG-019: access log Nginx tidak lagi memakai `$request` yang dapat memuat query
  string. Log hanya mencatat metode dan path; preflight menolak empat token query berisiko.
- Menambahkan 10 test fail-closed. Preflight scaffold lulus dengan 10 pemeriksaan,
  `environmentFile: NOT_CHECKED`, `containersStarted: false`, dan `tunnelActivated: false`.
- Docker, environment host aktual, firewall, TLS, restore, dan scan port tetap belum divalidasi;
  paket masih `PROPOSED — NOT ACTIVATED`.
- Validasi aktual: Ruff, ESLint, mypy strict (62 source files), TypeScript, 33 tes frontend,
  275 tes backend lulus dengan 40 tes PostgreSQL dilewati, build produksi bersih, preflight
  scaffold lulus, dan SQL Alembic ter-render.

## 2026-10-19 — Alat latihan backup-restore dan evaluator PostgreSQL

- Menambahkan `pnpm db:restore-drill` untuk dump custom sementara dan restore ke database uji
  kosong yang berbeda, kemudian memverifikasi jumlah baris seluruh tabel, revision Alembic,
  trigger append-only audit, serta asal data `SIMULATED_DATA`.
- Alat bersifat fail-closed: hanya `APP_ENV=test`, perlu konfirmasi eksplisit, menolak database
  sistem/sumber sama/target berisi/public host tanpa allowlist, tidak melakukan penghapusan,
  tidak mencetak URL, dan menghapus file dump sementara di luar repository.
- Menambahkan `pnpm search:eval:postgres` agar relevance set 10 kasus dapat dijalankan terhadap
  database uji PostgreSQL atau hasil restore dengan guard yang sama.
- Menambahkan 15 uji pengaman. Baseline pencarian simulated tetap lulus dengan hit@5 1,00,
  MRR 1,00, dan kebocoran akses 0.
- Restore aktual dan baseline FTS PostgreSQL belum diklaim: `pnpm db:test` terblokir karena
  lingkungan tidak mengizinkan `pgserver` membuat user sistem; Docker juga tidak tersedia.
- Validasi aktual: Ruff, ESLint, mypy strict (62 source files), TypeScript, 33 tes frontend,
  265 tes backend lulus dengan 40 tes PostgreSQL dilewati, build produksi bersih setelah cache
  `.next` dibuat ulang, evaluator simulated lulus, dan SQL Alembic ter-render. Guard tanpa
  konfigurasi pada kedua alat baru menolak dengan pesan aman; `pnpm db:test` berstatus BLOCKED
  tanpa traceback kredensial.

## 2026-10-19 — Paket demo privat dan probe 25 pengguna

- Menambahkan resolusi client IP fail-closed: `X-Forwarded-For` hanya dipakai jika direct peer berada pada CIDR proxy tepercaya; chain berlebih, kosong, atau cacat kembali ke direct peer.
- Menambahkan paket `deploy/demo/` berisi image web/API, Compose satu host, Nginx dengan rate/body/connection limit, timeout, security header, network internal, healthcheck, dan bind hanya ke `127.0.0.1`.
- Menyediakan contoh Cloudflare Tunnel yang tidak aktif, memakai domain `.invalid`, tanpa tunnel ID, kredensial, service Compose, atau perintah aktivasi.
- Menambahkan probe load berbasis pustaka standar Python yang menolak target publik. Baseline API-only lokal 25 pengguna virtual/100 request lulus: error 0%, p95 41,26 ms; hasil bukan klaim kapasitas aplikasi penuh atau komputer kantor.
- Docker/host kantor, backup/restore, login resmi, TLS, observability resmi, circuit breaker provider, dan UAT tetap memerlukan persetujuan serta validasi.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, 33 tes frontend, 250 tes backend, build produksi bersih, parse YAML paket demo, probe lokal 25 pengguna, dan render SQL Alembic lulus; 40 pengujian PostgreSQL dilewati pada mode simulated. Docker Compose/Nginx belum dapat dibangun karena Docker tidak tersedia di lingkungan pengembangan.

## 2026-10-18 — Kontrol API satu proses

- Menambahkan sliding-window rate limiter tanpa dependency baru dengan batas global serta kelompok login, SAVI, pencarian, ingestion, dan endpoint umum.
- Menolak body deklaratif maupun aktual di atas 3 MiB sebelum handler dengan 413, memberi timeout penerimaan body 15 detik dengan 408, dan mengembalikan 429 plus `Retry-After` saat batas request tercapai.
- Menggunakan hash satu arah authorization untuk identitas limiter tanpa menyimpan token mentah, membatasi jumlah key, dan tidak mempercayai `X-Forwarded-For`.
- Menambahkan counter agregat privat per proses tanpa endpoint metrik publik dan tanpa mencatat body, token, atau isi pertanyaan.
- Menambahkan ADR-019, R-25, SEC-14 sampai SEC-17, dokumentasi konfigurasi, error contract, serta delapan pengujian regresi. Reverse proxy, trusted client IP, metrik resmi, dan limit multi-instance tetap gate deployment.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, 33 tes frontend, 246 tes backend, build produksi, dan render SQL Alembic lulus; 40 pengujian PostgreSQL dilewati pada mode simulated.

## 2026-10-17 — Batas data privat dan pencegahan exfiltration

- Mengunci SUNOVATE pada mode privat: public indexing, egress data ke AI, akses agent eksternal, dan telemetry egress tidak dapat diaktifkan melalui konfigurasi; nilai tidak aman menggagalkan startup.
- Menambahkan `no-store`, anti-index/anti-archive, no-referrer, frame denial, CSP, resource same-origin, serta `robots.txt` yang menolak seluruh path pada web dan API.
- Menonaktifkan telemetry Next.js sebelum development, build, dan start serta menambahkan konfigurasi environment yang eksplisit.
- Menyembunyikan OpenAPI dan dokumentasi interaktif API di luar development/test.
- Memperluas ScopeGuard untuk menolak sebelum retrieval ketika diminta mengirim data ke AI/agent/MCP/webhook, memublikasikan atau mengindeks ke AI Search/SEO/GEO/AIO/crawler, menyamarkan data sensitif melalui encoding, atau memecahnya menjadi beberapa pesan.
- Menambahkan ADR-018, TASK-023, R-24, keputusan project lead, dan pedoman private-data boundary. Data asli tetap dilarang sampai kontrol jaringan, firewall egress, identitas, enkripsi, audit, pentest, dan persetujuan resmi selesai.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, 33 test frontend, 238 test backend, build produksi, dan render SQL Alembic lulus; 40 pengujian PostgreSQL dilewati pada mode simulated.

## 2026-10-16 — Fondasi pilot RAG-Anything terisolasi

- Menetapkan RAG-Anything sebagai kandidat adapter parser-only untuk dokumen multimodal, bukan pengganti SAVI AI, kontrol akses, PostgreSQL, pemeriksaan manusia, atau alur penerbitan SUNOVATE.
- Menambahkan ADR-017, TASK-022, R-23, tahapan pilot P0 sampai P4, gate supply-chain/security/resource, dataset simulasi, metrik, dan kriteria adopsi.
- Menambahkan preflight fail-closed yang tidak membaca isi dokumen dan tidak menjalankan parser. Pemeriksaan membatasi lokasi input/output, label `SIMULASI`, format, symlink, jaringan, serta versi paket; versi 1.4.1 diblokir dan kandidat minimal 1.4.2.
- Tidak menambahkan dependency RAG-Anything, tidak mengaktifkan jaringan/model/OCR eksternal, tidak mengubah database atau runtime aplikasi, dan tidak memproses dokumen SUN asli.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, 31 test frontend, 231 test backend, build produksi, dan render SQL Alembic lulus; 40 pengujian PostgreSQL dilewati pada mode simulated.

## 2026-10-16 — Karantina indikasi prompt injection saat ingestion

- Memeriksa teks hasil ekstraksi sebelum chunking dan menghentikan berkas yang menyerupai instruksi untuk AI dengan status `QUARANTINED` serta kode `PROMPT_INJECTION_SUSPECTED`.
- Menerapkan gerbang yang sama pada penyimpanan draf manual agar pemeriksaan tidak dapat dilewati dengan menempelkan teks langsung.
- Normalisasi Unicode menghapus karakter format tersembunyi sebelum pola diperiksa; isi yang ditolak tidak disimpan dan tidak disalin ke audit.
- Deteksi tetap berbasis aturan dan diperlakukan sebagai indikasi untuk pemeriksaan manusia, bukan keputusan bahwa dokumen berbahaya.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, 31 test frontend, 227 test backend, dan build produksi lulus; 40 pengujian PostgreSQL dilewati pada mode simulated.

## 2026-10-16 — Status ekstraksi dan karantina simulasi

- Respons ekstraksi berhasil kini menyertakan status `PENDING → EXTRACTED` dan tindak lanjut pemeriksaan manusia; antarmuka menerjemahkannya menjadi tiga tahapan kerja yang mudah dipahami.
- Penolakan keamanan diklasifikasikan sebagai `QUARANTINED`, sedangkan kegagalan pembacaan biasa sebagai `FAILED`. Berkas tetap tidak disimpan pada kedua kondisi.
- Audit penolakan hanya mencatat status, kode alasan, dan ukuran berkas tanpa nama maupun isi berkas.
- Status pemeriksaan manusia tidak ditambahkan ke `extraction_status`; hasil ekstraksi tetap harus masuk draf dan alur pemeriksaan/penerbitan yang sudah ada.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, 31 test frontend, 225 test backend, dan build produksi lulus; 40 pengujian PostgreSQL dilewati pada mode simulated.

## 2026-10-15 — Ekstraksi aman berkas simulasi

- Menambahkan pembacaan TXT, Markdown, PDF, DOCX, XLSX, dan XLS melalui Python pada ruang pemeriksaan dokumen; hanya nama berkas berawalan `SIMULASI` dan nama bahan berawalan `SIMULASI -` yang diterima.
- Membatasi berkas maksimal 2 MB, hasil pembacaan 100.000 karakter, PDF 50 halaman, struktur DOCX, serta Excel maksimal 20 lembar, 5.000 baris per lembar, 100 kolom, dan 50.000 sel berisi. PDF terenkripsi, tipe/isi yang tidak cocok, data biner, makro, dan tautan data luar Excel ditolak; rumus Excel tidak dijalankan.
- Berkas sumber diproses di memori dan tidak disimpan. Hanya teks yang sudah diperiksa pengguna yang dapat diteruskan ke draf; draf tetap tidak masuk pencarian umum atau SAVI sebelum diterbitkan.
- Audit hanya mencatat format, ukuran, jumlah karakter, dan jumlah bagian tanpa nama berkas maupun isi dokumen.
- Ekstraksi produksi, OCR, pemindai malware, penyimpanan objek, serta integrasi SharePoint/Azure tetap belum aktif dan memerlukan persetujuan.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, 30 test frontend, 224 test backend, dan build produksi lulus; 40 pengujian PostgreSQL dilewati pada mode simulated.

## 2026-10-15 — Baseline evaluasi kualitas pencarian

- Menambahkan 10 skenario `SIMULATED_DATA` untuk pencarian metadata, isi bagian, akses lintas tim, klasifikasi, draf, dan konten lintas direktorat.
- Menambahkan evaluator `pnpm search:eval` dengan metrik hit@5, mean reciprocal rank, dan unauthorized leakage tanpa menyimpan isi pertanyaan pada laporan.
- Gate awal menetapkan hit@5 minimal 0,90 dan kebocoran akses wajib 0; suite yang sama otomatis memakai PostgreSQL FTS saat runtime pengujian PostgreSQL tersedia.
- Baseline simulated lulus dengan hit@5 1,00, MRR 1,00, dan kebocoran 0. Hasil PostgreSQL aktual belum boleh diklaim sebelum `pnpm db:test` dapat dijalankan.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, 29 test frontend, 211 test backend, evaluator pencarian, dan build produksi lulus; 40 pengujian PostgreSQL dilewati pada mode simulated.

## 2026-10-15 — PostgreSQL Full-Text Search terotorisasi

- Mengaktifkan indeks GIN `search_vector` untuk pencarian pengetahuan terbit dan draf pada mode PostgreSQL tanpa mengubah skema database.
- Daftar entri yang boleh dibaca ditentukan sebelum query FTS; ID terotorisasi juga menjadi batas pada pencarian judul, ringkasan, dan bagian dokumen.
- Mode simulasi mempertahankan pencarian leksikal deterministik. Penilaian akhir tetap memakai normalisasi Python agar urutan dan skor hasil tetap konsisten.
- Retrieval SAVI belum diubah dan tetap memakai evidence gate yang ada; draf tidak menjadi sumber SAVI sebelum diterbitkan.
- Menambahkan kontrak pengujian bahwa kandidat pencarian tidak dapat melebar di luar ID terotorisasi serta paritas hasil lintas backend.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, 29 test frontend, 209 test backend, render SQL Alembic, dan build produksi lulus. Sebanyak 40 pengujian PostgreSQL dilewati pada mode simulasi; `pnpm db:test` belum dapat berjalan karena lingkungan tidak mengizinkan pembuatan user sistem `pgserver`.

## 2026-10-15 — Antrean pemeriksaan pengetahuan

- Menambahkan halaman `/approvals` untuk merangkum pengajuan publikasi sesuai peran, tim, dan klasifikasi pengguna.
- Menambahkan filter status dan tim, ringkasan jumlah permintaan, identitas pengaju, judul bahan, klasifikasi, waktu pengajuan, dan tautan pemeriksaan.
- API antrean mendukung filter `status`, `requestType`, dan `teamCode`; nama pengaju serta informasi bahan baru ditambahkan setelah pemeriksaan akses.
- Pengaju hanya melihat permintaannya sendiri. Pemeriksa melihat permintaan dalam kewenangannya, sedangkan keputusan tetap dilakukan pada detail bahan.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, build produksi, 29 test frontend, dan 208 test backend lulus (39 pengujian PostgreSQL dilewati pada mode simulasi).

## 2026-10-15 — Alur draf sampai penerbitan pada halaman detail

- Menambahkan ruang tindak lanjut kontekstual pada detail pengetahuan untuk mengubah draf dan mengajukannya kepada pemeriksa.
- Pengaju hanya melihat status menunggu dan tidak memperoleh tombol keputusan atas permintaannya sendiri.
- Pemeriksa dapat mengembalikan draf dengan alasan; tindakan menyetujui dan menerbitkan hanya tampil bagi pemeriksa dengan kewenangan penerbitan.
- Pengguna baca-saja tetap dapat membuka detail tanpa membutuhkan akses persetujuan.
- Menambahkan pengujian antarmuka untuk peran pemilik, pengaju, pemeriksa, penerbit, dan isi permintaan keputusan.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, build produksi, 28 test frontend, dan 208 test backend lulus (39 pengujian PostgreSQL dilewati pada mode simulasi).

## 2026-10-15 — Pencarian draf terbatas bagi pemilik dan pemeriksa

- Menambahkan ruang kerja `/knowledge/drafts` untuk mencari judul, ringkasan, dan bagian dokumen yang masih berstatus DRAFT.
- `knowledge_owner` hanya melihat draf miliknya; pemeriksa hanya melihat draf dalam lingkup tim dan klasifikasinya. Pengguna baca-saja dan staf tanpa peran terkait ditolak.
- Penyaringan akses dilakukan sebelum pencocokan isi. Audit hanya menyimpan panjang kata kunci dan jumlah hasil, bukan kata kunci atau isi draf.
- Pencarian draf tetap terpisah dari pencarian pengetahuan terbit dan retrieval SAVI.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, build produksi, 24 test frontend, dan 208 test backend lulus (39 pengujian PostgreSQL dilewati pada mode simulasi).

## 2026-10-14 — Penyimpanan hasil pemeriksaan sebagai draf simulasi

- Menambahkan aksi **Setujui pembagian dan simpan draf** pada layar pemeriksaan isi dokumen.
- Backend menyimpan knowledge DRAFT, referensi teks simulasi, versi, dan bagian terstruktur dalam satu transaksi. Judul wajib diawali `SIMULASI -` dan akses memerlukan gabungan kewenangan pemeriksaan serta penulisan dokumen.
- Draf yang tersimpan tetap tidak muncul pada pencarian umum dan tidak dapat digunakan SAVI sebelum melewati alur publikasi.
- Audit menyimpan identitas record dan jumlah bagian tanpa menyalin isi dokumen. Ekstraksi berkas asli dan ingestion produksi tetap tidak aktif.
- Validasi aktual: Ruff, ESLint, mypy strict, TypeScript, build produksi, 24 test frontend, dan 205 test backend lulus (39 pengujian PostgreSQL dilewati pada mode simulasi). `pnpm db:test` tidak dapat memulai PostgreSQL sementara karena lingkungan tidak mengizinkan pembuatan user sistem `pgserver`; migrasi tetap diperiksa melalui render SQL.

## 2026-10-14 — Layar pemeriksaan pembagian isi dokumen

- Menambahkan endpoint Python review-only untuk membagi teks contoh menjadi bagian terstruktur tanpa membaca berkas, menulis database, atau menerbitkan pengetahuan.
- Menambahkan layar institusional `/knowledge/ingestion-preview` bagi pemeriksa, dengan ringkasan jumlah bagian/kata, isi per bagian, dan kode pemeriksaan.
- Menambahkan gerbang `knowledge:review`, proxy server Next.js agar token tidak masuk browser, tautan kontekstual dari Basis Pengetahuan, serta pengujian bahwa preview tidak menambah entri pengetahuan.
- Ekstraksi berkas, penyimpanan chunk, FTS produksi, embedding, dan publikasi tetap belum diaktifkan.
- Validasi aktual: Ruff, ESLint, mypy strict, dan TypeScript lulus; 23 test frontend serta 203 test backend lulus (39 dilewati); build produksi Next.js lulus setelah cache Turbopack lokal dipindahkan; SQL migrasi `0001` dan `0002` berhasil dirender sampai `COMMIT`.
- Peninjauan visual otomatis lokal belum dapat dijalankan karena Chromium Playwright tidak tersedia dan browser terisolasi tidak dapat menjangkau `127.0.0.1`; struktur responsif dan komponen mengikuti sistem desain SUNOVATE yang ada, tetapi screenshot baru belum menjadi bukti validasi sesi ini.

## 2026-10-14 — Jawaban parsial tata kelola glosarium SAVI

- Mencatat jawaban mentor untuk OQ-37: SUN berarti Surat Utang Negara; sumber glosarium adalah peraturan SUN dan playbook transaksi; glosarium dapat dilihat pegawai; review setiap tiga bulan; singkatan tanpa sumber resmi dilarang; pemeriksaan diarahkan ke admin.
- Menjaga status PARTIAL karena `admin` belum dipetakan ke role/permission dan pasangan istilah lain belum disahkan secara individual.
- Tujuh kandidat domain tetap diblokir. Istilah lama tidak ditampilkan sebagai istilah aktif, tetapi audit perubahan tetap dipertahankan.

## 2026-10-14 — Evidence reranking dan answer gate SAVI

- Memisahkan reranking dari keputusan menjawab melalui `EvidenceGate` Python yang deterministik.
- SAVI menolak sebelum provider jawaban dipanggil bila kandidat terotorisasi tidak memenuhi coverage, dukungan istilah, skor rerank, atau ambang relatif.
- Audit mencatat alasan gate, jumlah kandidat, skor/coverage teratas, dan jumlah passage yang diterima tanpa menyimpan teks pertanyaan.
- Menambahkan pengujian penerimaan kandidat kuat dan abstention kandidat lemah. Model reranker eksternal tetap tidak aktif sampai OQ-11 disetujui.

## 2026-10-14 — Rencana induk dan urutan implementasi

- Menambahkan satu rencana induk yang mengurutkan perubahan requirement, fondasi platform, kontrol API Gateway, Knowledge Hub, SAVI AI, web workflow, integrasi, demo, UAT, dan handover.
- Memisahkan status kontrol API yang sudah tersedia dari rate limiting, batas request, timeout, security headers, cache, load balancing, dan gateway terpisah yang belum diimplementasikan.
- Menetapkan aturan intake ide baru agar gambar referensi atau tambahan teknologi tidak langsung mengubah scope dan urutan pengerjaan.
- Menambahkan TASK-021 untuk kontrol API Gateway di dalam modular monolith; load balancing dan gateway terpisah tetap pengembangan setelah kebutuhan terukur.

## 2026-10-14 — Referensi pola RAG dan preview chunking terstruktur

- Memetakan referensi visual Agentic AI dan lima lapisan RAG ke arsitektur SAVI AI dengan status implementasi, batas kewenangan, dan human-in-the-loop yang eksplisit.
- Menambahkan preview chunking Python deterministik untuk regulasi, SOP/playbook, kajian/laporan, dan teks umum. Preview mengenali `Pasal29`, menjaga batas struktur, serta menghasilkan label, jumlah kata, urutan, dan SHA-256 tanpa membaca berkas atau menulis database.
- Menambahkan pengujian batas Pasal, tahapan SOP, batas jumlah kata, kestabilan hash, teks kosong, dan instruksi berbahaya sebagai konten inert.
- Embedding, OCR, ingestion produksi, web search, multi-agent, serta koneksi dokumen internal tetap tidak aktif dan menunggu persetujuan terkait.

## Unreleased 2026-10-14 - Tindak lanjut aman SAVI AI

### Ditambahkan

- Respons terstruktur ketika sumber yang dapat diakses belum cukup: alasan yang jelas, panduan memperjelas periode/dokumen/proses/unit, dan arahan meminta pemeriksaan pegawai berwenang.
- Panel "Langkah berikutnya" pada percakapan SAVI dengan bahasa pengguna nonteknis.
- Test API dan antarmuka yang memastikan jawaban berhasil tidak membuat tindak lanjut, sedangkan bukti tidak cukup menampilkan panduan yang sesuai.
- Pencarian ulang maksimal satu kali untuk lima kelompok variasi ejaan terdaftar, tanpa membuang konsep pertanyaan atau menurunkan filter akses, batas klasifikasi, dan ambang bukti.
- Jumlah percobaan pencarian dicatat pada audit dan respons; antarmuka memberi tahu pengguna ketika pencarian lanjutan dilakukan.
- Register glosarium SAVI berisi 12 entri: 5 variasi ejaan aktif dan 7 kandidat pemetaan domain yang tetap diblokir.
- Endpoint baca terotorisasi dan panel glosarium pada halaman Pemeriksaan SAVI, lengkap dengan sumber, catatan, jenis istilah, dan status pemeriksaan.
- OQ-37 untuk mengesahkan pemilik glosarium, pemetaan domain, sumber, klasifikasi, masa tinjau, dan mekanisme pencabutan.

### Batas

- SAVI tidak otomatis menunjuk PIC, membuat tiket, mengirim pesan, mengubah data, atau menerbitkan pengetahuan.
- Nama PIC, SLA, kanal notifikasi, alur persetujuan, sinonim domain, serta perubahan istilah berbasis model belum ditetapkan dan tetap menunggu keputusan OQ-36 atau glosarium tervalidasi.

### Validasi aktual

- Ruff, ESLint, mypy strict, dan TypeScript lulus.
- 21 test frontend lulus; 193 test backend lulus dan 39 dilewati.
- Next.js production build dengan webpack lulus.
- `pnpm db:sql` berhasil merender migrasi `0001` dan `0002` sampai `COMMIT`.

## Unreleased 2026-10-13 - Intake pertanyaan mentor untuk SAVI AI

### Ditambahkan

- Register `sme_question_intake.json` untuk delapan pertanyaan operasional dari arahan mentor dengan jawaban acuan awal, sumber yang diberikan, kandidat sumber, catatan validasi, dan status review.
- Test struktural yang memastikan seluruh kasus intake tetap diblokir dari runtime, memiliki bukti review minimum, dan tidak dipromosikan diam-diam ke golden set aktif.
- Panduan validasi SME, hukum, SOP, klasifikasi, akses, serta gerbang promosi ke golden set.
- OQ-36 untuk menentukan validator, sumber resmi per klaim, SOP/checklist, klasifikasi, dan kondisi eskalasi atau penolakan SAVI.
- Endpoint baca terotorisasi dan halaman `/savi-validation` untuk meninjau delapan pertanyaan, jawaban awal, sumber, status, dan catatan validasi.
- Ringkasan status, pencarian menyeluruh, filter status, kondisi tanpa hasil, serta format cetak pada register validasi SAVI tanpa menambahkan aksi persetujuan.
- Lembar keputusan mentor OQ-36 pada halaman Validasi SAVI dan dokumentasi proyek untuk mencatat peran validator, urutan review, sumber/SOP wajib, klasifikasi, eskalasi, serta masa tinjau. Isian web bersifat lokal, tidak disimpan, dan tidak mengaktifkan jawaban.
- Bahasa antarmuka disederhanakan menjadi bahasa kerja pengguna: label teknis, enum mentah, nama internal, istilah akses, status pengembangan, riwayat aktivitas, Basis Pengetahuan, Monitoring Kerja, dan pesan gangguan kini memiliki padanan Indonesia yang jelas.
- Pedoman bahasa antarmuka dan AC-32 ditambahkan agar AI agent berikutnya tidak mengembalikan istilah pengembang ke halaman pengguna.

### Batas

- Golden set aktif tetap 24 kasus `SIMULATED_DATA`; delapan pertanyaan mentor belum menjadi jawaban produksi.
- Tidak ada dokumen internal, data pribadi, angka transaksi, integrasi, migration, aksi keputusan, atau perubahan perilaku retrieval/jawaban SAVI.

### Validasi aktual

- Ruff, ESLint, mypy strict, dan TypeScript lulus.
- 19 test frontend lulus; 186 test backend lulus dan 39 dilewati, termasuk pemetaan istilah antarmuka, lembar keputusan lokal, filter register, gate intake, dan otorisasi endpoint review.
- Next.js production build lulus setelah cache build lokal yang rusak dipindahkan dan dibuat ulang.
- `pnpm db:sql` berhasil merender migrasi `0001` dan `0002` sampai `COMMIT`.

## Unreleased 2026-10-11 - Penguatan SAVI AI ScopeGuard

### Diperbaiki

- ScopeGuard menolak variasi permintaan kredensial, jailbreak bahasa Inggris, mode unrestricted, akses data tanpa izin, dan saran investasi yang lebih beragam.
- Input dinormalisasi dengan NFKC dan karakter format Unicode dihapus agar variasi zero-width sederhana tidak melewati pola.
- Write intent dipersempit ke bentuk perintah sehingga pertanyaan informasional yang memuat kata "menghapus" tidak membuat approval palsu.
- Penyebutan bahasa pemrograman dalam konteks SUNOVATE tidak otomatis dianggap permintaan coding; dokumen umum seperti CV tidak dianggap domain SUN.
- Golden set bertambah dari 16 menjadi 24 kasus dan unit test membuktikan pertanyaan tertolak tidak mencapai retrieval.
- Ambang coverage retrieval dinaikkan dari 0,4 menjadi 0,6 setelah RAG-21 menemukan jawaban yang menyitir materi umum tetapi tidak mendukung klaim "otomatis menghapus seluruh ketentuan lama" (BUG-018).

## Unreleased 2026-10-11 - Status sumber indikator dashboard

### Ditambahkan

- Dashboard menampilkan Yield SUN dan Kepemilikan SBN sebagai indikator terkunci dengan keterangan "Sumber data belum tersedia".
- Tidak ada angka simulasi atau tabel bisnis baru; sumber, definisi, dan hak akses tetap menunggu OQ-21.
- Smoke E2E memeriksa kedua label dan dua status sumber data.

## Unreleased 2026-10-11 - Specification-ready Draft Workspace

### Dokumentasi

- Menambahkan spesifikasi lengkap `work-file-draft-workspace.md`: batas unggah versus terbit, lifecycle, kontrol tindakan, validasi file, model data kandidat, kontrak API, UI, dan gate keputusan.
- Menambahkan AC-26 sampai AC-31 untuk kepemilikan draft, pembekuan saat submit, immutability, revisi baru, dan grant akses terbatas.
- Menyelaraskan model logis, endpoint catalog, future development, task tracker, indeks dokumentasi, dan handoff AI.
- TASK-019 tetap `NEEDS APPROVAL`; tidak ada migration, endpoint, permission aktif, atau UI baru.

## Unreleased 2026-10-10 - Proposal Draft Workspace dan immutable work files

### Dokumentasi

- Menambahkan FR-56 dan TASK-019 untuk lampiran file pekerjaan dengan dua fase utama: DRAFT yang dapat diedit/dihapus lunak dan PUBLISHED yang immutable.
- Menetapkan koreksi sebagai versi baru, penarikan sebagai perubahan status tanpa hard delete, serta pemisahan administrasi akses dari kewenangan mengubah konten.
- Menambahkan kandidat permission terperinci, OQ-35 untuk validasi mentor/TIK, dan R-22 untuk risiko override akun utama atau penghapusan rekaman terbit.
- Fitur tetap `NEEDS APPROVAL` dan belum diimplementasikan; tidak ada perubahan API, database, UI, atau matriks permission aktif.

## Unreleased 2026-10-10 - CRUD Monitoring Kerja end-to-end

### Ditambahkan
- API create/update/soft-delete untuk output kerja, tugas, milestone, pending matter, dan tindak lanjut.
- Validasi permission, team scope, clearance klasifikasi, relasi induk satu tim, optimistic revision, dan audit untuk seluruh operasi tulis.
- UI Monitoring Kerja berbasis tab dengan jumlah record, form tambah, perubahan status, aksi arsip, feedback, dan kontrol yang mengikuti permission pengguna.
- Proxy mutasi server-side `/api/work` sehingga token development tetap berada di cookie HTTP-only.
- Dua test backend untuk CRUD, scope, permission `pending:manage`, revision, dan soft delete; satu skenario E2E untuk alur tambah output melalui UI.

### Batas
- Approval khusus monitoring belum diimplementasikan karena OQ-12 dan OQ-25 belum diputuskan. TASK-005 tetap `IN PROGRESS`.
- Seluruh record demonstrasi tetap `SIMULATED_DATA`/`USER_ENTERED` dalam lingkungan simulasi; tidak ada integrasi produksi.

### Validasi aktual
- `pnpm validate` lulus: Ruff, ESLint, mypy strict, TypeScript, 12 test frontend, 173 test backend (39 dilewati), dan Next.js production build.
- `pnpm db:sql` berhasil merender migrasi `0001` dan `0002` sampai `COMMIT`.
- `pnpm e2e` belum berjalan karena binary Chromium tidak tersedia; unduhan Playwright menghasilkan arsip kosong/truncated. Pemeriksaan screenshot desktop/mobile tidak dapat dilakukan pada runtime ini.
- `pnpm db:test` belum berjalan karena `pgserver` mencoba membuat user sistem `pgserver` dan ditolak environment (`useradd` exit 1). Suite simulasi dan render migrasi tetap lulus; paritas PostgreSQL perubahan write ini masih perlu dijalankan pada host yang mengizinkan pgserver atau Docker.

## Docs 2026-10-09 - Baseline demo, roadmap stack, dan handoff lintas AI agent

### Ditambahkan
- `docs/13-handover/task-tracker.md` sebagai sumber status task aktif, approval gate, bukti, dan urutan eksekusi.
- `docs/13-handover/ai-agent-handoff.md` sebagai snapshot wajib baca untuk AI agent.
- ADR-016 serta DEC-20261009-01/02: baseline demo sekitar 25 pengguna pada komputer kantor khusus; Docker Compose + Nginx; Cloudflare Tunnel/Access sebagai opsi yang belum aktif; Python tetap inti; Go/Rust/mobile ditunda.
- OQ-34 serta risiko R-19 sampai R-21 untuk persetujuan tunnel, pembuktian kapasitas, dan pencegahan kompleksitas stack prematur.

### Diubah
- Deployment architecture, runbook, UAT, asumsi, roadmap, MVP scope, technology stack, developer handover, dan future development diselaraskan dengan arahan project lead 2026-10-09.
- `AGENTS.md` kini mewajibkan pembaruan task tracker dan changelog pada setiap perubahan material. Status `DONE` harus memiliki bukti implementasi dan validasi.
- Nama produk asisten pada frontend ditegaskan sebagai SAVI AI; nama internal `HermesGateway` dipertahankan sementara agar tidak terjadi rename berisiko tanpa migration plan.

### Batas dan approval
- Komputer kantor adalah target demo/UAT sementara, bukan target produksi. Cloudflare tidak boleh diaktifkan sebelum persetujuan mentor dan TIK/keamanan.
- Hanya `SIMULATED_DATA`. Tidak ada data internal, data pribadi, angka keuangan nyata, atau integrasi produksi yang ditambahkan.
- Dokumen sumber root dan `docs/_archive/` tidak diubah.

### Validasi
- Pemeriksa 116 file Markdown otoritatif: 0 tautan relatif rusak; `git diff --check` bersih.
- `pnpm validate`: lint lulus; TypeScript dan mypy strict lulus; frontend 12 test lulus; backend 171 test lulus dan 39 dilewati; Next.js production build lulus.
- `pnpm db:sql`: migrasi Alembic `0001_initial_schema` dan `0002_ordering_columns` berhasil dirender sampai `COMMIT`.

## Docs 2026-10-06 - Dokumentasi domain diselaraskan dengan Kompilasi Peraturan SUN (hanya dokumentasi)
### Diubah
- Hasil pembacaan terbantu mesin atas `Kompilasi_Peraturan_SUN_formal.pdf` (ekstraksi teks tanpa OCR; kutipan diperiksa terhadap teks ekstraksi, bukan gambar halaman; tidak dibandingkan dengan Berita Negara atau JDIH) diterapkan ke dokumentasi. Sitasi memakai format `Kompilasi Peraturan SUN, <regulasi>, Pasal X, hal. N` (hal. = halaman PDF).
- Koreksi: judul PMK 165/2022 pada naskah adalah "Transaksi Surat Utang Negara Secara Langsung" (CONFIRMED), berbeda dari indeks kompilasi (NEEDS LEGAL CONFIRMATION); definisi private placement, bookbuilding, pembelian kembali (tunai dan/atau penukaran), dan penukaran di `glossary.md` dan `sun-domain-overview.md`; judul enam regulasi yang sebelumnya "belum dicatat" diisi dengan sumber dan halaman.
- Klaim deck yang tidak ada di kompilasi (ORI/SBR, "debt switch", BEI, SBN, PMK 124/2024, Pasal 1441) dipisahkan dari teks regulasi dan ditandai NOT VERIFIABLE FROM COMPILATION. Pemetaan "debt switch" ke "penukaran" berstatus PROPOSED.
- OQ-17 diperbarui dengan fakta terverifikasi (PMK 128/PMK.08/2012, hal. 168-175, tentang penjualan SUN valuta asing di pasar perdana domestik dengan cara bookbuilding); kompilasi tidak menjelaskan penggantian "PMK 128 tahun 2019" dan status tetap OPEN.
- Desain (PROPOSED, tidak diimplementasikan): metadata regulasi tambahan (`metadata-schema.md`), hierarki BAB/Bagian/Pasal/ayat/huruf, Lampiran, dan Penjelasan (`chunking-strategy.md`, `ingestion-pipeline.md`), cakupan pencabutan sebagian dan dasar relasi (`logical-data-model.md`, `conceptual-data-model.md`, `document-lifecycle.md`), format sitasi dan catatan status "Berlaku" (`citation-policy.md`). Pencabutan sebagian tidak menjadikan target `SUPERSEDED`; status hukum tidak diturunkan otomatis.
- Catatan sumber kompilasi ditambahkan ke `market-data-proposal.md`, `integration-overview.md`, dan `dashboard-requirements.md`.
### Ditambahkan
- Open question OQ-26 sampai OQ-33 (status berlaku terkini, sumber acuan judul dan nomor, pengundangan PMK 111/2024, pencabutan sebagian dan ketentuan peralihan, rujukan tak bernomor, regulasi tambahan, validasi teks ekstraksi, nama unit lama); dua kandidat lain digabung ke OQ-16 dan OQ-03/OQ-02.
- Aturan bisnis BR-40 sampai BR-45 (regulasi dan sitasi) dan risiko R-18 (status berlaku regulasi tidak dapat diturunkan dari kompilasi).
### Tidak diubah
- Kode, test, migrasi, file paket, seed, dokumen sumber di root, `docs/_archive`, dan decision log (tidak ada keputusan baru). SUN Tematik dan peran internal Direktorat SUN tidak diubah. Tidak ada integrasi yang diaktifkan atau diklaim tersedia. Digest dan teks ekstraksi kompilasi tidak dimasukkan ke repository.
### Hasil validasi aktual (2026-10-06, Windows, PowerShell 7)
| Pemeriksaan | Hasil |
|---|---|
| Pemeriksa dokumentasi (skrip sementara di luar repository, `docs/**/*.md` tanpa `_archive`) | 111 file, 0 tautan relatif rusak, 0 file tanpa baris `**Status:**`, 0 file dengan emoji atau ikon Unicode, 0 penanda konflik, 0 pagar kode tidak seimbang |
| `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, `pnpm db:sql`, `pnpm db:check` | Tidak dijalankan: tidak ada perubahan kode, test, migrasi, atau paket |## Docs 2026-10-06 - Jawaban knowledge owner diteruskan ke requirement, alur sistem, database, pengujian, dan bug (hanya dokumentasi)
### Diubah
- Tahap kedua dari jawaban knowledge owner (deck `v1_` slide 24; `CONFIRMED (knowledge owner, deck v1_ slide 24)`, pengakuan mentor tertunda OQ-24). Slide 11, 12, 15, dan 20 tidak berubah pada deck `v1_`, sehingga prioritas, alur dokumen, model data inti, dan definisi P0 sampai P3 tidak digeser; dampaknya hanya pada pelaku, batas data, indikator, dan server pilot.
- Requirement: `functional-requirements.md` (FR-50 sampai FR-55; FR-09, FR-10, FR-22, FR-23, FR-39, FR-41, FR-42, FR-48 diselaraskan), `non-functional-requirements.md` (NFR-39 sampai NFR-44 untuk server khusus), `acceptance-criteria.md` (AC-16 sampai AC-25 dengan status terhadap kode), `user-stories.md` (US-35 sampai US-40; US-05 diselaraskan), `prd.md` dan `mvp-scope.md` (sisa pass 1 dan status persistence).
- Alur sistem: `document-lifecycle.md` (pelaku, gerbang intake, sequence ujung ke ujung), `knowledge-lifecycle.md`, `review-and-approval.md`, `work-monitoring-flow.md`, `business-rules.md` (BR-33 sampai BR-39 dengan penandaan konflik terhadap matriks `staff`).
- Database: `logical-data-model.md` (opsi penunjukan ketua tim dan PIC, dampak PD-1 pada `role_permissions` dan seed, pengguna simulasi tambahan, yield dan SBN tidak dimodelkan), `database-schema.md` (mode persistence, pengecekan ulang 30 tabel dan kolom `0002`), `metadata-schema.md`, `simulated-data-policy.md`, `conceptual-data-model.md`, `data-retention.md`.
- Pengujian: `test-strategy.md`, `security-testing.md` (SEC-40 sampai SEC-91 berstatus PLANNED kecuali disebut ada, dan daftar uji yang ada terkait PD-1), `rag-testing.md` (rencana golden set per tim dan prosedur dokumen asli), `backend-testing.md`, `frontend-testing.md`, `uat-plan.md` (UAT-01 ditandai bertentangan; UAT-12 sampai UAT-16), `threat-model.md` (T-20 sampai T-26), `security-checklist.md`.
- Bug: `bug-severity.md` (contoh dari jawaban knowledge owner, tautan ke register).
### Ditambahkan
- `docs/10-testing/bug-register.md`: BUG-001 sampai BUG-009 (diperbaiki, dirujuk ke commit `357df94`, `3fba69f`, `6ed05bb`, `a084a53`), BUG-010 sampai BUG-013 (KL-21 sampai KL-24, terbuka), REQ-GAP-01 sampai REQ-GAP-03 (celah persyaratan, terbuka). Kandidat yang tidak dapat ditelusuri (uji API gagal dan plugin mypy pada scaffold awal; tumpang tindih label grafik, indeks sitasi, tinggi sidebar) dicatat terpisah dan tidak dimasukkan sebagai cacat.
### Temuan yang dicatat (tidak diperbaiki di sini)
- `staff` masih dapat membuat, mengubah, dan mengajukan knowledge (pengecekan manual: 201, 200, 200); PD-1 belum diterapkan. Tidak ada uji yang ada yang mengandalkan hal ini.
- Seed hanya menambah baris; PD-1 pada database yang sudah di-seed memerlukan langkah data.
- `APP_ENV=production` menolak dev auth sementara belum ada mekanisme login lain, sehingga server pilot pada mode production belum dapat dipakai login.
### Tidak diubah
- Kode, test, migrasi, file paket, seed, katalog role, `references/README.md`, dan dokumen sumber di root. Tidak ada integrasi yang diaktifkan atau diklaim tersedia.
### Hasil validasi aktual (2026-10-06, Windows, PowerShell 7, Python 3.14.4)
| Pemeriksaan | Hasil |
|---|---|
| Pemeriksa dokumentasi (skrip sementara, `docs/**/*.md` tanpa `_archive`) | 111 file, 0 tautan relatif rusak, 0 file tanpa baris `**Status:**`, 0 file dengan emoji atau ikon Unicode, 0 penanda konflik, 0 pagar kode tidak seimbang |
| Pengecekan manual perilaku `staff` dan bentuk respons dashboard (skrip sementara dengan `TestClient`, dihapus) | `staff` POST/PATCH/submit knowledge 201/200/200; `staff` POST versi dokumen 403; tidak ada field yield atau SBN pada `/dashboard/summary`; `GET /teams` enam kode; route webhook kanal 404 |
| `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, `pnpm db:sql`, `pnpm db:check` | Tidak dijalankan: tidak ada perubahan kode, test, migrasi, atau paket |
| Diagram Mermaid | Tidak dirender otomatis; sintaks diperiksa manual |
## Docs 2026-10-02 - Jawaban knowledge owner dari deck proposal versi tetap (hanya dokumentasi)
### Diubah
- Dokumentasi memasukkan deck `v1_SUNOVATE_Proposal_Arsitektur_dan_Tim_Kerja_v2.4.pptx`, versi tetap (fixed) dari deck proposal yang dikonfirmasi pengguna. Slide 24 kini berjudul "konfirmasi knowledge owner" dan delapan pertanyaannya dijawab. Jawaban diberi label `CONFIRMED (knowledge owner, deck v1_ slide 24)`; pengakuan mentor masih tertunda (OQ-24). Tafsiran, pemetaan role, dan konsekuensi tetap `PROPOSED`.
- Status open question: OQ-03, OQ-08, OQ-09 ANSWERED (knowledge owner); OQ-02, OQ-04, OQ-05, OQ-06, OQ-07, OQ-10 PARTIAL; OQ-01, OQ-11 sampai OQ-20 tidak berubah.
- Slide 9 dan 18 deck `v1_` ("Ketua tim kerja", "Pengelola Knowledge / PIC", "Ketua Tim", "PMP") tercermin di stakeholder map, persona, dan tata kelola. "PMP" tidak dijelaskan di deck dan ditulis sebagai kemungkinan Program dan Manajemen Pengetahuan, perlu konfirmasi (OQ-25).
- Dokumen hosting (deployment, runbook, backup, batas integrasi, identity provider), SharePoint, Telegram, WhatsApp, dan dashboard diselaraskan dengan jawaban (komputer tersendiri sebagai server, "Sandbox server", "bisa", indikator "yield" dan "kepemilikan SBN" tanpa data).
- Agenda sesi mentor 01 diubah menjadi sesi konfirmasi.
### Ditambahkan
- Open question OQ-21 sampai OQ-25 (sumber data yield dan kepemilikan SBN, makna "Sandbox server", persyaratan server dan login, pengakuan mentor, pemetaan peran).
- Entri decision log DEC-20261002-01 sampai DEC-20261002-09 (di bagian jawaban, bukan di tabel ADR).
- Risiko R-13 sampai R-17 (server tunggal, cakupan "semua dokumen", indikator tanpa sumber data, jawaban belum diakui mentor, matriks izin belum selaras).
- Asumsi A-17 sampai A-19 dan usulan perubahan izin `staff` (PROPOSED, belum diimplementasikan) di `docs/06-security/permission-matrix.md`, `docs/06-security/authorization-rbac.md`, dan `docs/13-handover/future-development.md` (PD-1 sampai PD-6).
- `references/README.md` mencatat deck `v1_` sebagai versi tetap dan slide yang berubah.
### Tidak diubah
- Kode, test, migrasi, file paket, katalog role, dan dokumen sumber di root. Tidak ada integrasi yang diaktifkan atau diklaim tersedia.
### Hasil validasi aktual (2026-10-02, Windows, Python 3.14)
| Pemeriksaan | Hasil |
|---|---|
| Pemeriksa tautan dokumentasi (skrip sementara, `docs/**/*.md` tanpa `_archive`) | 110 file, 0 tautan relatif rusak, semua file memiliki baris `**Status:**` dan `Last Updated` |
| Karakter emoji/ikon | 0 ditemukan |
| `git diff --stat main..HEAD` | Hanya `docs/`, `references/README.md`, dan `CHANGELOG.md` |
| `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, `pnpm db:sql` | Tidak dijalankan: tidak ada perubahan kode, test, migrasi, atau paket |


## Unreleased - 2026-10-02 (persistence PostgreSQL, PROPOSED ADR-015)

### Ditambahkan
- Backend runtime kedua `DATA_BACKEND=postgres` di belakang interface `Repository` sinkron per request (`store/repository.py`, `store/postgres.py`): SQLAlchemy 2 sinkron + `psycopg[binary]==3.3.6` (satu-satunya dependency baru). `DATA_BACKEND=simulated` tetap default. Data bertahan setelah API di-restart.
- Revisi Alembic `0002_ordering_columns`: `audit_logs.seq` (identity, urutan insert audit) dan `knowledge_tags.position` (urutan tag). `0001_initial_schema` tidak diubah.
- `db/urls.py`: satu aturan `DATABASE_URL` (hanya `postgresql+asyncpg`/`postgresql+psycopg`) untuk runtime, Alembic, seed, dan `/health/database`; `db/testing_reset.py` (reset TRUNCATE + seed, hanya `APP_ENV=test` dan `SUNOVATE_DB_RESET_ALLOWED=1`).
- `pnpm db:test` (`scripts/validation/db_test_pgserver.py`): seluruh pytest pada PostgreSQL sementara (pgserver). Test baru: kontrak repository pada kedua backend, pemetaan constraint ke 409 `DUPLICATE_CHECKSUM` / 403 `SEPARATION_OF_DUTIES`, revision atomik dan konkuren, rollback, audit persisten dan append-only, paritas respons lintas backend, guard konfigurasi production, 503 tanpa kebocoran URL.
- Dokumentasi: ADR-015 di `architecture-decisions.md` dan `decision-log.md`; pembaruan arsitektur data, container, komponen, konfigurasi environment, pengembangan lokal, skema database, retrieval, endpoint catalog, pengujian integrasi, known limitations (KL-01, KL-02, KL-20 sampai KL-24), future development, `.env.example`, `README.md`, `tests/README.md`. Pernyataan "runtime hanya simulated / repository belum ada" juga dikoreksi di project overview, assumptions (A-06), MVP scope, data retention, RAG architecture, API overview, prototype notes, backend testing, backup-and-restore, migration guide, observability, troubleshooting, change management, risk register (R-10), dan administrator guide; rujukan ke skrip `db-check-pgserver.ps1` yang tidak ada diganti `pnpm db:check`.

### Diubah
- Semua akses data modul, `AuthorizationService`, `RetrievalService`, dan `HermesGateway` lewat `Repository`; write wajib di dalam `transaction()`.
- Urutan natural koleksi `(created_at, id)` pada kedua backend; `AuditLog` memakai satu waktu (`createdAt == updatedAt == occurredAt`).
- `tags` duplikat pada POST/PATCH knowledge dibuang (kemunculan pertama dipertahankan); `null` pada PATCH knowledge/task berarti tidak diubah.
- Production: `DATA_BACKEND=postgres` diizinkan bila `DEV_AUTH_ENABLED=false`; `simulated` dan dev auth tetap ditolak.

### Perbaikan temuan review (NIT, PROPOSED ADR-015)
- Log error tak tertangani (`log_unhandled_error` di `core/errors.py`, dipakai handler `Exception` dan fallback middleware `main.py`) tidak lagi memuat pesan exception, `DETAIL` driver, SQL, atau parameter. Hanya `errorType`, `sqlstate`, `stack` (`berkas:baris fungsi`), dan `requestId`. Respons klien tetap 500 `INTERNAL_ERROR`.
- `GET /api/v1/health` melaporkan backend yang benar-benar terpasang (`AppContext.data_backend` dari `AppRuntime.backend.name`), bukan nilai `DATA_BACKEND` di settings.
- `OperationalError` diklasifikasi lewat SQLSTATE: 57014, 55P03, 40P01, 40001 menjadi 503 `DATABASE_BUSY` (pesan "sibuk atau melewati batas waktu", header `Retry-After: 5`); kegagalan koneksi tetap 503 `DATABASE_UNAVAILABLE`. `ApiError` kini mendukung `headers`. Kode baru didokumentasikan di `docs/07-api/error-format.md`.
- `DataBackend.close()` (no-op pada backend simulasi, `dispose()` engine pada PostgreSQL) dipanggil oleh lifespan FastAPI saat shutdown.
- Test baru: `apps/api/tests/test_runtime_hardening.py` (20 test, tanpa database) dan 3 test di `tests/postgres/test_postgres_backend.py` (health postgres, dispose saat shutdown, statement timeout nyata menjadi `DATABASE_BUSY`). Tidak ada dependency baru dan tidak ada perubahan skema.
### Hasil validasi perbaikan temuan review (Windows, PowerShell 7, Python 3.12)
| Perintah | Hasil |
|---|---|
| `pnpm lint` | ESLint tanpa temuan; Ruff "All checks passed!"; exit 0 |
| `pnpm typecheck` | tsc tanpa error; mypy strict "Success: no issues found in 53 source files"; exit 0 |
| `pnpm test` (simulated) | Vitest 12 passed; pytest 171 passed, 39 skipped in 26.39s; exit 0 (baseline 151 passed, 36 skipped) |
| `pnpm build` | next build berhasil; exit 0 |
| `pnpm db:sql` | SQL offline ter-render sampai `0002_ordering_columns`; exit 0 |
| `pnpm db:check` | "DATABASE CHECK PASSED"; exit 0 |
| `pnpm db:test` | pytest "210 passed in 201.81s (0:03:21)"; exit 0 (baseline 187 passed) |
### Hasil validasi aktual (2026-10-02, Windows, PowerShell 7, Python 3.12.13, branch `feat/postgres-persistence`)
| Perintah | Hasil |
|---|---|
| `pnpm lint` | ESLint tanpa temuan; Ruff "All checks passed!"; exit 0 (dijalankan ulang setelah perubahan dokumentasi) |
| `pnpm typecheck` | tsc tanpa error; mypy strict "Success: no issues found in 53 source files"; exit 0 |
| `pnpm test` (simulated) | Vitest 12 passed (3 file); pytest 151 passed, 36 skipped in 22.86s; exit 0. Tidak ada regresi terhadap baseline 105 passed; 36 skipped = 3 `tests/integration` + 33 test khusus postgres |
| `pnpm build` | next build berhasil, 13 route; exit 0 |
| `pnpm db:sql` | SQL offline ter-render untuk `0001_initial_schema` lalu `0002_ordering_columns` (`ADD COLUMN seq BIGINT GENERATED ALWAYS AS IDENTITY`, `uq_audit_logs_seq`, `ADD COLUMN position INTEGER DEFAULT '0' NOT NULL`, `ck_knowledge_tags_position`); exit 0 |
| `pnpm db:check` (pgserver) | upgrade `0001` -> `0002`; `alembic check` "No new upgrade operations detected."; seed run 1 menyisipkan baris, run 2 0 baris di 21 tabel; 30 tabel; FTS `metadata` 2 hit; non-simulasi 0; `audit seq` 1; `knowledge_tags` 8 baris, `position` 0: 8; append-only OK (UPDATE ditolak); downgrade `0002` -> `0001` -> base; "DATABASE CHECK PASSED"; exit 0 |
| `pnpm db:test` (pgserver, `SUNOVATE_TEST_BACKEND=postgres`) | upgrade `0001` -> `0002` + seed, lalu pytest "187 passed in 207.92s (0:03:27)", 0 skipped, 0 failed; exit 0; wall clock 269 s |
| Smoke manual `DATA_BACKEND=postgres` (skrip sementara di `%TEMP%`, pgserver, uvicorn port 8010, dihapus setelahnya) | `alembic upgrade head` dan seed exit 0; `GET /api/v1/health` 200 dengan `dataBackend` `postgres`; login `sim.staff.pppsun` 200; `GET /api/v1/dashboard/summary` 200; `GET /api/v1/knowledge` 200 (total 3); `POST /api/v1/hermes/query` 200 dengan decision `ANSWERED`; login `sim.owner.ppsun` dan `POST /api/v1/knowledge` draft (tim PPSUN, INTERNAL, tags `["smoke","smoke"]`) 201 dengan tags `["smoke"]`; uvicorn dihentikan dan dijalankan ulang; login ulang lalu `GET /api/v1/knowledge/{id}` 200 dengan judul yang sama. "SMOKE PASSED", wall clock 21 s. URI database tidak dicetak; tidak ada skrip atau direktori sementara tersisa |
| Pencarian emoji/ikon Unicode (U+2190-U+21FF, U+2600-U+27BF, U+1F300-U+1FAFF) pada file dokumentasi yang diubah | 0 temuan |

## 0.1.0 - 2026-10-01 (fondasi, belum siap produksi)

### Ditambahkan
- Dokumentasi 108 file di `docs/00-project` sampai `docs/13-handover` (+ indeks), termasuk 20 open question (OQ-01 sampai OQ-20), decision log ADR-001 sampai ADR-014, dan risk register R-01 sampai R-12. Draf sebelumnya diarsipkan ke `docs/_archive/legacy-docs-v0/`.
- Backend FastAPI modular: 13 modul router di `/api/v1`, otorisasi permission + team scope + klasifikasi, login pengembangan (token HMAC), audit append-only, approval dengan separation of duties, pipeline Hermes (ScopeGuard, retrieval terotorisasi, rerank, filter injeksi, CitationValidator, OutputGuard).
- Skema PostgreSQL 30 tabel (SQLAlchemy 2) dan migrasi Alembic `0001_initial_schema` dengan pgvector, FTS, dan trigger append-only; seed `SIMULATED_DATA` idempoten.
- Frontend Next.js: login dev, dashboard, Knowledge Hub, detail, pencarian, monitoring kerja, Hermes chat, administrasi, halaman 403/404/error/loading.
- Paket `@sunovate/contracts`, `@sunovate/shared-types`, `@sunovate/config`.
- Test: pytest (API, security, RAG golden set, integrasi DB opsional), Vitest, Playwright smoke.

### Diubah / dihapus
- Scaffold sebelumnya diganti: migrasi tabel generik, seed SQL dengan nama tim karangan, dashboard dengan nama tim karangan, shell ganda, dan tabel SUN Business yang belum tervalidasi.

### Hasil validasi aktual (2026-10-01, Windows, Node 24.19.0, Python 3.14.4)
| Perintah | Hasil |
|---|---|
| `pnpm lint` | ESLint tanpa temuan; Ruff "All checks passed" |
| `pnpm typecheck` | tsc tanpa error; mypy strict "no issues found in 49 source files" |
| `pnpm test` | Vitest 12 passed (3 file); pytest 105 passed, 3 skipped (integrasi DB tanpa `SUNOVATE_TEST_DATABASE_URL`) |
| `pnpm build` | next build berhasil, 13 route |
| `pnpm e2e` (API + web berjalan, Chromium lokal via `PW_CHROMIUM_PATH`) | 3 passed |
| `pnpm db:check` (PostgreSQL sementara + pgvector 0.6.2) | upgrade, `alembic check`, seed dua kali, 30 tabel, FTS, trigger append-only, downgrade: PASSED |
| `pnpm db:sql` | SQL migrasi ter-render offline |
| `pnpm compose:check` | Tidak dapat dijalankan: Docker tidak terpasang. `docker-compose.yml` hanya diparse sebagai YAML |
| Tautan dokumentasi | 0 tautan relatif rusak pada 109 file; diagram Mermaid belum dirender otomatis |
