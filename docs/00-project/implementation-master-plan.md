# Rencana Induk Implementasi SUNOVATE

**Status:** ACTIVE, NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-23

## Tujuan

Dokumen ini adalah urutan kerja utama SUNOVATE. Tambahan ide, gambar referensi, atau perubahan teknologi tidak boleh langsung mengubah urutan implementasi. Setiap perubahan harus dipetakan ke fase, dependensi, persetujuan, task tracker, dan changelog.

Roadmap enam bulan tetap mengikuti [product-roadmap.md](../01-product/product-roadmap.md). Dokumen ini menjelaskan urutan teknis di dalam roadmap tersebut.

## Prinsip Pengendalian Perubahan

1. Utamakan kebutuhan Dit. SUN dan hasil validasi mentor, bukan banyaknya teknologi.
2. Fitur tidak boleh berstatus selesai hanya karena sudah ada desain, mockup, atau dokumen.
3. Komponen yang menyentuh data asli, jaringan eksternal, identitas, AI eksternal, atau dokumen resmi membutuhkan persetujuan yang sesuai.
4. Implementasi baru harus memiliki pengujian, bukti validasi, pembaruan task tracker, dan changelog.
5. Frontend memakai nama **SAVI AI**. Nama internal lama hanya boleh muncul pada kode atau catatan migrasi yang memang diperlukan.
6. Modular monolith tetap menjadi baseline. Go, Rust, microservices, mobile, dan gateway terpisah hanya masuk setelah ada kebutuhan yang terbukti.
7. Batas data privat adalah gate sebelum seluruh fitur. Tidak ada data asli, publikasi, indexing, atau egress AI/agent eksternal sampai persetujuan dan kontrol infrastruktur diverifikasi.

## Empat Jalur Kerja

| Jalur | Cakupan | Tujuan akhir |
|---|---|---|
| Produk dan proses | requirement, peran, alur kerja, dashboard, Draft Workspace, reward | Kebutuhan pengguna jelas dan tidak mengarang proses Dit. SUN |
| Data dan SAVI AI | metadata, ekstraksi, chunking, retrieval, RAG, sitasi, evaluasi | Jawaban berbukti, terotorisasi, dan tetap di dalam domain SUN |
| Platform dan keamanan | API, autentikasi, otorisasi, audit, gateway control, database | Sistem dapat diuji dengan aman dan setiap akses dapat ditelusuri |
| Operasional dan implementasi | server demo, backup, load test, UAT, dokumentasi | Demo terbatas dapat dijalankan dan diserahterimakan secara terukur |

## Urutan Implementasi Wajib

### Tahap 0. Baseline dan kendali perubahan

**Target:** 14 sampai 20 Oktober 2026, masih di bulan pertama magang.

| Pekerjaan | Status | Syarat selesai |
|---|---|---|
| Menyatukan roadmap, task tracker, arsitektur, dan changelog | IN PROGRESS | Tidak ada fitur yang memiliki status saling bertentangan. Pemeriksaan 23 Okt menyelaraskan jumlah tim (tujuh), jumlah tabel (31), katalog endpoint, komponen, dan status roadmap (TASK-038) |
| Menjaga daftar pertanyaan mentor dan keputusan terbuka | IN PROGRESS | Pertanyaan prioritas memiliki pemilik keputusan dan dampak |
| Menetapkan skenario demo berbasis `SIMULATED_DATA` | READY FOR MENTOR REVIEW | Alur 8-10 menit terdokumentasi (diperbarui 23 Okt); `pnpm demo:smoke` memvalidasi 12 langkah: login, dashboard, monitoring, Knowledge Hub, pencarian, jawaban bersumber, dua penolakan SAVI, unduhan Excel, penampil dokumen rahasia, dan penolakan pengguna tanpa akses |
| Membekukan penambahan framework tanpa alasan terukur | ACTIVE RULE | Stack baru hanya masuk melalui keputusan arsitektur |
| Mengunci batas data privat | IN PROGRESS | Kontrol aplikasi lulus uji; firewall egress, jaringan privat, SSO/MFA, dan persetujuan TIK/pemilik data wajib sebelum data asli |

**Gate T0:** scope P0, tim, klasifikasi, login target, sumber dokumen, dan batas demo dibawa ke validasi mentor.

### Tahap 1. Fondasi platform dan kontrol API

**Target:** 21 Oktober sampai 20 November 2026.

Urutan pekerjaan:

1. Menuntaskan repository PostgreSQL dan konsistensi transaksi.
2. Memastikan autentikasi target dan matriks izin disetujui.
3. Menegakkan pemeriksaan peran, tim, klasifikasi, dan status dokumen pada service layer.
4. Melengkapi kontrol gateway di FastAPI: ukuran request, timeout, rate limiting, security headers, dan metrik dasar.
5. Menjaga prefix `/api/v1`, `X-Request-ID`, format error, audit log, dan CORS terbatas yang sudah tersedia.
6. Menambah reverse proxy Nginx hanya pada paket demo, bukan membuat microservice baru.

| Kontrol API | Status 14 Okt 2026 | Langkah berikutnya |
|---|---|---|
| Routing `/api/v1` | IMPLEMENTED | Pertahankan kontrak dan uji kompatibilitas |
| Request ID dan format error | IMPLEMENTED | Tambahkan pemeriksaan pada seluruh respons penting |
| Autentikasi pengembangan | IMPLEMENTED | Ganti dengan mekanisme yang disetujui sebelum produksi |
| RBAC, scope tim, dan klasifikasi | IMPLEMENTED pada scaffold | Validasi matriks bersama mentor dan uji PostgreSQL |
| Audit logging | IMPLEMENTED | Tinjau retensi dan akses auditor |
| CORS | IMPLEMENTED, perlu konfigurasi lingkungan | Batasi ke origin demo yang disetujui |
| Rate limiting | IMPLEMENTED untuk satu proses dan konfigurasi Nginx demo | Validasi paket pada Docker/host demo yang disetujui |
| Batas ukuran request dan unggahan | IMPLEMENTED baseline 3 MiB pada API dan Nginx demo | Selaraskan dengan kebijakan dokumen sebelum deployment |
| Trusted client IP | IMPLEMENTED fail-closed | CIDR proxy kosong secara default; validasi alamat proxy pada host demo |
| Timeout dan circuit breaker layanan eksternal | PARTIAL | Timeout body, database, dan proxy tersedia; circuit breaker diterapkan saat provider eksternal disetujui |
| Metrik kontrol API | IMPLEMENTED privat per proses | Hubungkan ke observability resmi tanpa body, token, atau data sensitif setelah alat disetujui |
| Cache | DEFERRED | Hanya untuk data tidak sensitif dan setelah pola akses terukur |
| Load balancing | DEFERRED | Tidak dibutuhkan untuk demo satu komputer sekitar 25 pengguna |

**Gate T1:** autentikasi target, matriks izin, konfigurasi server, backup, TLS, dan administrator disetujui.

### Tahap 2. Knowledge Hub dan SAVI AI

**Target:** 21 November sampai 20 Desember 2026.

Urutan pekerjaan:

1. Menyetujui jenis dokumen, klasifikasi, pemilik, retensi, dan sumber resmi.
2. Menyiapkan ekstraksi pada dokumen simulasi dan review manusia.
3. Menggunakan preview chunking Python dan layar pemeriksaan manusia yang sudah tersedia untuk Pasal, tahap, dan bagian; hasil tetap tidak tersimpan sebelum gerbang intake disetujui.
4. Menilai RAG-Anything sebagai adapter parser-only terisolasi melalui pilot dokumen simulasi; paket tidak menjadi dependency aplikasi sebelum gate keamanan, resource, dan OQ-11 terpenuhi.
5. Menyimpan chunk terverifikasi dan mengaktifkan PostgreSQL full-text search.
6. Menggunakan reranker leksikal dan evidence gate deterministik yang sudah tersedia sebagai baseline aman.
7. Memilih model embedding, reranker model, dan LLM hanya setelah OQ-11 ditutup.
8. Mengaktifkan hybrid retrieval bila evaluasi menunjukkan peningkatan yang nyata.
9. Menjalankan scope guard, prompt-injection defense, penyaringan izin sebelum retrieval, validasi sitasi, dan respons bukti tidak cukup.
10. Menguji pertanyaan mentor, golden set, akurasi retrieval, sitasi, penolakan, dan kebocoran akses.

Pola Agentic AI dibatasi pada orkestrasi terkendali. Multi-agent, web search bebas, memori jangka panjang, dan tindakan otomatis tidak termasuk MVP.

**Gate T2:** sumber RAG, model, evaluator, ambang kualitas, dan batas eskalasi SAVI disetujui.

### Tahap 3. Alur kerja web dan dashboard

**Target:** 21 Desember 2026 sampai 20 Januari 2027.

Urutan pekerjaan:

1. Menuntaskan monitoring kerja dan alur persetujuan yang telah disahkan.
2. Menghubungkan Knowledge Hub, pencarian, dan SAVI ke antarmuka institusional.
3. Menampilkan indikator dashboard hanya bila definisi dan sumber datanya tersedia.
4. Mengimplementasikan Draft Workspace hanya setelah permission, provider, approval chain, penarikan, dan retensi disetujui.
5. Melakukan pengujian aksesibilitas, responsif, bahasa pengguna nonteknis, dan usability bersama pengguna terbatas.

**Gate T3:** indikator dashboard, format laporan, alur publikasi, dan permission file disetujui.

### Tahap 4. Integrasi yang disetujui

**Target:** 21 Januari sampai 20 Februari 2027.

Prioritasnya adalah document automation Python berdasarkan template resmi, notifikasi dalam aplikasi, dan integrasi yang telah lulus review. Telegram, WhatsApp, SharePoint, Power BI, SSO, serta provider AI tidak otomatis aktif hanya karena sudah direncanakan.

Setiap integrasi harus memiliki:

- pemilik sistem dan dasar penggunaan;
- autentikasi serta pengelolaan secret;
- klasifikasi data yang boleh keluar;
- timeout, retry terbatas, circuit breaker, dan audit;
- prosedur penghentian serta fallback;
- pengujian kegagalan tanpa membuka data.

**Gate T4:** feature-complete, template resmi, integrasi, serta lingkungan UAT disetujui.

### Tahap 5. Demo, UAT, dan serah terima

**Target:** 21 Februari sampai 20 Maret 2027. Persiapan demo teknis dapat dilakukan lebih awal tanpa data asli dan tanpa membuka tunnel.

Urutan pekerjaan:

1. Menyiapkan satu komputer server dengan konfigurasi yang disetujui.
2. Menjalankan backup dan restore drill.
3. Melakukan security checklist dan pemindaian dependency.
4. Melakukan load test sekitar 25 pengguna berdasarkan spesifikasi host aktual.
5. Mengaktifkan Cloudflare Tunnel/Access hanya dengan persetujuan mentor dan TIK/keamanan.
6. Melaksanakan UAT terbatas menggunakan data yang diizinkan.
7. Menutup bug P0, mendokumentasikan bug P1/P2, dan menyusun handover.

**Gate T5:** UAT ditandatangani, tidak ada bug P0 terbuka, runbook dan dokumentasi pemulihan tersedia.

## Urutan Pekerjaan Terdekat

Urutan ini berlaku sampai ada keputusan mentor yang mengubah prioritas:

1. Rapikan baseline requirement dan daftar keputusan yang masih terbuka.
2. Tinjau naskah demo bulan pertama bersama mentor; pemeriksa API simulasi sudah tersedia melalui `pnpm demo:smoke`, tetapi browser, PostgreSQL, Nginx, jaringan, dan host aktual belum tervalidasi.
3. Validasi paket Nginx/Compose, trusted proxy, dan probe 25 pengguna pada host demo yang disetujui; jangan aktifkan tunnel.
4. Tuntaskan pengujian repository PostgreSQL dan otorisasi.
5. Pertahankan baseline `pnpm extraction:eval` untuk ingestion dokumen simulasi dari ekstraksi
   sampai preview chunk. Perluas corpus secara bertahap, lalu jalankan preflight dan benchmark
   parser-only RAG-Anything secara terisolasi tanpa memublikasikan isi atau hasil dokumen.
6. Minta keputusan mentor untuk sumber RAG, model AI, login, klasifikasi, server, dan UAT.
7. Setelah keputusan tersedia, lanjutkan ingestion tersimpan, FTS, dan evaluasi SAVI.

## Status Urutan Terdekat per 23 Oktober 2026

| No | Pekerjaan | Status | Bukti atau hambatan |
|---|---|---|---|
| 1 | Baseline requirement dan keputusan terbuka | IN PROGRESS | Dokumen ini, [open-questions.md](open-questions.md) (OQ-38 sampai OQ-42), DEC-20261021-01 dan DEC-20261021-02 di [decision-log.md](../12-governance/decision-log.md), task tracker sampai TASK-038 |
| 2 | Naskah demo untuk ditinjau mentor | READY FOR MENTOR REVIEW | [demo-scenario-month-one.md](demo-scenario-month-one.md) dan `pnpm demo:smoke` 12 langkah |
| 3 | Validasi Nginx/Compose, trusted proxy, probe 25 pengguna | BLOCKED | Membutuhkan host demo yang disetujui dan Docker; per 23 Okt Docker belum terpasang di laptop pengembang (dicek dari Git Bash dan PowerShell), sehingga `pnpm compose:demo:check` dan `pnpm demo:load` belum dijalankan. `pnpm demo:preflight` (statis) lulus |
| 4 | Pengujian repository PostgreSQL dan otorisasi | DONE untuk pengembangan | `pnpm db:test` lulus penuh di Linux dan Windows (PostgreSQL sementara), termasuk migrasi 0003; PostgreSQL pada host belum diuji |
| 5 | Baseline ekstraksi dan corpus | IN PROGRESS | `pnpm extraction:eval` 13 kasus + 4 penolakan; preflight tahap P0 RAG-Anything (`scripts/experiments/rag_anything/preflight.py`, tersedia sejak 16 Okt) dijalankan 23 Okt dan berstatus tidak siap sesuai rancangan karena paket belum terpasang; benchmark parser-only P1 menunggu OQ-11 dan review keamanan |
| 6 | Keputusan mentor | IN PROGRESS | Butir 1 sampai 4 dijawab 21 Okt (dokumen rahasia); model AI, rujukan PMK, server, peran, dan UAT masih ditunggu |
| 7 | Ingestion tersimpan, FTS, evaluasi SAVI | WAITING | Menunggu butir 6; evaluasi SAVI berkategori (`pnpm savi:eval`, 43 kasus) sudah tersedia |

Pekerjaan di luar urutan ini yang telah dikerjakan atas permintaan project lead dan arahan mentor,
beserta pemetaan fasenya:

| Pekerjaan | Tahap | Dasar |
|---|---|---|
| Penampil dokumen RAHASIA, pengelolaan akses, enkripsi envelope (TASK-027, 028, 031, 032) | Tahap 1 (kontrol akses) dengan isi dokumen asli tertahan gate OQ-40 sampai OQ-42 | Arahan setelah rapat 6 Oktober 2026, DEC-20261021-01/02, ADR-020 |
| Penyempurnaan visual landing, login, dashboard (TASK-026) | Tahap 3 butir 5 (responsif dan bahasa pengguna) | Permintaan project lead |
| Fitur ala Excel dan unduhan (TASK-033, 034) | Tahap 3 butir 1 (monitoring kerja) | Kebiasaan pengguna Dit. SUN dengan dashboard Excel |
| Panduan singkat (TASK-035) | Tahap 3 butir 5 (usability) | Permintaan project lead; uji dengan pegawai masih diperlukan |

## Aturan Memasukkan Ide Baru

Setiap ide baru harus menjawab lima pertanyaan:

1. Masalah Dit. SUN apa yang diselesaikan?
2. Termasuk P0, P1, P2, atau pasca-MVP?
3. Data dan kewenangan apa yang dibutuhkan?
4. Fitur yang sudah ada mana yang menjadi dependensi?
5. Bagaimana fitur diuji dan kapan dianggap selesai?

Jika jawaban belum tersedia, ide dicatat sebagai `PROPOSED`, `NEEDS APPROVAL`, atau `DEFERRED`, bukan langsung diimplementasikan.

## Related Documents

- [product-roadmap.md](../01-product/product-roadmap.md)
- [task-tracker.md](../13-handover/task-tracker.md)
- [open-questions.md](./open-questions.md)
- [technology-stack.md](../03-architecture/technology-stack.md)
- [deployment-architecture.md](../03-architecture/deployment-architecture.md)
- [rag-pattern-reference.md](../05-ai-rag/rag-pattern-reference.md)
- [change-management.md](../12-governance/change-management.md)
