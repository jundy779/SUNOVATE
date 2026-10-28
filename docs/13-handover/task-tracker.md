# Task Tracker SUNOVATE

**Status:** ACTIVE
**Last Updated:** 2026-10-27

## Purpose

Menjadi sumber status pekerjaan lintas sesi dan lintas AI agent. Setiap perubahan material wajib memperbarui baris terkait, bukti implementasi, dokumen keputusan, dan `CHANGELOG.md`.

## Aturan Status

| Status | Arti |
|---|---|
| DONE | Implementasi dan validasi tersedia pada repository. |
| IN PROGRESS | Sedang dikerjakan; belum boleh diklaim selesai. |
| PLANNED | Sudah masuk urutan kerja, belum dimulai. |
| NEEDS APPROVAL | Diblokir keputusan mentor, TIK/keamanan, atau pemilik data. |
| DEFERRED | Roadmap setelah MVP; bukan komitmen fase demo. |

## Tracker Aktif

| ID | Task | Fase | Status | Gate / bukti |
|---|---|---|---|---|
| TASK-001 | Landing page, login simulasi, shell aplikasi, dan dashboard institusional | MVP | DONE | Implementasi web; dashboard editorial v2 selesai 2026-10-19; data tetap `SIMULATED_DATA`. QA visual screenshot desktop/mobile masih perlu dijalankan pada host dengan browser Playwright. |
| TASK-002 | Dashboard berkonteks Dit. SUN tanpa angka bisnis yang tidak tervalidasi | MVP | DONE | Dashboard memakai jumlah terotorisasi dari API untuk prioritas, fokus kerja, status tugas, persetujuan, tindak lanjut, dan pengetahuan terbaru. Grafik/persentase statis dihapus melalui BUG-023. Yield SUN dan Kepemilikan SBN tetap "Sumber data belum tersedia" dan diblokir OQ-21. |
| TASK-003 | Fondasi FastAPI, Repository, PostgreSQL, pgvector, Alembic, RBAC, dan audit | MVP | DONE | ADR-002, ADR-003, ADR-015; mode simulated tetap default. |
| TASK-004 | Monitoring kerja: pembacaan output, tugas, milestone, pending matter, follow-up | MVP | DONE | Endpoint dan halaman baca tersedia. |
| TASK-005 | CRUD lengkap monitoring kerja dan alur persetujuan | MVP | IN PROGRESS | CRUD API/UI, scope, revision, soft delete, audit, dan test selesai 2026-10-10. Approval tetap NEEDS APPROVAL karena OQ-12/OQ-25. |
| TASK-006 | Knowledge Hub: ingestion, ekstraksi, chunking, FTS dan semantic retrieval | MVP | IN PROGRESS | Ekstraksi Python di memori untuk TXT/MD/PDF/DOCX/XLSX/XLS simulasi, status `PENDING/EXTRACTED/FAILED/QUARANTINED`, review manusia, chunking, draf, FTS PostgreSQL untuk pencarian umum/draf, evaluator pencarian 10 kasus, evaluator ekstraksi 7 kasus, dan runner eksplisit `search:eval:postgres` telah ada. Baseline `extraction:eval` lulus seluruh rasio 1,00 dan forbidden hits 0; mencakup PDF dua halaman, DOCX berjudul dengan tabel berurutan, XLSX/XLS multi-lembar, serta karantina instruksi pada lembar tersembunyi. Rumus Excel tidak dijalankan, berkas sumber tidak disimpan, dan draf tidak masuk pencarian umum/SAVI. Baseline PostgreSQL aktual, persistensi status ingestion produksi, OCR, pemindai malware, FTS untuk retrieval SAVI, dan semantic retrieval belum selesai. |
| TASK-007 | SAVI AI: RAG bersitasi dengan provider AI yang disetujui | MVP | IN PROGRESS | Provider ekstraktif development, reranker leksikal, evidence gate deterministik, respons bukti tidak cukup, dan retry satu kali untuk lima kelompok variasi ejaan tersedia. Dashboard dan halaman SAVI menjelaskan sumber terkendali, batas domain, sitasi, serta pemeriksaan manusia dengan bahasa awam. Percakapan kini memiliki contoh pertanyaan teruji, jumlah dan daftar rujukan, percakapan baru, serta tindak lanjut berbeda untuk sumber tidak ditemukan dan bukti lemah. Ini belum menjadi LLM produksi: model generatif, reranker model, embedding, dan lokasi pemrosesan tetap menunggu OQ-11/OQ-37 final. |
| TASK-008 | Guard domain SUN, prompt-injection defense, output guard, dan human approval | MVP | IN PROGRESS | Guard deterministik, filter retrieval, karantina indikasi injeksi pada ekstraksi/simpan draf simulasi, output guard, approval, dan 24 golden cases tersedia. Deteksi ingestion berbasis aturan dan bukan keputusan final; antrean karantina produksi belum ada. Delapan pertanyaan mentor tetap diblokir dari retrieval/jawaban SAVI sambil menunggu validasi. |
| TASK-020 | Bahasa antarmuka pengguna nonteknis | MVP | DONE | Pemetaan label terpusat, penggantian istilah teknis pada halaman publik dan ruang kerja, pedoman UI, AC-32, serta test fallback label tersedia. Audit 2026-10-20 menutup BUG-025: jenis pengetahuan pada hasil pencarian, tujuh nama layanan administrasi, keterangan kewenangan, nama pengguna simulasi, dan pesan kegagalan kini memakai bahasa Indonesia yang jelas serta nama SAVI AI. Kode internal tetap dipertahankan. Audit kanal Telegram/WhatsApp dilakukan saat kanal diimplementasikan. |
| TASK-009 | Generator dokumen/arsip resmi berbasis Python dan template yang disetujui | P1 | PLANNED | Diblokir OQ-16; tidak boleh membuat format resmi dari asumsi. |
| TASK-010 | Reward/trophy pegawai untuk mendorong kontribusi | P1 | NEEDS APPROVAL | Mekanisme, indikator, fairness, dan dampak perilaku harus disetujui mentor. |
| TASK-011 | Paket demo satu komputer kantor: Docker Compose, Nginx, web, API, PostgreSQL | Demo | NEEDS APPROVAL | Scaffold `deploy/demo/` tersedia dengan bind localhost-only, network internal, limit Nginx, non-root app container, healthcheck, placeholder secret, dan preflight privat 10 test. Access log tidak merekam query string. Alat latihan backup-restore fail-closed tersedia, tetapi Compose/restore belum dijalankan aktual. Docker/host, OS, admin, backup off-host, TLS, dan aktivasi menunggu OQ-23. |
| TASK-012 | Akses demo melalui Cloudflare Tunnel dan Cloudflare Access | Demo | NEEDS APPROVAL | Contoh konfigurasi nonaktif memakai domain `.invalid`, tanpa tunnel ID/kredensial dan tanpa service Compose. Aktivasi tetap wajib persetujuan mentor dan TIK/keamanan. |
| TASK-013 | Load test target sekitar 25 pengguna demo | Demo | IN PROGRESS | Probe privat tersedia. Baseline API-only lokal 25 pengguna/100 request lulus dengan error 0% dan p95 41,26 ms; ini bukan uji aplikasi penuh. Host aktual, SLA, CPU/RAM/disk/DB, ramp-up/steady/spike masih wajib. |
| TASK-014 | UAT terbatas sekitar 25 pengguna dengan `SIMULATED_DATA` | Demo | NEEDS APPROVAL | Daftar pengguna dan lingkungan menunggu OQ-20; sign-off mentor. |
| TASK-015 | Layanan Go untuk gateway, webhook, notifikasi, atau worker berkongkurensi tinggi | Pasca-MVP | DEFERRED | Hanya ditambahkan jika metrik beban menunjukkan kebutuhan; bukan syarat 25 pengguna. |
| TASK-016 | Komponen Rust untuk validasi file, checksum, parsing aman, atau redaction | Pasca-MVP | DEFERRED | Hanya setelah kebutuhan keamanan/performa terbukti dan threat review selesai. |
| TASK-017 | PWA dan aplikasi Android/iOS (Flutter atau native wrapper) | Pasca-MVP | DEFERRED | API dan auth harus stabil; kebijakan distribusi perangkat belum ditentukan. |
| TASK-018 | Keputusan hosting produksi: private cloud/Azure/internal data center/hybrid | Produksi | NEEDS APPROVAL | Keputusan instansi/TIK; komputer kantor bukan target produksi. |
| TASK-019 | Draft Workspace dan file pekerjaan terbit yang immutable | Pasca-MVP | NEEDS APPROVAL | Desain teknis, status, model kandidat, API kandidat, UI, permission, dan AC-26 sampai AC-31 selesai 2026-10-11. Permission, provider, approval chain, penarikan, dan retensi menunggu OQ-35; kode belum diimplementasikan. |
| TASK-021 | Kontrol API Gateway pada modular monolith: rate limit, batas request, timeout, security headers, metrik | Foundation | IN PROGRESS | Kontrol aplikasi sebelumnya ditambah trusted proxy CIDR fail-closed serta paket Nginx dengan limit request/body/koneksi, timeout, header privat, error JSON, dan format log tanpa query string. `demo:preflight` mengunci invariant ini. Compose belum diuji pada Docker/host aktual; timeout proxy bukan pembatalan transaksi; metrik resmi dan circuit breaker provider tetap menunggu alat/provider disetujui. |
| TASK-022 | Pilot RAG-Anything sebagai pemroses dokumen multimodal terisolasi | AI & Data | IN PROGRESS | ADR-017, rencana pilot, risk R-23, dan preflight fail-closed tersedia. Parser/dependency belum dipasang; hanya fixture `SIMULATED_DATA`; benchmark, sandbox worker, SBOM, security test, dan OQ-11 masih diperlukan. |
| TASK-023 | Batas data privat dan pencegahan publikasi/AI exfiltration | Foundation | IN PROGRESS | Lock startup untuk mode privat dan larangan public indexing/AI egress/agent eksternal/telemetry egress; nilai boolean aman dari `.env` dapat dibaca dan nilai pelonggaran tetap ditolak oleh model validator; header no-store dan anti-index; robots menolak semua path; CSP same-origin; docs API disembunyikan di non-development; pola exfiltration/jailbreak ditolak sebelum retrieval; preflight menolak konfigurasi demo yang tidak aman tanpa menampilkan secret. Verifikasi firewall egress, jaringan privat, SSO/MFA, pentest, dan persetujuan TIK/pemilik data masih wajib sebelum data asli. |
| TASK-024 | Skenario dan pemeriksaan perjalanan demo bulan pertama | Demo | IN PROGRESS | Naskah 8-10 menit dan `pnpm demo:smoke` tersedia (diperbarui 23 Okt). Dua belas langkah API simulasi memeriksa health, login, dashboard, monitoring, Knowledge Hub, pencarian, jawaban SAVI bersumber, dua penolakan aman, unduhan Excel, penampil dokumen rahasia, dan penolakan pengguna tanpa akses tanpa mencetak konten. Review mentor, pengujian browser, PostgreSQL, Nginx, jaringan, dan host aktual masih diperlukan. |
| TASK-025 | Tambah MONEV sebagai tim pilot ketujuh pada shared types, seed `SIMULATED_DATA`, tes, dan dokumentasi; perbarui nama resmi di README | MVP | DONE | DEC-20261020-01; tanpa record simulasi MONEV; tes `test_teams_are_the_seven_pilot_codes`; validasi pada CHANGELOG 2026-10-20. |
| TASK-026 | Penyempurnaan visual landing, halaman masuk, dan dashboard (gabungan gaya Bank Indonesia dan The Economist, palet terkunci, satu animasi per halaman, aman untuk reduced motion) | MVP | DONE | QA visual Chromium desktop 1440 px dan mobile 390 px; perbaikan overflow mobile pada shell dan tabel; validasi pada CHANGELOG 2026-10-21. |
| TASK-027 | Fondasi dokumen RAHASIA: penampil hanya-baca (halaman PNG bertanda air dari server, tanpa route unduh/teks), pembaca eksplisit per dokumen, audit, batas laju, dan enkripsi envelope AES-256-GCM dengan antarmuka `KeyProvider` | MVP | DONE (simulasi) | ADR-020; 12 tes keamanan; penyedia TPM, persistensi, dan UI penampil menunggu OQ-40 sampai OQ-42. |
| TASK-028 | Penampil dokumen RAHASIA di web: daftar dokumen yang diberikan, pernyataan kerahasiaan wajib (dicatat dan berlaku 30 menit), pembaca per halaman lewat proxy same-origin, serta penghalang salin/simpan/cetak di browser | MVP | DONE (simulasi) | ADR-020; 3 test API, 3 test unit web, 2 skenario e2e baru; penampil desktop dan kebijakan browser terkelola menunggu OQ-41. |
| TASK-029 | Kepatuhan dokumentasi dan pengerasan: bug register BUG-026 sampai BUG-033, keputusan terbaru di handoff, dependency di technology stack, dokumen keamanan penampil RAHASIA, pemetaan peran dan klasifikasi rancangan ke kode, CSP ketat gambar halaman, soft 404 detail dokumen, pembaruan `source-map-js`, dan perbaikan dua uji mode PostgreSQL | MVP | DONE | `pnpm db:test` 347/347 lulus pada PostgreSQL sementara; dua temuan audit high tersisa dicatat di KL-28. |
| TASK-030 | Perluasan corpus ekstraksi (13 kasus + 4 penolakan) dan evaluasi jawaban SAVI berkategori (43 kasus, `pnpm savi:eval`), serta penguatan ScopeGuard untuk leetspeak, bermain peran, muatan terenkode, permintaan rahasia, waktu beli/jual, dan query SQL | MVP | DONE | Gate keras kebocoran 0, sitasi 100%, serangan terjawab 0; uji false positive untuk pertanyaan kebijakan kata sandi. |
| TASK-031 | Pengelolaan akses baca dokumen RAHASIA sesuai jawaban mentor: hanya Kasubdit PMP dan Ketua Tim, API daftar/beri/cabut pembaca dengan validasi clearance dan audit, serta halaman Kelola akses baca | MVP | DONE (simulasi) | DEC-20261021-01; 6 test API dan 1 skenario e2e baru; jenis dokumen menunggu kurasi ketua tim. |
| TASK-032 | Pengelolaan akses RAHASIA oleh Ketua Tim dan Kasubdit PMP (DEC-20261021-02): kewenangan lewat permission katalog `secure_document:manage_team` dan `secure_document:manage_all`, daftar pembaca permanen di PostgreSQL (migrasi 0003), dan batas waktu reset database uji | MVP | DONE | `db:check` (31 tabel, upgrade/downgrade) dan `db:test` lulus. |
| TASK-033 | Fitur ala Excel di Monitoring Kerja: cari judul, saring status dan tim, urutkan per kolom, dan Unduh Excel (`GET /exports/work`) berisi hanya data yang boleh dilihat pengguna, dengan filter otomatis, header beku, perlindungan formula, dan audit `WORK_EXPORT` | MVP | DONE | 9 test API, 3 test unit web, 1 skenario e2e; tabel Ringkasan belum memiliki unduhan. |
| TASK-034 | Unduh Excel daftar "Perlu ditindaklanjuti" di Ringkasan (`GET /exports/attention`): seluruh tugas dan tindak lanjut yang terlambat atau segera jatuh tempo dalam cakupan pengguna, bukan hanya enam baris di layar | MVP | DONE | 2 test API dan 1 skenario e2e; perhitungan daftar dipakai bersama dengan ringkasan. |
| TASK-035 | Panduan singkat di dalam aplikasi: halaman `/panduan` dengan lima panduan langkah demi langkah yang tampil sesuai kewenangan, tombol bantuan di bilah atas dan menu akun, serta catatan sambutan di Ringkasan yang dapat ditutup | MVP | DONE | 3 test unit web dan 1 skenario e2e; isi panduan belum diuji dengan pegawai. |
| TASK-036 | Sinkronisasi baseline sesuai urutan rencana induk: status urutan terdekat per 23 Oktober, pemetaan pekerjaan di luar urutan ke fase, naskah demo diperbarui dengan fitur terbaru dan daftar keputusan mentor, serta `pnpm demo:smoke` menjadi 12 langkah | Demo | DONE | Naskah tetap menunggu review mentor (TASK-024); validasi Nginx/Compose menunggu host. |
| TASK-038 | Pemeriksaan konsistensi status antardokumen (rencana induk Tahap 0 butir 1): jumlah tim menjadi tujuh di PRD, kebutuhan fungsional, kriteria penerimaan, aturan bisnis, user story, UAT, uji keamanan, dan dokumen proyek; skema 31 tabel di dokumen data dan arsitektur; katalog endpoint dan komponen memuat dokumen rahasia serta unduhan Excel; status roadmap bulan 2; koreksi status RAG-Anything P0; FR-58 sampai FR-60 untuk fitur yang sudah dibangun | Produk dan proses | DONE | Catatan historis (arsip, agenda sesi lama, audit 8 Okt, log keputusan) sengaja tidak diubah. |
| TASK-039 | Sisa sinkronisasi dokumen: kepanjangan resmi SUNOVATE di AGENTS.md, docs/README.md, project-overview (beserta tagline), dan developer-handover; status Secure Viewer di README; alias MEKPK untuk MONEV di glosarium; ID ganda KL-25/KL-26 di known-limitations | Dokumentasi | DONE | Hanya dokumen; validasi Linux 27 Okt pada PR #1 (lihat CHANGELOG 0.2.0). Blueprint v0.5 yang dirujuk README dan handoff belum ada di repository. |
| TASK-040 | ScopeGuard mengenali kosakata inti Narasi SUN (yield, kupon, cut-off, ORI, SBR, DMFAS, BI-ETP, JLM, seri FR/VR, MEKPK, dan lainnya) agar pertanyaan istilah tidak ditolak sebagai di luar lingkup (BUG-038) | MVP | DONE | 30 test baru, termasuk penolakan rekomendasi investasi berkode seri; validasi Linux 27 Okt pada PR #1; pertanyaan tanpa sumber tetap berakhir `INSUFFICIENT_EVIDENCE`; pemetaan makna glosarium tetap diblokir (OQ-37). |
| TASK-041 | Rilis versi 0.2.0: nomor versi di root, web, paket bersama, dan API dinaikkan dari 0.1.0; versi tampil di footer halaman depan dan `GET /api/v1/health` | Foundation | DONE | Penanda pengembangan, bukan rilis produksi. Validasi Linux 27 Okt: `pnpm validate` lulus, footer hasil build memuat "Versi 0.2.0", `GET /api/v1/health` melaporkan 0.2.0 (CHANGELOG 0.2.0). Validasi Windows belum. |
| TASK-042 | Tahap 1 butir 2 dan 5: matriks izin disinkronkan dengan kode (permission dokumen rahasia, 16 endpoint yang belum tercatat) dan dijaga oleh test drift; kontrak respons (badan error, `X-Request-ID`, header keamanan) diuji pada seluruh route; pesan 404/405 bawaan router diterjemahkan ke bahasa Indonesia | Platform | DONE | Matriks tetap NEEDS MENTOR VALIDATION (Gate T1). |

## Urutan Eksekusi Terdekat

1. Pertahankan TASK-023 sebagai gate paling awal. Dilarang memasukkan data asli sampai kontrol infrastruktur privat dan persetujuan terkait tervalidasi.
2. Ikuti urutan pada `implementation-master-plan.md`; jangan memulai ide baru hanya dari gambar referensi.
3. Tutup open question prioritas tinggi bersama mentor, khususnya OQ-05, OQ-07, OQ-11, OQ-20, OQ-23, OQ-24, dan OQ-25.
4. Minta mentor meninjau skenario demo bulan pertama. Baseline API simulasi sudah tersedia melalui `pnpm demo:smoke`; lanjutkan validasi browser dan host hanya pada lingkungan yang disetujui.
5. Pada host PostgreSQL uji yang disetujui, jalankan `pnpm db:restore-drill`, lalu
   `pnpm search:eval:postgres` pada hasil restore. Jangan menganggap uji unit alat sebagai bukti
   restore aktual atau baseline FTS PostgreSQL.
6. Lanjutkan TASK-006 dengan baseline PostgreSQL aktual dan perluasan corpus evaluasi ekstraksi.
   Baseline tujuh kasus untuk enam format dasar sudah tersedia. Jalankan TASK-022 hanya sebagai
   pilot parser terisolasi; jangan memasang dependency ke runtime atau mengaktifkan FTS pada
   retrieval SAVI sebelum gate evaluasi lulus.
7. Siapkan paket deployment tanpa mengaktifkan tunnel eksternal; setelah persetujuan, lakukan
   security checklist, backup/restore aktual, load test, lalu UAT.
8. Evaluasi Go, Rust, mobile, load balancing, dan gateway terpisah hanya dari metrik pasca-MVP.

## Kewajiban Handoff

- Agent yang mengubah kode, skema, arsitektur, scope, deployment, atau status approval harus memperbarui tracker ini.
- Satu task tidak boleh menjadi `DONE` hanya berdasarkan rencana atau mockup; cantumkan bukti implementasi dan hasil validasi.
- Perubahan keputusan dicatat pula di [decision-log.md](../12-governance/decision-log.md); risiko baru di [risk-register.md](../12-governance/risk-register.md).
- Dokumen sumber dan arsip historis tidak diedit.

## Related Documents

- [ai-agent-handoff.md](ai-agent-handoff.md)
- [developer-handover.md](developer-handover.md)
- [future-development.md](future-development.md)
- [deployment-architecture.md](../03-architecture/deployment-architecture.md)

