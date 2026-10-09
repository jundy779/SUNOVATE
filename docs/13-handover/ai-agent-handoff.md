# AI Agent Handoff

**Status:** ACTIVE
**Last Updated:** 2026-10-09

## Baca Sebelum Bertindak

Urutan wajib: root `AGENTS.md`, [task-tracker.md](task-tracker.md), [developer-handover.md](developer-handover.md), [open-questions.md](../00-project/open-questions.md), lalu dokumen domain/arsitektur yang berkaitan dengan task.

## Snapshot Saat Ini

- SUNOVATE adalah modular monolith Next.js/TypeScript + FastAPI/Python + PostgreSQL/pgvector. Nama asisten pada frontend adalah **SAVI AI**; beberapa nama internal lama masih dapat memakai `HermesGateway` dan tidak boleh diganti massal tanpa migration plan.
- Semua demo memakai `SIMULATED_DATA`. Tidak ada integrasi produksi yang aktif atau boleh diklaim tersedia.
- Target demo yang sedang diusulkan adalah sekitar 25 pengguna pada satu komputer kantor khusus, menggunakan Docker Compose dan reverse proxy. Cloudflare Tunnel + Cloudflare Access adalah **PROPOSED** dan belum boleh diaktifkan tanpa persetujuan mentor serta TIK/keamanan.
- Komputer kantor adalah target demo/UAT sementara, bukan arsitektur produksi. Produksi menunggu keputusan private cloud/Azure/internal data center/hybrid.
- Go, Rust, PWA, Android, dan iOS adalah roadmap pasca-MVP. Jangan menambah service atau dependency hanya agar stack tampak lebih banyak.
- Ketua tim proyek mengarahkan implementasi; mentor mengawasi dan memvalidasi kebutuhan. Keputusan jaringan, domain, identitas, data, keamanan, dan produksi tetap memerlukan pihak instansi yang berwenang.

## Batas yang Tidak Boleh Dilanggar

- Jangan mengarang fungsi SUN Tematik, proses kerja Dit. SUN, angka yield/kepemilikan SBN, struktur persetujuan, atau format dokumen resmi.
- Jangan mengubah label `NEEDS APPROVAL`/`OPEN QUESTION` menjadi selesai tanpa sumber keputusan.
- Jangan menyimpan file sebagai BLOB, memberi SAVI AI akses DB langsung, atau mengeksekusi aksi tulis AI tanpa human approval.
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

