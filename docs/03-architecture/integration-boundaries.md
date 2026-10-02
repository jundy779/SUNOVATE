# Integration Boundaries

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Menetapkan sumber kebenaran (source of truth) per jenis data dan aturan melewati batas sistem.

## Source of truth
| Data | Sumber kebenaran | Peran SUNOVATE | Status |
|---|---|---|---|
| File dokumen resmi | Document provider yang disetujui (SharePoint atau lainnya) | Menyimpan referensi, metadata, checksum, versi, klasifikasi | CONFIRMED (prinsip), OQ-06 |
| Korespondensi resmi | Kemenkeu Satu | Tidak menyimpan; mungkin referensi di masa depan | CONFIRMED (prinsip) |
| Identitas pegawai | Identity provider instansi | Dev identity saja | OQ-07 |
| Knowledge metadata, ringkasan, relasi | PostgreSQL SUNOVATE | Pemilik data | PROPOSED |
| Output, tugas, pending matters | PostgreSQL SUNOVATE | Pemilik data | PROPOSED |
| Audit log | PostgreSQL SUNOVATE (append-only) | Pemilik data | PROPOSED |
| Chunk FTS dan embedding | Data turunan; dapat dibangun ulang | Indeks | PROPOSED |
| Data transaksi, yield, lelang | Sistem resmi | Tidak disimpan pada scaffold (ADR-013) | OUT OF SCOPE |

## Aturan batas
1. **PROPOSED** Satu provider interface per sistem eksternal; tidak ada panggilan API eksternal di dalam modul bisnis.
2. **CONFIRMED (implementasi)** Semua provider produksi tidak ada; `GET /api/v1/providers` melaporkan `productionReady=false` untuk semua.
3. **PROPOSED** Setiap sinkronisasi dicatat di `integration_sync_logs` dengan `is_production`.
4. **CONFIRMED** Hermes tidak melewati batas API; tidak memegang kredensial DB.
5. **PROPOSED** Data RESTRICTED ke atas tidak dikirim ke kanal eksternal (Telegram/WhatsApp) secara default.

```mermaid
flowchart LR
    M["Modul bisnis"] --> I["Provider interface"]
    I --> D["Implementasi dev / disabled"]
    I -.-> P["Implementasi produksi<br/>belum ada"]
    P -.-> E["Sistem eksternal"]
```

## Related Documents
- [provider-abstraction.md](provider-abstraction.md)
- [integration-overview.md](../08-integrations/integration-overview.md)
- [integration-readiness-checklist.md](../08-integrations/integration-readiness-checklist.md)
