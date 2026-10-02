# Security Checklist

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Daftar periksa keamanan yang dijalankan sebelum merge dan sebelum rilis (termasuk rilis ke lingkungan UAT). Item yang tidak berlaku ditandai N/A beserta alasannya di deskripsi perubahan.

## Pre-merge

### Data dan secret

- [ ] Seluruh data contoh, seed, fixture, dan screenshot berlabel `SIMULATED_DATA`; tidak ada angka SUN riil, data pribadi, nomor surat tugas, atau dokumen internal.
- [ ] Tidak ada secret, token, password, atau connection string di kode, uji, dokumentasi, atau commit.
- [ ] `.env` tidak ikut ter-commit; `.env.example` hanya berisi placeholder.
- [ ] File sumber PDF/PPTX tetap dikecualikan oleh `.gitignore` (ADR-014).

### Otorisasi

- [ ] Endpoint baru atau yang diubah memeriksa permission di API, sesuai [permission-matrix](permission-matrix.md).
- [ ] Akses rekaman tunggal memeriksa team scope dan klasifikasi; rekaman tak terbaca menghasilkan 404.
- [ ] Endpoint daftar menyaring rekaman yang tidak boleh dibaca.
- [ ] Penolakan dicatat sebagai `ACCESS_DENIED`.
- [ ] Tidak ada kontrol keamanan yang hanya mengandalkan frontend.
- [ ] Uji mencakup role tanpa permission (403), tim lain (404), dan clearance kurang (404).

### Hermes dan pencarian

- [ ] Retrieval tetap menyaring otorisasi sebelum scoring dan hanya memakai rekaman `PUBLISHED`.
- [ ] Tidak ada jalur Hermes yang mengakses database atau repository secara langsung.
- [ ] `CitationValidator` dan `OutputGuard` tetap aktif pada semua jalur jawaban.
- [ ] Write intent tetap menghasilkan `REQUIRES_HUMAN_APPROVAL` tanpa eksekusi.
- [ ] Uji jailbreak dan prompt injection tetap lulus (lihat [rag-testing](../10-testing/rag-testing.md)).

### Integritas dan logging

- [ ] Perubahan rekaman memakai `revision`; pembaruan basi menghasilkan 409 `REVISION_CONFLICT`.
- [ ] Audit log tetap append-only; tidak ada kode yang mengubah atau menghapus baris audit.
- [ ] Log dan audit tidak memuat token, secret, isi dokumen, atau prompt lengkap berkonteks RESTRICTED.
- [ ] Error mengikuti [error-format](../07-api/error-format.md) tanpa stack trace.

### Dependency dan kualitas

- [ ] Tidak ada dependency baru tanpa kebutuhan konkret; bila ada, versi dikunci dan nama paket diperiksa terhadap typosquatting.
- [ ] Lockfile diperbarui bersama perubahan dependency.
- [ ] `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm api:lint`, `pnpm api:typecheck`, `pnpm api:test` lulus untuk area yang diubah.
- [ ] Integrasi produksi tetap nonaktif kecuali sudah divalidasi.

## Pre-release

- [ ] Seluruh item pre-merge terpenuhi untuk perubahan dalam rilis.
- [ ] `pnpm validate` dan `pnpm build` lulus; hasil dilaporkan apa adanya.
- [ ] `pnpm e2e` dijalankan terhadap web dan API yang berjalan.
- [ ] Tidak ada bug P0 terbuka; bug P1 terbuka disetujui untuk ditunda secara tertulis (lihat [bug-severity](../10-testing/bug-severity.md)).
- [ ] Skenario wajib diuji: akses tanpa izin, jailbreak, prompt injection, sitasi keliru, duplikasi ingestion, konflik pembaruan (sumber: Proposal v2.4, slide 20).
- [ ] `APP_ENV` sesuai lingkungan; API tidak dapat start dengan `APP_ENV=production` dan `DEV_AUTH_ENABLED=true`.
- [ ] `DEV_AUTH_SECRET` dan password database lingkungan target tidak sama dengan nilai pengembangan lokal.
- [ ] `HERMES_MAX_CLASSIFICATION` dan `AI_PROVIDER` sesuai keputusan yang berlaku (OQ-11).
- [ ] `CORS_ORIGINS` hanya berisi origin yang diperlukan.
- [ ] Label `SIMULATED_DATA` tampil di UI dan `meta.dataLabel` selama data masih simulasi.
- [ ] Migrasi diuji: upgrade, seed, dan downgrade (lihat [migration-guide](../11-operations/migration-guide.md)).
- [ ] [threat-model](threat-model.md) dan [risk-register](../12-governance/risk-register.md) ditinjau untuk perubahan dalam rilis.
- [ ] Untuk integrasi baru: [integration-readiness-checklist](../08-integrations/integration-readiness-checklist.md) lengkap dan disetujui.

## Open Questions

- **OPEN QUESTION** OQ-20 Lingkungan UAT dan pihak yang menandatangani pre-release.
- **OPEN QUESTION** Apakah instansi mewajibkan uji keamanan pihak ketiga sebelum rilis.

## Related Documents

- [security-overview](security-overview.md)
- [test-strategy](../10-testing/test-strategy.md)
- [deployment-runbook](../11-operations/deployment-runbook.md)
