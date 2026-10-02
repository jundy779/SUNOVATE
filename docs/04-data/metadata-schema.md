# Metadata Schema

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-01

## Purpose
Mendefinisikan metadata wajib dan opsional untuk knowledge entry dan dokumen.

## Knowledge entry
| Field (API) | Wajib | Nilai | Catatan |
|---|---|---|---|
| `title` | Ya | 5 sampai 255 karakter | |
| `knowledgeType` | Ya | REGULATION, POLICY, STUDY, SOP, PLAYBOOK, REPORT, MEETING_MATERIAL, CLOSE_OUT_NOTE, LESSON_LEARNED, TACIT_KNOWLEDGE, DECISION_RECORD, ARCHIVE, REFERENCE, OTHER | PROPOSED |
| `summary` | Ya | 10 sampai 2000 karakter | |
| `classificationCode` | Ya | PUBLIC, INTERNAL, RESTRICTED, CONFIDENTIAL | tidak boleh melebihi clearance pembuat |
| `ownerTeamId` | Ya | UUID tim dalam scope pembuat | |
| `sharingScope` | Tidak | TEAM (default), DIRECTORATE | DIRECTORATE berlaku hanya saat PUBLISHED |
| `tags` | Tidak | maks. 20, masing-masing 1 sampai 48 karakter | |
| `lifecycleStatus` | Sistem | diatur oleh alur submit dan approval | tidak dapat diubah langsung |
| `versionLabel`, `effectiveDate`, `expiresAt`, `sourceNote`, `supersededById` | Opsional | | `effectiveDate` wajib untuk REGULATION (PROPOSED, belum ditegakkan) |

## Dokumen dan versi
| Field | Wajib | Catatan |
|---|---|---|
| `provider` | Ya | `LOCAL_REFERENCE` pada pengembangan |
| `providerLocation` | Ya | hanya `local://...` pada pengembangan |
| `versionLabel` | Ya | 1 sampai 64 karakter |
| `checksumSha256` | Ya | 64 hex huruf kecil; duplikat per dokumen ditolak |
| `sizeBytes` | Tidak | >= 0 |
| `extractionStatus` | Sistem | versi baru `PENDING` karena pipeline ekstraksi belum ada |

## Metadata regulasi (PROPOSED)
Nomor, jenis peraturan, tanggal penetapan, tanggal berlaku, status berlaku, relasi (`regulation_relations`). Status hukum ditentukan pemilik konten, bukan sistem (OQ-09, OQ-17).

## Open Questions
OQ-04 jenis dokumen yang boleh masuk; OQ-05 klasifikasi per jenis; OQ-09 pemilik metadata.

## Related Documents
- [document-classification.md](document-classification.md)
- [data-quality.md](data-quality.md)
- [document-lifecycle.md](../02-business/document-lifecycle.md)
