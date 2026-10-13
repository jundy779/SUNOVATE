# Validasi Pertanyaan SME untuk SAVI AI

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-13

## Purpose

Mengatur penerimaan pertanyaan nyata dari mentor atau SME sebelum dipakai sebagai jawaban aktif SAVI AI. Arahan bisnis dipertahankan tanpa menjadikan jawaban awal, rujukan hukum, atau langkah operasional sebagai fakta final sebelum divalidasi.

## Register Saat Ini

- **CONFIRMED (arahan mentor diteruskan project lead, 2026-10-13):** delapan pertanyaan operasional SUN diterima untuk bahan pengembangan dan pengujian.
- Register berada di `tests/fixtures/sme_question_intake.json` dengan label `MENTOR_PROVIDED_DRAFT`.
- Seluruh kasus `BLOCKED` untuk runtime dan tidak dibaca `HermesGateway`.
- Golden set aktif tetap di `tests/fixtures/rag_golden_set.json` dan hanya memakai `SIMULATED_DATA`.
- Test `tests/rag-evaluation/test_sme_question_intake.py` mencegah promosi tanpa sengaja ke golden set aktif.

## Status Validasi

| Status | Makna |
|---|---|
| `PENDING_SME_VALIDATION` | Substansi dan prosedur perlu disahkan SME/PIC proses. |
| `PENDING_LEGAL_VALIDATION` | Kesesuaian dasar hukum perlu diperiksa reviewer berwenang. |
| `NEEDS_REVISION` | Ditemukan rujukan atau klaim yang harus diperbaiki. |
| `VERIFIED` | Jawaban, sumber, akses, dan pemilik validasi disahkan; belum otomatis aktif. |
| `REJECTED` | Kasus tidak digunakan dan alasannya dipertahankan untuk audit. |

## Gerbang Promosi ke Golden Set

1. Pertanyaan dan jawaban disahkan SME atau PIC proses yang ditunjuk.
2. Setiap klaim hukum dipetakan ke regulasi, pasal, ayat, dan sumber resmi yang tepat.
3. Langkah operasional didukung SOP, petunjuk teknis, atau checklist yang disetujui.
4. Klasifikasi informasi, tim yang boleh mengakses, dan kondisi penolakan ditetapkan.
5. Dokumen sumber telah lolos gerbang ingestion, klasifikasi, dan publikasi.
6. Kasus memakai data simulasi atau lingkungan uji data asli yang telah disetujui.
7. Reviewer, tanggal validasi, dan versi sumber dicatat tanpa data pribadi di repository.
8. Test retrieval, sitasi, keputusan, dan kebocoran akses lulus.

## Temuan Awal

| ID | Topik | Status awal | Alasan utama |
|---|---|---|---|
| SME-001 | Selisih hasil lelang | `NEEDS_REVISION` | Pasal 12 PMK 111/2024 tidak mengatur penetapan hasil lelang; SOP rekonsiliasi belum tersedia. |
| SME-002 | Koreksi setelah lock | `PENDING_SME_VALIDATION` | Mekanisme lock dan koreksi merupakan proses sistem atau SOP internal. |
| SME-003 | Penawaran berdasarkan yield | `NEEDS_REVISION` | Kandidat dasar lebih sesuai pada Pasal 14 ayat (3), Pasal 17, dan Pasal 18 PMK 111/2024. |
| SME-004 | Selisih T&C | `PENDING_SME_VALIDATION` | Dasar unsur T&C tersedia, tetapi prosedur koreksi internal belum ada. |
| SME-005 | Pemeriksaan sebelum setelmen | `NEEDS_REVISION` | Rujukan Pasal 24 perlu diperiksa; checklist resmi belum tersedia. |
| SME-006 | Kegagalan pembayaran Dealer Utama | `PENDING_LEGAL_VALIDATION` | Dasar, kondisi pemicu, kewenangan, dan konsekuensi perlu pemeriksaan khusus. |
| SME-007 | Target lelang belum tercapai | `NEEDS_REVISION` | Pasal yang diberikan belum membuktikan prosedur lengkap lelang tambahan. |
| SME-008 | Selisih data investor ritel | `PENDING_SME_VALIDATION` | UU mendukung penatausahaan umum, bukan alur rinci rekonsiliasi. |

## Batas Perilaku SAVI

- SAVI tidak boleh menjalankan koreksi, membuka lock, menetapkan hasil lelang, menentukan sanksi, atau mengubah catatan kepemilikan.
- Jawaban tanpa SOP harus menghasilkan `INSUFFICIENT_EVIDENCE` atau arahan eskalasi, bukan langkah yang dikarang.
- Pertanyaan yield tidak boleh berubah menjadi rekomendasi investasi personal.
- Keberadaan pertanyaan di register tidak berarti sumbernya tersedia untuk retrieval.

## Open Question

OQ-36 mencatat kebutuhan pengesahan delapan kasus, sumber hukum per klaim, SOP internal, klasifikasi, dan reviewer berwenang.

## Related Documents

- [rag-testing.md](rag-testing.md)
- [rag-evaluation.md](../05-ai-rag/rag-evaluation.md)
- [citation-policy.md](../05-ai-rag/citation-policy.md)
- [open-questions.md](../00-project/open-questions.md)

## Last Updated

2026-10-13
