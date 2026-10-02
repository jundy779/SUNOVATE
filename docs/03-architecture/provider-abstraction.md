# Provider Abstraction

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Mendokumentasikan interface provider dan implementasi yang ada, agar integrasi produksi dapat ditambahkan tanpa mengubah modul bisnis.

## Interface (`apps/api/sunovate_api/providers/interfaces.py`)
| Interface | Metode | Implementasi saat ini | Setting | Produksi |
|---|---|---|---|---|
| `AIProvider` | `generate(GenerationRequest)` | `DevelopmentExtractiveAIProvider`, `DisabledAIProvider` | `AI_PROVIDER=development_extractive\|disabled` | Belum ada (OQ-11) |
| `EmbeddingProvider` | `embed(texts)` | `DisabledEmbeddingProvider` (raise) | `EMBEDDING_PROVIDER=disabled` | Belum ada |
| `DocumentProvider` | `describe(location)` | `LocalDocumentProvider` (hanya validasi `local://`, tidak membaca file) | `DOCUMENT_PROVIDER=local` | Belum ada (OQ-06) |
| `IdentityProvider` | `resolve_login(email)` | `DevelopmentIdentityProvider` (hanya pengguna `SIMULATED_DATA`) | `IDENTITY_PROVIDER=development` | Belum ada (OQ-07) |
| `NotificationProvider` | `send(...)` | `DisabledNotificationProvider` (selalu `False`) | `NOTIFICATION_PROVIDER=disabled` | Belum ada |
| `HermesClient` | `answer(GenerationRequest)` | `DevelopmentHermesClient` (mendelegasikan ke `AIProvider`) | `HERMES_MODE=development\|disabled` | Belum ada |
| `MarketDataProvider` | - | Tidak diimplementasikan; dilaporkan `not_implemented` | - | Belum ada |

Komponen aplikasi pendukung: `RetrievalService`, `AuthorizationService`, `CitationValidator`, `OutputGuard`, `ScopeGuard`, `HermesGateway` (lihat [hermes-overview.md](../05-ai-rag/hermes-overview.md)).

## Prinsip
- **CONFIRMED (implementasi)** Setting provider memakai tipe `Literal`; nilai provider produksi yang belum ada tidak dapat dikonfigurasi dan akan ditolak saat start.
- **CONFIRMED (implementasi)** Provider pengembangan tidak melakukan panggilan jaringan.
- **PROPOSED** Implementasi produksi baru wajib melewati [integration-readiness-checklist.md](../08-integrations/integration-readiness-checklist.md), contract test, dan ADR baru.
- **PROPOSED** `GenerationRequest` hanya berisi pertanyaan, passage yang sudah diotorisasi, dan term query. Tidak ada identitas atau kredensial.

## Menambah provider (PROPOSED)
1. Implementasikan Protocol di `providers/<nama>.py`.
2. Tambahkan nilai baru ke `Literal` di `core/config.py` dan wiring di `providers/registry.py`.
3. Tambahkan status jujur di `Providers.statuses()`.
4. Tulis test, perbarui dokumen ini dan decision log.

## Related Documents
- [integration-boundaries.md](integration-boundaries.md)
- [technology-stack.md](technology-stack.md)
