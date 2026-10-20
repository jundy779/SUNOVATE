# Design System

**Status:** CONFIRMED (token terkunci) | PROPOSED (aturan komponen)
**Last Updated:** 2026-10-21

## Purpose

Mendokumentasikan token desain SUNOVATE yang terkunci, aturan visual, dan komponen dasar yang tersedia di `apps/web`.

## Status

- **CONFIRMED:** Token warna, font, radius, dan focus terkunci; tidak boleh ada gradient, warna ungu, ikon Unicode, atau grid kartu generik berukuran besar (sumber: fact sheet bagian 9; AGENTS.md).
- **CONFIRMED:** Token diimplementasikan sebagai CSS custom properties di `apps/web/src/app/globals.css`.
- **CONFIRMED:** shadcn/ui belum dipasang karena belum ada kebutuhan konkret (sumber: fact sheet bagian 9).

## Token

### Warna

| Token | Nilai | Penggunaan |
|---|---|---|
| `--navy` | `#0D2E5E` | Sidebar, judul, tombol utama |
| `--navy-deep` | `#091F42` | Teks utama, hover tombol |
| `--gold` | `#C9A227` | Aksen merek, focus outline, label data |
| `--white` | `#FFFFFF` | Permukaan panel |
| `--paper` | `#F7F8FA` | Latar halaman |
| `--line` | `#D8DDE3` | Garis tabel dan batas panel |
| `--muted` | `#6B7280` | Teks sekunder |
| `--success` | `#2E8B57` | Status positif, selalu dengan teks |
| `--risk` | `#B22222` | Status risiko dan label klasifikasi, selalu dengan teks |

Catatan kontras untuk token ada di [Accessibility](accessibility.md).

### Tipografi

| Token | Nilai |
|---|---|
| `--font-heading` | `"Aptos Display", "Segoe UI", system-ui, sans-serif` |
| `--font-body` | `"Aptos", "Segoe UI", system-ui, sans-serif` |

- **CONFIRMED:** Ukuran dasar body 14px dengan line-height 1.5 (sumber: `globals.css`).
- **PROPOSED:** Aptos tidak dibundel; aplikasi bergantung pada font yang terpasang di perangkat, dengan Segoe UI sebagai fallback. Lisensi pembundelan font adalah OPEN QUESTION bila kelak dibutuhkan.

### Bentuk dan fokus

| Token | Nilai |
|---|---|
| `--radius` | `0.35rem` |
| Focus | `outline: 3px solid var(--gold); outline-offset: 2px` pada `:focus-visible` |

- **CONFIRMED:** `globals.css` juga mendefinisikan `--space` (`0.5rem`) dan `--shadow` (bayangan tipis navy-deep) sebagai variabel pendukung implementasi.

## Aturan visual

1. **CONFIRMED:** Tidak ada gradient.
2. **CONFIRMED:** Tidak ada warna ungu atau warna di luar token.
3. **CONFIRMED:** Tidak ada ikon berupa karakter Unicode atau emoji. Bila ikon dibutuhkan kelak, pemilihan pustaka ikon memerlukan kebutuhan konkret dan persetujuan dependency.
4. **CONFIRMED:** Tidak ada grid kartu generik berukuran besar.
5. **PROPOSED:** Tabel didahulukan untuk data operasional (knowledge, tugas, output, approval, audit). Tabel dibungkus `.table-wrap` agar dapat digulir horizontal.
6. **PROPOSED:** Status selalu ditampilkan sebagai teks yang bermakna; warna hanya penguat, tidak pernah satu-satunya penanda.
7. **PROPOSED:** Ringkasan angka memakai satu baris metrik bergaris (`.metric-grid`), bukan kartu terpisah dengan bayangan besar.
8. **PROPOSED:** Label klasifikasi (`.classification`) selalu menampilkan kode teks, misalnya `RESTRICTED`.
9. **PROPOSED:** Bahasa antarmuka Bahasa Indonesia; identifier teknis tetap dalam bahasa Inggris.

## Komponen yang tersedia

Lokasi: `apps/web/src/components/page-elements.tsx`.

| Komponen | Fungsi | Catatan |
|---|---|---|
| `PageHeader` | Eyebrow, judul `h1`, deskripsi, dan slot aksi | Dipakai di setiap halaman workspace |
| `StatusTag` | Teks status dengan tone `neutral`, `success`, atau `risk` | Alias `StatusBadge`; teks wajib diisi |
| `SimulatedLabel` | Label `SIMULATED_DATA` berbingkai gold | Alias `DataLabel` |
| `EmptyState` | Keadaan kosong dengan judul dan deskripsi, `role="status"` | Default "Belum ada data" |

- **CONFIRMED:** `AppShell` di `apps/web/src/components/app-shell.tsx` menyediakan sidebar, topbar, dan area `main`.
- **PROPOSED:** Komponen baru ditambahkan hanya bila dipakai minimal di dua halaman; selain itu cukup markup lokal dengan kelas yang ada.

### Pemetaan status ke tone (PROPOSED)

| Status | Tone |
|---|---|
| `OVERDUE`, `REJECTED`, `FAILED`, `QUARANTINED` | `risk` |
| `COMPLETED`, `PUBLISHED`, `APPROVED`, `SAFE` | `success` |
| Status lain | `neutral` |

Label teks status ditampilkan dalam Bahasa Indonesia; pemetaan istilah ada di [Glossary](../00-project/glossary.md).

## Lapisan editorial (landing, masuk, dashboard)

- **PROPOSED (2026-10-21):** Arah visual memadukan struktur institusional situs Bank Indonesia (bar pemerintah navy, header institusional, sidebar navy, baris akses cepat dengan garis pemisah) dengan disiplin editorial The Economist (hierarki dipimpin judul, garis rambut, sumber pada setiap grafik). Gaya diterapkan di `apps/web/src/app/editorial.css`.
- **PROPOSED:** Tab emas `32 x 5 px` di atas judul bagian dan grafik (`.ed-head`) menjadi penanda khas, pengganti tab merah The Economist. Hanya token terkunci yang dipakai; tidak ada font serif tambahan.
- **PROPOSED:** Satu momen gerak per halaman: grafik siklus pengetahuan di landing, garis emas tagline di halaman masuk, dan batang grafik status tugas di dashboard. Semuanya dimatikan bila `prefers-reduced-motion: reduce`.
- **PROPOSED:** Label tanpa huruf kapital penuh, tanpa panah karakter pada tautan, dan angka ringkasan disajikan sebagai satu baris ledger bergaris, bukan kartu terpisah.

## Keputusan terbuka

- **PROPOSED:** shadcn/ui hanya dipertimbangkan bila ada kebutuhan konkret, misalnya dialog atau combobox yang aksesibel, dan wajib memakai token yang sama.
- **OPEN QUESTION:** Apakah warna `--success` dan `--gold` perlu varian lebih gelap untuk teks kecil; perubahan token memerlukan keputusan karena token terkunci (lihat [Accessibility](accessibility.md)).

## Related Documents

- [Accessibility](accessibility.md)
- [Responsive Design](responsive-design.md)
- [Dashboard Requirements](dashboard-requirements.md)
- [Prototype Notes](prototype-notes.md)
