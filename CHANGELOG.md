# Changelog

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
