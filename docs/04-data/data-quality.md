# Data Quality

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Mendefinisikan dimensi kualitas data dan cara isu kualitas dicatat.

## Dimensi
| Dimensi | Contoh pemeriksaan | Status |
|---|---|---|
| Kelengkapan | knowledge memiliki pemilik, klasifikasi, ringkasan | Ditegakkan validasi API |
| Validitas | enum status, checksum 64 hex, progress 0 sampai 100 | Validasi API + CHECK DB |
| Keunikan | checksum versi per dokumen unik | API 409 + constraint |
| Ketepatan waktu | tanggal berlaku, review berkala | PROPOSED (OQ-13) |
| Konsistensi | relasi regulasi tidak menunjuk diri sendiri | CHECK DB |
| Ketelusuran | sumber (`source_note`), versi, audit | Kolom ada |

## Pencatatan isu
- Tabel `data_quality_issues` (ber-governance): `entity_type`, `entity_id`, `issue_type`, `severity` (LOW, MEDIUM, HIGH), `status` (OPEN, IN_PROGRESS, RESOLVED, DISMISSED).
- Endpoint baca: `GET /api/v1/data-quality-issues` (permission `data_quality:read`). Pengelolaan (`data_quality:manage`) belum memiliki endpoint.
- Dataset simulasi berisi dua isu contoh: `MISSING_EFFECTIVE_DATE` dan `SOURCE_REFERENCE_PLACEHOLDER`.

## Usulan berikut (PROPOSED)
- Pemeriksaan otomatis terjadwal untuk metadata wajib dan tautan sumber.
- Kualitas metadata menjadi metrik retrieval Hermes (R-11).

## Related Documents
- [metadata-schema.md](metadata-schema.md)
- [knowledge-governance.md](../12-governance/knowledge-governance.md)
