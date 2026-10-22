# Penampil Dokumen RAHASIA

**Status:** PROPOSED (ADR-020), IMPLEMENTED untuk `SIMULATED_DATA` saja
**Last Updated:** 2026-10-21

## Purpose

Menjelaskan kontrol keamanan untuk file SUN rahasia tertentu yang hanya boleh dibaca sebagai pratinjau, batasnya, dan cara mengujinya. Keputusan arsitektur ada di [ADR-020](../03-architecture/architecture-decisions.md).

## Cakupan

- Berlaku hanya untuk dokumen yang ditetapkan RAHASIA, bukan seluruh repository.
- Terpisah dari aturan cover/metadata untuk dokumen sangat sensitif seperti Juknis Penetapan Hasil Lelang (`METADATA_ONLY` belum diimplementasikan).
- Dokumen asli dilarang sampai OQ-40, OQ-41, dan OQ-42 terjawab serta penyedia kunci TPM terpasang.

## Kontrol yang berjalan

| Kontrol | Implementasi | Bukti uji |
|---|---|---|
| Tanpa unduhan dan tanpa teks | API hanya punya daftar, metadata, persetujuan pernyataan, dan satu halaman PNG | `test_no_route_exposes_file_text_or_download` |
| Render di server dan tanda air | Halaman dirender Pillow dengan nama, email, waktu WIB, dan rujukan sesi berulang diagonal | `test_granted_reader_receives_watermarked_png_without_text` |
| Pembaca eksplisit per dokumen | Email pembaca terdaftar per dokumen dan clearance harus mencakup klasifikasi | `test_only_granted_readers_see_the_document` |
| Penolakan tanpa membuka keberadaan | Dokumen tidak ada dan tidak diberikan sama-sama 404, percobaan diaudit `DENIED` | `test_ungranted_reader_gets_not_found_and_attempt_is_audited` |
| Pernyataan kerahasiaan | Halaman 428 sampai pernyataan disetujui; persetujuan diaudit, berlaku 30 menit, per pembaca per dokumen | `test_pages_stay_locked_until_notice_is_accepted`, `test_notice_acceptance_expires_and_is_per_reader` |
| Anti pengambilan massal | Maksimal 40 halaman per menit per pengguna, 429 + `Retry-After` | `test_bulk_page_requests_are_rate_limited` |
| Enkripsi envelope | AES-256-GCM per halaman, terikat id dokumen dan nomor halaman; kunci data dibungkus `KeyProvider`; crypto-shredding | empat test enkripsi di `test_secure_viewer.py` |
| Pengelolaan akses | Ketua Tim pemilik dokumen (`secure_document:manage_team`) dan Kasubdit PMP untuk seluruh tim (`secure_document:manage_all`); pembaca boleh lintas tim, wajib aktif dengan clearance cukup; daftar pembaca permanen di tabel `secure_document_readers`; pencabutan menutup penampil terbuka; semua tindakan diaudit; halaman `/dokumen-rahasia/kelola` tanpa isi dokumen | delapan test pengelolaan akses di `test_secure_viewer.py`, e2e pengelolaan akses |
| Terisolasi dari AI | Vault terpisah dari indeks pencarian dan SAVI AI | `test_rahasia_content_never_reaches_search_or_savi` |
| Header gambar | `no-store`, `inline`, `nosniff`, CORP same-origin, dan CSP `default-src 'none'; frame-ancestors 'none'; sandbox` yang dideklarasikan setelah aturan situs di `next.config.ts` | QA HTTP pada proxy |
| Penghalang browser | Menu konteks, seret gambar, pintasan simpan/cetak/salin/DevTools, cetak halaman dicegah; tampilan dikaburkan saat jendela tidak aktif | `secure-documents.test.ts`, e2e penampil |

## Batas yang diketahui

- Foto layar dengan kamera dan perangkat yang disusupi pada level sistem operasi tidak dapat dicegah aplikasi web; tanda air dan audit menjadi kontrol penelusuran.
- Pemblokiran DevTools, extension, dan tangkapan layar memerlukan perangkat terkelola atau penampil desktop (OQ-41, P3).
- Kunci saat ini sementara per proses; isi tersegel di vault berada di memori dan hilang saat API dimulai ulang. Daftar pembaca sudah permanen di PostgreSQL.
- Batas laju dan persetujuan pernyataan berada di memori satu proses.
- URL detail dokumen yang tidak diberikan menampilkan halaman tidak ditemukan dengan status HTTP 200 (soft 404 dengan `noindex`), karena area kerja melakukan streaming di balik `loading.tsx`. Isi dan judul dokumen tidak ikut terkirim. Status 404 sungguhan memerlukan pemeriksaan sebelum streaming (mis. di `proxy`).

## Related Documents

- [ADR-020](../03-architecture/architecture-decisions.md)
- [data-classification.md](data-classification.md)
- [authorization-rbac.md](authorization-rbac.md)
- [private-data-boundary.md](private-data-boundary.md)
