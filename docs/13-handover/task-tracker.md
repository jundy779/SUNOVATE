# Task Tracker SUNOVATE

**Status:** ACTIVE
**Last Updated:** 2026-10-11

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
| TASK-001 | Landing page, login simulasi, shell aplikasi, dan dashboard institusional | MVP | DONE | Implementasi web; data tetap `SIMULATED_DATA`. |
| TASK-002 | Dashboard berkonteks Dit. SUN tanpa angka bisnis yang tidak tervalidasi | MVP | DONE | Commit remote `53f9bd4`; sejak 2026-10-11 UI menampilkan Yield SUN dan Kepemilikan SBN sebagai "Sumber data belum tersedia". Angka tetap diblokir OQ-21. |
| TASK-003 | Fondasi FastAPI, Repository, PostgreSQL, pgvector, Alembic, RBAC, dan audit | MVP | DONE | ADR-002, ADR-003, ADR-015; mode simulated tetap default. |
| TASK-004 | Monitoring kerja: pembacaan output, tugas, milestone, pending matter, follow-up | MVP | DONE | Endpoint dan halaman baca tersedia. |
| TASK-005 | CRUD lengkap monitoring kerja dan alur persetujuan | MVP | IN PROGRESS | CRUD API/UI, scope, revision, soft delete, audit, dan test selesai 2026-10-10. Approval tetap NEEDS APPROVAL karena OQ-12/OQ-25. |
| TASK-006 | Knowledge Hub: ingestion, ekstraksi, chunking, FTS dan semantic retrieval | MVP | IN PROGRESS | Repository dasar ada; ingestion dan semantic retrieval menunggu OQ-04/OQ-06/OQ-11. |
| TASK-007 | SAVI AI: RAG bersitasi dengan provider AI yang disetujui | MVP | IN PROGRESS | Provider ekstraktif development ada; nama frontend adalah SAVI AI. Model eksternal belum disetujui. |
| TASK-008 | Guard domain SUN, prompt-injection defense, output guard, dan human approval | MVP | IN PROGRESS | Guard deterministik, output guard, approval, dan 24 golden cases tersedia. Regresi 2026-10-11 mencakup credential request, English jailbreak, zero-width, financial advice, domain generik, serta false-positive write/coding. Validasi SME atas pertanyaan nyata tetap diperlukan. |
| TASK-009 | Generator dokumen/arsip resmi berbasis Python dan template yang disetujui | P1 | PLANNED | Diblokir OQ-16; tidak boleh membuat format resmi dari asumsi. |
| TASK-010 | Reward/trophy pegawai untuk mendorong kontribusi | P1 | NEEDS APPROVAL | Mekanisme, indikator, fairness, dan dampak perilaku harus disetujui mentor. |
| TASK-011 | Paket demo satu komputer kantor: Docker Compose, Nginx, web, API, PostgreSQL | Demo | NEEDS APPROVAL | Komputer khusus berasal dari jawaban knowledge owner; detail OS, admin, backup, TLS menunggu OQ-23. |
| TASK-012 | Akses demo melalui Cloudflare Tunnel dan Cloudflare Access | Demo | NEEDS APPROVAL | Usulan project lead 2026-10-09; wajib persetujuan mentor dan TIK/keamanan sebelum aktivasi. |
| TASK-013 | Load test target sekitar 25 pengguna demo | Demo | PLANNED | Skenario, SLA, spesifikasi host, dan data uji harus dicatat. |
| TASK-014 | UAT terbatas sekitar 25 pengguna dengan `SIMULATED_DATA` | Demo | NEEDS APPROVAL | Daftar pengguna dan lingkungan menunggu OQ-20; sign-off mentor. |
| TASK-015 | Layanan Go untuk gateway, webhook, notifikasi, atau worker berkongkurensi tinggi | Pasca-MVP | DEFERRED | Hanya ditambahkan jika metrik beban menunjukkan kebutuhan; bukan syarat 25 pengguna. |
| TASK-016 | Komponen Rust untuk validasi file, checksum, parsing aman, atau redaction | Pasca-MVP | DEFERRED | Hanya setelah kebutuhan keamanan/performa terbukti dan threat review selesai. |
| TASK-017 | PWA dan aplikasi Android/iOS (Flutter atau native wrapper) | Pasca-MVP | DEFERRED | API dan auth harus stabil; kebijakan distribusi perangkat belum ditentukan. |
| TASK-018 | Keputusan hosting produksi: private cloud/Azure/internal data center/hybrid | Produksi | NEEDS APPROVAL | Keputusan instansi/TIK; komputer kantor bukan target produksi. |
| TASK-019 | Draft Workspace dan file pekerjaan terbit yang immutable | Pasca-MVP | NEEDS APPROVAL | Desain teknis, status, model kandidat, API kandidat, UI, permission, dan AC-26 sampai AC-31 selesai 2026-10-11. Permission, provider, approval chain, penarikan, dan retensi menunggu OQ-35; kode belum diimplementasikan. |

## Urutan Eksekusi Terdekat

1. Tutup open question prioritas tinggi bersama mentor, khususnya OQ-05, OQ-07, OQ-11, OQ-20, OQ-23, OQ-24, dan OQ-25.
2. Selesaikan fitur P0 yang belum lengkap dan perkuat SAVI AI beserta evaluasi domain SUN.
3. Siapkan paket deployment demo tanpa mengaktifkan tunnel eksternal.
4. Setelah persetujuan tertulis, lakukan security checklist, backup/restore drill, load test 25 pengguna, lalu UAT.
5. Evaluasi Go, Rust, dan mobile hanya dari metrik dan kebutuhan pasca-MVP.

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

