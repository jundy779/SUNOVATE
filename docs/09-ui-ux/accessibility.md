# Accessibility

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose

Menetapkan target dan daftar periksa aksesibilitas antarmuka SUNOVATE.

## Status

- **PROPOSED:** Target kesesuaian WCAG 2.2 level AA.
- **CONFIRMED:** Validasi kesesuaian WCAG secara penuh memerlukan pengujian manual dengan teknologi bantu (misalnya pembaca layar dan navigasi keyboard saja) serta tinjauan oleh ahli aksesibilitas. Test otomatis hanya menemukan sebagian masalah.
- **CONFIRMED:** Dokumen HTML memakai `lang="id"` (sumber: `apps/web/src/app/layout.tsx`).

## Daftar periksa

### Struktur

- [ ] Setiap halaman memiliki satu `h1` (melalui `PageHeader`) dan urutan heading tidak melompat.
- [ ] Landmark tersedia: `nav` dengan label, `header`, dan `main` dengan `id="main-content"`.
- [ ] Skip link ke `#main-content` menjadi elemen fokus pertama (lihat [Navigation](navigation.md)).
- [ ] Judul dokumen (`title`) unik per halaman dengan pola `Judul | SUNOVATE`.

### Keyboard dan fokus

- [ ] Semua fungsi dapat dijalankan dengan keyboard saja.
- [ ] Fokus terlihat pada semua elemen interaktif (`:focus-visible` outline gold 3px).
- [ ] Elemen yang menerima fokus tidak tertutup elemen lain (WCAG 2.2, Focus Not Obscured).
- [ ] Tidak ada keyboard trap.

### Warna dan teks

- [ ] Status tidak disampaikan dengan warna saja; `StatusTag` selalu berisi teks.
- [ ] Kontras teks normal minimal 4.5:1 dan teks besar minimal 3:1.
- [ ] Kontras batas komponen UI yang dibutuhkan untuk mengenali kontrol (misalnya tepi input) minimal 3:1.
- [ ] Konten tetap terbaca pada zoom 200% dan reflow pada lebar 320px CSS.

### Formulir

- [ ] Setiap input memiliki `label` yang terhubung (`for`/`id` atau pembungkus `label`); placeholder bukan pengganti label.
- [ ] Pesan error validasi (React Hook Form + Zod) dihubungkan ke input melalui `aria-describedby` dan input ditandai `aria-invalid="true"`.
- [ ] Ringkasan error formulir diumumkan dan fokus dipindahkan ke field pertama yang salah saat submit gagal.
- [ ] Field wajib ditandai dengan teks, bukan simbol saja.

### Tabel

- [ ] Tabel data memakai `th` dengan `scope` yang sesuai dan `caption` atau label yang menjelaskan isi.
- [ ] Area tabel yang dapat digulir horizontal dapat difokuskan dan digulir dengan keyboard.

### Grafik

- [ ] Grafik status dashboard (Recharts) memiliki alternatif berupa tabel atau teks angka yang sama.
- [ ] Grafik tidak menjadi satu-satunya sumber informasi.

### Hermes

- [ ] Area jawaban Hermes memakai live region `aria-live="polite"` sehingga jawaban, penolakan, dan status `INSUFFICIENT_EVIDENCE` diumumkan pembaca layar.
- [ ] Status pemrosesan ("Sedang memproses") diumumkan satu kali, tidak berulang.
- [ ] Sitasi berupa tautan dengan teks bermakna (judul sumber), bukan hanya nomor `[n]`.
- [ ] Error jaringan atau penolakan ditampilkan sebagai teks, dengan `role="alert"` bila memerlukan tindakan.

### Status dan keadaan kosong

- [ ] `EmptyState` memakai `role="status"` (sumber: `page-elements.tsx`).
- [ ] Halaman loading dan error mengumumkan keadaannya.

## Catatan kontras token

Rasio di bawah dihitung dengan rumus relative luminance WCAG 2.x dari nilai heksadesimal token, tanpa memperhitungkan anti-aliasing atau transparansi. Hasil ini wajib diverifikasi ulang dengan contrast checker sebelum dinyatakan lulus.

| Teks / elemen | Latar | Rasio | Catatan |
|---|---|---|---|
| `--navy-deep` | `--paper` | 15.36:1 | Teks utama |
| `--navy` | `--white` | 13.38:1 | Judul, tombol sekunder |
| `--white` | `--navy` | 13.38:1 | Teks sidebar, tombol utama |
| `--line` | `--navy` | 9.79:1 | Teks kecil di sidebar |
| `--muted` | `--white` | 4.83:1 | Teks sekunder; lulus 4.5:1 dengan margin tipis |
| `--muted` | `--paper` | 4.55:1 | Lulus 4.5:1 dengan margin sangat tipis |
| `--risk` | `--white` | 6.68:1 | Status risiko |
| `--success` | `--white` | 4.25:1 | Di bawah 4.5:1 untuk teks normal |
| `--gold` | `--white` | 2.42:1 | Di bawah 3:1; tidak untuk teks, dan perlu dikaji sebagai focus indicator |
| `--gold` | `--navy` | 5.53:1 | Focus indicator di sidebar |
| `--navy-deep` | `--gold` | 6.75:1 | Teks terpilih (`::selection`) |
| `--line` | `--white` | 1.37:1 | Garis dekoratif saja; tidak cukup sebagai satu-satunya tepi input |

Temuan yang perlu keputusan (token terkunci, sehingga perubahan memerlukan persetujuan):

- **OPEN QUESTION:** Teks `--success` di atas putih di bawah 4.5:1. Opsi: tampilkan status sukses dengan teks `--navy-deep` dan penanda `--success` non-teks, atau tambah varian token yang lebih gelap.
- **OPEN QUESTION:** Focus outline `--gold` di atas putih di bawah 3:1. Opsi: kombinasi outline gold dengan cincin `--navy` di sekelilingnya.
- **OPEN QUESTION:** Tepi input memakai `--line` (1.37:1 terhadap putih). Opsi: tepi input memakai `--muted`.

## Acceptance Criteria

- **PROPOSED:** Pemeriksaan otomatis aksesibilitas pada test end-to-end tidak menemukan pelanggaran serius pada route utama.
- **PROPOSED:** Pengujian manual keyboard dan pembaca layar dilakukan pada login, knowledge, pencarian, dan Hermes sebelum UAT.
- **PROPOSED:** Temuan kontras di atas diputuskan dan dicatat pada [Decision Log](../12-governance/decision-log.md).

## Related Documents

- [Design System](design-system.md)
- [Navigation](navigation.md)
- [Responsive Design](responsive-design.md)
- [Frontend Testing](../10-testing/frontend-testing.md)
- [UAT Plan](../10-testing/uat-plan.md)
