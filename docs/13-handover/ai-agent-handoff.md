# AI Agent Handoff

**Status:** ACTIVE
**Last Updated:** 2026-10-14

## Baca Sebelum Bertindak

Urutan wajib: root `AGENTS.md`, [task-tracker.md](task-tracker.md), [developer-handover.md](developer-handover.md), [open-questions.md](../00-project/open-questions.md), lalu dokumen domain/arsitektur yang berkaitan dengan task.

## Snapshot Saat Ini

- SUNOVATE adalah modular monolith Next.js/TypeScript + FastAPI/Python + PostgreSQL/pgvector. Nama asisten pada frontend adalah **SAVI AI**; beberapa nama internal lama masih dapat memakai `HermesGateway` dan tidak boleh diganti massal tanpa migration plan.
- Semua demo memakai `SIMULATED_DATA`. Tidak ada integrasi produksi yang aktif atau boleh diklaim tersedia.
- Target demo yang sedang diusulkan adalah sekitar 25 pengguna pada satu komputer kantor khusus, menggunakan Docker Compose dan reverse proxy. Cloudflare Tunnel + Cloudflare Access adalah **PROPOSED** dan belum boleh diaktifkan tanpa persetujuan mentor serta TIK/keamanan.
- Komputer kantor adalah target demo/UAT sementara, bukan arsitektur produksi. Produksi menunggu keputusan private cloud/Azure/internal data center/hybrid.
- Go, Rust, PWA, Android, dan iOS adalah roadmap pasca-MVP. Jangan menambah service atau dependency hanya agar stack tampak lebih banyak.
- Monitoring kerja memiliki CRUD terotorisasi untuk output, tugas, milestone, pending matter, dan follow-up. Approval khusus monitoring belum boleh dikarang; TASK-005 tetap IN PROGRESS sampai OQ-12/OQ-25 diputuskan.
- Dashboard menyebut Yield SUN dan Kepemilikan SBN tanpa angka, masing-masing "Sumber data belum tersedia". Jangan menambahkan angka, grafik, atau tabel bisnis sebelum OQ-21 diputuskan.
- ScopeGuard SAVI memiliki 24 golden cases sejak 2026-10-11. Pertanyaan tertolak harus berhenti sebelum retrieval; karakter zero-width sederhana dinormalisasi; permintaan kredensial/jailbreak/keputusan investasi ditolak; penyebutan Python dalam konteks SUNOVATE dan kata "menghapus" yang informasional tidak boleh menjadi false refusal.
- Arahan mentor yang diteruskan project lead pada 2026-10-14 menyatakan mekanisme tindak lanjut bukti tidak cukup dapat dilanjutkan. Implementasi saat ini hanya menampilkan panduan memperjelas konteks atau meminta pemeriksaan pegawai berwenang. Jangan menambahkan penunjukan PIC, tiket, notifikasi, SLA, atau publikasi otomatis sebelum peran dan kewenangannya diputuskan. Pencarian ulang dengan perluasan istilah belum diimplementasikan.
- Delapan pertanyaan operasional dari arahan mentor 2026-10-13 berada di `apps/api/sunovate_api/resources/sme_question_intake.json`, bukan golden set aktif. Halaman read-only `/savi-validation` tersedia bagi role simulasi dengan `knowledge:review` dan `scope:all_teams`, dilengkapi ringkasan status, pencarian, filter, format cetak, serta lembar persiapan keputusan mentor yang hanya hidup pada state browser. Pertanyaan tetap diblokir dari retrieval dan jawaban SAVI (OQ-36). Jangan menyimpan keputusan, menambahkan aksi approval, atau mempromosikan kasus sebelum keputusan mentor diterima melalui mekanisme resmi.
- Draft Workspace untuk file hasil pekerjaan adalah proposal tertunda (FR-56/TASK-019), bukan fitur aktif. DRAFT boleh diubah/dihapus lunak oleh pemilik berizin; versi PUBLISHED harus immutable; koreksi menjadi versi baru; penarikan mempertahankan audit. Jangan implementasikan atau menganggap akun utama sebagai super-admin konten sebelum OQ-35 diputuskan.
- Specification-ready package Draft Workspace ada di `docs/02-business/work-file-draft-workspace.md`, termasuk model dan endpoint kandidat serta AC-26 sampai AC-31. Jangan membuat migration atau route dari rancangan ini sebelum OQ-35, provider file, dan approval chain dikonfirmasi.
- Ketua tim proyek mengarahkan implementasi; mentor mengawasi dan memvalidasi kebutuhan. Keputusan jaringan, domain, identitas, data, keamanan, dan produksi tetap memerlukan pihak instansi yang berwenang.

## Batas yang Tidak Boleh Dilanggar

- Jangan mengarang fungsi SUN Tematik, proses kerja Dit. SUN, angka yield/kepemilikan SBN, struktur persetujuan, atau format dokumen resmi.
- Jangan mengubah label `NEEDS APPROVAL`/`OPEN QUESTION` menjadi selesai tanpa sumber keputusan.
- Jangan menyimpan file sebagai BLOB, memberi SAVI AI akses DB langsung, atau mengeksekusi aksi tulis AI tanpa human approval.
- Teks yang terlihat pengguna wajib memakai bahasa Indonesia nonteknis sesuai `docs/09-ui-ux/content-language.md`. Jangan tampilkan nama internal Hermes, API/endpoint, permission/scope, runtime, enum mentah, atau label mesin seperti `SIMULATED_DATA`, `PROPOSED`, dan `BLOCKED` pada antarmuka. Istilah tersebut tetap boleh berada pada kode dan dokumentasi pengembang.
- Jangan mengaktifkan Cloudflare Tunnel, SSO, SharePoint, Telegram, WhatsApp, Power BI, model AI eksternal, atau data pasar hanya berdasarkan roadmap.
- Jangan mengedit dokumen sumber root atau `docs/_archive/`.

## Definition of Handoff Selesai

1. Task tracker dan changelog diperbarui.
2. ADR/decision log/risk register diperbarui bila ada perubahan arsitektur atau kebijakan.
3. Test relevan benar-benar dijalankan dan hasil aktual dicatat.
4. Tidak ada klaim yang melampaui implementasi atau persetujuan.
5. Commit kecil, dapat ditinjau, dan tidak mencampur file pengguna yang tidak terkait.

## Related Documents

- [task-tracker.md](task-tracker.md)
- [architecture-decisions.md](../03-architecture/architecture-decisions.md)
- [decision-log.md](../12-governance/decision-log.md)
- [risk-register.md](../12-governance/risk-register.md)

