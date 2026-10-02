# Secrets Management

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Mengatur bagaimana secret (password database, secret penandatangan token, kredensial provider di masa depan) disimpan, dibagikan, dirotasi, dan dijauhkan dari repository, log, dan prompt.

## Confirmed Information

- **CONFIRMED** `.env` diabaikan git; `.env.example` hanya berisi placeholder (sumber: fact sheet bagian 9; implementasi scaffold sesi 2026-10-01).
- **CONFIRMED** Variabel lingkungan yang memuat secret pada scaffold: `DEV_AUTH_SECRET`, `POSTGRES_PASSWORD`, dan `DATABASE_URL` (yang memuat kredensial database) (sumber: fact sheet bagian 9).
- **CONFIRMED** Jika `DEV_AUTH_SECRET` kosong pada development, API membuat secret acak sementara per proses; token tidak berlaku setelah restart (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED** Hermes tidak memiliki kredensial database (sumber: ADR-004).
- **CONFIRMED** Integrasi produksi dinonaktifkan; belum ada kredensial provider eksternal yang dibutuhkan (sumber: fact sheet bagian 9).

## Aturan

| Aturan | Status |
|---|---|
| Secret tidak pernah di-commit; `.env` tetap di `.gitignore` | CONFIRMED |
| `.env.example` hanya berisi placeholder atau nilai pengembangan yang jelas tidak rahasia | CONFIRMED |
| Secret lokal pengembangan bukan secret asli dan tidak dipakai ulang di lingkungan lain | PROPOSED |
| Secret tidak dicatat di log aplikasi, audit log, pesan error, atau output uji | PROPOSED (sebagian ditegakkan `OutputGuard` untuk jawaban Hermes) |
| Secret tidak pernah dimasukkan ke prompt atau konteks Hermes | CONFIRMED (Hermes hanya menerima chunk terotorisasi) |
| Secret tidak dikirim melalui chat, email, atau dokumen knowledge | PROPOSED |
| Production menolak start dengan dev auth aktif | CONFIRMED |

## Pengembangan lokal

1. Salin `.env.example` menjadi `.env`.
2. Isi `DEV_AUTH_SECRET` dengan nilai acak panjang bila token harus bertahan saat API di-restart; biarkan kosong untuk secret sementara per proses.
3. `POSTGRES_PASSWORD` lokal hanya untuk container atau server PostgreSQL lokal.
4. Jangan menyalin `.env` ke folder lain di dalam repository.

Lihat [environment-configuration](../11-operations/environment-configuration.md) untuk daftar lengkap variabel.

## Proposed Design: production

- **OPEN QUESTION** Secret store produksi (mis. layanan secret management milik instansi atau platform hosting) belum ditetapkan; bergantung pada OQ-07.
- **PROPOSED** Secret produksi disuntikkan sebagai environment variable atau file terpasang saat runtime, tidak dibangun ke dalam image.
- **PROPOSED** Akses ke secret store dibatasi pada administrator sistem yang ditunjuk dan tercatat.
- **PROPOSED** Validasi start-up: API gagal start bila secret wajib produksi kosong.

## Rotasi

| Secret | Pemicu rotasi (PROPOSED) | Dampak |
|---|---|---|
| `DEV_AUTH_SECRET` | Dugaan kebocoran, pergantian pengembang | Semua token pengembangan tidak berlaku; pengguna login ulang |
| Password database | Dugaan kebocoran, berkala sesuai kebijakan instansi | Perlu restart API dengan `DATABASE_URL` baru |
| Kredensial provider masa depan | Sesuai kebijakan provider dan instansi | Ditentukan saat integrasi divalidasi |

- **PROPOSED** Bila secret terlanjur ter-commit: anggap bocor, rotasi segera, lalu tangani sebagai insiden (lihat [incident-response](incident-response.md)). Menghapus commit saja tidak cukup.

## Open Questions

- **OPEN QUESTION** OQ-07 Hosting dan secret store yang disetujui.
- **OPEN QUESTION** Periode rotasi berkala yang diwajibkan kebijakan instansi.

## Acceptance Criteria

- Pemindaian repository tidak menemukan secret.
- `.env.example` tidak memuat nilai rahasia.
- Log uji tidak memuat token, password, atau connection string.

## Related Documents

- [authentication](authentication.md)
- [security-checklist](security-checklist.md)
- [local-development](../11-operations/local-development.md)
