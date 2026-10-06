# Authentication

**Status:** PROPOSED
**Last Updated:** 2026-10-02

## Purpose

Menjelaskan cara pengguna dibuktikan identitasnya pada SUNOVATE: mekanisme development token yang sudah diimplementasikan untuk scaffold, penanganan sesi di aplikasi web, dan arah login produksi yang masih menunggu keputusan.

## Status

- Development authentication: diimplementasikan pada scaffold, hanya untuk pengguna `SIMULATED_DATA` (ADR-005, PROPOSED sebagai keputusan desain).
- Production authentication: belum ada; menunggu OQ-07 (hosting dijawab knowledge owner sebagai komputer tersendiri sebagai server; mekanisme login belum dijawab, OQ-23).

## Confirmed Information

- **CONFIRMED** Token pengembangan diterbitkan oleh `POST /api/v1/auth/dev/login` untuk pengguna simulasi yang sudah di-seed (sumber: ADR-005; fact sheet bagian 9).
- **CONFIRMED** Token ditandatangani HMAC-SHA256 dan memuat user id serta waktu kedaluwarsa (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED** Masa berlaku token diatur `DEV_AUTH_TOKEN_TTL_MINUTES`, default 480 menit (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED** Secret penandatangan diambil dari `DEV_AUTH_SECRET`. Jika kosong pada development, proses membuat secret acak sementara per proses sehingga seluruh token tidak berlaku lagi setelah API di-restart (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED** Dev auth dinonaktifkan di luar development; API menolak start jika `APP_ENV=production` dan `DEV_AUTH_ENABLED=true` (sumber: ADR-005; implementasi scaffold sesi 2026-10-01).
- **CONFIRMED** Saat dev auth dinonaktifkan, endpoint login mengembalikan `DEV_AUTH_DISABLED` (404) (sumber: fact sheet bagian 9).
- **CONFIRMED** Aplikasi web menyimpan token di cookie httpOnly dengan SameSite=Lax dan memanggil API dari server; browser tidak pernah membaca token (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED** Login dicatat di `audit_logs` dengan action `LOGIN` (sumber: fact sheet bagian 9).

## Development authentication

### Pengguna simulasi

Login development hanya menerima akun simulasi berikut (seluruhnya fiktif, domain `@sunovate.local`):

| Email | Role | Team | Clearance |
|---|---|---|---|
| sim.admin | system_admin | — (all teams via scope) | INTERNAL |
| sim.coordinator | knowledge_coordinator | — (all teams) | RESTRICTED |
| sim.lead.psun | team_lead | PSUN | RESTRICTED |
| sim.owner.ppsun | knowledge_owner | PPSUN | INTERNAL |
| sim.reviewer.akpsun | reviewer | AKPSUN | INTERNAL |
| sim.staff.pppsun | staff | PPPSUN | INTERNAL |
| sim.auditor | auditor | — (all teams) | RESTRICTED |
| sim.readonly.dhtv | read_only | DHTV | INTERNAL |

### Verifikasi token di API

Setiap request ke endpoint terproteksi wajib membawa header `Authorization: Bearer <token>`. API:

1. Memverifikasi tanda tangan HMAC-SHA256 dengan secret aktif.
2. Menolak token kedaluwarsa atau tidak valid dengan `UNAUTHENTICATED` (401).
3. Memuat pengguna berdasarkan user id dan menyusun principal (role, permission, tim, clearance).
4. Meneruskan principal ke pemeriksaan otorisasi (lihat [authorization-rbac](authorization-rbac.md)).

Alur lengkap beserta jalur gagal ada di [authentication-flow](../07-api/authentication-flow.md).

### Penanganan sesi di web

| Aspek | Perilaku |
|---|---|
| Penyimpanan token | Cookie httpOnly, SameSite=Lax |
| Akses token oleh JavaScript browser | Tidak ada |
| Pemanggilan API | Server component dan route handler Next.js (termasuk proxy `/api/hermes`) menambahkan header Bearer |
| Token kedaluwarsa | API mengembalikan 401 `UNAUTHENTICATED`; pengguna diarahkan kembali ke `/login` (diimplementasikan di `apps/web/src/lib/api.ts`; diuji e2e untuk pengunjung tanpa sesi) |
| Logout | Menghapus cookie sesi; token tidak lagi dikirim |
| Restart API tanpa `DEV_AUTH_SECRET` | Semua token lama gagal diverifikasi; pengguna login ulang |

- **PROPOSED** Atribut `Secure` pada cookie diaktifkan pada setiap lingkungan berbasis HTTPS.
- **CONFIRMED** Logout tidak mencabut token di sisi server; token yang telah disalin tetap valid sampai kedaluwarsa. Karena itu TTL dijaga terbatas dan dev auth tidak boleh dipakai di luar development (sumber: implementasi scaffold sesi 2026-10-01).

## Proposed Design: production

- **PROPOSED** Login produksi melalui identity provider organisasi (SSO) di balik interface `IdentityProvider`; provider produksi saat ini berupa placeholder yang dinonaktifkan (sumber: fact sheet bagian 9; Proposal v2.4, slide 11 P2).
- **PROPOSED** Role dan team membership tetap dikelola di SUNOVATE kecuali ada keputusan lain; atribut dari identity provider hanya dipakai setelah pemetaan disetujui.
- **PROPOSED** Pencabutan sesi sisi server (revocation list atau sesi bertabel) dipertimbangkan bersama keputusan identity provider.
- **OUT OF SCOPE** Integrasi SSO organisasi pada MVP; termasuk P2 dan bukan janji (sumber: Proposal v2.4, slide 11).

Lihat [identity-provider-proposal](../08-integrations/identity-provider-proposal.md).

## Open Questions

- **OPEN QUESTION** OQ-07 Mekanisme login dan hosting yang disetujui.
- **OPEN QUESTION** OQ-20 Lingkungan UAT dan pengguna uji yang ditunjuk; apakah UAT tetap memakai dev auth atau identity provider.

## Risks

- Dev auth aktif di lingkungan non-development. Mitigasi: guard start-up pada `APP_ENV=production`.
- Secret pengembangan disalahgunakan sebagai secret produksi. Mitigasi: lihat [secrets-management](secrets-management.md).

## Acceptance Criteria

- API tidak start dengan `APP_ENV=production` dan `DEV_AUTH_ENABLED=true`.
- Request tanpa token atau dengan token rusak/kedaluwarsa menghasilkan 401 `UNAUTHENTICATED`.
- Token tidak muncul di JavaScript browser, URL, maupun log.

## Related Documents

- [authentication-flow](../07-api/authentication-flow.md)
- [secrets-management](secrets-management.md)
- [environment-configuration](../11-operations/environment-configuration.md)
