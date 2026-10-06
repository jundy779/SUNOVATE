# Error Format

**Status:** PROPOSED
**Last Updated:** 2026-10-01

## Purpose
Format error yang konsisten untuk semua endpoint `/api/v1` (implementasi: `apps/api/sunovate_api/core/errors.py`).

## Envelope

```json
{
  "code": "REVISION_CONFLICT",
  "message": "Data telah diperbarui oleh pengguna lain. Muat ulang data sebelum menyimpan perubahan.",
  "details": { "currentRevision": 2 },
  "requestId": "6f1c..."
}
```

- `code`: kode stabil untuk logika klien.
- `message`: pesan Bahasa Indonesia untuk pengguna.
- `details`: data tambahan atau `null`.
- `requestId`: sama dengan header `X-Request-ID`.
- Stack trace dan detail internal tidak pernah dikembalikan; error tak tertangani dicatat di log JSON dan dibalas `INTERNAL_ERROR`.

## Kode yang diimplementasikan
| HTTP | Code | Kapan |
|---|---|---|
| 401 | `UNAUTHENTICATED` | tanpa token, token tidak valid atau kedaluwarsa, pengguna simulasi tidak dikenal, dev auth nonaktif |
| 403 | `PERMISSION_DENIED` | permission tidak dimiliki, atau target di luar scope/klasifikasi pada aksi tulis |
| 403 | `SEPARATION_OF_DUTIES` | pengaju mencoba memutuskan approval miliknya |
| 404 | `NOT_FOUND` | record tidak ada **atau** tidak boleh dibaca (BR-20) |
| 404 | `DEV_AUTH_DISABLED` | login dev dipanggil saat dev auth nonaktif |
| 405 | `METHOD_NOT_ALLOWED` | metode HTTP tidak didukung |
| 409 | `REVISION_CONFLICT` | `revision` tidak cocok; `details.currentRevision` |
| 409 | `DUPLICATE_CHECKSUM` | versi dokumen dengan checksum yang sama sudah ada |
| 409 | `INVALID_STATE` | transisi status tidak sah (mis. mengubah knowledge PUBLISHED, memutuskan approval yang sudah diputuskan) |
| 422 | `VALIDATION_ERROR` | body/query tidak valid atau field tidak dikenal |
| 500 | `INTERNAL_ERROR` | error tak tertangani |
| 503 | `DATABASE_UNAVAILABLE` | `/health/database` tidak dapat menjangkau PostgreSQL; pada `DATA_BACKEND=postgres`, koneksi gagal atau database tidak terjangkau |
| 503 | `DATABASE_BUSY` | pada `DATA_BACKEND=postgres`, database terjangkau tetapi menolak atau membatalkan permintaan secara sementara: statement timeout, lock timeout, deadlock, atau serialization failure. Respons memuat header `Retry-After: 5`; klien boleh mengulang |
| 503 | `HERMES_DISABLED` | `HERMES_MODE=disabled` atau `AI_PROVIDER=disabled` |

## Detail validasi

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Input tidak valid",
  "details": [{ "location": ["body", "email"], "message": "String should match pattern ...", "type": "string_pattern_mismatch" }],
  "requestId": "..."
}
```

## Panduan klien
- 401: arahkan ke `/login` (diimplementasikan di `apps/web/src/lib/api.ts`).
- 403: tampilkan halaman `/unauthorized`.
- 404: tampilkan not-found; jangan menyiratkan bahwa record ada.
- 409 `REVISION_CONFLICT`: minta pengguna memuat ulang data.

## Related Documents
- [api-conventions.md](api-conventions.md)
- [endpoint-catalog.md](endpoint-catalog.md)
