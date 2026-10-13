# Pengujian Frontend

**Status:** DRAFT

**Last Updated:** 2026-10-06

## Purpose

Menjelaskan cara menguji aplikasi web `apps/web` (Next.js App Router), mencakup unit test komponen dan end-to-end.

## Confirmed Information

- **CONFIRMED**: Frontend memakai Next.js 16 App Router, React 19, TypeScript strict, Tailwind CSS 4, React Hook Form + Zod, TanStack Query, dan Recharts (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Unit test memakai Vitest dan Testing Library React, berlokasi di `apps/web/src/**/*.test.tsx` (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: End-to-end memakai Playwright, berlokasi di `apps/web/e2e/` (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Route yang ada: `/login`, `/dashboard`, `/knowledge`, `/knowledge/[id]`, `/search`, `/work-monitoring`, `/hermes`, `/admin`, `/unauthorized`, ditambah state not-found, error, dan loading (sumber: implementasi scaffold sesi 2026-10-01).
- **CONFIRMED**: Hasil eksekusi tidak dicatat di sini; lihat laporan validasi terbaru di CHANGELOG.md.

## Perintah

| Tujuan | Perintah | Catatan |
|---|---|---|
| Lint | `pnpm lint` | ESLint frontend lalu Ruff backend |
| Typecheck | `pnpm typecheck` | TypeScript frontend lalu mypy backend |
| Unit test | `pnpm test` | Vitest frontend lalu pytest backend |
| Build | `pnpm build` | Build produksi Next.js |
| End-to-end | `pnpm e2e` | Membutuhkan web dan API yang sedang berjalan |
| Semua gate | `pnpm validate` | Lint, typecheck, test, build |

## Cakupan Unit Test (PROPOSED)

| Area | Yang diuji |
|---|---|
| Form login | Validasi Zod, pesan error yang dapat dibaca, tombol submit nonaktif saat proses |
| Form Hermes | Validasi pertanyaan kosong, tampilan keputusan (`ANSWERED`, `INSUFFICIENT_EVIDENCE`, `REFUSED_*`, `REQUIRES_HUMAN_APPROVAL`, `BLOCKED_BY_OUTPUT_GUARD`), tampilan sitasi |
| Register validasi SAVI | Pencarian lintas konten, filter status, reset, kondisi tanpa hasil, dan pemanggilan fungsi cetak tanpa aksi persetujuan |
| Lembar keputusan mentor OQ-36 | Isian hanya pada state browser, indikator kelengkapan, reset, cetak, dan tidak memiliki aksi simpan/setujui/aktifkan |
| Label data | Label `SIMULATED_DATA` tampil pada halaman yang menampilkan data |
| Status dan tenggat | Label `deadline state` ditampilkan sesuai nilai dari backend, tanpa perhitungan ulang di frontend |
| State kosong dan error | Komponen menampilkan pesan yang jelas saat data kosong atau API gagal |
| Aksesibilitas dasar | Elemen form memiliki label, fokus terlihat (outline gold 3px), peran ARIA yang wajar |

- **PROPOSED**: Uji komponen lewat perilaku yang terlihat pengguna (role, label, teks), bukan detail implementasi.
- **PROPOSED**: Panggilan API di unit test di-mock; unit test tidak boleh membutuhkan API yang berjalan.
- **PROPOSED**: Server component yang memanggil API diuji melalui e2e, bukan unit test.

## Cakupan End-to-End (PROPOSED)

1. Login pengembangan dengan pengguna simulasi lalu diarahkan ke `/dashboard`.
2. Akses halaman tanpa cookie sesi diarahkan ke `/login`.
3. Pengguna tanpa permission yang sesuai melihat `/unauthorized` atau data tidak tampil.
4. Pencarian `/search?q=` menampilkan hasil yang hanya berasal dari record yang boleh dibaca.
5. Membuka `/knowledge/[id]` untuk record yang tidak boleh dibaca menampilkan not-found.
6. Pertanyaan Hermes menampilkan jawaban bersitasi atau penolakan yang sesuai.

- **CONFIRMED**: Penyembunyian menu di frontend hanya kosmetik; otorisasi ditegakkan di API (sumber: ADR-006). Karena itu e2e tidak menggantikan pengujian otorisasi backend.
- **CONFIRMED**: Token login pengembangan disimpan di cookie httpOnly dan Hermes diproksikan lewat route handler `/api/hermes` (sumber: implementasi scaffold sesi 2026-10-01). E2E sebaiknya memverifikasi token tidak terbaca dari JavaScript halaman (PROPOSED).

## Tambahan dari Jawaban Knowledge Owner (PLANNED)

- **PLANNED**: Unit test atau e2e memastikan `/dashboard` tidak memuat angka yield atau kepemilikan SBN dan menampilkan "sumber data belum tersedia" untuk kedua indikator (FR-54, AC-22). Teks itu belum ada di UI, sehingga uji ini akan gagal sampai diimplementasikan.
- **PROPOSED**: Frontend saat ini tidak memiliki formulir pembuatan atau pengubahan knowledge (pencarian `knowledge:create` pada `apps/web/src` tidak menemukan hasil), sehingga pembatasan hak ubah/unggah (FR-50) tidak dapat diuji dari UI; pengujiannya di API (SEC-40). Bila formulir dibuat, menu tetap hanya kosmetik dan e2e tidak menggantikan uji API (ADR-006).
- **PLANNED**: Tidak ada tombol atau rute kanal Telegram/WhatsApp (FR-55).
- **OPEN QUESTION**: Pengujian aksesibilitas manual pada server pilot belum terjadwal (OQ-20).

## Aturan Pengujian Frontend

- **PROPOSED**: Hanya memakai data `SIMULATED_DATA` dan pengguna simulasi `@sunovate.local`.
- **PROPOSED**: Tidak ada snapshot test berukuran besar; gunakan assertion eksplisit.
- **PROPOSED**: Pengujian visual mengikuti token desain terkunci (navy, gold, paper, line, muted, success, risk); lihat [design-system.md](../09-ui-ux/design-system.md).
- **OPEN QUESTION**: Audit aksesibilitas formal belum dilakukan; validasi penuh memerlukan pengujian manual dengan teknologi asistif (lihat [accessibility.md](../09-ui-ux/accessibility.md)).

## Related Documents

- [test-strategy.md](test-strategy.md)
- [test-pyramid.md](test-pyramid.md)
- [information-architecture.md](../09-ui-ux/information-architecture.md)
- [local-development.md](../11-operations/local-development.md)
