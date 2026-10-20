# Task Tracker SUNOVATE

**Status:** ACTIVE
**Last Updated:** 2026-10-20

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
| TASK-024 | Skenario dan pemeriksaan perjalanan demo bulan pertama | Demo | IN PROGRESS | Naskah 8-10 menit dan `pnpm demo:smoke` tersedia. Sembilan langkah API simulasi memeriksa health, login, dashboard, monitoring, Knowledge Hub, pencarian, jawaban SAVI bersumber, serta dua penolakan aman tanpa mencetak konten. Review mentor, pengujian browser, PostgreSQL, Nginx, jaringan, dan host aktual masih diperlukan. |
| TASK-025 | Tambah MONEV sebagai tim pilot ketujuh pada shared types, seed `SIMULATED_DATA`, tes, dan dokumentasi; perbarui nama resmi di README | MVP | DONE | DEC-20261020-01; tanpa record simulasi MONEV; tes `test_teams_are_the_seven_pilot_codes`; validasi pada CHANGELOG 2026-10-20. |
| TASK-026 | Penyempurnaan visual landing, halaman masuk, dan dashboard (gabungan gaya Bank Indonesia dan The Economist, palet terkunci, satu animasi per halaman, aman untuk reduced motion) | MVP | DONE | QA visual Chromium desktop 1440 px dan mobile 390 px; perbaikan overflow mobile pada shell dan tabel; validasi pada CHANGELOG 2026-10-21. |

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

