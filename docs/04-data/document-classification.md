# Document Classification

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose
Menjelaskan bagaimana klasifikasi data disimpan dan dipakai dalam model data. Aturan penanganan per level ada di [data-classification.md](../06-security/data-classification.md).

## Tingkat (PROPOSED)
| Code | Rank | Label | Hermes pada pengembangan |
|---|---|---|---|
| PUBLIC | 0 | Publik | Ya |
| INTERNAL | 1 | Internal | Ya |
| RESTRICTED | 2 | Terbatas | Ya, bila clearance pengguna cukup |
| CONFIDENTIAL | 3 | Sangat terbatas | Tidak (`HERMES_MAX_CLASSIFICATION=RESTRICTED`) |

## Penyimpanan
- `data_classifications` adalah tabel referensi; kolom `classification_code` di tabel lain adalah FK ke `code`.
- `users.clearance_code` menentukan batas baca pengguna.
- Akses baca: rank(clearance) >= rank(klasifikasi record). Kode yang tidak dikenal ditolak.
- Klasifikasi pesan Hermes = klasifikasi tertinggi dari sumber yang dikutip (minimal INTERNAL).

## Dataset simulasi
Dataset sengaja memuat satu entri `CONFIDENTIAL` (K6) dan tidak ada pengguna dengan clearance tersebut, sehingga test dapat membuktikan entri itu tidak pernah bocor.

## Open Questions
- **OPEN QUESTION** OQ-05 pemetaan ke skema klasifikasi resmi Kemenkeu dan klasifikasi per jenis dokumen.
- **OPEN QUESTION** Siapa yang berwenang menetapkan atau menurunkan klasifikasi.

## Related Documents
- [data-classification.md](../06-security/data-classification.md)
- [authorization-rbac.md](../06-security/authorization-rbac.md)
