# Data Retention

**Status:** NEEDS MENTOR VALIDATION
**Last Updated:** 2026-10-02

## Purpose
Mencatat mekanisme teknis yang mendukung retensi. Tidak ada periode retensi yang ditetapkan karena kebijakannya belum diketahui.

## Confirmed Information
- **OPEN QUESTION** OQ-13 kebijakan retensi dan penghapusan dokumen, audit log, dan percakapan AI.

## Mekanisme yang tersedia
| Data | Mekanisme | Status |
|---|---|---|
| Record bisnis | soft delete `deleted_at`; record terhapus tidak terbaca API | Kolom ada; endpoint hapus belum dibuat |
| Knowledge | status ARCHIVED dan SUPERSEDED | Nilai status ada; alur arsip belum dibuat |
| File dokumen | tetap di document provider; SUNOVATE hanya referensi | Prinsip CONFIRMED |
| Audit log | append-only; tidak ada penghapusan via aplikasi | Trigger ada |
| Percakapan Hermes | `ai_conversations`, `ai_messages` | `DATA_BACKEND=simulated` (default): in-memory, hilang saat restart; `DATA_BACKEND=postgres`: tersimpan di tabel tersebut (ADR-015, PROPOSED); retensi belum ditetapkan |
| Chunk dan embedding | turunan; dapat dihapus dan dibangun ulang | PROPOSED |

## Usulan (PROPOSED)
- Retensi audit mengikuti ketentuan instansi; penghapusan, bila diizinkan, dilakukan oleh DBA dengan prosedur terdokumentasi, bukan oleh aplikasi.
- Percakapan Hermes tidak menyimpan isi pertanyaan di audit log (hanya panjang pertanyaan dan keputusan); retensi isi percakapan menunggu OQ-13.
- Data `SIMULATED_DATA` dapat dibuang kapan saja.

## Related Documents
- [audit-logging.md](../06-security/audit-logging.md)
- [backup-and-restore.md](../11-operations/backup-and-restore.md)
